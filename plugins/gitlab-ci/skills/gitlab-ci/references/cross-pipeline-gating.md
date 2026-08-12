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

build-repo-c:
  stage: build-downstream
  trigger:
    project: group/repo-c
    branch: main
    strategy: depend

release:
  stage: release
  script: echo "All builds complete"
```

**Key**: `strategy: depend` makes the trigger job block until downstream finishes.

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

publish:
  stage: publish
  extends: .trigger-base
  script:
    - echo "Publish final artifacts"
  when: manual
```

## Pattern 3: Cross-Pipeline Gate (Repo B Waits for Repo A)

```yaml
# repo-b/.gitlab-ci.yml
stages:
  - wait-for-upstream
  - build

wait-for-repo-a:
  stage: wait-for-upstream
  trigger:
    project: group/repo-a
    branch: $CI_COMMIT_TAG
    strategy: depend
  rules:
    - if: $CI_COMMIT_TAG

build:
  stage: build
  script: echo "Repo A's build is complete"
  rules:
    - if: $CI_COMMIT_TAG
```

**Alternative**: If Repo A has its own tag pipeline running, use API polling:

```yaml
wait-for-repo-a:
  stage: wait-for-upstream
  script:
    - |
      PIPELINE_ID=$(curl -s --header "PRIVATE-TOKEN: $API_TOKEN" \
        "${CI_API_V4_URL}/projects/${REPO_A_ID}/pipelines?ref=${CI_COMMIT_TAG}&status=running" \
        | jq '.[0].id')
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

## More Patterns

- [MR Cross-Validation and Scheduled/Manual Triggers](cross-pipeline-gating-mr.md)
