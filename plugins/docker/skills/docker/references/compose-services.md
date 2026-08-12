# Docker Compose Services

## Compose File Structure (v3.8+)

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: development  # Multi-stage target
      args:
        NODE_ENV: development
    image: myapp:dev
    container_name: myapp
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules  # Anonymous volume (preserves container's node_modules)
    environment:
      - NODE_ENV=development
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - backend

volumes:
  postgres_data:

networks:
  backend:
    driver: bridge
```

## Build Optimization

### BuildKit in Compose

```yaml
# Enable BuildKit
services:
  app:
    build:
      context: .
      cache_from:
        - myapp:cache
      cache_to:
        - type=registry,ref=myapp:cache,mode=max
```

```bash
# Run with BuildKit
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose build
```

### Parallel Builds

```bash
# Build all services in parallel
docker compose build --parallel

# Build specific services
docker compose build app worker
```

## Health Checks

```yaml
services:
  api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Dependency Management

```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
      migrations:
        condition: service_completed_successfully
```
