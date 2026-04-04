# Open WebUI HTTPS & Reverse Proxy Configuration

HTTPS encrypts traffic and is required for browser features like Voice Calls (microphone access blocked on non-HTTPS).

## Approach Comparison

| Method | Best For | TLS Management |
|---|---|---|
| Cloudflare Tunnel | Production, no open ports | Automatic (Cloudflare edge) |
| ngrok | Development and testing | Automatic (ngrok edge) |
| Tailscale | Private access across devices | Automatic (tailscale serve) |
| Nginx | Self-hosted production | Manual or Let's Encrypt |
| Caddy | Self-hosted, minimal config | Automatic (Let's Encrypt) |
| HAProxy | High-availability / load balancing | Manual or Let's Encrypt |

## Key Configuration Notes

| Setting | Why It Matters |
|---|---|
| `WEBUI_URL` | Set to public HTTPS URL for OAuth callbacks |
| `CORS_ALLOW_ORIGIN` | Must match public URL or WebSocket fails |
| Proxy buffering OFF | Required for SSE streaming |
| WebSocket support | Pass `Upgrade` and `Connection` headers |
| Extended timeouts | LLM responses can take minutes (300s+) |

## Cloudflare Tunnel

No open ports, no certs, no reverse proxy. Creates outbound-only connection.

**Dashboard setup:** Zero Trust > Networks > Tunnels > Create > Add Public Hostname (HTTP, localhost:8080).

**CLI setup:**
```bash
cloudflared tunnel login
cloudflared tunnel create open-webui
cloudflared tunnel route dns open-webui chat.your-domain.com
```

Config (`~/.cloudflared/config.yml`):
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /home/USER/.cloudflared/TUNNEL_ID.json
ingress:
  - hostname: chat.your-domain.com
    service: http://localhost:8080
  - service: http_status:404
```

**Docker Compose:** No `ports` needed on open-webui. cloudflared connects via Docker network. Change service URL to `http://open-webui:8080`.

**System service:** `sudo cloudflared service install && sudo systemctl enable cloudflared`

## ngrok

Instant public HTTPS for development. Free-tier URLs change on restart.

```bash
ngrok config add-authtoken YOUR_TOKEN
ngrok http 8080
```

Custom domain (paid): `ngrok http 8080 --url=your-name.ngrok-free.app`

## Tailscale

Private mesh VPN with automatic HTTPS certificates.

```bash
sudo tailscale up
sudo tailscale serve https / http://localhost:8080
```

Access at `https://my-server.tail1234.ts.net`. Enable HTTPS in Tailscale Admin > DNS.

**Funnel** (public access): `sudo tailscale funnel https / http://localhost:8080`

## Caddy

Automatic TLS with Let's Encrypt. Minimal config.

```caddyfile
your-domain.com {
  reverse_proxy localhost:8080
}
```

Install Caddy, edit `/etc/caddy/Caddyfile`, run `docker compose up -d`.

## HAProxy

Install: `sudo apt install haproxy certbot openssl -y`

Key config sections: global (SSL, DH param), defaults (timeouts: 300s http-request, 10m client/server), frontend (port 80/443, Let's Encrypt ACL, subdomain/path routing), backend (forwardfor, X-Forwarded-Proto).

For HTTP/2 WebSocket issues: add `option h2-workaround-bogus-websocket-clients` to defaults/frontend.

Self-signed placeholder: `openssl req -x509 -newkey rsa:2048 -keyout /tmp/haproxy.key -out /tmp/haproxy.crt -days 3650 -nodes -subj "/CN=localhost"`

Let's Encrypt: `certbot certonly -n --standalone --preferred-challenges http --http-01-port-8688 -d yourdomain.com`

Combine cert: `cat fullchain.pem privkey.pem > /etc/haproxy/certs/domain.pem`

## Nginx Critical Configuration

**CORS for WebSocket:** Set `CORS_ALLOW_ORIGIN` env var. Failure causes silent WebSocket failures.

**HTTP/2 + WebSocket:** Use `proxy_http_version 1.1` with `Upgrade`/`Connection` headers for backend.

**Disable proxy buffering (critical for SSE):**
```nginx
proxy_buffering off;
proxy_cache off;
```

Without this: garbled markdown, visible `##`/`**`, missing words in streaming responses.

**Optimized upstream:**
```nginx
upstream openwebui {
    server 127.0.0.1:3000;
    keepalive 128;
    keepalive_timeout 1800s;
}
```

**Timeouts:** API: 1800s (30 min). WebSocket: 86400s (24 hr).

**Headers/limits:** `client_max_body_size 100M`, `proxy_buffer_size 128k`, `large_client_header_buffers 4 32k`.

**Never cache:** `/api/v1/auths/`, `/oauth/`, `/api/` (general), `/ws/`.

## Monitoring

**Level 1:** `GET /health` -- No auth, returns 200 when service is up.

**Level 2:** `GET /api/models` with auth -- Verifies provider connectivity. JSONata: `$count(data[*])>0`.

**Level 3:** `POST /api/chat/completions` with real prompt -- End-to-end inference validation.

## OpenTelemetry

Enable with `ENABLE_OTEL=true`, `ENABLE_OTEL_TRACES=true`, `ENABLE_OTEL_METRICS=true`, `OTEL_EXPORTER_OTLP_ENDPOINT=http://grafana:4317`.

Instruments: FastAPI routes, SQLAlchemy queries, Redis, httpx/aiohttp calls.

Metrics: `http.server.requests` (counter), `http.server.duration` (histogram in ms).

Quick start: `docker compose -f docker-compose.otel.yaml up -d` -- sets up Grafana LGTM stack.
