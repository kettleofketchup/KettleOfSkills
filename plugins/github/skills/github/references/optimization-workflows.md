# GitHub Actions: Workflow Optimization

## Parallelization

### Matrix Strategies

```yaml
# Basic matrix
strategy:
  fail-fast: false            # Don't cancel siblings
  matrix:
    os: [ubuntu-latest, macos-latest]
    version: [18, 20, 22]

# Sharding tests
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: npm test -- --shard=${{ matrix.shard }}/4

# Dynamic matrix from JSON
jobs:
  setup:
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
      - id: set
        run: echo "matrix=$(jq -c . matrix.json)" >> $GITHUB_OUTPUT

  build:
    needs: setup
    strategy:
      matrix: ${{ fromJSON(needs.setup.outputs.matrix) }}
```

### Parallel Jobs

```yaml
jobs:
  lint:                       # These run in parallel
    runs-on: ubuntu-latest
    steps:
      - run: npm run lint

  typecheck:                  # Parallel with lint
    runs-on: ubuntu-latest
    steps:
      - run: npm run typecheck

  test:                       # Parallel with lint & typecheck
    runs-on: ubuntu-latest
    steps:
      - run: npm test

  build:
    needs: [lint, typecheck, test]  # Waits for all
    runs-on: ubuntu-latest
    steps:
      - run: npm run build
```

## Early Termination

### Path Filters

```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'package.json'
      - '.github/workflows/**'
    paths-ignore:
      - '**.md'
      - 'docs/**'
      - '.vscode/**'
```

### Conditional Jobs

```yaml
jobs:
  changes:
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'api/**'
            frontend:
              - 'web/**'

  backend-tests:
    needs: changes
    if: needs.changes.outputs.backend == 'true'
    # ...

  frontend-tests:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    # ...
```

### Skip Conditions

```yaml
jobs:
  build:
    # Skip for docs-only, drafts, or [skip ci]
    if: |
      !contains(github.event.head_commit.message, '[skip ci]') &&
      !github.event.pull_request.draft &&
      (
        github.event_name != 'pull_request' ||
        !contains(github.event.pull_request.labels.*.name, 'documentation')
      )
```

## Checkout Optimization

```yaml
# Shallow clone (fastest)
- uses: actions/checkout@v4
  with:
    fetch-depth: 1

# Sparse checkout (for monorepos)
- uses: actions/checkout@v4
  with:
    sparse-checkout: |
      packages/my-app
      shared/

# No checkout (for API-only jobs)
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - run: curl -X POST $WEBHOOK_URL
        env:
          WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Self-Hosted Runner Optimization

### Runner Setup

```yaml
runs-on: [self-hosted, linux, x64]

# With container
container:
  image: node:20
  options: --cpus 4 --memory 8g
```

### Persistent Cache

```bash
# Pre-install common dependencies on runner
npm install -g typescript eslint prettier

# Pre-pull Docker images
docker pull node:20
docker pull postgres:15
```

### Cleanup

```yaml
# Add cleanup step
- name: Cleanup
  if: always()
  run: |
    docker system prune -f
    rm -rf node_modules dist
```

## Workflow Optimization Checklist

### Before Running
- [ ] Use `paths` filter to skip irrelevant changes
- [ ] Add `concurrency` to cancel stale runs
- [ ] Set `timeout-minutes` on all jobs

### Parallelization
- [ ] Run independent jobs in parallel
- [ ] Use matrix for multi-version testing
- [ ] Shard large test suites

### Cost Reduction
- [ ] Use ubuntu-latest when possible
- [ ] Shallow checkout with `fetch-depth: 1`
- [ ] Consider self-hosted for high volume
- [ ] Use `if: failure()` for cleanup instead of `always()`
