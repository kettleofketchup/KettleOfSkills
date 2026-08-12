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
