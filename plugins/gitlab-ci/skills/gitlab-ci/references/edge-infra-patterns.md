# Edge Infrastructure Pipeline Templates

Ready-to-use patterns for the multi-repo Nix flake architecture
(builder, os, k3s-core, services, docs, utils).

## Architecture: Pipeline Dependencies

```
utils ──────────────────────────────────────┐
  │                                         │
  ├── triggers → os.flake pipeline          │
  ├── triggers → k3s-core.flake pipeline    │
  └── triggers → services.flake pipeline    │
                                            │
builder (orchestrator for tags) ────────────┘
  Stage 1: trigger k3s-core + services (parallel, strategy: depend)
  Stage 2: build ISO + combined images (uses artifacts from stage 1)
  Stage 3: upload ISO, push cache, release
```

## Template: Utils Triggers Downstream Repos

When utils changes on main, trigger rebuilds in dependent repos.

```yaml
# utils/.gitlab-ci.yml (add to existing)
stages:
  - validate
  - build
  - trigger-downstream

# Existing jobs...

trigger-os:
  stage: trigger-downstream
  trigger:
    project: inf/flakes/os.flake
    branch: main
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

trigger-k3s-core:
  stage: trigger-downstream
  trigger:
    project: inf/flakes/k3s-core.flake
    branch: main
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

trigger-services:
  stage: trigger-downstream
  trigger:
    project: inf/flakes/services.flake
    branch: main
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Template: Builder Tag Cascade Orchestrator

Builder triggers submodule pipelines in order on tag push, waits for completion.

```yaml
# builder/.gitlab-ci.yml (tag pipeline additions)
stages:
  - validate
  - build-submodules     # NEW: trigger sub-repo builds
  - build                # Existing: build ISO, images
  - upload
  - publish

# Reusable trigger base
.tag-trigger:
  rules:
    - if: $CI_COMMIT_TAG
  variables:
    RELEASE_TAG: $CI_COMMIT_TAG

# Stage: build-submodules — trigger and wait for sub-repos
trigger-k3s-core:
  stage: build-submodules
  extends: .tag-trigger
  trigger:
    project: inf/flakes/k3s-core.flake
    branch: main
    strategy: depend  # Wait for k3s-core build to finish

trigger-services:
  stage: build-submodules
  extends: .tag-trigger
  trigger:
    project: inf/flakes/services.flake
    branch: main
    strategy: depend  # Wait for services build to finish

# Stage: build — only runs after sub-repo builds complete
# These jobs use artifacts already pushed to Attic by sub-repos
build-iso:
  stage: build
  extends: [.nix-with-submodules]
  script:
    - nix build .#iso $NIX_OVERRIDE_INPUTS
  rules:
    - if: $CI_COMMIT_TAG

build-all-images:
  stage: build
  extends: [.nix-with-submodules]
  script:
    - nix build .#allImages $NIX_OVERRIDE_INPUTS $NIX_SANDBOX_PATHS
  rules:
    - if: $CI_COMMIT_TAG
```

## Template: Cross-Pipeline Gate (Services Waits for K3s-Core)

Services tag pipeline waits for k3s-core to finish building before proceeding.

```yaml
# services/.gitlab-ci.yml (tag pipeline additions)
stages:
  - wait-upstream
  - pin
  - validate
  - build
  - cache

wait-for-k3s-core:
  stage: wait-upstream
  trigger:
    project: inf/flakes/k3s-core.flake
    branch: main
    strategy: depend
  rules:
    - if: $CI_COMMIT_TAG

# Existing jobs now gated behind wait-upstream stage
pin-images:
  stage: pin
  # ... existing config
  rules:
    - if: $CI_COMMIT_TAG
```

**Alternative**: If both repos have independent tag pipelines (from `just git::version`),
use the API polling pattern from [cross-pipeline-gating.md](cross-pipeline-gating.md#pattern-3-cross-pipeline-gate-repo-b-waits-for-repo-a)
with `CI_JOB_TOKEN` header and k3s-core project ID.

## Template: MR Cross-Validation (Test K3s-Core Changes Against Builder)

When a MR is opened in k3s-core, validate it builds correctly in builder context.

```yaml
# k3s-core/.gitlab-ci.yml (MR pipeline addition)
cross-validate-builder:
  stage: test
  trigger:
    project: inf/flakes/builder
    strategy: depend
  variables:
    K3S_CORE_MR_REF: $CI_COMMIT_REF_NAME
    K3S_CORE_SHA: $CI_COMMIT_SHA
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

Builder handles the cross-validation:

```yaml
# builder/.gitlab-ci.yml (cross-validation handler)
cross-validate-k3s-core:
  stage: validate
  extends: .nix-with-submodules
  script:
    - cd k3s-core && git fetch origin $K3S_CORE_MR_REF && git checkout $K3S_CORE_SHA
    - cd .. && nix flake check $NIX_OVERRIDE_INPUTS
  rules:
    - if: $CI_PIPELINE_SOURCE == "pipeline" && $K3S_CORE_MR_REF
```

## Template: Scheduled Full Rebuild + Manual Buttons

Add to builder. Use scheduled pipeline (CI/CD Schedules, e.g. `0 2 * * 0`):

```yaml
# builder/.gitlab-ci.yml — add these jobs
.schedule-only:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"

scheduled-rebuild-k3s:
  stage: build-submodules
  extends: .schedule-only
  trigger:
    project: inf/flakes/k3s-core.flake
    branch: main
    strategy: depend

scheduled-rebuild-services:
  stage: build-submodules
  extends: .schedule-only
  trigger:
    project: inf/flakes/services.flake
    branch: main
    strategy: depend
```

For manual buttons, add `when: manual` and `allow_failure: true`:

```yaml
manual-rebuild-k3s:
  stage: build-submodules
  trigger:
    project: inf/flakes/k3s-core.flake
    branch: main
    strategy: depend
  when: manual
  allow_failure: true
```

## Integration Notes

- Triggering user needs Developer access in downstream projects
- `CI_JOB_TOKEN` works for same-instance API calls
- `just git::version` tags all repos — builder orchestrates the rest
- Group CI/CD vars (`ATTIC_TOKEN`, `VCENTER_*`) auto-available in downstream
- Sub-repos need `$CI_PIPELINE_SOURCE == "pipeline"` added to workflow rules
