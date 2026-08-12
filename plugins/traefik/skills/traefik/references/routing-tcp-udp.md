# Traefik TCP/UDP Routing

## TCP Router

```yaml
tcp:
  routers:
    my-tcp-router:
      entryPoints:
        - tcp
      rule: HostSNI(`example.com`)  # Requires TLS
      service: my-tcp-service
      tls:
        passthrough: true  # TLS passthrough to backend
```

## TCP Matchers

| Matcher | Description |
|---------|-------------|
| `HostSNI()` | Match TLS SNI (requires TLS) |
| `HostSNIRegexp()` | SNI with regex |
| `ClientIP()` | Match client IP |
| `ALPN()` | Match TLS ALPN protocol |

## UDP Router

```yaml
udp:
  routers:
    my-udp-router:
      entryPoints:
        - udp
      service: my-udp-service
```

UDP routers have no rules - they forward all traffic on the entrypoint.

## TCP Kubernetes IngressRouteTCP

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRouteTCP
metadata:
  name: db-route
spec:
  entryPoints:
    - tcp
  routes:
    - match: HostSNI(`db.example.com`)
      services:
        - name: db-svc
          port: 5432
  tls:
    passthrough: true
```

## UDP Kubernetes IngressRouteUDP

```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRouteUDP
metadata:
  name: dns-route
spec:
  entryPoints:
    - udp
  routes:
    - services:
        - name: dns-svc
          port: 53
```
