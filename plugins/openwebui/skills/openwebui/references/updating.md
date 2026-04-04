# Updating Open WebUI

Your data (chats, users, settings, uploads) lives in a Docker volume or local database, not inside the container. Updating means swapping the container image for a newer one.

## Choose Your Update Strategy

| Scenario | Recommended approach |
|---|---|
| **Personal / homelab** | Use the `:main` tag and pull manually |
| **Shared / team instance** | Pin a specific version (e.g. `:v0.8.6`) and use Diun for update notifications |
| **Production / critical** | Pin a version, review release notes before upgrading, test in staging first |

The `:main` tag always points to the latest build. For stability, pin a specific release tag:

```
ghcr.io/open-webui/open-webui:v0.8.6
ghcr.io/open-webui/open-webui:v0.8.6-cuda
ghcr.io/open-webui/open-webui:v0.8.6-ollama
```

## Before You Update

1. Back up your data (see Backup and Restore below).
2. Check the [release notes](https://github.com/open-webui/open-webui/releases) for breaking changes.
3. Clear your browser cache after updating (Ctrl+F5 / Cmd+Shift+R).

For multiple workers or replicas: run migrations on a single instance first with `UVICORN_WORKERS=1` or `ENABLE_DB_MIGRATIONS=false` on all but one instance.

## Manual Update

### Docker Run

```bash
docker rm -f open-webui
docker pull ghcr.io/open-webui/open-webui:main
docker run -d -p 3000:8080 \
  -v open-webui:/app/backend/data \
  -e WEBUI_SECRET_KEY="your-secret-key" \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:main
```

For NVIDIA GPU support, add `--gpus all`.

### Docker Compose

```bash
docker compose pull
docker compose up -d
```

Ensure `docker-compose.yml` includes `WEBUI_SECRET_KEY`:

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
    environment:
      - WEBUI_SECRET_KEY=your-secret-key
    restart: unless-stopped

volumes:
  open-webui:
```

### Python (pip)

```bash
pip install -U open-webui
open-webui serve
```

Without a persistent `WEBUI_SECRET_KEY`, a new key is generated each time the container is recreated, invalidating all sessions. Generate one with `openssl rand -hex 32`.

### Verify the Update

1. Check version in logs: `docker logs open-webui 2>&1 | head -20`
2. Load the UI at http://localhost:3000
3. If UI looks broken, clear browser cache (Ctrl+F5)
4. If migration errors in logs, check release notes

## Rolling Back

Pin a previous version tag.

### Docker Run

```bash
docker rm -f open-webui
docker pull ghcr.io/open-webui/open-webui:v0.8.3
docker run -d -p 3000:8080 -v open-webui:/app/backend/data \
  -e WEBUI_SECRET_KEY="your-secret-key" \
  --name open-webui --restart always \
  ghcr.io/open-webui/open-webui:v0.8.3
```

### Docker Compose

Change image tag in `docker-compose.yml` to the desired version, then `docker compose pull && docker compose up -d`.

### Python (pip)

```bash
pip install open-webui==0.8.3
open-webui serve
```

Database migrations are one-way. If the version you updated to ran a migration, rolling back the container does not undo it. Restore from a backup taken before the update.

## Update Notification Tools

| Feature | Diun | WUD | Watchtower |
|---------|:---:|:---:|:---:|
| Auto-updates containers | No | No (manual via UI) | Yes |
| Web interface | No | Yes | No |
| Notifications | Yes | Yes | Yes |

### Diun (Notification-Only)

Alerts when updates are available without touching containers.

```yaml
services:
  diun:
    image: crazymax/diun:latest
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./data:/data
    environment:
      - DIUN_WATCH_SCHEDULE=0 */6 * * *
      - DIUN_PROVIDERS_DOCKER=true
```

### Watchtower (Automated)

The original `containrrr/watchtower` is no longer maintained and fails with Docker 29+. Use the [nicholas-fedor/watchtower](https://watchtower.nickfedor.com/) fork.

**One-time update:**
```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock nickfedor/watchtower --run-once open-webui
```

**Continuous (every 6 hours):**
```bash
docker run -d --name watchtower --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  nickfedor/watchtower --interval 21600 open-webui
```

## Backup and Restore

All data lives in the `open-webui` Docker volume.

### Backup

```bash
docker run --rm -v open-webui:/data -v $(pwd):/backup \
  alpine tar czf /backup/openwebui-$(date +%Y%m%d).tar.gz /data
```

Back up before every update and on a regular schedule.

### Restore

```bash
docker stop open-webui
docker run --rm -v open-webui:/data -v $(pwd):/backup \
  alpine sh -c "rm -rf /data/* && tar xzf /backup/openwebui-YYYYMMDD.tar.gz -C /"
docker start open-webui
```

Replace `YYYYMMDD` with the actual date of your backup file. The restore command deletes everything in the volume before extracting.
