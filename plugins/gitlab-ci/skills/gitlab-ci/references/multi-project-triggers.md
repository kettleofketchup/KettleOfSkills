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
    branch: main                      # Target branch (optional, defaults to default branch)
```

### With strategy: depend

Block until downstream completes. Parent job status mirrors downstream result.

```yaml
trigger_and_wait:
  stage: deploy
  trigger:
    project: group/project
    branch: main
    strategy: depend
  # If downstream fails, this job fails → upstream pipeline fails
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

Variables from dotenv artifacts automatically pass to downstream triggers.

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
# In downstream .gitlab-ci.yml
use_upstream_artifacts:
  stage: test
  script:
    - ls upstream-artifacts/
  needs:
    - project: group/upstream-project
      job: build_job          # Job name in upstream
      ref: main               # Branch/tag in upstream
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

Auto-trigger pipeline when upstream project's tag pipeline finishes.

**Setup**: Settings → CI/CD → Pipeline subscriptions → Add `namespace/project`

**Behavior**:
- Triggers on tag pipeline completion (success, failure, or cancel)
- Runs subscribing project's default branch pipeline
- Upstream must be public (or accessible)
- Max 2 subscriptions per project (self-managed: configurable)

**Detect subscription trigger** in downstream:

```yaml
from_subscription:
  rules:
    - if: $CI_PIPELINE_SOURCE == "pipeline"
  script: echo "Triggered by upstream subscription"
```

## API Trigger

Create trigger token: Settings → CI/CD → Pipeline trigger tokens.

```yaml
# From a CI job in another project
trigger_via_api:
  script:
    - >
      curl --request POST
      --form "token=$TRIGGER_TOKEN"
      --form "ref=main"
      --form "variables[UPSTREAM_TAG]=$CI_COMMIT_TAG"
      "https://gitlab.example.com/api/v4/projects/${PROJECT_ID}/trigger/pipeline"
```

Using `CI_JOB_TOKEN` (no trigger token needed, same GitLab instance):

```yaml
trigger_via_job_token:
  script:
    - >
      curl --request POST
      --form "token=$CI_JOB_TOKEN"
      --form "ref=main"
      "${CI_API_V4_URL}/projects/${DOWNSTREAM_ID}/trigger/pipeline"
```

## Detecting Pipeline Source

Use `$CI_PIPELINE_SOURCE` to conditionally run jobs:

| Value | Meaning |
|-------|---------|
| `pipeline` | Triggered by multi-project trigger or subscription |
| `parent_pipeline` | Triggered by parent (child pipeline) |
| `trigger` | Triggered by API trigger token |
| `schedule` | Triggered by scheduled pipeline |
| `web` | Triggered by "Run pipeline" button |
| `merge_request_event` | Triggered by MR |
