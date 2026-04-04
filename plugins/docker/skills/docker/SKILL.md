---
name: docker
version: 2026-02-01
description: Docker layer optimization for fast builds. This skill should be used when writing Dockerfiles, optimizing build times, setting up multi-stage builds, configuring BuildKit cache mounts, debugging slow builds, writing docker-compose.yml files, or integrating Docker with CI/CD pipelines (GitHub Actions, GitLab CI). Covers layer ordering, dependency caching, .dockerignore, multi-stage patterns, BuildKit features, and Docker Compose patterns.
---

# Docker Layer Optimization

Optimize Docker builds for speed through proper layer ordering, BuildKit caching, and CI/CD integration.

## Core Principles

1. **Layer order matters** - least-changing content first, most-changing last
2. **Separate dependencies from code** - package manifests before source
3. **Use BuildKit cache mounts** - persist package manager caches between builds
4. **Multi-stage builds** - separate build-time from runtime dependencies

## Layer Ordering Pattern

```dockerfile
# 1. Base image (rarely changes)
FROM node:20-slim AS base

# 2. System dependencies (rarely changes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && rm -rf /var/lib/apt/lists/*

# 3. Package manifests ONLY (changes when deps change)
WORKDIR /app
COPY package.json package-lock.json ./

# 4. Install dependencies (cached unless manifests change)
RUN npm ci

# 5. Source code (changes frequently - LAST)
COPY . .

# 6. Build step
RUN npm run build
```

## BuildKit Cache Mounts

Enable BuildKit: `DOCKER_BUILDKIT=1` or set in `/etc/docker/daemon.json`

```dockerfile
# Node.js - cache npm
RUN --mount=type=cache,target=/root/.npm npm ci

# Python - cache pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# Go - cache modules
RUN --mount=type=cache,target=/go/pkg/mod go build -o app .
```

## Multi-Stage Build Pattern

```dockerfile
# Build stage
FROM golang:1.22 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o app

# Runtime stage (minimal image)
FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/app /app
ENTRYPOINT ["/app"]
```

## .dockerignore (Critical)

Always create `.dockerignore` to reduce build context:

```
.git
node_modules
*.log
.env*
dist
build
__pycache__
.pytest_cache
.coverage
```

## Quick Diagnosis

Slow build? Check in order:
1. Missing `.dockerignore`? → Large build context
2. `COPY . .` before `RUN npm install`? → Reinstalls on every code change
3. Not using BuildKit cache mounts? → Downloads deps every build
4. Not using multi-stage? → Large final image, slow push/pull

## References

For detailed patterns by language and CI/CD integration:

- `references/language-patterns.md` - Node.js, Python, Go, Rust specific patterns
- `references/cicd-integration.md` - GitHub Actions & GitLab CI caching setup
- `references/buildkit-advanced.md` - Advanced BuildKit features (bake, secrets, SSH)
- `references/compose-services.md` - Compose file structure, services, build, networking, volumes, health checks, commands
- `references/compose-patterns.md` - Dev patterns, override files, profiles, watch mode, environment variable priority
