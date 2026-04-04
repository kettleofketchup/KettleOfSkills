# Copyparty Reverse Proxy Configuration

## Overview

Copyparty supports running behind nginx, caddy, traefik, apache, haproxy, lighttpd. Two modes:
1. **Subdomain** (recommended): copyparty gets its own domain/subdomain
2. **Subpath**: use `--rp-loc=/stuff` to tell copyparty its mount point (slight performance cost)

## Real-IP Configuration (Critical)

When behind a reverse proxy or Cloudflare, copyparty must know the real client IP. Without this, features like unpost, banning, and rate limiting break.

```yaml
[global]
  # Which header contains the real IP
  xff-hdr: x-forwarded-for           # default
  xff-hdr: cf-connecting-ip          # for Cloudflare

  # Trust reverse proxy from these subnets
  xff-src: 127.0.0.0/8, ::1/128     # default (localhost only)
  xff-src: lan                       # all private/LAN IPs
  xff-src: 10.88.0.0/16             # specific subnet
  xff-src: any                       # trust all (only with cf-connecting-ip)

  # How to pick client IP from header
  rproxy: 1    # first IP in header (default, good for single proxy)
  rproxy: -1   # rightmost/nearest proxy (usually NOT the client)
  rproxy: -2   # second from right
  rproxy: 0    # use TCP connection IP (no proxy)
```

**Important:** If everyone gets "thank you for playing" bans, real-IP is misconfigured.

## Nginx (Recommended)

```nginx
upstream cpp_tcp {
    server 127.0.0.1:3923 fail_timeout=1s;
    keepalive 1;
}

# Alternative: unix socket (5-10% faster)
upstream cpp_uds {
    server unix:/dev/shm/party.sock fail_timeout=1s;
    keepalive 1;
}

server {
    listen 443 ssl;
    server_name fs.example.com;

    location / {
        proxy_pass http://cpp_tcp;  # or http://cpp_uds
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_request_buffering off;
        # Speed optimization
        proxy_buffers 32 8k;
        proxy_buffer_size 16k;
        proxy_busy_buffers_size 24k;

        proxy_set_header Connection "Keep-Alive";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        # For Cloudflare:
        #proxy_set_header X-Forwarded-For $http_cf_connecting_ip;
    }
}

# Required for large uploads
client_max_body_size 1024M;
client_header_timeout 610m;
client_body_timeout 610m;
send_timeout 610m;
```

### Nginx Subpath

```nginx
location /qw/er/ {
    proxy_pass http://cpp_tcp/qw/er/;
    # ... same headers as above
}
```

And run copyparty with `--rp-loc /qw/er`.

### Cloudflare IP Allowlist for Nginx

```bash
# Generate allowlist
(curl -s https://www.cloudflare.com/ips-v{4,6} | \
  sed 's/^/allow /; s/$/;/'; echo; echo "deny all;") \
  > /etc/nginx/cloudflare-only.conf

# Include in server block:
# include /etc/nginx/cloudflare-only.conf;
```

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

See `contrib/lighttpd/subdomain.conf` (full domain) or `contrib/lighttpd/subpath.conf` (location-based).

## Unix Socket (Recommended)

Listen on unix socket for better security and 5-10% more performance:

```bash
# Run copyparty with:
copyparty -i unix:770:www:/dev/shm/party.sock

# 770 = permission, www = group
# nginx and copyparty must share a common group
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

## Copyparty Config for Reverse Proxy

```yaml
[global]
  # Basic reverse proxy setup
  xff-hdr: x-forwarded-for
  xff-src: lan           # or specific subnet
  rproxy: 1              # use first IP from xff header

  # Subpath (if not using dedicated subdomain)
  rp-loc: /files         # must match proxy location

  # Cloudflare-specific
  xff-hdr: cf-connecting-ip
  xff-src: any           # safe because cf-connecting-ip is trustworthy

  # Disable bans if troubleshooting (NOT recommended for production)
  # ban-404: no
  # ban-403: no
  # ban-422: no
  # ban-url: no
  # ban-pw: no
```

## Troubleshooting

- **"thank you for playing"**: Real-IP misconfigured. Check server log for guidance
- **"incorrect --rp-loc"**: Webserver is stripping the proxy location from URLs
- **copyparty thinks HTTP not HTTPS**: Reverse proxy not sending `X-Forwarded-Proto: https`
- **Thumbnails broken**: Proxy stripping query parameters (`?th=w`) or bad caching
- **WebDAV with IdP**: See IdP docs for rclone workarounds with base64 auth header
