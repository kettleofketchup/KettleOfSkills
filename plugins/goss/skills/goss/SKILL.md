---
name: goss
description: "Goss YAML-based server validation and testing tool. This skill should be used when writing goss.yaml gossfiles, validating server configuration (packages, services, files, ports, processes, users, groups, DNS, HTTP endpoints, mounts, kernel parameters, network interfaces), using goss CLI commands (validate, serve, add, autoadd, render), testing Docker containers with dgoss, testing Kubernetes pods with kgoss, testing docker-compose stacks with dcgoss, writing goss templates with Go text/template and Sprig functions, using goss matchers (regex, numeric, semver, gjson), configuring goss serve health endpoints, modularizing gossfiles with includes, or troubleshooting goss validation failures."
last_updated: 2026-03-18
---

# Goss - Server Validation Tool

YAML-based server testing/validation tool. Single Go binary, no dependencies. Generates tests from current system state via `goss add`/`goss autoadd`.

## Installation

```bash
# Binary install
curl -L https://github.com/goss-org/goss/releases/latest/download/goss-linux-amd64 -o /usr/local/bin/goss
chmod +rx /usr/local/bin/goss

# dgoss (Docker wrapper)
curl -L https://raw.githubusercontent.com/goss-org/goss/master/extras/dgoss/dgoss -o /usr/local/bin/dgoss
chmod +rx /usr/local/bin/dgoss
```

## CLI Quick Reference

| Command | Alias | Purpose |
|---------|-------|---------|
| `goss validate` | `goss v` | Run tests, show results |
| `goss serve` | `goss s` | Expose health endpoint (default `:8080/healthz`) |
| `goss add <type> <name>` | `goss a` | Add single resource test |
| `goss autoadd <name>` | `goss aa` | Auto-discover all resources for a service |
| `goss render` | `goss r` | Render gossfile with includes/templates |

### Common Flags

```bash
goss validate --format documentation   # verbose output
goss validate --retry-timeout 30s      # retry for 30s (startup waits)
goss validate -g custom.yaml           # custom gossfile
goss validate --vars vars.yaml         # template variables
goss serve --listen-addr 0.0.0.0:9000 --format json --cache 30s
```

### Output Formats

`rspecish` (default), `documentation`, `json`, `junit`, `tap`, `nagios`, `prometheus`, `silent`

## Resource Types

| Type | Key Attributes | Notes |
|------|---------------|-------|
| `file` | exists, mode, owner, group, contents, filetype, sha256 | Supports checksums, symlink targets |
| `package` | installed, versions | Use `--package` flag for manager type |
| `service` | enabled, running | systemd/init |
| `port` | listening, ip | Format: `tcp:22:`, `tcp6:22:`, `udp:53:` |
| `process` | running | Match by command name |
| `command` | exit-status, stdout, stderr, timeout | Default timeout 10s (in ms) |
| `user` | exists, uid, gid, groups, home, shell | |
| `group` | exists, gid | |
| `dns` | resolvable, addrs, server | Record types: A, AAAA, CNAME, MX, etc. |
| `http` | status, body, headers, allow-insecure | Auth, TLS certs, proxy support |
| `addr` | reachable, timeout | Remote TCP/UDP reachability |
| `mount` | exists, filesystem, source, opts, usage | `defaults` is fstab alias, not actual opt |
| `kernel-param` | value | sysctl parameters |
| `interface` | exists, addrs, mtu | Network interfaces |
| `gossfile` | (import) | Include other gossfiles, supports globs |
| `matching` | content, matches | Best with templates for complex assertions |

## Gossfile Structure

```yaml
# Multiple resources consolidated under single type key
# YAML overwrites duplicate keys - never declare same type twice
package:
  nginx: {installed: true}
  curl: {installed: true}

service:
  nginx:
    enabled: true
    running: true

port:
  tcp:80:
    listening: true
  tcp:443:
    listening: true

file:
  /etc/nginx/nginx.conf:
    exists: true
    mode: "0644"
    owner: root

# Import other gossfiles
gossfile:
  goss.d/*.yaml: {}
```

## Reference Files

| File | Content |
|------|---------|
| `references/matchers.md` | Pattern matching, regex, numeric/array/logical matchers, gjson |
| `references/templating.md` | Go templates, Sprig functions, variables, conditionals |
| `references/containers.md` | dgoss (Docker), kgoss (Kubernetes), dcgoss (docker-compose) |
| `references/patterns.md` | Modular gossfiles, retry/wait patterns, health endpoints, gotchas |

## Cross-References

- **Docker images**: Use `docker` skill for Dockerfile writing, then goss `dgoss` for validation
- **Kubernetes**: Use `k3s` skill for cluster setup, then goss `kgoss` for pod validation
- **CI/CD**: Use `gitlab-ci` or `github` skills for pipeline integration with `goss validate --format junit`
