# Cloudflare Tunnel — Connecting to Traefik

## Recommended: HTTP to Traefik Port 80

TLS is terminated at the Cloudflare edge. Route all traffic to Traefik and let Traefik handle per-host routing:

```yaml
ingress:
  - hostname: "*.home.kettle.sh"
    service: http://traefik.traefik.svc.cluster.local:80
  - service: http_status:404
```

Configure Traefik to trust forwarded headers from the cloudflared pod CIDR:

```yaml
# Traefik Helm values
entryPoints:
  web:
    forwardedHeaders:
      trustedIPs:
        - 10.244.0.0/16    # Cluster pod CIDR
  websecure:
    forwardedHeaders:
      trustedIPs:
        - 10.244.0.0/16
```
