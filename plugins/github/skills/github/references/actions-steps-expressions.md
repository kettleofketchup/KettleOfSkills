# GitHub Actions: Steps & Expressions

## Steps

### Actions

```yaml
steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0          # Full history
      submodules: recursive

  - uses: actions/setup-node@v4
    with:
      node-version: '20'
      cache: 'npm'
      registry-url: 'https://npm.pkg.github.com'

  - uses: ./.github/actions/custom  # Local action
  - uses: owner/repo/path@v1        # Subdirectory action
```

### Run Commands

```yaml
steps:
  - run: npm test

  - run: |
      npm ci
      npm run build

  - name: Multi-line with env
    run: |
      echo "Building $VERSION"
      ./build.sh
    env:
      VERSION: ${{ github.sha }}
    shell: bash
    working-directory: ./app
    continue-on-error: true
```

### Conditionals

```yaml
steps:
  - if: github.event_name == 'push'
    run: echo "Push event"

  - if: github.ref == 'refs/heads/main'
    run: echo "Main branch"

  - if: contains(github.event.head_commit.message, '[deploy]')
    run: ./deploy.sh

  - if: always()              # Run even if previous failed
    run: ./cleanup.sh

  - if: failure()             # Only on failure
    run: ./notify-failure.sh
```

## Contexts

```yaml
${{ github.actor }}           # User who triggered
${{ github.repository }}      # owner/repo
${{ github.ref }}             # refs/heads/main
${{ github.sha }}             # Commit SHA
${{ github.event_name }}      # push, pull_request, etc
${{ github.run_id }}          # Unique run ID
${{ github.workflow }}        # Workflow name
${{ env.MY_VAR }}
${{ secrets.GITHUB_TOKEN }}
${{ job.status }}
${{ steps.step-id.outputs.value }}
${{ steps.step-id.outcome }}  # success, failure, cancelled, skipped
${{ matrix.os }}
${{ needs.job-id.outputs.value }}
${{ needs.job-id.result }}
```

## Expressions

```yaml
${{ contains(github.event.head_commit.message, '[skip ci]') }}
${{ startsWith(github.ref, 'refs/tags/') }}
${{ endsWith(github.repository, '-demo') }}
${{ format('Hello {0}!', github.actor) }}
${{ toJSON(github.event) }}
${{ fromJSON(steps.data.outputs.json) }}
${{ github.ref == 'refs/heads/main' && github.event_name == 'push' }}
${{ !cancelled() }}
${{ hashFiles('**/package-lock.json') }}
```

## Environment & Secrets

```yaml
env:
  GLOBAL_VAR: value           # Workflow level

jobs:
  build:
    env:
      JOB_VAR: value          # Job level
    steps:
      - env:
          STEP_VAR: value     # Step level
        run: echo $STEP_VAR

# Dynamic env
steps:
  - run: echo "VERSION=1.0.0" >> $GITHUB_ENV
  - run: echo "Version is $VERSION"

# Secrets best practice
steps:
  - run: ./deploy.sh
    env:
      API_KEY: ${{ secrets.API_KEY }}

# Environment protection
jobs:
  deploy:
    environment:
      name: production
      url: https://example.com
```

See [optimization-caching.md](optimization-caching.md) for artifact upload/download patterns.
