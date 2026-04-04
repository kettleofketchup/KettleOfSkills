# CI/CD Docker Build Integration

## GitHub Actions

### Basic with Layer Caching

```yaml
name: Build and Push
on: push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Registry Cache (Persistent Across Workflows)

```yaml
- name: Build and Push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ghcr.io/${{ github.repository }}:latest
    cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:cache
    cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:cache,mode=max
```

### Multi-Platform Build

```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3

- name: Build Multi-Platform
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## GitLab CI

### Basic with Registry Cache

```yaml
variables:
  DOCKER_BUILDKIT: "1"

build:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker buildx create --use
    - docker buildx build
      --cache-from type=registry,ref=$CI_REGISTRY_IMAGE:cache
      --cache-to type=registry,ref=$CI_REGISTRY_IMAGE:cache,mode=max
      --push
      --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
      .
```

### GitLab Kubernetes Executor with Kaniko

Kaniko builds without Docker daemon - works in unprivileged pods:

```yaml
build:
  stage: build
  image:
    name: gcr.io/kaniko-project/executor:v1.19.2-debug
    entrypoint: [""]
  script:
    - /kaniko/executor
      --context $CI_PROJECT_DIR
      --dockerfile $CI_PROJECT_DIR/Dockerfile
      --destination $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
      --cache=true
      --cache-repo=$CI_REGISTRY_IMAGE/cache
```

### GitLab with Local Runner Cache

```yaml
build:
  image: docker:24
  services:
    - docker:24-dind
  variables:
    DOCKER_DRIVER: overlay2
  script:
    - docker build
      --cache-from $CI_REGISTRY_IMAGE:latest
      --tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
      --build-arg BUILDKIT_INLINE_CACHE=1
      .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

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
