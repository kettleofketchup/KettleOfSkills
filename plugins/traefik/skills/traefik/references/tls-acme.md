# Traefik TLS - ACME (Let's Encrypt)

## Basic ACME Configuration

```yaml
certificateResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /data/acme.json
      caServer: https://acme-v02.api.letsencrypt.org/directory
      keyType: RSA4096  # EC256, EC384, RSA2048, RSA4096, RSA8192

      # Choose ONE challenge type
      httpChallenge:
        entryPoint: web
      # OR
      tlsChallenge: {}
      # OR
      dnsChallenge:
        provider: cloudflare
```

## Challenge Types

| Challenge | Port | Wildcard | Notes |
|-----------|------|----------|-------|
| HTTP-01 | 80 | No | Most common, requires port 80 |
| TLS-ALPN-01 | 443 | No | Uses TLS handshake |
| DNS-01 | None | Yes | Only option for wildcards |

## HTTP Challenge

```yaml
certificateResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /data/acme.json
      httpChallenge:
        entryPoint: web  # Must listen on :80
```

## DNS Challenge

```yaml
certificateResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /data/acme.json
      dnsChallenge:
        provider: cloudflare
        delayBeforeCheck: 10s
        resolvers:
          - 1.1.1.1:53
          - 8.8.8.8:53
```

**Environment variables for Cloudflare:**
```bash
CF_API_EMAIL=user@example.com
CF_API_KEY=your-api-key
# Or use API token:
CF_DNS_API_TOKEN=your-token
```

Common providers: `cloudflare`, `route53`, `gcloud`, `digitalocean`, `azure`, `namecheap`

## Wildcard Certificates

```yaml
http:
  routers:
    wildcard:
      rule: HostRegexp(`[a-z]+\.example\.com`)
      tls:
        certResolver: letsencrypt
        domains:
          - main: example.com
            sans:
              - "*.example.com"
```

## Staging Server

```yaml
certificateResolvers:
  letsencrypt-staging:
    acme:
      email: admin@example.com
      storage: /data/acme-staging.json
      caServer: https://acme-staging-v02.api.letsencrypt.org/directory
      httpChallenge:
        entryPoint: web
```

## Manual Certificates (File Provider)

```yaml
tls:
  certificates:
    - certFile: /certs/example.com.crt
      keyFile: /certs/example.com.key
    - certFile: /certs/other.com.crt
      keyFile: /certs/other.com.key
```

## Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-tls
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
---
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: myapp
spec:
  routes:
    - match: Host(`myapp.example.com`)
      kind: Rule
      services:
        - name: myapp
          port: 80
  tls:
    secretName: myapp-tls
```

## Default Certificate

```yaml
tls:
  stores:
    default:
      defaultCertificate:
        certFile: /certs/default.crt
        keyFile: /certs/default.key
      # Or: defaultGeneratedCert: {resolver: letsencrypt, domain: {main: example.com}}
```
