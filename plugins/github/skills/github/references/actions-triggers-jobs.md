# GitHub Actions: Triggers & Jobs

## Triggers (on)

### Push/Pull Request

```yaml
on:
  push:
    branches: [main, 'release/*']
    branches-ignore: ['feature/*']
    tags: ['v*']
    paths: ['src/**', '*.json']
    paths-ignore: ['**.md', 'docs/**']

  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
    branches: [main]
    paths: ['src/**']

  pull_request_target:        # Runs in base branch context (security!)
    types: [opened]
```

### Scheduled/Manual

```yaml
on:
  schedule:
    - cron: '0 2 * * *'       # Daily at 2am UTC
    - cron: '*/15 * * * *'    # Every 15 minutes

  workflow_dispatch:          # Manual trigger
    inputs:
      environment:
        type: choice
        options: [dev, staging, prod]
        default: dev
      debug:
        type: boolean
        default: false
```

### Other Events

```yaml
on:
  release:
    types: [published, created]
  workflow_call:              # Reusable workflow
    inputs:
      config:
        type: string
        required: true
    secrets:
      token:
        required: true
    outputs:
      result:
        value: ${{ jobs.build.outputs.result }}
  repository_dispatch:        # External trigger
    types: [deploy]
  issue_comment:
    types: [created]
```

## Concurrency

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true          # Cancel older runs
# Queue deploys per environment:
# group: deploy-${{ github.event.inputs.environment }}
# cancel-in-progress: false
```

## Jobs

### Structure & Runners

```yaml
jobs:
  build:
    runs-on: ubuntu-latest        # or: macos-latest (10x), windows-latest (2x)
    # runs-on: [self-hosted, linux]
    # runs-on: { group: my-group, labels: [linux, x64] }
    timeout-minutes: 15
    permissions:
      contents: read
      packages: write
    environment:
      name: production
      url: https://example.com
    defaults:
      run:
        working-directory: ./app
        shell: bash
    env:
      NODE_ENV: production
```

```yaml
runs-on: ubuntu-latest        # GitHub-hosted (default)
runs-on: macos-latest         # macOS (10x cost)
runs-on: windows-latest       # Windows (2x cost)
runs-on: [self-hosted, linux] # Self-hosted with labels
runs-on:
  group: my-runner-group
  labels: [linux, x64]
```

### Dependencies & Outputs

```yaml
jobs:
  build:
    outputs:
      version: ${{ steps.version.outputs.value }}
    steps:
      - id: version
        run: echo "value=1.0.0" >> $GITHUB_OUTPUT
  test:
    needs: build
  deploy:
    needs: [build, test]
    if: success()
    steps:
      - run: echo "${{ needs.build.outputs.version }}"
```

### Matrix

```yaml
strategy:
  fail-fast: false
  max-parallel: 4
  matrix:
    os: [ubuntu-latest, macos-latest]
    node: [18, 20, 22]
    include:
      - os: ubuntu-latest
        node: 22
        coverage: true  # add property to specific combo
    exclude:
      - os: macos-latest
        node: 18        # skip this combination
```

See [actions-jobs-services.md](actions-jobs-services.md) for services and container jobs.