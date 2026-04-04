---
name: gitlab-ci
description: "GitLab CI/CD multi-project pipeline orchestration and cross-pipeline dependencies. This skill should be used when configuring trigger jobs to start downstream pipelines in other GitLab projects, implementing cross-pipeline gating (Repo B waits for Repo A's build), setting up tag cascade pipelines across multiple repos, creating pipeline subscriptions, passing variables between pipelines, using strategy depend for synchronous triggers, building scheduled cross-project rebuilds, MR cross-validation against dependent repos, manual orchestration buttons, or writing .gitlab-ci.yml files with multi-project trigger patterns. Covers both generic GitLab CI patterns and edge infrastructure-specific templates for multi-repo Nix flake architectures."
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

## Key Constraints

- Max 1000 downstream pipelines per hierarchy
- Parent-child pipelines: max depth of 2 levels
- Triggering user needs Developer access in downstream project
- `needs: project:` requires GitLab 15.9+ and job token scope allowlist
- Cannot use CI/CD variables in `include:` sections
- Pipeline subscriptions: max 2 per project (self-managed configurable)
- Pipeline subscriptions only trigger on tag pipeline completion

## References

Detailed patterns, templates, and architecture-specific configurations:

- [Multi-Project Trigger Reference](references/multi-project-triggers.md) — all trigger
  mechanisms, variable passing, artifact sharing, pipeline subscriptions
- [Cross-Pipeline Gating Patterns](references/cross-pipeline-gating.md) — orchestrator
  pattern, sequential stage triggers, tag cascade, scheduled rebuilds
- [Edge Infrastructure Templates](references/edge-infra-patterns.md) — ready-to-use
  templates for multi-repo Nix flake architecture with builder/os/k3s-core/services

## External Docs

- [GitLab Downstream Pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/)
- [Pipeline Architecture](https://docs.gitlab.com/ci/pipelines/pipeline_architectures/)
- [CI/CD Pipelines](https://docs.gitlab.com/ci/pipelines/)
