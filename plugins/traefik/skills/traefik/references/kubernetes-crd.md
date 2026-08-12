# Traefik Kubernetes CRDs

## Available CRDs

| CRD | API Version | Purpose |
|-----|-------------|---------|
| IngressRoute | traefik.io/v1alpha1 | HTTP routing |
| IngressRouteTCP | traefik.io/v1alpha1 | TCP routing |
| IngressRouteUDP | traefik.io/v1alpha1 | UDP routing |
| Middleware | traefik.io/v1alpha1 | HTTP middleware |
| MiddlewareTCP | traefik.io/v1alpha1 | TCP middleware |
| TraefikService | traefik.io/v1alpha1 | Advanced load balancing |
| TLSOption | traefik.io/v1alpha1 | TLS parameters |
| TLSStore | traefik.io/v1alpha1 | Default certificates |
| ServersTransport | traefik.io/v1alpha1 | Backend transport settings |
| ServersTransportTCP | traefik.io/v1alpha1 | TCP backend transport |

## IngressRoute

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: myapp
  namespace: default
spec:
  entryPoints:
    - web
    - websecure
  routes:
    - match: Host(`myapp.example.com`)
      kind: Rule
      priority: 10
      services:
        - name: myapp-svc
          port: 80
          weight: 1
          passHostHeader: true
          sticky:
            cookie:
              name: myapp-sticky
      middlewares:
        - name: auth-middleware
          namespace: default
  tls:
    certResolver: letsencrypt
    domains:
      - main: myapp.example.com
        sans:
          - www.myapp.example.com
    options:
      name: modern-tls
      namespace: default
    secretName: myapp-tls
```

## Middleware CRD

```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: auth-middleware
  namespace: default
spec:
  basicAuth:
    secret: auth-secret
    removeHeader: true
---
apiVersion: v1
kind: Secret
metadata:
  name: auth-secret
type: kubernetes.io/basic-auth
stringData:
  username: admin
  password: password123
```

### Common Middleware Examples

```yaml
# Rate limiting
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: ratelimit
spec:
  rateLimit:
    average: 100
    burst: 50
    period: 1m
---
# Strip path prefix
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: strip-api
spec:
  stripPrefix:
    prefixes:
      - /api
---
# Add headers
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: security-headers
spec:
  headers:
    frameDeny: true
    browserXssFilter: true
    contentTypeNosniff: true
    stsSeconds: 31536000
    stsIncludeSubdomains: true
---
# Redirect to HTTPS
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: redirect-https
spec:
  redirectScheme:
    scheme: https
    permanent: true
---
# Forward auth
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: forward-auth
spec:
  forwardAuth:
    address: http://auth-service.default.svc.cluster.local/verify
    authResponseHeaders:
      - X-User-Id
      - X-User-Email
```

For TraefikService (weighted/mirroring/failover), TLSOption CRD, and provider config → [kubernetes-crd-advanced.md](kubernetes-crd-advanced.md)
