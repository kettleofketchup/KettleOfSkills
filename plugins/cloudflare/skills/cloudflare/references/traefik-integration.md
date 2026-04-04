# Traefik + Cloudflare Tunnel Integration Reference

*Last updated: 2026-03-23*

## Dual-Route IngressRoute Pattern

Two routes per service: machine access (high priority, no forwardAuth) and human access (low priority, forwardAuth).

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: grafana
  namespace: grafana
spec:
  entryPoints:
    - websecure
  routes:
    # Machine access: CF Service Token validated by Cloudflare
    - match: Host(`grafana.home.kettle.sh`) && HeadersRegexp(`Cf-Access-Jwt-Assertion`, `.+`)
      kind: Rule
      priority: 100
      services:
        - name: grafana
          port: 3000

    # Human access: Authentik forwardAuth
    - match: Host(`grafana.home.kettle.sh`)
      kind: Rule
      priority: 10
      middlewares:
        - name: authentik-forwardauth
          namespace: authentik
      services:
        - name: grafana
          port: 3000
```

**Priority**: Higher number = evaluated first. Route 1 (priority 100) matches when JWT header present. Route 2 (priority 10) catches everything else.

**Header to check**: Use `Cf-Access-Jwt-Assertion` (the signed JWT), NOT `CF-Access-Client-Id` (raw token — Cloudflare strips it after validation).

## HeadersRegexp Syntax

```
# Match any non-empty value
HeadersRegexp(`Cf-Access-Jwt-Assertion`, `.+`)

# Match specific Client ID
HeadersRegexp(`CF-Access-Client-Id`, `^abc123\.access$`)

# Combine with AND
Host(`app.example.com`) && HeadersRegexp(`Cf-Access-Jwt-Assertion`, `.+`)
```

Uses Go `regexp` syntax. Values must use backticks.

## Cross-Namespace Middleware

**Required**: `providers.kubernetesCRD.allowCrossNamespace: true` in Traefik Helm values.

Without this, IngressRoutes can only reference middleware in their own namespace. Error: `middleware authentik/authentik-forwardauth is not in the IngressRoute namespace`.

**Chain middleware limitation**: Middlewares within a chain must be in the same namespace as the chain itself.

## IPAllowList for Tunnel Traffic

cloudflared runs in-cluster — source IP is the pod IP, not the real client.

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: cluster-only
spec:
  ipAllowList:
    sourceRange:
      - 10.244.0.0/16    # Cluster pod CIDR
```

For real client IP filtering, use `ipStrategy.depth`:
```yaml
spec:
  ipAllowList:
    sourceRange:
      - 203.0.113.50/32    # Droplet IP
    ipStrategy:
      depth: 1              # Use last X-Forwarded-For entry
```

## Forwarded Headers Trust

Configure Traefik to trust headers from cloudflared:

```yaml
# Traefik Helm values
entryPoints:
  web:
    forwardedHeaders:
      trustedIPs:
        - 10.244.0.0/16
  websecure:
    forwardedHeaders:
      trustedIPs:
        - 10.244.0.0/16
```

## Cloudflare Headers Available at Traefik

| Header | Description |
|--------|-------------|
| `CF-Connecting-IP` | Real visitor IP |
| `CF-IPCountry` | Two-letter country code |
| `CF-Ray` | Unique request ID |
| `X-Forwarded-For` | Visitor IP chain |
| `X-Forwarded-Proto` | `https` |
| `Cf-Access-Jwt-Assertion` | Signed JWT (if Access configured) |

## JWT Validation (Defense in Depth)

For high-security services, validate `Cf-Access-Jwt-Assertion` at the app layer:

1. Fetch public keys: `https://<team>.cloudflareaccess.com/cdn-cgi/access/certs`
2. Verify JWT signature (RS256)
3. Validate claims: `aud` (Application AUD tag), `iss`, `exp`

Keys rotate every ~6 weeks — fetch dynamically, don't hardcode.

## Human-Only Services (No Machine Access)

For services that should never accept service tokens:

```yaml
routes:
  - match: Host(`foundry.home.kettle.sh`)
    kind: Rule
    middlewares:
      - name: authentik-forwardauth
        namespace: authentik
    services:
      - name: foundry
        port: 30000
```

Single route, no priority needed. All requests go through forwardAuth regardless of headers.
