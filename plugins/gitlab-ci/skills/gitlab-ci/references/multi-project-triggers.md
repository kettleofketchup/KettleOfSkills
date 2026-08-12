# Multi-Project Trigger Reference

## Trigger Mechanisms Comparison

| Mechanism | Direction | Sync | Use Case |
|-----------|-----------|------|----------|
| `trigger: project:` | Parent→child | Optional | Explicit downstream trigger |
| `trigger:` + `strategy: depend` | Parent→child | Yes | Wait for downstream completion |
| `needs: project:` | Child←parent | N/A | Fetch artifacts from another project |
| Pipeline subscriptions | Auto | No | Auto-trigger on upstream tag completion |
| API trigger token | External→project | No | Trigger from scripts, webhooks, other CI |
| `CI_JOB_TOKEN` API call | Job→project | No | Trigger from within a running job |

## Trigger Job Syntax

### Basic multi-project trigger

```yaml
trigger_downstream:
  stage: deploy
  trigger:
    project: group/subgroup/project  # Full project path
    branch: main                      # Target branch (optional)
```

### With strategy: depend

```yaml
trigger_and_wait:
  stage: deploy
  trigger:
    project: group/project
    branch: main
    strategy: depend
```

### With rules

```yaml
trigger_on_tag_only:
  stage: deploy
  trigger:
    project: group/project
  rules:
    - if: $CI_COMMIT_TAG
      variables:
        RELEASE_TAG: $CI_COMMIT_TAG

trigger_on_main_push:
  stage: deploy
  trigger:
    project: group/project
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Variable Passing

### Inline variables

```yaml
trigger_with_vars:
  variables:
    UPSTREAM_PROJECT: $CI_PROJECT_NAME
    UPSTREAM_SHA: $CI_COMMIT_SHA
    UPSTREAM_TAG: $CI_COMMIT_TAG
    CUSTOM_VAR: "my-value"
  trigger:
    project: group/project
```

### Dotenv artifact variables

```yaml
generate_vars:
  stage: build
  script:
    - echo "BUILD_VERSION=$(cat version.yaml | yq .version)" >> build.env
  artifacts:
    reports:
      dotenv: build.env

trigger_downstream:
  stage: deploy
  trigger:
    project: group/project
  # BUILD_VERSION automatically available in downstream
```

### Block inherited variables

```yaml
trigger_clean:
  inherit:
    variables: false  # Don't pass parent pipeline variables
  variables:
    ONLY_THIS: "value"
  trigger:
    project: group/project
```

## Cross-Project Artifact Fetching

Requires: GitLab 15.9+, downstream project in job token scope allowlist.

```yaml
use_upstream_artifacts:
  stage: test
  script:
    - ls upstream-artifacts/
  needs:
    - project: group/upstream-project
      job: build_job
      ref: main
      artifacts: true
```

Multiple upstream sources:

```yaml
aggregate_job:
  needs:
    - project: group/project-a
      job: build
      ref: main
      artifacts: true
    - project: group/project-b
      job: build
      ref: main
      artifacts: true
```

## Pipeline Subscriptions

Auto-trigger on upstream tag pipeline completion. Setup: Settings → CI/CD → Pipeline subscriptions.

- Max 2 per project; runs subscribing project's default branch pipeline

```yaml
from_subscription:
  rules:
    - if: $CI_PIPELINE_SOURCE == "pipeline"
  script: echo "Triggered by upstream subscription"
```

## More: API Triggers and Pipeline Source Values

See [multi-project-triggers-api.md](multi-project-triggers-api.md).
