# Playwright GitHub Actions CI

Official best practices from playwright.dev/docs/ci-intro.

## Key Principles

1. **Run on host runner, not Docker** - More resources, better Chromium support
2. **Use `--with-deps`** - Installs system dependencies (fonts, libs)
3. **Cache browsers** - Key on package-lock.json (includes Playwright version)
4. **Only install needed browsers** - `chromium` only unless testing cross-browser
5. **Linux runners** - 10x cheaper than macOS

**Important**: `microsoft/playwright-github-action` is deprecated. Use CLI directly.

## Recommended Workflow

```yaml
name: Playwright Tests
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Cancel in-progress runs when new commit pushed to same branch
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - run: npm ci
        working-directory: frontend

      # Cache Playwright browsers
      - uses: actions/cache@v4
        id: playwright-cache
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ hashFiles('frontend/package-lock.json') }}

      # Install browsers + deps if cache miss
      - if: steps.playwright-cache.outputs.cache-hit != 'true'
        run: npx playwright install --with-deps chromium
        working-directory: frontend

      # Just install system deps if browsers cached
      - if: steps.playwright-cache.outputs.cache-hit == 'true'
        run: npx playwright install-deps chromium
        working-directory: frontend

      - run: npx playwright test
        working-directory: frontend
        env:
          CI: true

      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report
          path: frontend/playwright-report/
          retention-days: 30
```

## Sharding for Large Suites

Split tests across parallel jobs for faster CI:

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      # ... setup steps ...
      - run: npx playwright test --shard=${{ matrix.shard }}
```

## Docker Considerations

If must run in Docker (not recommended):

```yaml
services:
  app:
    shm_size: 1gb  # Required for Chromium shared memory
```

Browser flags for containers (in playwright.config.ts):
```typescript
launchOptions: {
  args: [
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
    '--disable-setuid-sandbox',
  ],
}
```

## Trace on Failure

Configure traces for CI debugging:

```typescript
// playwright.config.ts
use: {
  trace: 'on-first-retry',  // Only on retries to save resources
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
}
```

Refs: https://playwright.dev/docs/ci-intro, https://playwright.dev/docs/best-practices
