# CI/CD Docker Build Optimization

## Cache Strategies Comparison

| Strategy | GitHub Actions | GitLab CI | Speed | Persistence |
|----------|---------------|-----------|-------|-------------|
| GHA Cache | `type=gha` | N/A | Fast | 7 days |
| Registry | `type=registry` | `--cache-repo` | Medium | Permanent |
| Local | `type=local` | Volume mount | Fastest | Runner-local |
| Inline | `BUILDKIT_INLINE_CACHE=1` | Same | Slow | In image |

## Optimization Tips

### 1. Use `mode=max` for Full Cache

```yaml
cache-to: type=gha,mode=max  # Caches all layers, not just final
```

### 2. Separate Build and Test Stages

```yaml
jobs:
  build:
    outputs:
      image: ${{ steps.build.outputs.imageid }}
    steps:
      - id: build
        uses: docker/build-push-action@v5
        with:
          load: true  # Load to local daemon
          tags: app:test

  test:
    needs: build
    steps:
      - run: docker run app:test npm test
```

### 3. Parallel Multi-Arch Builds

```yaml
strategy:
  matrix:
    platform: [linux/amd64, linux/arm64]
steps:
  - uses: docker/build-push-action@v5
    with:
      platforms: ${{ matrix.platform }}
```

### 4. Cache Warming on Schedule

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Nightly

jobs:
  warm-cache:
    steps:
      - uses: docker/build-push-action@v5
        with:
          push: false
          cache-to: type=gha,mode=max
```

## Debugging CI Builds

```yaml
# Add to see cache behavior
- name: Build with Debug
  run: |
    docker buildx build \
      --progress=plain \
      --cache-from type=gha \
      .
```

Check for:
- `CACHED` vs `RUN` in build output
- "importing cache manifest" messages
- Layer hash mismatches
