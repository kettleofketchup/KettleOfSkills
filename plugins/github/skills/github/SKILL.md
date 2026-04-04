---
name: github
version: 1.1.0
updated: 2026-02-01
description: GitHub CLI (gh) and GitHub Actions workflow development. This skill should be used when working with gh commands (PRs, issues, releases, API), writing GitHub Actions workflows, configuring workflow triggers/jobs/steps, optimizing CI/CD pipelines with caching/parallelization, reducing action minutes, matrix builds, self-hosted runners, debugging workflow failures, setting up Node.js/npm/pnpm/yarn with actions/setup-node, or caching Playwright/Cypress browsers.
---

# GitHub

## Overview

Comprehensive GitHub development covering the `gh` CLI for repository operations and GitHub Actions for CI/CD automation, with emphasis on workflow optimization and cost reduction.

## gh CLI Quick Reference

Authentication and common operations:

```bash
# Auth
gh auth login                    # Interactive login
gh auth status                   # Check auth state
gh auth token                    # Print token

# PRs
gh pr create --fill              # Create PR, auto-fill title/body from commits
gh pr create --base main --head feature --title "Title" --body "Body"
gh pr list --state open          # List open PRs
gh pr view 123                   # View PR details
gh pr checkout 123               # Checkout PR branch
gh pr merge 123 --squash         # Squash merge

# Issues
gh issue create --title "Bug" --body "Description" --label bug
gh issue list --assignee @me     # My assigned issues
gh issue close 123 --reason completed

# Releases
gh release create v1.0.0 --generate-notes
gh release upload v1.0.0 ./dist/*

# API (powerful for automation)
gh api repos/{owner}/{repo}/actions/runs --jq '.workflow_runs[].status'
gh api graphql -f query='{ viewer { login } }'
```

See [gh-cli.md](references/gh-cli.md) for complete command reference.

## GitHub Actions Workflow Structure

```yaml
name: CI
on:
  push:
    branches: [main]
    paths-ignore: ['**.md']      # Skip docs-only changes
  pull_request:
    branches: [main]
  workflow_dispatch:              # Manual trigger

concurrency:                      # Cancel in-flight runs
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest        # or: self-hosted, macos-latest, windows-latest
    timeout-minutes: 10           # Prevent runaway jobs
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'            # Built-in caching
      - run: npm ci
      - run: npm test
```

See [actions-triggers-jobs.md](references/actions-triggers-jobs.md) and [actions-steps-expressions.md](references/actions-steps-expressions.md) for triggers, contexts, expressions, and job configuration.

## Optimization Strategies

### 1. Caching (Biggest Impact)

```yaml
# Dependency caching - use setup-action's built-in cache
- uses: actions/setup-node@v4
  with:
    cache: 'npm'                  # Also: yarn, pnpm

# Custom cache for build artifacts
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache
      .build
    key: ${{ runner.os }}-build-${{ hashFiles('**/lockfile') }}
    restore-keys: |
      ${{ runner.os }}-build-
```

### 2. Parallelization

```yaml
# Matrix builds - run variants in parallel
jobs:
  test:
    strategy:
      fail-fast: false            # Don't cancel siblings on failure
      matrix:
        os: [ubuntu-latest, macos-latest]
        node: [18, 20, 22]
    runs-on: ${{ matrix.os }}

# Split large test suites
  test-shard:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npm test -- --shard=${{ matrix.shard }}/4
```

### 3. Early Termination

```yaml
# Path filters - skip irrelevant changes
on:
  push:
    paths:
      - 'src/**'
      - 'package.json'
    paths-ignore:
      - '**.md'
      - 'docs/**'

# Conditional jobs
jobs:
  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

# Skip CI commits
    if: "!contains(github.event.head_commit.message, '[skip ci]')"
```

### 4. Reduce Minutes

| Technique | Savings |
|-----------|---------|
| Use `ubuntu-latest` over `macos-latest` | 10x cheaper |
| Shallow clone: `fetch-depth: 1` | Faster checkout |
| Cache dependencies | 50-80% faster installs |
| Parallel matrix jobs | Wall-clock time |
| `timeout-minutes` on jobs | Prevent runaways |
| `concurrency.cancel-in-progress` | Kill stale runs |

See [optimization-caching.md](references/optimization-caching.md) and [optimization-workflows.md](references/optimization-workflows.md) for advanced patterns including Docker layer caching, artifact strategies, and self-hosted runner optimization.

## Common Patterns

### Reusable Workflows

```yaml
# .github/workflows/reusable-build.yml
on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '20'

# Caller workflow
jobs:
  build:
    uses: ./.github/workflows/reusable-build.yml
    with:
      node-version: '22'
```

### Composite Actions

```yaml
# .github/actions/setup/action.yml
name: 'Setup'
runs:
  using: composite
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    - run: npm ci
      shell: bash
```

### Job Dependencies

```yaml
jobs:
  build:
    # ...
  test:
    needs: build
  deploy:
    needs: [build, test]
    if: success()              # Only if all dependencies passed
```

## Debugging Workflows

```yaml
# Enable debug logging
env:
  ACTIONS_STEP_DEBUG: true

# Dump contexts
- run: echo '${{ toJSON(github) }}'
- run: echo '${{ toJSON(env) }}'

# SSH into runner (act or tmate)
- uses: mxschmitt/action-tmate@v3
  if: failure()
```

Local testing with `act`:
```bash
act push                         # Simulate push event
act -j build                     # Run specific job
act --secret-file .secrets       # With secrets
```

## Resources

- [gh-cli.md](references/gh-cli.md) - Complete gh command reference
- [actions-triggers-jobs.md](references/actions-triggers-jobs.md) - Workflow triggers, concurrency, jobs, matrix, runners, services
- [actions-steps-expressions.md](references/actions-steps-expressions.md) - Steps, conditionals, contexts, expressions, secrets, artifacts
- [optimization-caching.md](references/optimization-caching.md) - Dependency caching, build cache, Docker layer caching
- [optimization-workflows.md](references/optimization-workflows.md) - Parallelization, path filters, conditional jobs, checkout optimization
- [nodejs.md](references/nodejs.md) - Node.js/npm/pnpm/yarn setup, Playwright/Cypress caching, monorepo patterns
