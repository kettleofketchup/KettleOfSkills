---
description: dgoss Docker testing, kgoss Kubernetes testing, dcgoss docker-compose testing, CI/CD integration
last_updated: 2026-03-18
---

# Goss Container Testing

## dgoss - Docker Container Testing

Wrapper script that orchestrates container startup and goss validation.

### Usage

```bash
# Run mode - validate against existing goss.yaml
dgoss run [docker-flags] image:tag

# Edit mode - interactive shell to author tests
dgoss edit [docker-flags] image:tag
# Use goss add/autoadd inside container, tests copied out on exit
```

### File Structure

| File | Purpose |
|------|---------|
| `goss.yaml` | Main test file (required) |
| `goss_wait.yaml` | Readiness conditions before main tests (optional) |

### Flow

1. Container starts with goss binary mounted/copied in
2. `goss_wait.yaml` validates (if exists) - polls until ready
3. `goss.yaml` validates
4. Container stops, results reported

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOSS_PATH` | `$(which goss)` | Path to goss binary |
| `GOSS_FILE` | `goss.yaml` | Test file name |
| `GOSS_WAIT_OPTS` | (empty) | Flags for goss_wait.yaml validation |
| `GOSS_OPTS` | `--color --format documentation` | Flags for main validation |
| `GOSS_SLEEP` | `0.2` | Delay before tests start (seconds) |
| `GOSS_FILES_STRATEGY` | `mount` | `mount` or `copy` (use copy for remote Docker) |
| `CONTAINER_RUNTIME` | `docker` | `docker`, `podman`, or `nerdctl` |
| `DEBUG` | (empty) | Set to anything for debug output |

### Examples

```bash
# Test nginx image
dgoss run -p 80:80 nginx:latest

# With environment variables
dgoss run -e "APP_ENV=test" -e "DB_HOST=db" myapp:latest

# With volume mounts
dgoss run -v /data:/data myapp:latest

# Using podman
CONTAINER_RUNTIME=podman dgoss run myimage:latest

# Copy strategy (remote Docker hosts)
GOSS_FILES_STRATEGY=copy dgoss run myimage:latest

# Custom wait options (retry for 60s)
GOSS_WAIT_OPTS="--retry-timeout 60s --sleep 2s" dgoss run myimage:latest
```

### Wait File Pattern

`goss_wait.yaml` - readiness gate before main tests:

```yaml
# goss_wait.yaml - wait for app to be ready
port:
  tcp:8080:
    listening: true

http:
  http://localhost:8080/health:
    status: 200
```

Container logs available inside container at `/goss/docker_output.log`:

```yaml
# goss.yaml - validate container logs
command:
  check-logs:
    exec: cat /goss/docker_output.log
    exit-status: 0
    stdout:
      - "Server started"
      - "!FATAL"
```

## kgoss - Kubernetes Pod Testing

Wrapper for testing containers in Kubernetes pods. Linux goss binary runs inside container; wrapper runs from any platform (Mac, Windows git-bash).

### Prerequisites

- kgoss script in PATH
- goss binary in `$HOME` or `$GOSS_PATH`
- kubectl installed and configured

### Usage

```bash
# Run mode
kgoss run -i image:tag

# Edit mode
kgoss edit -i image:tag

# With options
kgoss run -i myapp:latest -e "ENV=test" -c "mycommand" -a "--flag"
```

### Options

| Flag | Purpose |
|------|---------|
| `-i <image>` | Container image (required) |
| `-p` | Interactive entrypoint |
| `-c "cmd"` | Command to run |
| `-a "args"` | Arguments |
| `-d "dir"` | Directories to copy into pod |
| `-e "K=V"` | Environment variables |

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `GOSS_PATH` | `$HOME/goss` | Path to goss binary |
| `KUBECTL_NAMESPACE` | default | Kubernetes namespace |

## dcgoss - Docker Compose Testing

Convenience wrapper using docker-compose.yml for container definition.

### Usage

```bash
# Run mode - uses docker-compose.yml in current directory
dcgoss run [service-name]

# Edit mode
dcgoss edit [service-name]
```

### File Structure

```
project/
  docker-compose.yml
  goss.yaml
  goss_wait.yaml    # optional
```

Same environment variables and flow as dgoss. Service name argument specifies which docker-compose service to test.

## CI/CD Integration

### GitLab CI

```yaml
test:
  image: myapp:latest
  script:
    - goss validate --format junit > report.xml
  artifacts:
    reports:
      junit: report.xml
```

### GitHub Actions

```yaml
- name: Test with goss
  run: |
    dgoss run myapp:${{ github.sha }}
  env:
    GOSS_OPTS: "--format junit"
```

### Dockerfile Integration

Embed goss in image for self-testing:

```dockerfile
FROM alpine:3.19
COPY --from=aelsabbahy/goss:latest /usr/local/bin/goss /usr/local/bin/goss
COPY goss.yaml /goss/goss.yaml
HEALTHCHECK --interval=30s CMD goss -g /goss/goss.yaml validate
```
