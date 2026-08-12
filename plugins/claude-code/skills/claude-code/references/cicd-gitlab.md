# CI/CD Integration — GitLab CI/CD

Integrate Claude Code into GitLab CI/CD pipelines.

## Basic Pipeline

**.gitlab-ci.yml:**
```yaml
stages:
  - review
  - test
  - deploy

claude-review:
  stage: review
  image: node:18
  script:
    - npm install -g @anthropic-ai/claude-code
    - claude login --api-key $ANTHROPIC_API_KEY
    - claude '/fix:types && /test'
  only:
    - merge_requests
```

## Advanced Pipeline

```yaml
variables:
  CLAUDE_MODEL: "claude-sonnet-4-5-20250929"

stages:
  - lint
  - test
  - review
  - deploy

before_script:
  - npm install -g @anthropic-ai/claude-code
  - claude login --api-key $ANTHROPIC_API_KEY

lint:
  stage: lint
  script:
    - claude '/fix:types'
  artifacts:
    paths: [src/]
    expire_in: 1 hour

test:
  stage: test
  script:
    - npm test || claude '/fix:test analyze failures and fix'
  coverage: '/Coverage: \d+\.\d+%/'

review:
  stage: review
  script:
    - |
      claude "Review this MR: check code quality, verify tests,
      review security, assess performance" > review.md
  artifacts:
    reports:
      codequality: review.md
  only:
    - merge_requests

deploy:
  stage: deploy
  script:
    - claude '/deploy-check'
    - ./deploy.sh
  only:
    - main
```

## Automated Fixes on Failure

```yaml
fix-on-failure:
  stage: test
  script:
    - npm test
  retry:
    max: 2
    when:
      - script_failure
  after_script:
    - |
      if [ $CI_JOB_STATUS == 'failed' ]; then
        claude '/fix:test analyze CI logs and fix issues'
        git add . && git commit -m "fix: auto-fix from CI"
        git push origin HEAD:$CI_COMMIT_REF_NAME
      fi
```

## Common Patterns

### PR Comment Bot / Parallel Jobs / Caching

```yaml
# Save MR review as artifact
review:
  script: [claude "review this MR" > review.md]
  artifacts: { expose_as: 'Claude Review', paths: [review.md] }

# Parallel sharding
test:
  parallel: 3
  script: [claude "/test --shard $CI_NODE_INDEX/$CI_NODE_TOTAL"]

# Cache
cache:
  key: claude-cache
  paths: [.claude/cache]
```

## Security Best Practices

**Store API key:**
```
Settings → CI/CD → Variables
Add: ANTHROPIC_API_KEY (Protected, Masked)
```

**Restrict clone depth:**
```yaml
variables:
  GIT_STRATEGY: clone
  GIT_DEPTH: 1
```

## Monitoring & Debugging

```yaml
debug:
  script:
    - echo "Pipeline: $CI_PIPELINE_ID | Job: $CI_JOB_ID | Branch: $CI_COMMIT_BRANCH"

artifacts:
  paths: [claude-output.md]
  expire_in: 1 week
```

## See Also

- GitHub Actions: `references/cicd-github.md`
- GitLab CI docs: https://docs.gitlab.com/ee/ci/
