# Traefik Forward Auth Middleware

## Overview

Authentik proxy provider + outpost acts as forward auth middleware for Traefik.
Protects any app behind Traefik without modifying the app itself.

## Architecture

```
Client → Traefik → forwardAuth → Authentik Outpost (port 9000/9443)
                                       ↓ (authenticated)
                 Traefik → Backend App (with X-authentik-* headers)
```

## Setup Steps

### 1. Create Proxy Provider

Admin UI → Applications → Providers → Create → Proxy Provider:

| Setting | Value |
|---------|-------|
| Name | `forward-auth-<app>` or `forward-auth-domain` |
| Authorization flow | `default-provider-authorization-implicit-consent` |
| Mode | **Forward auth (single application)** or **Forward auth (domain level)** |
| External host | `https://app.example.com` (single) or `https://auth.example.com` (domain) |
| Authentication flow | Default authentication flow |

### 2. Create Application

Bind the proxy provider to an application with appropriate slug.

### 3. Create/Configure Outpost

Admin UI → Applications → Outposts:
- **Embedded outpost** (simplest): auto-deployed, no extra pods
- **Standalone outpost**: separate deployment, better for production

Outpost config:
```json
{
  "log_level": "info",
  "authentik_host": "https://auth.example.com",
  "kubernetes_namespace": "authentik",
  "kubernetes_service_type": "ClusterIP"
}
```

Outpost listens on:
- Port `9000` (HTTP)
- Port `9443` (HTTPS)
- Port `9300` (Prometheus metrics)

### 4. Traefik Middleware (Kubernetes CRDs)

#### Single Application Mode

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: authentik-auth
  namespace: authentik
spec:
  forwardAuth:
    address: http://ak-outpost-<outpost-name>.authentik.svc.cluster.local:9000/outpost.goauthentik.io/auth/traefik
    trustForwardHeader: true
    authResponseHeaders:
      - X-authentik-username
      - X-authentik-groups
      - X-authentik-entitlements
      - X-authentik-email
      - X-authentik-name
      - X-authentik-uid
      - X-authentik-meta-outpost
      - X-authentik-meta-provider
      - X-authentik-meta-app
      - X-authentik-meta-version
```

#### Domain-Level Mode

For domain-level, all apps on a domain share one authentication session:

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: authentik-auth-domain
  namespace: authentik
spec:
  forwardAuth:
    address: http://ak-outpost-<outpost-name>.authentik.svc.cluster.local:9000/outpost.goauthentik.io/auth/traefik
    trustForwardHeader: true
    authResponseHeaders:
      - X-authentik-username
      - X-authentik-groups
      - X-authentik-entitlements
      - X-authentik-email
      - X-authentik-name
      - X-authentik-uid
```

### 5. Apply Middleware to IngressRoute

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: my-protected-app
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`app.example.com`)
      kind: Rule
      middlewares:
        - name: authentik-auth
          namespace: authentik
      services:
        - name: my-app
          port: 80
```

## Embedded Outpost

Uses the authentik server itself (no separate outpost deployment).
Service name pattern: `authentik-server` on port 9000.

```yaml
spec:
  forwardAuth:
    address: http://authentik-server.authentik.svc.cluster.local:9000/outpost.goauthentik.io/auth/traefik
```

## Headers Injected

| Header | Value |
|--------|-------|
| `X-authentik-username` | Username |
| `X-authentik-groups` | Pipe-delimited groups (`foo\|bar\|baz`) |
| `X-authentik-entitlements` | Pipe-delimited entitlements |
| `X-authentik-email` | Email address |
| `X-authentik-name` | Full name |
| `X-authentik-uid` | Hashed user identifier |
| `X-authentik-meta-outpost` | Outpost name |
| `X-authentik-meta-provider` | Provider name |
| `X-authentik-meta-app` | Application slug |

## Unauthenticated Paths

Regex patterns to skip auth (compiled with Go regex):
- Single app: matches request path
- Domain-level: matches full URL

## Logout

- Single app: `https://app.example.com/outpost.goauthentik.io/sign_out`
- Domain-level: `https://auth.example.com/outpost.goauthentik.io/sign_out`

## Blueprint Example

```yaml
- model: authentik_providers_proxy.proxyprovider
  state: present
  identifiers:
    name: forward-auth-myapp
  id: proxy-myapp
  attrs:
    authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
    mode: forward_single
    external_host: https://app.example.com

- model: authentik_core.application
  state: present
  identifiers:
    slug: myapp
  attrs:
    name: My Protected App
    provider: !KeyOf proxy-myapp

- model: authentik_outposts.outpost
  state: present
  identifiers:
    name: authentik Embedded Outpost
  attrs:
    providers:
      - !KeyOf proxy-myapp
    type: proxy
    config:
      authentik_host: https://auth.example.com
```
