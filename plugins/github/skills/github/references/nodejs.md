# Node.js GitHub Actions Patterns

## Basic Setup

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'           # Or: 20, 18, 'lts/*', 'latest'
    cache: 'npm'                 # Also: yarn, pnpm
    cache-dependency-path: frontend/package-lock.json  # For monorepos
```

## Package Manager Variants

### npm
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
    cache: 'npm'
- run: npm ci
```

### pnpm
```yaml
- uses: pnpm/action-setup@v4
  with:
    version: 9
- uses: actions/setup-node@v4
  with:
    node-version: '22'
    cache: 'pnpm'
- run: pnpm install --frozen-lockfile
```

### yarn
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
    cache: 'yarn'
- run: yarn install --frozen-lockfile
```

### Bun
```yaml
- uses: oven-sh/setup-bun@v2
  with:
    bun-version: latest
- run: bun install --frozen-lockfile
```

## Monorepo Patterns

```yaml
# Single frontend package
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json

# Multiple packages
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
    cache-dependency-path: |
      packages/app/package-lock.json
      packages/shared/package-lock.json
```

## Tool-Specific Caching

### Playwright Browsers
```yaml
- uses: actions/cache@v4
  id: playwright-cache
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
- if: steps.playwright-cache.outputs.cache-hit != 'true'
  run: npx playwright install --with-deps chromium
- if: steps.playwright-cache.outputs.cache-hit == 'true'
  run: npx playwright install-deps chromium
```

### Cypress
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/Cypress
    key: cypress-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
```

### Next.js / Vite Build Cache
```yaml
# Next.js
- uses: actions/cache@v4
  with:
    path: .next/cache
    key: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('**/*.ts', '**/*.tsx') }}
    restore-keys: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-

# Vite
- uses: actions/cache@v4
  with:
    path: node_modules/.vite
    key: vite-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
```

## Node Version Matrix

```yaml
strategy:
  fail-fast: false
  matrix:
    node: [18, 20, 22]
steps:
  - uses: actions/setup-node@v4
    with:
      node-version: ${{ matrix.node }}
      cache: 'npm'
```

## Common Patterns

```yaml
# Run scripts in parallel
- run: npm run lint & npm run typecheck & wait

# Working directory for monorepos
- run: npm ci
  working-directory: frontend

# Registry authentication (private packages)
- uses: actions/setup-node@v4
  with:
    node-version: '22'
    registry-url: 'https://npm.pkg.github.com'
- run: npm ci
  env:
    NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

# CI environment variables
env:
  CI: true
  NODE_ENV: test
  HUSKY: 0                       # Disable husky hooks in CI
```
