# Edge Infrastructure: MR Cross-Validation and Scheduled Rebuilds

Continuation of [edge-infra-patterns.md](edge-infra-patterns.md).

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
