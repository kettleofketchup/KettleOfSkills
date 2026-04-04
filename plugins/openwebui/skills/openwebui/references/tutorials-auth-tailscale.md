# Tailscale SSO and Docker Setup for Open WebUI

## Authentication via Tailscale (SSO)

Tailscale Serve can act as an authenticating reverse proxy. When a request passes through `tailscale serve`, Tailscale automatically sets the `Tailscale-User-Login` header with the email address of the authenticated user. Open WebUI can trust this header as a single sign-on mechanism. Users on your tailnet are automatically logged in without needing a separate Open WebUI password.

### How it works

1. A Tailscale sidecar container runs alongside Open WebUI
2. Tailscale Serve proxies HTTPS traffic to Open WebUI and injects identity headers
3. Open WebUI reads `Tailscale-User-Login` and `Tailscale-User-Name` to identify the user
4. Users are auto-registered and logged in on first visit

### Docker Compose Setup

Create a `tailscale/serve.json` file that configures Tailscale Serve to proxy to Open WebUI:

```json
{
    "TCP": {
        "443": {
            "HTTPS": true
        }
    },
    "Web": {
        "${TS_CERT_DOMAIN}:443": {
            "Handlers": {
                "/": {
                    "Proxy": "http://open-webui:8080"
                }
            }
        }
    }
}
```

Then set up the Docker Compose file with a Tailscale sidecar:

```yaml
---
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    volumes:
      - open-webui:/app/backend/data
    environment:
      - WEBUI_AUTH_TRUSTED_EMAIL_HEADER=Tailscale-User-Login
      - WEBUI_AUTH_TRUSTED_NAME_HEADER=Tailscale-User-Name
    restart: unless-stopped
  tailscale:
    image: tailscale/tailscale:latest
    environment:
      - TS_AUTH_ONCE=true
      - TS_AUTHKEY=${TS_AUTHKEY}
      - TS_EXTRA_ARGS=--advertise-tags=tag:open-webui
      - TS_SERVE_CONFIG=/config/serve.json
      - TS_STATE_DIR=/var/lib/tailscale
      - TS_HOSTNAME=open-webui
    volumes:
      - tailscale:/var/lib/tailscale
      - ./tailscale:/config
      - /dev/net/tun:/dev/net/tun
    cap_add:
      - net_admin
      - sys_module
    restart: unless-stopped

volumes:
  open-webui: {}
  tailscale: {}
```

You will need to create an OAuth client with **device write** permission in the Tailscale admin console and pass the key as `TS_AUTHKEY`.

Your instance will be reachable at `https://open-webui.TAILNET_NAME.ts.net`.

**Important:** If you run Tailscale in the same network context as Open WebUI, users could bypass the Serve proxy and reach Open WebUI directly, skipping the trusted header authentication. Use Tailscale ACLs to restrict access to only port 443.

---

## Tailscale Funnel (Optional Public Access)

If you want to share Open WebUI publicly without requiring Tailscale on the client, Tailscale Funnel exposes your `tailscale serve` endpoint to the internet:

```bash
sudo tailscale funnel https / http://localhost:8080
```

Your Open WebUI is now publicly accessible at `https://my-server.tail1234.ts.net` with a valid TLS certificate. Funnel routes traffic through Tailscale's infrastructure, similar to Cloudflare Tunnel.

**Warning:** Funnel makes your Open WebUI accessible to **anyone on the internet**. Make sure you have authentication configured in Open WebUI before enabling it.

---

## Quick Reference

| What | Command / Value |
| :--- | :--- |
| Connect to tailnet | `sudo tailscale up` |
| Check hostname | `tailscale status` |
| Serve over HTTPS | `sudo tailscale serve https / http://localhost:8080` |
| Public access (Funnel) | `sudo tailscale funnel https / http://localhost:8080` |
| Generate cert manually | `sudo tailscale cert my-server.tail1234.ts.net` |
| Admin console | login.tailscale.com/admin |
| Set CORS origin | `CORS_ALLOW_ORIGIN=https://my-server.tail1234.ts.net` |
| Trusted email header | `WEBUI_AUTH_TRUSTED_EMAIL_HEADER=Tailscale-User-Login` |
| Trusted name header | `WEBUI_AUTH_TRUSTED_NAME_HEADER=Tailscale-User-Name` |
