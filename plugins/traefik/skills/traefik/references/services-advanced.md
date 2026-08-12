# Traefik Advanced Services (Weighted, Mirroring, Failover)

## Weighted Service (TraefikService CRD)

Distribute traffic across multiple services:

```yaml
apiVersion: traefik.io/v1alpha1
kind: TraefikService
metadata:
  name: canary
spec:
  weighted:
    services:
      - name: app-stable
        port: 80
        weight: 90
      - name: app-canary
        port: 80
        weight: 10
```

File provider equivalent:
```yaml
http:
  services:
    canary:
      weighted:
        services:
          - name: app-stable
            weight: 90
          - name: app-canary
            weight: 10
```

## Mirroring

Send a copy of traffic to another service:

```yaml
apiVersion: traefik.io/v1alpha1
kind: TraefikService
metadata:
  name: mirror
spec:
  mirroring:
    name: production-svc
    port: 80
    mirrors:
      - name: shadow-svc
        port: 80
        percent: 20
        excludeBody: true   # Don't mirror request body
        maxBodySize: 1024   # Limit mirrored body size
```

File provider equivalent:
```yaml
http:
  services:
    mirror:
      mirroring:
        service: production
        mirrors:
          - name: shadow
            percent: 20
```

## Failover

Route to fallback on primary failure:

```yaml
apiVersion: traefik.io/v1alpha1
kind: TraefikService
metadata:
  name: failover
spec:
  failover:
    service:
      name: primary-svc
      port: 80
    fallback:
      name: backup-svc
      port: 80
```

Requires health checks on primary service.

## TCP Services

```yaml
tcp:
  services:
    my-tcp:
      loadBalancer:
        servers:
          - address: backend1:3306
          - address: backend2:3306
        terminationDelay: 100ms
```

## UDP Services

```yaml
udp:
  services:
    my-udp:
      loadBalancer:
        servers:
          - address: backend1:53
          - address: backend2:53
```
