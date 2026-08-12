---
name: traefik
description: Traefik v3 reverse proxy and load balancer for Kubernetes and Docker. Covers entrypoints, IngressRoute CRDs, middlewares, load balancing, TLS/ACME, and HTTP/TCP/UDP routing.
---

# Traefik v3

Cloud-native reverse proxy and load balancer with automatic service discovery. Traefik connects incoming requests to backend services using dynamic configuration from providers (Kubernetes, Docker, etc.).

## Quick Start (Kubernetes Helm)

```bash
helm repo add traefik https://traefik.github.io/charts
helm install traefik traefik/traefik
```

**Install CRDs manually (if needed):**
```bash
kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v3.6/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml
kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v3.6/docs/content/reference/dynamic-configuration/kubernetes-crd-rbac.yml
```

## Core Concepts

| Component | Description |
|-----------|-------------|
| **EntryPoints** | Network ports where Traefik listens (e.g., :80, :443) |
| **Routers** | Match incoming requests using rules (Host, Path, Headers) |
| **Services** | Define backend targets with load balancing |
| **Middlewares** | Transform requests/responses (auth, headers, redirects) |
| **Providers** | Configuration sources (Kubernetes, Docker, File) |

## Task Reference

### Routing Configuration
- HTTP rules, matchers, priority → [references/routing.md](references/routing.md)
- TCP/UDP routing, IngressRouteTCP/UDP → [references/routing-tcp-udp.md](references/routing-tcp-udp.md)

### Kubernetes CRDs
- IngressRoute, Middleware CRDs → [references/kubernetes-crd.md](references/kubernetes-crd.md)
- TraefikService, TLSOption, provider config → [references/kubernetes-crd-advanced.md](references/kubernetes-crd-advanced.md)

### Middlewares
- Auth: BasicAuth, ForwardAuth, IPAllowList, Chain → [references/middlewares-auth.md](references/middlewares-auth.md)
- Traffic: RateLimit, Headers, Redirects, CircuitBreaker → [references/middlewares-traffic.md](references/middlewares-traffic.md)

### Load Balancing & Services
- Strategies, health checks, sticky sessions → [references/services-load-balancing.md](references/services-load-balancing.md)
- Weighted, mirroring, failover, TCP/UDP → [references/services-advanced.md](references/services-advanced.md)

### TLS & Certificates
- ACME/Let's Encrypt, challenges, manual certs → [references/tls-acme.md](references/tls-acme.md)
- TLS options, mTLS, router TLS, passthrough → [references/tls-options.md](references/tls-options.md)

### EntryPoints
- Configuration, redirects, proxy protocol → [references/entrypoints.md](references/entrypoints.md)
- Complete example, Helm values → [references/entrypoints-helm.md](references/entrypoints-helm.md)

## Minimal IngressRoute Example

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: myapp
  namespace: default
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`myapp.example.com`)
      kind: Rule
      services:
        - name: myapp-svc
          port: 80
      middlewares:
        - name: myapp-headers
  tls:
    certResolver: letsencrypt
```

## Common CLI/Static Config

```yaml
# traefik.yml (static configuration)
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

providers:
  kubernetesCRD: {}
  kubernetesIngress: {}

certificateResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /data/acme.json
      httpChallenge:
        entryPoint: web
```

## Official Documentation
- [Traefik Docs](https://doc.traefik.io/traefik/)
- [Kubernetes CRD Reference](https://doc.traefik.io/traefik/reference/install-configuration/providers/kubernetes/kubernetes-crd/)
- [Middleware Reference](https://doc.traefik.io/traefik/reference/routing-configuration/http/middlewares/overview/)
