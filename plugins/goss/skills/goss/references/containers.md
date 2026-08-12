---
description: dgoss Docker testing, kgoss Kubernetes testing, dcgoss docker-compose testing
last_updated: 2026-03-18
---

# Goss Container Testing

## dgoss - Docker Container Testing

Wrapper script that orchestrates container startup and goss validation.

```bash
dgoss run [docker-flags] image:tag   # validate
dgoss edit [docker-flags] image:tag  # interactive authoring
```

Files: `goss.yaml` (required), `goss_wait.yaml` (readiness gate, optional). Flow: start container → wait (if goss_wait.yaml) → validate → stop.

### Key Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOSS_PATH` | `$(which goss)` | Path to goss binary |
| `GOSS_OPTS` | `--color --format documentation` | Flags for main validation |
| `GOSS_WAIT_OPTS` | (empty) | Flags for goss_wait.yaml |
| `GOSS_FILES_STRATEGY` | `mount` | `mount` or `copy` (remote Docker) |
| `CONTAINER_RUNTIME` | `docker` | `docker`, `podman`, or `nerdctl` |

### Examples

```bash
dgoss run -p 80:80 nginx:latest
dgoss run -e "APP_ENV=test" myapp:latest
CONTAINER_RUNTIME=podman dgoss run myimage:latest
GOSS_FILES_STRATEGY=copy dgoss run myimage:latest
GOSS_WAIT_OPTS="--retry-timeout 60s --sleep 2s" dgoss run myimage:latest
```

### Wait File Pattern

```yaml
# goss_wait.yaml - readiness gate
port:
  tcp:8080:
    listening: true
http:
  http://localhost:8080/health:
    status: 200
```

Container logs available inside container at `/goss/docker_output.log`:

```yaml
command:
  check-logs:
    exec: cat /goss/docker_output.log
    exit-status: 0
    stdout:
      - "Server started"
      - "!FATAL"
```

## kgoss - Kubernetes Pod Testing

Wrapper for testing containers in Kubernetes pods. Linux goss binary runs inside container; wrapper runs from any platform.

Prerequisites: kgoss in PATH, goss binary at `$HOME/goss` or `$GOSS_PATH`, kubectl configured.

```bash
kgoss run -i image:tag
kgoss edit -i image:tag
kgoss run -i myapp:latest -e "ENV=test" -c "mycommand" -a "--flag"
```

Flags: `-i <image>` (required), `-e K=V` (env vars), `-c "cmd"`, `-a "args"`, `-d "dir"` (copy dir into pod), `-p` (interactive).

Env: `GOSS_PATH=$HOME/goss`, `KUBECTL_NAMESPACE=default`.

## dcgoss - Docker Compose Testing

Convenience wrapper using docker-compose.yml.

```bash
dcgoss run [service-name]
dcgoss edit [service-name]
```

Same env vars and flow as dgoss. Requires `docker-compose.yml` + `goss.yaml` in current directory. Service name selects which compose service to test.

## CI/CD Integration

See [containers-ci.md](containers-ci.md) for GitLab CI, GitHub Actions, and Dockerfile integration patterns.
