---
description: felddy/foundryvtt-docker image, all environment variables, docker-compose, secrets, S3 config
last_updated: 2026-03-18
---

# Foundry VTT Docker (felddy/foundryvtt)

Image: `felddy/foundryvtt` on Docker Hub. Recommended tag: `:13` (major version).

## Authentication (choose one)

| Method | Variables |
|--------|-----------|
| Credentials | `FOUNDRY_USERNAME` + `FOUNDRY_PASSWORD` |
| Presigned URL | `FOUNDRY_RELEASE_URL` (from foundryvtt.com profile) |
| Cached archive | `CONTAINER_CACHE` path with pre-downloaded zip |

## Core Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `FOUNDRY_VERSION` | `13.351` | Foundry VTT version to install |
| `FOUNDRY_ADMIN_KEY` | — | Admin password |
| `FOUNDRY_LICENSE_KEY` | — | License key or index number |
| `FOUNDRY_WORLD` | — | Auto-launch world directory name |
| `FOUNDRY_HOSTNAME` | null | Custom hostname for invite links |
| `FOUNDRY_PROXY_PORT` | null | External port behind reverse proxy |
| `FOUNDRY_PROXY_SSL` | false | Running behind SSL reverse proxy |
| `FOUNDRY_ROUTE_PREFIX` | null | URL path prefix (e.g., `/foundry`) |
| `FOUNDRY_LANGUAGE` | `en.core` | Default language |
| `FOUNDRY_CSS_THEME` | `foundry` | Theme: foundry, fantasy, scifi |
| `FOUNDRY_COMPRESS_WEBSOCKET` | false | Enable WebSocket compression |
| `FOUNDRY_HOT_RELOAD` | false | Asset hot-reload (development) |
| `FOUNDRY_MINIFY_STATIC_FILES` | false | Serve minified JS/CSS |
| `FOUNDRY_UPNP` | false | UPnP port forwarding |
| `FOUNDRY_TELEMETRY` | null | Anonymous telemetry |

## Container Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONTAINER_CACHE` | `/data/container_cache` | Cache download location |
| `CONTAINER_CACHE_SIZE` | unlimited | Max cached versions |
| `CONTAINER_PRESERVE_CONFIG` | false | Don't regenerate config on restart |
| `CONTAINER_PATCHES` | — | Directory of post-install shell scripts |
| `CONTAINER_VERBOSE` | false | Verbose logging |
| `CONTAINER_URL_FETCH_RETRY` | 0 | Retry with exponential backoff |

## SSL/TLS Variables

| Variable | Purpose |
|----------|---------|
| `FOUNDRY_SSL_CERT` | Path to SSL certificate |
| `FOUNDRY_SSL_KEY` | Path to SSL private key |

## S3 / AWS Configuration

| Variable | Purpose |
|----------|---------|
| `FOUNDRY_AWS_CONFIG` | Path to aws config file, or `true` for env credentials |

When `FOUNDRY_AWS_CONFIG=true`, use standard AWS env vars:
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`

## Volume Mount

Single mount: `/data` — contains Config, Data, and Logs subdirectories.

```
/data/
├── Config/
│   └── options.json     # Server configuration
├── Data/
│   ├── modules/         # Installed modules
│   ├── systems/         # Installed game systems
│   └── worlds/          # World data
└── Logs/
    └── debug.log
```

## Port

Default: `30000/tcp`

## Docker Compose

```yaml
services:
  foundry:
    image: felddy/foundryvtt:13
    hostname: foundry
    restart: unless-stopped
    volumes:
      - foundry-data:/data
    environment:
      FOUNDRY_USERNAME: ${FOUNDRY_USERNAME}
      FOUNDRY_PASSWORD: ${FOUNDRY_PASSWORD}
      FOUNDRY_ADMIN_KEY: ${FOUNDRY_ADMIN_KEY}
      FOUNDRY_PROXY_SSL: "true"
      FOUNDRY_PROXY_PORT: "443"
      FOUNDRY_HOSTNAME: "foundry.example.com"
    ports:
      - "30000:30000"

volumes:
  foundry-data:
```

## Docker Secrets

Create `config/secrets.json`:
```json
{
  "foundry_admin_key": "mykey",
  "foundry_password": "mypass",
  "foundry_username": "myuser"
}
```

## Important Notes

- Config regenerates every startup unless `CONTAINER_PRESERVE_CONFIG=true`
- GUI setting changes don't persist between restarts (by design)
- Update: change tag version, `docker compose pull && docker compose up -d`
- Pre-downloaded archives: name as `foundryvtt-{version}.zip`
- Node.js vars (`NODE_*`) passed through to Foundry server
- Proxy vars (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`) supported
