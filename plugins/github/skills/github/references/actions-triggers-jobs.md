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
  cancel-in-progress: true    # Cancel older runs

# Per-environment concurrency
concurrency:
  group: deploy-${{ github.event.inputs.environment }}
  cancel-in-progress: false   # Queue deploys
```

## Jobs

### Basic Structure

```yaml
jobs:
  build:
    name: Build Application
    runs-on: ubuntu-latest
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

### Runners

```yaml
runs-on: ubuntu-latest        # GitHub-hosted
runs-on: ubuntu-22.04         # Specific version
runs-on: macos-latest         # macOS (10x cost)
runs-on: windows-latest       # Windows (2x cost)
runs-on: [self-hosted, linux] # Self-hosted with labels
runs-on:
  group: my-runner-group      # Runner group
  labels: [linux, x64]
```

### Dependencies

```yaml
jobs:
  build:
    # ...
  test:
    needs: build
  deploy:
    needs: [build, test]
    if: success()             # Only if all passed
```

### Matrix

```yaml
strategy:
  fail-fast: false            # Don't cancel on failure
  max-parallel: 4             # Limit concurrent jobs
  matrix:
    os: [ubuntu-latest, macos-latest]
    node: [18, 20, 22]
    include:
      - os: ubuntu-latest
        node: 22
        coverage: true        # Add property to specific combo
    exclude:
      - os: macos-latest
        node: 18              # Skip this combination
```

### Outputs

```yaml
jobs:
  build:
    outputs:
      version: ${{ steps.version.outputs.value }}
    steps:
      - id: version
        run: echo "value=1.0.0" >> $GITHUB_OUTPUT

  deploy:
    needs: build
    steps:
      - run: echo "Deploying ${{ needs.build.outputs.version }}"
```

### Services (Containers)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379
```

### Container Jobs

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node:20
      env:
        NODE_ENV: test
      volumes:
        - /data:/data
      options: --cpus 2
```
