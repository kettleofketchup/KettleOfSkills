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
  - build-submodules
  - build
  - upload
  - publish

.tag-trigger:
  rules:
    - if: $CI_COMMIT_TAG
  variables:
    RELEASE_TAG: $CI_COMMIT_TAG

trigger-k3s-core:
  stage: build-submodules
  extends: .tag-trigger
  trigger:
    project: inf/flakes/k3s-core.flake
    branch: main
    strategy: depend

trigger-services:
  stage: build-submodules
  extends: .tag-trigger
  trigger:
    project: inf/flakes/services.flake
    branch: main
    strategy: depend

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
```

**Alternative**: Use the API polling pattern from
[cross-pipeline-gating.md](cross-pipeline-gating.md#pattern-3-cross-pipeline-gate-repo-b-waits-for-repo-a)
with `CI_JOB_TOKEN` header and k3s-core project ID.

## Integration Notes

- Triggering user needs Developer access in downstream projects
- `CI_JOB_TOKEN` works for same-instance API calls
- `just git::version` tags all repos — builder orchestrates the rest
- Group CI/CD vars (`ATTIC_TOKEN`, `VCENTER_*`) auto-available in downstream
- Sub-repos need `$CI_PIPELINE_SOURCE == "pipeline"` added to workflow rules

## More Templates

- [MR Cross-Validation and Scheduled Rebuilds](edge-infra-patterns-advanced.md)
