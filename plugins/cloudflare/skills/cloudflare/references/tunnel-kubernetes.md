# Cloudflare Tunnel Kubernetes Deployment Reference

*Last updated: 2026-03-23*

## Image

`cloudflare/cloudflared:2026.3.0` (latest stable as of March 2026)

Tag convention: `cloudflare/cloudflared:<year>.<month>.<patch>`. Pin to specific version in production.

## Deployment Pattern

Use **Deployment with 2 replicas** for HA. Each replica connects to 2+ Cloudflare data centers (4 connections each). Max 25 replicas per tunnel.

**Do NOT autoscale** — downscaling breaks active connections.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudflared
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cloudflared
  template:
    spec:
      containers:
        - name: cloudflared
          image: cloudflare/cloudflared:2026.3.0
          args:
            - tunnel
            - --config
            - /etc/cloudflared/config/config.yaml
            - --no-autoupdate
            - --metrics
            - 0.0.0.0:2000
            - run
          ports:
            - containerPort: 2000
              name: metrics
          livenessProbe:
            httpGet:
              path: /ready
              port: 2000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 2000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              memory: 256Mi
          volumeMounts:
            - name: creds
              mountPath: /etc/cloudflared/creds
              readOnly: true
            - name: config
              mountPath: /etc/cloudflared/config
              readOnly: true
      volumes:
        - name: creds
          secret:
            secretName: cloudflared-credentials
        - name: config
          secret:
            secretName: cloudflared-config
```

## Config File (config.yaml)

```yaml
tunnel: <TUNNEL-UUID>
credentials-file: /etc/cloudflared/creds/credentials.json
protocol: auto        # auto | quic | http2
no-autoupdate: true
metrics: 0.0.0.0:2000

# Route ALL traffic to Traefik (let Traefik do host-based routing)
ingress:
  - hostname: "*.home.kettle.sh"
    service: http://traefik.traefik.svc.cluster.local:80
  - service: http_status:404
```

### Ingress Rule Options

```yaml
ingress:
  - hostname: app.example.com
    path: /api/.*                    # Optional path regex
    service: http://backend:8080
    originRequest:
      connectTimeout: 30s
      noTLSVerify: true              # Skip TLS verification to backend
      httpHostHeader: app.example.com # Override Host header
      originServerName: app.example.com # TLS SNI
```

### Service URL Formats

| Format | Use |
|--------|-----|
| `http://svc.ns.svc.cluster.local:port` | HTTP backend |
| `https://svc.ns.svc.cluster.local:port` | HTTPS backend |
| `http_status:404` | Catch-all (required, must be last) |

## Credential File

Created by `cloudflared tunnel create <name>`. JSON format:

```json
{
  "AccountTag": "account-id",
  "TunnelID": "uuid",
  "TunnelName": "name",
  "TunnelSecret": "base64-secret"
}
```

### SOPS Encryption

```bash
sops --encrypt --age <AGE-PUBLIC-KEY> \
  --encrypted-regex '^(data|stringData)$' \
  secret-credentials.yaml > secret-credentials.enc.yaml
```

Use ksops generator in kustomization:

```yaml
# secret-generator.yaml
apiVersion: viaduct.ai/v1
kind: ksops
metadata:
  name: cloudflared-secrets
files:
  - secret-cloudflared-credentials.enc.yaml
  - secret-cloudflared-config.enc.yaml
```

## Tunnel CLI Commands

```bash
# Create tunnel
cloudflared tunnel create my-tunnel

# Create DNS record
cloudflared tunnel route dns my-tunnel app.example.com

# List tunnels
cloudflared tunnel list

# Delete tunnel
cloudflared tunnel delete my-tunnel
```

## Connecting to Traefik

**Recommended: HTTP to Traefik port 80** (TLS terminated at Cloudflare edge):

```yaml
ingress:
  - hostname: "*.home.kettle.sh"
    service: http://traefik.traefik.svc.cluster.local:80
  - service: http_status:404
```

Configure Traefik to trust forwarded headers from cloudflared pod CIDR:

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
