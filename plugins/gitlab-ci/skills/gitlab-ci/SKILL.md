---
name: gitlab-ci
description: "GitLab CI/CD multi-project orchestration and Catalog publishing. Use for trigger jobs, cross-pipeline gating, tag cascades, strategy:depend, multi-repo .gitlab-ci.yml, or Catalog components."
---

# GitLab CI Multi-Project Pipelines

## Overview

Orchestrate CI/CD pipelines across multiple GitLab projects using trigger jobs,
cross-pipeline dependencies, and pipeline subscriptions. Covers patterns from simple
downstream triggers to complex tag cascade orchestration.

## Trigger Mechanism Decision Tree

```
Need cross-project pipeline orchestration?
├── One repo triggers another's pipeline
│   ├── Fire-and-forget → trigger: (default)
│   └── Wait for completion → trigger: + strategy: depend
├── Repo B depends on Repo A's artifacts
│   └── needs: project: + job: + ref: + artifacts: true
├── Orchestrate multiple repos in sequence
│   └── Orchestrator pattern: parent triggers children via stages
├── Auto-trigger on upstream completion
│   └── Pipeline subscriptions (Settings > CI/CD)
└── Tag/release cascade across repos
    └── Orchestrator with strategy: depend per stage
```

## Core Patterns

### 1. Downstream Trigger (Fire-and-Forget)

```yaml
trigger_downstream:
  stage: deploy
  trigger:
    project: my-group/downstream-project
    branch: main
```

### 2. Synchronous Trigger (Wait for Completion)

```yaml
trigger_downstream:
  stage: deploy
  trigger:
    project: my-group/downstream-project
    branch: main
    strategy: depend  # Parent job status mirrors downstream result
```

### 3. Cross-Project Artifact Dependency

```yaml
# In downstream project - fetch artifacts from upstream
consume_artifacts:
  stage: test
  script: cat artifact.txt
  needs:
    - project: my-group/upstream-project
      job: build_artifacts
      ref: main
      artifacts: true
```

### 4. Conditional Triggers

```yaml
trigger_on_tag:
  stage: deploy
  trigger:
    project: my-group/downstream-project
  rules:
    - if: $CI_COMMIT_TAG
```

### 5. Passing Variables Downstream

```yaml
trigger_with_vars:
  stage: deploy
  variables:
    UPSTREAM_VERSION: $CI_COMMIT_TAG
    UPSTREAM_REF: $CI_COMMIT_SHA
  trigger:
    project: my-group/downstream-project
```

## Pipeline Auto-Cancel and Interruptible Jobs

Cancel redundant pipelines on new commits. Set `workflow.auto_cancel.on_new_commit` (GitLab 16.10+):
- `conservative` (default) — cancel if no `interruptible: false` jobs started
- `interruptible` — cancel only jobs with `interruptible: true`
- `none` — never auto-cancel

```yaml
workflow:
  auto_cancel:
    on_new_commit: interruptible

default:
  interruptible: true

publish-binary:
  stage: publish
  interruptible: false  # Never cancel mid-upload
```

## Key Constraints

- Max 1000 downstream pipelines per hierarchy
- Parent-child pipelines: max depth of 2 levels
- Triggering user needs Developer access in downstream project
- `needs: project:` requires GitLab 15.9+ and job token scope allowlist
- Cannot use CI/CD variables in `include:` sections
- Pipeline subscriptions: max 2 per project (self-managed configurable)
- Pipeline subscriptions only trigger on tag pipeline completion

## CI/CD Catalog Component Publishing

See [CI/CD Catalog Publishing](references/cicd-catalog-publishing.md) for full
patterns. Key invariants:

- Publish job needs `image: registry.gitlab.com/gitlab-org/release-cli:latest`
- Org CA trust: use temp bundle + `export SSL_CERT_FILE` (not `/etc/ssl/certs`)
- CA variable must be Type: File; Protect OFF unless tag is protected
- Catalog browse API may 404 on some tiers; use CI lint API to verify instead

## References

Detailed patterns, templates, and architecture-specific configurations:

- [Multi-Project Trigger Reference](references/multi-project-triggers.md) — trigger mechanisms, variable passing, artifact sharing, pipeline subscriptions; [API triggers + pipeline source values](references/multi-project-triggers-api.md)
- [Cross-Pipeline Gating Patterns](references/cross-pipeline-gating.md) — orchestrator pattern, tag cascade, API polling; [MR validation + scheduled/manual triggers](references/cross-pipeline-gating-mr.md)
- [Edge Infrastructure Templates](references/edge-infra-patterns.md) — multi-repo Nix flake (builder/os/k3s-core/services); [MR cross-validation + scheduled rebuilds](references/edge-infra-patterns-advanced.md)
- [CI/CD Catalog Publishing](references/cicd-catalog-publishing.md) — building + publishing reusable components, runner-fleet quirks, CA trust for release-cli, recovery

## External Docs

- [GitLab Downstream Pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/)
- [Pipeline Architecture](https://docs.gitlab.com/ci/pipelines/pipeline_architectures/)
- [CI/CD Pipelines](https://docs.gitlab.com/ci/pipelines/)
