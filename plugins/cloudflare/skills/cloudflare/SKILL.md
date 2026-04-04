---
name: cloudflare
description: Cloudflare Tunnel (cloudflared) deployment on Kubernetes, Cloudflare Access Service Tokens for machine-to-machine auth, DNS management, and integration with Traefik IngressRoutes and Authentik forwardAuth. Use when deploying cloudflared tunnels, creating Access applications and service tokens, configuring dual-route IngressRoutes for human vs machine access, managing Cloudflare DNS records via API, or troubleshooting tunnel connectivity and Access policy issues.
---

# Cloudflare Tunnel + Access + Traefik Integration

Expose Kubernetes services through Cloudflare Tunnel with opt-in per-service access, Authentik forwardAuth for humans, and Service Tokens for machine-to-machine auth.

## Architecture

```
Human (browser):
  → Cloudflare DNS (proxied) → CF Access (IdP) → Tunnel → cloudflared → Traefik
    → forwardAuth (Authentik) → app

Machine (service token):
  → Cloudflare DNS (proxied) → CF Access (Service Token) → Tunnel → cloudflared → Traefik
    → HeadersRegexp match → app (skips forwardAuth)
```

Cloudflare Access = outer gate (validates before traffic reaches cluster).
Traefik = inner gate (routes by header presence, applies forwardAuth for humans).

## Quick Reference

| Task | Reference |
|------|-----------|
| Tunnel deployment on K8s | [references/tunnel-kubernetes.md](references/tunnel-kubernetes.md) |
| Access Service Tokens API | [references/access-service-tokens.md](references/access-service-tokens.md) |
| Traefik dual-route pattern | [references/traefik-integration.md](references/traefik-integration.md) |
| DNS management | [references/dns-management.md](references/dns-management.md) |

## Dual-Route IngressRoute Pattern

Per exposed service, two routes on the same IngressRoute:

```yaml
routes:
  # Route 1: Machine access (CF Service Token — skips forwardAuth)
  - match: Host(`app.home.kettle.sh`) && HeadersRegexp(`Cf-Access-Jwt-Assertion`, `.+`)
    kind: Rule
    priority: 100
    services:
      - name: app-svc
        port: 80

  # Route 2: Human access (forwardAuth)
  - match: Host(`app.home.kettle.sh`)
    kind: Rule
    priority: 10
    middlewares:
      - name: authentik-forwardauth
        namespace: authentik
    services:
      - name: app-svc
        port: 80
```

Route 1 matches first (higher priority) when `Cf-Access-Jwt-Assertion` header is present (Cloudflare validated the service token). Route 2 catches all other requests and applies Authentik forwardAuth.

**IMPORTANT:** Check `Cf-Access-Jwt-Assertion` (the JWT), not `CF-Access-Client-Id` (the raw token). Cloudflare strips the raw token and replaces it with a signed JWT after validation. If the JWT header is present, Cloudflare already validated the request.

## Opt-In Service Exposure

Only services with a Cloudflare DNS record pointing to the tunnel get exposed. The tunnel config maps hostnames to Traefik:

```yaml
# cloudflared config.yaml
ingress:
  - hostname: "*.home.kettle.sh"
    service: http://traefik.traefik.svc.cluster.local:80
  - service: http_status:404
```

Traefik IngressRoutes handle per-host routing. No IngressRoute = Traefik returns 404.

## Cloudflare Access Policy Model

Per-application in Cloudflare Access:

| App | Human Policy | Machine Policy |
|-----|-------------|----------------|
| grafana.home.kettle.sh | Allow: IdP (Authentik) | Service Auth: "dota-production" token |
| foundry.home.kettle.sh | Allow: IdP (Authentik) | None (human-only) |
| argocd.home.kettle.sh | Allow: IdP (Authentik) | None (human-only) |
| celery.home.kettle.sh | None | Service Auth: "dota-production" token |

**Policy `decision` must be `non_identity`** for Service Token policies. Using `allow` redirects to IdP login.

## Defense in Depth

1. **Cloudflare Access** — validates service token before traffic enters tunnel
2. **Tunnel** — outbound-only, no inbound ports on cluster
3. **Traefik HeadersRegexp** — routes by JWT presence
4. **Traefik IPAllowList** — restrict machine routes to cluster pod CIDR
5. **JWT validation** — application-level verification of `Cf-Access-Jwt-Assertion` for high-security services

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Policy `decision: allow` for service tokens | Use `decision: non_identity` (Service Auth) |
| Checking `CF-Access-Client-Id` header at Traefik | Check `Cf-Access-Jwt-Assertion` — Cloudflare strips raw token |
| `allowCrossNamespace` not enabled in Traefik | Set `providers.kubernetesCRD.allowCrossNamespace: true` |
| cloudflared connecting to Traefik HTTPS without `noTLSVerify` | Use HTTP backend or set `originRequest.noTLSVerify: true` |
| ForwardAuth address using wrong port | Authentik embedded outpost: `http://authentik-server.authentik.svc.cluster.local/outpost.goauthentik.io/auth/traefik` |
| DNS record still proxied through Cloudflare after removing tunnel | Delete the CNAME record entirely; DNS-only mode still resolves to Cloudflare |
