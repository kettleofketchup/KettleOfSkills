# Docker Compose Patterns

## Development Patterns

### Hot Reload Setup

```yaml
services:
  app:
    build:
      target: development
    volumes:
      - .:/app:cached           # Cached for macOS performance
      - /app/node_modules       # Exclude node_modules from bind mount
    command: npm run dev
```

### Override Files

```yaml
# docker-compose.yml (base)
services:
  app:
    build: .

# docker-compose.override.yml (auto-loaded in dev)
services:
  app:
    volumes:
      - .:/app
    command: npm run dev

# docker-compose.prod.yml
services:
  app:
    image: myapp:${TAG:-latest}
    restart: always
```

```bash
# Dev (auto-loads override)
docker compose up

# Prod (explicit files)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Profiles

```yaml
services:
  app:
    # Always starts

  debug:
    profiles: ["debug"]
    image: busybox
    command: sleep infinity

  test:
    profiles: ["test"]
    build:
      target: test
    command: npm test
```

```bash
docker compose up                    # Only app
docker compose --profile debug up    # app + debug
docker compose --profile test run test
```

## Environment Variables

### Priority (highest to lowest)

1. Shell environment
2. `.env` file in project directory
3. `env_file` in compose
4. `environment` in compose
5. Dockerfile ENV

### Variable Substitution

```yaml
services:
  app:
    image: myapp:${TAG:-latest}           # Default value
    environment:
      - DEBUG=${DEBUG:?error message}      # Required, error if missing
      - LOG_LEVEL=${LOG_LEVEL:-info}       # Optional with default
```

## Watch Mode (Compose 2.22+)

```yaml
services:
  app:
    build: .
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: package.json
        - action: sync+restart
          path: ./config
          target: /app/config
```

```bash
docker compose watch
```
