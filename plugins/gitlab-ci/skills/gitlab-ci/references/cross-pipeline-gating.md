# Cross-Pipeline Gating Patterns

Patterns for enforcing execution order across multiple GitLab projects.

## Pattern 1: Orchestrator Pipeline

A central "conductor" repo triggers downstream projects in stage order.
Each stage waits for the previous to complete via `strategy: depend`.

```yaml
# orchestrator/.gitlab-ci.yml
stages:
  - build-upstream
  - build-downstream
  - release

# Stage 1: Trigger upstream builds in parallel
build-repo-a:
  stage: build-upstream
  trigger:
    project: group/repo-a
    branch: main
    strategy: depend

build-repo-b:
  stage: build-upstream
  trigger:
    project: group/repo-b
    branch: main
    strategy: depend

# Stage 2: Only runs after all stage 1 jobs succeed
build-repo-c:
  stage: build-downstream
  trigger:
    project: group/repo-c
    branch: main
    strategy: depend
  # Implicitly waits for build-upstream stage

# Stage 3: Final release
release:
  stage: release
  script: echo "All builds complete"
```

**Key**: `strategy: depend` makes the trigger job block until downstream finishes.
Stage ordering ensures sequential execution between stages.

## Pattern 2: Tag Cascade

Version bump in root repo triggers tag pipelines across all sub-repos in order.

```yaml
# root-repo/.gitlab-ci.yml
stages:
  - validate
  - build-infra
  - build-apps
  - assemble
  - publish

# Pass the tag to all downstream
.trigger-base:
  variables:
    RELEASE_TAG: $CI_COMMIT_TAG
  rules:
    - if: $CI_COMMIT_TAG

validate:
  stage: validate
  extends: .trigger-base
  trigger:
    project: group/validation-project
    strategy: depend

build-infra:
  stage: build-infra
  extends: .trigger-base
  trigger:
    project: group/infra-project
    strategy: depend

build-apps:
  stage: build-apps
  extends: .trigger-base
  trigger:
    project: group/apps-project
    strategy: depend

assemble:
  stage: assemble
  extends: .trigger-base
  script:
    - echo "Assemble artifacts from all upstream builds"

publish:
  stage: publish
  extends: .trigger-base
  script:
    - echo "Publish final artifacts"
  when: manual  # Optional manual gate before publishing
```

## Pattern 3: Cross-Pipeline Gate (Repo B Waits for Repo A)

Repo B's tag pipeline has a job that triggers Repo A's build and waits for it.

```yaml
# repo-b/.gitlab-ci.yml (the dependent repo)
stages:
  - wait-for-upstream
  - build
  - deploy

# Gate: trigger Repo A and wait for its build to complete
wait-for-repo-a:
  stage: wait-for-upstream
  trigger:
    project: group/repo-a
    branch: $CI_COMMIT_TAG  # Use same tag in upstream
    strategy: depend         # Block until repo-a finishes
  rules:
    - if: $CI_COMMIT_TAG

# Only runs after repo-a's pipeline succeeds
build:
  stage: build
  script: echo "Repo A's build is complete, safe to proceed"
  rules:
    - if: $CI_COMMIT_TAG
```

**Alternative**: If Repo A already has its own tag pipeline running,
use API polling instead of re-triggering:

```yaml
wait-for-repo-a:
  stage: wait-for-upstream
  script:
    - |
      # Find repo-a's pipeline for this tag
      PIPELINE_ID=$(curl -s --header "PRIVATE-TOKEN: $API_TOKEN" \
        "${CI_API_V4_URL}/projects/${REPO_A_ID}/pipelines?ref=${CI_COMMIT_TAG}&status=running" \
        | jq '.[0].id')
      # Poll until complete
      while true; do
        STATUS=$(curl -s --header "PRIVATE-TOKEN: $API_TOKEN" \
          "${CI_API_V4_URL}/projects/${REPO_A_ID}/pipelines/${PIPELINE_ID}" \
          | jq -r '.status')
        case $STATUS in
          success) echo "Upstream complete"; break ;;
          failed|canceled) echo "Upstream failed"; exit 1 ;;
          *) echo "Waiting... ($STATUS)"; sleep 30 ;;
        esac
      done
  rules:
    - if: $CI_COMMIT_TAG
```

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

Use `$CI_PIPELINE_SOURCE == "schedule"` rules with the orchestrator pattern (Pattern 1)
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
