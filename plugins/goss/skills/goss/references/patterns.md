---
description: Modular gossfiles, auto-generating tests, retry/wait patterns, health endpoints, common test patterns, gotchas
last_updated: 2026-03-18
---

# Goss Patterns & Best Practices

## Modular Gossfiles

Split tests across files and import:

```yaml
# goss.yaml (main entry)
gossfile:
  goss.d/packages.yaml: {}
  goss.d/services.yaml: {}
  goss.d/network.yaml: {}
  goss.d/security.yaml: {}

# Glob patterns
gossfile:
  goss.d/*.yaml: {}
  /etc/goss.d/*.yaml: {}

# Conditional includes
gossfile:
  optional-tests.yaml:
    skip: '{{if eq .Vars.env "dev"}}true{{end}}'
```

Render all into single file: `goss render > merged.yaml`

## Auto-generating Tests

```bash
# Add specific resource
goss add file /etc/nginx/nginx.conf
goss add service nginx
goss add port tcp:80
goss add user www-data
goss add dns example.com

# Auto-discover everything related to a service
goss autoadd sshd    # adds service, port, process, user, package, etc.
goss autoadd nginx

# Exclude noisy attributes
goss add file /etc/hosts --exclude-attr mode
```

`autoadd` discovers: package, service, port, process, user, group associated with the name.

## Retry/Wait Patterns

### Startup Validation

```bash
# Retry for 30s, checking every 2s
goss validate --retry-timeout 30s --sleep 2s

# Useful for waiting on services to start
goss validate --retry-timeout 2m --sleep 5s --format documentation
```

All tests re-run on each retry. Passes when all tests pass within timeout.

### Health Endpoint

```bash
# Start health endpoint
goss serve --format json --listen-addr 0.0.0.0:8080 --cache 10s

# Query with specific format
curl http://localhost:8080/healthz
curl -H "Accept: application/vnd.goss-json" http://localhost:8080/healthz

# Response codes: 200 = pass, 503 = fail
```

Use `--cache` to prevent re-running tests on every request. Content negotiation via Accept header: `application/vnd.goss-{format}`.

## JSON Schema Validation

IDE support via JSON Schema at `https://goss.rocks/schema.yaml`:

```json
// VS Code settings.json
{
  "yaml.schemas": {
    "https://goss.rocks/schema.yaml": "goss*.yaml"
  }
}
```

## Common Test Patterns

See [patterns-examples.md](patterns-examples.md) for web server, security baseline, and container smoke test examples.

## Gotchas

- **Duplicate type keys**: YAML silently overwrites. All resources of same type under one key
- **Mount `defaults`**: fstab alias, not actual mount option; check `mount` output
- **Command timeout**: In milliseconds (10000 = 10s), not seconds
- **Port format**: Must include protocol prefix: `tcp:80:`, not just `80`
- **Package manager**: Specify `--package deb|rpm|apk|pacman` for correct detection
- **Array matching**: Default is subset (contains); use `consist-of`/`equal` for exact
- **Template rendering**: Errors surface at render time, not validate time; use `goss render` to debug
- **gossfile paths**: Relative to the gossfile containing the include, not CWD
- **skip as string**: `skip` field expects string `"true"`, not boolean, when using templates
