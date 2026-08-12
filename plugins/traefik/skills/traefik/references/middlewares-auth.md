# Traefik Middlewares - Authentication

## Available HTTP Middlewares (Reference)

| Middleware | Purpose |
|------------|---------|
| AddPrefix | Adds path prefix to request |
| BasicAuth | HTTP Basic Authentication |
| Buffering | Buffers request/response |
| Chain | Combines multiple middlewares |
| CircuitBreaker | Prevents calling unhealthy services |
| Compress | Compresses responses (gzip, brotli) |
| ContentType | Handles Content-Type auto-detection |
| DigestAuth | HTTP Digest Authentication |
| Errors | Custom error pages |
| ForwardAuth | Delegates auth to external service |
| GrpcWeb | Converts gRPC-Web to HTTP/2 gRPC |
| Headers | Adds/modifies headers |
| IPAllowList | Restricts by client IP |
| InFlightReq | Limits concurrent connections |
| PassTLSClientCert | Passes client cert in header |
| RateLimit | Limits request rate |
| RedirectScheme | Redirects HTTP to HTTPS |
| RedirectRegex | Redirects based on regex |
| ReplacePath | Replaces request path |
| ReplacePathRegex | Replaces path with regex |
| Retry | Retries failed requests |
| StripPrefix | Removes path prefix |
| StripPrefixRegex | Removes prefix with regex |

## BasicAuth

```yaml
http:
  middlewares:
    auth:
      basicAuth:
        users:
          - "admin:$apr1$xyz..."  # htpasswd format
        usersFile: /path/to/users  # Or external file
        realm: "My Realm"
        removeHeader: true  # Remove auth header from backend
```

Generate password: `htpasswd -nb admin password`

**Kubernetes Secret:**
```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: auth
spec:
  basicAuth:
    secret: auth-secret
```

## ForwardAuth

```yaml
http:
  middlewares:
    forward-auth:
      forwardAuth:
        address: https://auth.example.com/verify
        trustForwardHeader: true
        authResponseHeaders:
          - X-User-Id
          - X-User-Email
        authRequestHeaders:
          - Authorization
```

Headers sent to auth service: `X-Forwarded-Method`, `X-Forwarded-Proto`, `X-Forwarded-Host`, `X-Forwarded-Uri`, `X-Forwarded-For`

## IPAllowList

```yaml
http:
  middlewares:
    internal:
      ipAllowList:
        sourceRange:
          - 10.0.0.0/8
          - 192.168.0.0/16
        ipStrategy:
          depth: 1  # Use X-Forwarded-For depth
```

## Chain (Combine Middlewares)

```yaml
http:
  middlewares:
    secured:
      chain:
        middlewares:
          - https-redirect
          - security-headers
          - ratelimit
          - auth
```
