# Open WebUI Nginx Configuration Variants

## Nginx Proxy Manager

1. Create directory `~/nginx_config`, create `docker-compose.yml` with `jc21/nginx-proxy-manager:latest` (ports 80, 81, 443)
2. Configure DNS/domain (e.g., DuckDNS) pointing to proxy's local IP
3. Access NPM at `http://server_ip:81`, default login: `admin@example.com` / `changeme`
4. SSL Certificates: Add Let's Encrypt cert with DNS challenge (DuckDNS token). Domain format: `*.hello.duckdns.org` and `hello.duckdns.org`
5. Proxy Hosts: Set domain, scheme HTTP, enable WebSocket support, point to Docker IP, select SSL cert

**Critical:** Set `CORS_ALLOW_ORIGIN="https://openwebui.hello.duckdns.org"` in Open WebUI config.

**Advanced tab custom config (required):**
```nginx
proxy_buffering off;
proxy_cache off;
proxy_read_timeout 1800;
proxy_send_timeout 1800;
proxy_connect_timeout 1800;
```

Exclude from caching: `/api/`, `/auth/`, `/signup/`, `/signin/`, `/sso/`, `/admin/`, `/signout/`, `/oauth/`, `/login/`, `/logout/`.

## Let's Encrypt (Docker)

### Phase 1: Certificate Validation
1. Create dirs: `mkdir -p nginx/conf.d ssl/certbot/conf ssl/certbot/www`
2. Create temp nginx config (`nginx/conf.d/open-webui.conf`) listening on port 80, serving `/.well-known/acme-challenge/`
3. Add nginx service to docker-compose with ports 80/443, volumes for configs and certbot dirs

### Phase 2: Obtain Certificate
Run certbot via Docker:
```bash
docker compose up -d nginx
docker run --rm -v "./ssl/certbot/conf:/etc/letsencrypt" -v "./ssl/certbot/www:/var/www/certbot" \
  certbot/certbot certonly --webroot --webroot-path=/var/www/certbot --email EMAIL --agree-tos -d DOMAIN
```

### Phase 3: HTTPS Config
Replace nginx config with full SSL server block: redirect 80->443, SSL certs from Let's Encrypt, TLS 1.2/1.3, separate location blocks for auth (no-cache), images (1d cache), static assets (7d cache), and default (proxy_buffering off, 1800s timeouts).

### Auto-Renewal
```cron
30 3 * * * /usr/bin/docker run --rm -v "PATH/ssl/certbot/conf:/etc/letsencrypt" -v "PATH/ssl/certbot/www:/var/www/certbot" certbot/certbot renew --quiet --webroot --webroot-path=/var/www/certbot --deploy-hook "docker compose restart nginx"
```

## Self-Signed Certificate (Docker)

1. Create dirs: `mkdir -p conf.d ssl`
2. Generate cert: `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/nginx.key -out ssl/nginx.crt -subj "/CN=your_domain_or_IP"`
3. Nginx config: listen 443 ssl, `proxy_pass http://host.docker.internal:3000`, proxy_buffering off, WebSocket headers, 1800s timeouts
4. Docker Compose: nginx:alpine with port 443, mount conf.d and ssl dirs

Caching strategy: Auth endpoints (no-cache, no-store), profile/model images (1d), static assets (7d), default (5min with must-revalidate).

## Windows Self-Signed (No Docker)

Assumes `open-webui serve` via pip installation.

1. Install OpenSSL: `choco install openssl -y`
2. Install nginx from nginx.org, extract to `C:\nginx`
3. Generate cert: `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx.key -out nginx.crt`
4. Configure `C:\nginx\conf\nginx.conf`:
   - Map block for WebSocket upgrade
   - Server on port 80 redirecting to 443
   - Server on 443 with SSL, proxy to `localhost:8080`
   - Auth endpoints: no-cache, proxy_buffering off
   - Static assets: 7d cache
   - Default: 1800s timeouts, proxy_buffering off
5. Test: `nginx -t`, start: `nginx`, reload: `nginx -s reload`

## Full Optimized Nginx Config

```nginx
upstream openwebui {
    server 127.0.0.1:3000;
    keepalive 128;
    keepalive_timeout 1800s;
    keepalive_requests 10000;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    gzip on;
    gzip_types text/plain text/css application/javascript image/svg+xml;
    # DO NOT include: application/json, text/event-stream

    location /api/ {
        proxy_pass http://openwebui;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        gzip off;
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_cache off;
        tcp_nodelay on;
        add_header X-Accel-Buffering "no" always;
        proxy_connect_timeout 1800;
        proxy_send_timeout 1800;
        proxy_read_timeout 1800;
    }

    location ~ ^/(ws/|socket\.io/) {
        proxy_pass http://openwebui;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        gzip off;
        proxy_buffering off;
        proxy_connect_timeout 86400;
        proxy_send_timeout 86400;
        proxy_read_timeout 86400;
    }

    location /static/ {
        proxy_pass http://openwebui;
        proxy_buffering on;
        proxy_cache_valid 200 7d;
        add_header Cache-Control "public, max-age=604800, immutable";
    }

    location / {
        proxy_pass http://openwebui;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Streaming Mistakes to Avoid

| Setting | Impact |
|---------|--------|
| `gzip on` with `application/json` | Buffers for compression |
| `proxy_buffering on` | Buffers entire response |
| `tcp_nodelay on` | Most critical: disables Nagle's algorithm |
| `chunked_transfer_encoding on` | Can break SSE |
| `proxy_cache` on `/api/` | Adds overhead |
| `X-Accel-Buffering "yes"` | Should be "no" |
