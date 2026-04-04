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

## Networking

### Service Discovery

```yaml
services:
  api:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend  # Only accessible from backend network

networks:
  frontend:
  backend:
    internal: true  # No external access
```

Services resolve by name: `http://api:3000`, `postgres://db:5432`

### External Networks

```yaml
networks:
  proxy:
    external: true
    name: traefik_network
```

## Volume Patterns

### Named Volumes

```yaml
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
```

### Bind Mounts with Options

```yaml
services:
  app:
    volumes:
      - type: bind
        source: ./src
        target: /app/src
        read_only: true
      - type: volume
        source: node_modules
        target: /app/node_modules
```

## Common Commands

```bash
# Build and start
docker compose up -d --build

# View logs
docker compose logs -f app

# Execute command in running container
docker compose exec app sh

# Run one-off command
docker compose run --rm app npm test

# Stop and remove
docker compose down

# Stop, remove, and delete volumes
docker compose down -v

# Rebuild single service
docker compose up -d --build --no-deps app
```
