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
  lint:                           # These three run in parallel
    runs-on: ubuntu-latest
    steps: [{ run: npm run lint }]
  typecheck:
    runs-on: ubuntu-latest
    steps: [{ run: npm run typecheck }]
  test:
    runs-on: ubuntu-latest
    steps: [{ run: npm test }]
  build:
    needs: [lint, typecheck, test]
    runs-on: ubuntu-latest
    steps: [{ run: npm run build }]
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

  frontend-tests:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
```

### Skip Conditions

```yaml
jobs:
  build:
    if: |
      !contains(github.event.head_commit.message, '[skip ci]') &&
      !github.event.pull_request.draft
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
```

## Self-Hosted Runner Optimization

```yaml
runs-on: [self-hosted, linux, x64]

# Pre-install on runner
# npm install -g typescript eslint prettier
# docker pull node:20 postgres:15

# Cleanup step
- name: Cleanup
  if: always()
  run: |
    docker system prune -f
    rm -rf node_modules dist
```

## Optimization Checklist

- Use `paths` filter to skip irrelevant changes
- Add `concurrency` to cancel stale runs
- Set `timeout-minutes` on all jobs
- Run independent jobs in parallel
- Shard large test suites
- Use ubuntu-latest (10x cheaper than macos)
- Shallow checkout with `fetch-depth: 1`