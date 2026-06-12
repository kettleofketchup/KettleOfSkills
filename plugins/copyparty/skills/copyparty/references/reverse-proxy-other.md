# Copyparty Reverse Proxy: Caddy, Traefik, Apache, HAProxy, Cloudflare

## Caddy

```bash
# Unix socket (recommended)
caddy reverse-proxy --from :8080 --to unix///dev/shm/party.sock

# TCP
caddy reverse-proxy --from :8081 --to http://127.0.0.1:3923
```

## Traefik

```yaml
# contrib/traefik/copyparty.yaml
# Use Traefik v3.6.7+ due to CVE-2025-66490
http:
  routers:
    copyparty:
      rule: "Host(`files.example.com`)"
      service: copyparty
      entryPoints:
        - websecure
      tls:
        certResolver: letsencrypt
  services:
    copyparty:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:3923"
```

## Apache

See `contrib/apache/copyparty.conf`. Key setting:
```apache
ProxyPass / http://127.0.0.1:3923/
ProxyPassReverse / http://127.0.0.1:3923/
```

For subpath: do NOT strip the location prefix (copyparty needs it).

## HAProxy

See `contrib/haproxy/copyparty.conf`.

## Lighttpd

See `contrib/lighttpd/subdomain.conf` (full domain) or `contrib/lighttpd/subpath.conf`.

## Cloudflare Tunnel

### Quick Tunnel (Anonymous)

```bash
cloudflared tunnel --url http://127.0.0.1:3923
```

### Permanent Tunnel

1. Create tunnel in Cloudflare Dashboard > Zero Trust > Networks > Tunnels
2. Set service type `http`, URL `127.0.0.1:3923`
3. Run: `cloudflared --no-autoupdate tunnel run --token BASE64`

```yaml
[global]
  xff-hdr: cf-connecting-ip  # Required for Cloudflare
```

### Nginx Cloudflare IP Allowlist

```bash
(curl -s https://www.cloudflare.com/ips-v{4,6} | \
  sed 's/^/allow /; s/$/;/'; echo; echo "deny all;") \
  > /etc/nginx/cloudflare-only.conf
# Include in server block: include /etc/nginx/cloudflare-only.conf;
```

## Performance Comparison

### Unix Socket (UDS)

| Metric | No Proxy | HAProxy | Caddy | Nginx | Apache | Lighttpd |
|--------|----------|---------|-------|-------|--------|----------|
| req/s | 28,900 | 18,750 | 9,900 | 18,700 | 9,700 | 9,900 |
| upload MiB/s | 6,900 | 3,500 | 3,750 | 2,200 | 1,750 | 1,300 |
| download MiB/s | 7,400 | 2,370 | 2,200 | 1,570 | 1,830 | 1,470 |

### TCP (127.0.0.1)

| Metric | No Proxy | HAProxy | Traefik | Caddy | Nginx | Apache | Lighttpd |
|--------|----------|---------|---------|-------|-------|--------|----------|
| req/s | 21,200 | 14,500 | 11,100 | 8,400 | 13,400 | 8,400 | 6,500 |
| upload MiB/s | 5,700 | 1,700 | 2,750 | 2,300 | 1,100 | 1,000 | 1,270 |
| download MiB/s | 6,700 | 2,170 | 2,000 | 1,950 | 1,480 | 1,000 | 1,500 |

Summary: `haproxy > caddy > traefik > nginx > apache > lighttpd`. Use UDS when possible.

**Note:** HTTP/1.1 is often 5x faster than HTTP/2. nginx-QUIC (HTTP/3) can make uploads slower.
