# Advanced BuildKit Features

## Enable BuildKit

```bash
# Per-command
DOCKER_BUILDKIT=1 docker build .

# Permanent (daemon.json)
{ "features": { "buildkit": true } }

# Docker Compose
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build
```

## Mount Types

### Cache Mount (Package Managers)

```dockerfile
# npm
RUN --mount=type=cache,target=/root/.npm npm ci

# pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# apt (with lock for parallel safety)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y curl

# Go modules
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go build -o app
```

### Bind Mount (Read-Only Source)

```dockerfile
# Mount source without copying (faster for large files)
RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    npm ci
```

### Secret Mount (Don't Leak in Layers)

```dockerfile
# Build with: docker build --secret id=npm,src=.npmrc .
RUN --mount=type=secret,id=npm,target=/root/.npmrc \
    npm ci

# GitHub token
RUN --mount=type=secret,id=github_token \
    GITHUB_TOKEN=$(cat /run/secrets/github_token) \
    go mod download
```

### SSH Mount (Private Repos)

```dockerfile
# Build with: docker build --ssh default .
RUN --mount=type=ssh \
    git clone git@github.com:org/private-repo.git

# Go private modules
RUN --mount=type=ssh \
    --mount=type=cache,target=/go/pkg/mod \
    GOPRIVATE=github.com/myorg/* go mod download
```

## Docker Bake (Multi-Target Builds)

### docker-bake.hcl

```hcl
group "default" {
  targets = ["api", "worker", "frontend"]
}

target "base" {
  dockerfile = "Dockerfile"
  context = "."
}

target "api" {
  inherits = ["base"]
  target = "api"
  tags = ["myapp/api:latest"]
}

target "worker" {
  inherits = ["base"]
  target = "worker"
  tags = ["myapp/worker:latest"]
}

target "frontend" {
  dockerfile = "frontend/Dockerfile"
  context = "frontend"
  tags = ["myapp/frontend:latest"]
}

# Variables
variable "TAG" {
  default = "latest"
}

target "production" {
  inherits = ["base"]
  tags = ["myapp:${TAG}"]
  platforms = ["linux/amd64", "linux/arm64"]
  cache-from = ["type=registry,ref=myapp:cache"]
  cache-to = ["type=registry,ref=myapp:cache,mode=max"]
}
```

### Usage

```bash
# Build all targets
docker buildx bake

# Build specific target
docker buildx bake api

# Build with variables
docker buildx bake --set *.tags=myapp:v1.0.0

# Push to registry
docker buildx bake --push
```

## Build Arguments & Secrets

### ARG vs Secret

```dockerfile
# ARG - visible in image history (use for non-sensitive)
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV

# Secret - never in image (use for tokens/keys)
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) ./configure
```

### Build-time Variables

```dockerfile
ARG BUILDPLATFORM
ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH

# Cross-compile Go
RUN --mount=type=cache,target=/go/pkg/mod \
    GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build -o app
```

## Heredocs (Multi-Line Scripts)

```dockerfile
# Bash script
RUN <<EOF
#!/bin/bash
set -ex
apt-get update
apt-get install -y curl git
rm -rf /var/lib/apt/lists/*
EOF

# Python script
RUN <<EOF python3
import sys
print(f"Python {sys.version}")
EOF

# Create file
COPY <<EOF /app/config.json
{
  "port": 8080,
  "debug": false
}
EOF
```

## Parallel Stage Execution

```dockerfile
# These run in parallel (no dependencies)
FROM base AS stage-a
RUN expensive-operation-a

FROM base AS stage-b
RUN expensive-operation-b

FROM base AS stage-c
RUN expensive-operation-c

# Final stage waits for all
FROM base
COPY --from=stage-a /output /a
COPY --from=stage-b /output /b
COPY --from=stage-c /output /c
```

## Debugging Builds

```bash
# Verbose output
docker buildx build --progress=plain .

# Debug failed step
docker buildx build --target=failing-stage .
docker run -it <image-id> /bin/sh

# Export cache for inspection
docker buildx build --cache-to=type=local,dest=./cache .

# Build without cache
docker buildx build --no-cache .

# Check Dockerfile syntax
docker buildx build --check .
```

## BuildKit Configuration

### buildkitd.toml

```toml
# /etc/buildkit/buildkitd.toml
[worker.oci]
  gc = true
  gckeepstorage = 10000  # 10GB

[registry."docker.io"]
  mirrors = ["mirror.gcr.io"]

[registry."ghcr.io"]
  insecure = false
```

### Garbage Collection

```bash
# Prune build cache
docker buildx prune

# Keep last 7 days
docker buildx prune --filter until=168h

# Remove all
docker buildx prune --all
```
