# Node.js GitHub Actions Patterns

Comprehensive Node.js/npm setup and caching patterns for GitHub Actions.

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
- run: npm ci                    # Clean install, faster than npm install
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

### cache-dependency-path
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

### Turborepo/Nx Build Cache
```yaml
- uses: actions/cache@v4
  with:
    path: .turbo
    key: ${{ runner.os }}-turbo-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-turbo-

# Or for Nx
- uses: actions/cache@v4
  with:
    path: .nx/cache
    key: ${{ runner.os }}-nx-${{ hashFiles('**/package-lock.json') }}-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-nx-${{ hashFiles('**/package-lock.json') }}-
```

## Tool-Specific Caching

### Playwright Browsers
```yaml
- uses: actions/cache@v4
  id: playwright-cache
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}

# Install browsers if cache miss
- if: steps.playwright-cache.outputs.cache-hit != 'true'
  run: npx playwright install --with-deps chromium

# Just system deps if browsers cached
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

### Next.js Build Cache
```yaml
- uses: actions/cache@v4
  with:
    path: |
      .next/cache
    key: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('**/*.js', '**/*.jsx', '**/*.ts', '**/*.tsx') }}
    restore-keys: |
      ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-
```

### Vite Build Cache
```yaml
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

### Run scripts in parallel
```yaml
- run: npm run lint & npm run typecheck & wait
```

### Working directory for monorepos
```yaml
- run: npm ci
  working-directory: frontend
- run: npm test
  working-directory: frontend
```

### Registry authentication (private packages)
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
    registry-url: 'https://npm.pkg.github.com'

- run: npm ci
  env:
    NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Publishing packages
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '22'
    registry-url: 'https://registry.npmjs.org'

- run: npm publish
  env:
    NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## CI Environment Variables

Common env vars for CI builds:

```yaml
env:
  CI: true                       # Many tools detect this
  NODE_ENV: test                 # Or: production
  HUSKY: 0                       # Disable husky hooks in CI
```

## Performance Tips

1. **Use `npm ci`** - Faster, deterministic, respects lockfile
2. **Built-in caching** - `cache: 'npm'` in setup-node is faster than manual cache
3. **Shallow checkout** - `fetch-depth: 1` for faster git clone
4. **Working directory** - Avoid `cd` by using `working-directory:`
5. **Parallel jobs** - Split lint/test/build into separate jobs
