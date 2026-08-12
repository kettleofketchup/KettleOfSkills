---
name: github
version: 1.2.0
updated: 2026-05-18
description: GitHub CLI (gh) and Actions workflow development. Use for gh PRs, issues, releases, API, Actions triggers/jobs/steps, caching, matrix builds, self-hosted runners, setup-node, or browser test caching.
---

# GitHub

## Overview

Comprehensive GitHub development covering the `gh` CLI for repository operations and GitHub Actions for CI/CD automation, with emphasis on workflow optimization and cost reduction.

## Related skills

- **[copilot](../copilot/SKILL.md)** — GitHub Copilot PR code review setup, `.github/copilot-instructions.md` authoring, and bridging Copilot config to `.claude/skills/`.

## gh CLI Quick Reference

```bash
# Auth
gh auth login                    # Interactive login
gh auth status                   # Check auth state
gh auth token                    # Print token

# PRs
gh pr create --fill              # Create PR, auto-fill title/body from commits
gh pr list --state open
gh pr checkout 123
gh pr merge 123 --squash

# Issues
gh issue create --title "Bug" --body "Description" --label bug
gh issue list --assignee @me

# Releases
gh release create v1.0.0 --generate-notes

# API
gh api repos/{owner}/{repo}/actions/runs --jq '.workflow_runs[].status'
gh api graphql -f query='{ viewer { login } }'
```

See [gh-cli.md](references/gh-cli.md) and [gh-cli-advanced.md](references/gh-cli-advanced.md) for complete reference.

## GitHub Actions Workflow Structure

```yaml
name: CI
on:
  push:
    branches: [main]
    paths-ignore: ['**.md']
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

See [actions-triggers-jobs.md](references/actions-triggers-jobs.md) and [actions-steps-expressions.md](references/actions-steps-expressions.md) for full details.

## Key Optimization Techniques

| Technique | Savings |
|-----------|---------|
| Use ubuntu-latest over macos-latest | 10x cheaper |
| Shallow clone: `fetch-depth: 1` | Faster checkout |
| Cache dependencies via setup-action | 50-80% faster |
| Parallel matrix jobs | Wall-clock time |
| `timeout-minutes` on jobs | Prevent runaways |
| `concurrency.cancel-in-progress` | Kill stale runs |

See [optimization-caching.md](references/optimization-caching.md) and [optimization-workflows.md](references/optimization-workflows.md) for advanced patterns.

## Debugging Workflows

```yaml
env:
  ACTIONS_STEP_DEBUG: true

- run: echo '${{ toJSON(github) }}'
- uses: mxschmitt/action-tmate@v3
  if: failure()
```

Local testing: `act push`, `act -j build`, `act --secret-file .secrets`

## Resources

- [gh-cli.md](references/gh-cli.md) - Core gh commands (PRs, issues, releases, repos, runs)
- [gh-cli-advanced.md](references/gh-cli-advanced.md) - API, secrets, extensions, config, patterns
- [actions-triggers-jobs.md](references/actions-triggers-jobs.md) - Triggers, concurrency, jobs, matrix, runners
- [actions-jobs-services.md](references/actions-jobs-services.md) - Services containers and container jobs
- [actions-steps-expressions.md](references/actions-steps-expressions.md) - Steps, contexts, expressions, secrets
- [optimization-caching.md](references/optimization-caching.md) - Dependency, build, Docker layer caching
- [optimization-workflows.md](references/optimization-workflows.md) - Parallelization, path filters, self-hosted runners
- [nodejs.md](references/nodejs.md) - Node.js/npm/pnpm/yarn, Playwright/Cypress caching, monorepos
- **[copilot skill](../copilot/SKILL.md)** - Copilot PR review and custom instructions
