# GitHub Actions: Caching Optimization

## Cost Comparison

| Runner | Multiplier | Use When |
|--------|------------|----------|
| ubuntu-latest | 1x | Default choice |
| windows-latest | 2x | Windows-only builds |
| macos-latest | 10x | iOS/macOS only |
| self-hosted | 0x | High volume, special hardware |

## Dependency Caching

```yaml
# Built-in (preferred for supported ecosystems)
- uses: actions/setup-node@v4
  with:
    cache: 'npm'              # Also: yarn, pnpm

- uses: actions/setup-python@v5
  with:
    cache: 'pip'              # Also: poetry, pipenv

- uses: actions/setup-go@v5
  with:
    cache: true               # Caches go modules

# Manual cache (for custom paths)
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.local/share/virtualenvs
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## Build Cache

```yaml
# Turborepo / Nx cache
- uses: actions/cache@v4
  with:
    path: .turbo
    key: ${{ runner.os }}-turbo-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-turbo-

# Gradle cache
- uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

# Rust cache
- uses: Swatinem/rust-cache@v2
```

## Docker Layer Caching

```yaml
# BuildKit cache mount (best)
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max

# Registry cache
- uses: docker/build-push-action@v5
  with:
    cache-from: type=registry,ref=user/app:cache
    cache-to: type=registry,ref=user/app:cache,mode=max
```

## Artifact Passing

```yaml
jobs:
  build:
    steps:
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
          retention-days: 1

  test-e2e:
    needs: build
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
      - run: npm run test:e2e
```

## Caching Checklist

- [ ] Use setup-action's built-in cache
- [ ] Cache build outputs (Turbo, Nx, Gradle)
- [ ] Use Docker BuildKit GHA cache
- [ ] Set short `retention-days` on artifacts
