# K3s Private Registry Configuration

## File Location

`/etc/rancher/k3s/registries.yaml` — K3s reads on startup, generates containerd config.
Restart K3s after changes. Configure on **every node** (servers and agents).

## Full Format

```yaml
mirrors:
  <REGISTRY_HOSTNAME>:
    endpoint:
      - "https://<MIRROR_URL>"
    rewrite:
      "^original/(.*)": "replacement/$1"
configs:
  <REGISTRY_HOSTNAME>:
    auth:
      username: <string>
      password: <string>
      token: <bearer-token>
    tls:
      ca_file: <path>
      cert_file: <path>
      key_file: <path>
      insecure_skip_verify: <bool>
```

## Mirror Examples

### Docker Hub through local mirror

```yaml
mirrors:
  docker.io:
    endpoint:
      - "https://registry.local:5000"
```

Pulling `docker.io/library/nginx:latest` transparently fetches from `registry.local:5000/library/nginx:latest`.

### Multiple registries mirrored

```yaml
mirrors:
  docker.io:
    endpoint:
      - "https://registry.local:5000"
  ghcr.io:
    endpoint:
      - "https://registry.local:5000"
  quay.io:
    endpoint:
      - "https://registry.local:5000"
```

### Wildcard default mirror

```yaml
mirrors:
  "*":
    endpoint:
      - "https://registry.local:5000"
```

Applies to all registries without a specific entry.

### Image name rewrites

```yaml
mirrors:
  docker.io:
    endpoint:
      - "https://registry.local:5000"
    rewrite:
      "^rancher/(.*)": "k3s-mirror/rancher-images/$1"
```

`docker.io/rancher/pause:3.6` → `registry.local:5000/k3s-mirror/rancher-images/pause:3.6`

## Authentication

### Basic auth

```yaml
configs:
  "registry.local:5000":
    auth:
      username: admin
      password: secret
```

### Bearer token

```yaml
configs:
  "registry.local:5000":
    auth:
      token: "eyJhbGciOiJSUzI1NiIs..."
```

## TLS Configuration

### Private CA

```yaml
configs:
  "registry.local:5000":
    tls:
      ca_file: /etc/ssl/certs/registry-ca.pem
```

### Mutual TLS (client cert)

```yaml
configs:
  "registry.local:5000":
    tls:
      ca_file: /etc/ssl/certs/registry-ca.pem
      cert_file: /etc/ssl/certs/client.pem
      key_file: /etc/ssl/private/client-key.pem
```

### Skip TLS verification (development only)

```yaml
configs:
  "registry.local:5000":
    tls:
      insecure_skip_verify: true
```

See `references/registries-advanced.md` for combined examples, default endpoint behavior, troubleshooting, and NixOS integration.
