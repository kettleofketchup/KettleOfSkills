# Copyparty Reverse Proxy Configuration

## Overview

Copyparty supports running behind nginx, caddy, traefik, apache, haproxy, lighttpd. Two modes:
1. **Subdomain** (recommended): copyparty gets its own domain/subdomain
2. **Subpath**: use `--rp-loc=/stuff` to tell copyparty its mount point

## Real-IP Configuration (Critical)

When behind a reverse proxy or Cloudflare, copyparty must know the real client IP. Without this, unpost, banning, and rate limiting break.

```yaml
[global]
  xff-hdr: x-forwarded-for           # default
  xff-hdr: cf-connecting-ip          # for Cloudflare

  xff-src: 127.0.0.0/8, ::1/128     # default (localhost only)
  xff-src: lan                       # all private/LAN IPs
  xff-src: 10.88.0.0/16             # specific subnet
  xff-src: any                       # trust all (only with cf-connecting-ip)

  rproxy: 1    # first IP in header (default, good for single proxy)
  rproxy: -1   # rightmost/nearest proxy
  rproxy: 0    # use TCP connection IP (no proxy)
```

**Important:** If everyone gets "thank you for playing" bans, real-IP is misconfigured.

## Nginx (Recommended)

```nginx
upstream cpp_tcp {
    server 127.0.0.1:3923 fail_timeout=1s;
    keepalive 1;
}

server {
    listen 443 ssl;
    server_name fs.example.com;

    location / {
        proxy_pass http://cpp_tcp;
        proxy_redirect off;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_buffers 32 8k;
        proxy_buffer_size 16k;

        proxy_set_header Connection "Keep-Alive";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
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
    # ... same headers
}
```

Run copyparty with `--rp-loc /qw/er`.

### Unix Socket (5-10% faster)

```nginx
upstream cpp_uds {
    server unix:/dev/shm/party.sock fail_timeout=1s;
    keepalive 1;
}
```

Run copyparty with: `copyparty -i unix:770:www:/dev/shm/party.sock`

nginx and copyparty must share a common group.

## Copyparty Config for Reverse Proxy

```yaml
[global]
  xff-hdr: x-forwarded-for
  xff-src: lan
  rproxy: 1

  # Subpath (if not using dedicated subdomain)
  rp-loc: /files

  # Cloudflare-specific
  xff-hdr: cf-connecting-ip
  xff-src: any
```

## Troubleshooting

- **"thank you for playing"**: Real-IP misconfigured. Check server log
- **"incorrect --rp-loc"**: Webserver stripping proxy location from URLs
- **copyparty thinks HTTP not HTTPS**: Reverse proxy not sending `X-Forwarded-Proto: https`
- **Thumbnails broken**: Proxy stripping query parameters (`?th=w`) or bad caching
- **WebDAV with IdP**: See IdP docs for rclone workarounds with base64 auth header

See [reverse-proxy-other.md](reverse-proxy-other.md) for Caddy, Traefik, Apache, HAProxy, Cloudflare, and performance benchmarks.
