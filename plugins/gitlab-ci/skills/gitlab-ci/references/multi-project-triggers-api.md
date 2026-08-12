# Multi-Project Triggers: API and Pipeline Source

Continuation of [multi-project-triggers.md](multi-project-triggers.md).

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
