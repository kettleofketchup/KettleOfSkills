# Docker Patterns for Go and Rust

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
| Node.js | `node:20` | `node:20-slim` or distroless |
| Python | `python:3.12` | `python:3.12-slim` |
| Go | `golang:1.22-alpine` | `scratch` or distroless |
| Rust | `rust:1.75` | `debian:bookworm-slim` or `scratch` |
