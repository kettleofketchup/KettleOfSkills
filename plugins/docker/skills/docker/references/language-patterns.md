# Language-Specific Docker Patterns

## Node.js / TypeScript

### Optimized Multi-Stage Build

```dockerfile
FROM node:20-slim AS base
WORKDIR /app

# Dependencies stage
FROM base AS deps
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --only=production

# Build stage
FROM base AS builder
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

# Runtime
FROM base AS runner
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
USER node
CMD ["node", "dist/index.js"]
```

### pnpm Variant

```dockerfile
FROM node:20-slim AS base
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app

FROM base AS deps
COPY pnpm-lock.yaml ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm fetch

COPY package.json ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --prod
```

## Python

### pip with Cache Mount

```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app

FROM base AS builder
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -r requirements.txt

FROM base AS runner
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
CMD ["python", "main.py"]
```

### Poetry Variant

```dockerfile
FROM python:3.12-slim AS base
ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false
RUN pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-dev --no-interaction

COPY . .
CMD ["python", "main.py"]
```

### uv (Fast Python Package Manager)

```dockerfile
FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY . .
CMD ["uv", "run", "python", "main.py"]
```

## Go

### Minimal Scratch Image

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app

# Cache deps
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download

COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o app

# Scratch for minimal image (no shell, no libc)
FROM scratch
COPY --from=builder /app/app /app
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
ENTRYPOINT ["/app"]
```

### With CGO (requires libc)

```dockerfile
FROM golang:1.22-alpine AS builder
RUN apk add --no-cache gcc musl-dev
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build -o app

FROM alpine:3.19
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/app /app
ENTRYPOINT ["/app"]
```

## Rust

### Cargo Chef Pattern (Optimal Caching)

```dockerfile
FROM rust:1.75 AS chef
RUN cargo install cargo-chef
WORKDIR /app

FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder
COPY --from=planner /app/recipe.json recipe.json
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    cargo chef cook --release --recipe-path recipe.json
COPY . .
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    cargo build --release

FROM debian:bookworm-slim AS runner
COPY --from=builder /app/target/release/app /app
CMD ["/app"]
```

## Base Image Selection

| Language | Dev/Build | Production |
|----------|-----------|------------|
| Node.js | `node:20` | `node:20-slim` or `gcr.io/distroless/nodejs20` |
| Python | `python:3.12` | `python:3.12-slim` |
| Go | `golang:1.22-alpine` | `scratch` or `gcr.io/distroless/static` |
| Rust | `rust:1.75` | `debian:bookworm-slim` or `scratch` |

## Common Anti-Patterns

**Bad:** Installing dev tools in production image
```dockerfile
# Don't do this
RUN npm install  # Includes devDependencies
```

**Good:** Separate build and runtime stages
```dockerfile
# Build stage installs everything
RUN npm ci
# Prod stage only copies production deps
COPY --from=deps /app/node_modules ./node_modules
```
