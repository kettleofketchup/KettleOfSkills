# Docker Compose Networking, Volumes, and Commands

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
