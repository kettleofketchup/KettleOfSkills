# Traefik EntryPoints - Complete Example & Helm Values

## Complete Multi-EntryPoint Example

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
          permanent: true

  websecure:
    address: ":443"
    http:
      tls:
        certResolver: letsencrypt
      middlewares:
        - security-headers@file
    forwardedHeaders:
      trustedIPs:
        - 10.0.0.0/8
    transport:
      respondingTimeouts:
        readTimeout: 60s
        idleTimeout: 180s

  traefik:
    address: ":8080"  # Dashboard

  metrics:
    address: ":8082"  # Prometheus metrics

  tcp:
    address: ":3306/tcp"

  udp:
    address: ":53/udp"
```

## Kubernetes Helm Values

```yaml
# values.yaml
ports:
  web:
    port: 8000
    exposedPort: 80
    expose: true
    protocol: TCP
  websecure:
    port: 8443
    exposedPort: 443
    expose: true
    protocol: TCP
    tls:
      enabled: true
      certResolver: letsencrypt
  traefik:
    port: 9000
    expose: false  # Internal only

additionalArguments:
  - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
  - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
```
