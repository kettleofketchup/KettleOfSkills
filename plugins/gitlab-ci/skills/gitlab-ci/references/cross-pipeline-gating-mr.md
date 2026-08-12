# Cross-Pipeline Gating: MR Validation and Scheduled Triggers

Continuation of [cross-pipeline-gating.md](cross-pipeline-gating.md).

## Pattern 4: MR Cross-Validation

Test MR changes against dependent repos before merge.

```yaml
# upstream-repo/.gitlab-ci.yml
cross-validate:
  stage: test
  trigger:
    project: group/downstream-repo
    strategy: depend
  variables:
    UPSTREAM_MR_REF: $CI_MERGE_REQUEST_REF_PATH
    UPSTREAM_SHA: $CI_COMMIT_SHA
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

Downstream picks up the variables and tests against the MR ref:

```yaml
# downstream-repo/.gitlab-ci.yml
validate-upstream-changes:
  stage: test
  script:
    - echo "Testing against upstream ref $UPSTREAM_MR_REF"
    - git clone --branch $UPSTREAM_MR_REF $UPSTREAM_REPO_URL upstream/
    - run-integration-tests
  rules:
    - if: $CI_PIPELINE_SOURCE == "pipeline" && $UPSTREAM_MR_REF
```

## Pattern 5: Scheduled + Manual Triggers

Use `$CI_PIPELINE_SOURCE == "schedule"` rules with the orchestrator pattern
for periodic full rebuilds. Set up: GitLab CI/CD Schedules with cron expression.

For manual buttons, add `when: manual` to any trigger job:

```yaml
manual-rebuild:
  stage: deploy
  trigger:
    project: group/repo
    strategy: depend
  when: manual
  allow_failure: true  # Don't block other jobs
```

### Scheduled rebuild example

```yaml
.schedule-only:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"

scheduled-rebuild:
  stage: build-submodules
  extends: .schedule-only
  trigger:
    project: group/repo
    branch: main
    strategy: depend
```
