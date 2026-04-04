# Trusted Header Authentication

Open WebUI can delegate authentication to a reverse proxy that passes user details in HTTP headers.

**Security Warning:** Incorrect configuration can allow users to authenticate as any user. Make sure to allow only the authenticating proxy access to Open WebUI, such as by not opening any ports directly to the container, or by setting `HOST=127.0.0.1` so it only listens on the loopback interface.

## Generic Configuration

Set `WEBUI_AUTH_TRUSTED_EMAIL_HEADER` to the header name containing the user's email. Open WebUI handles automatic registration and login.

Example: Setting `WEBUI_AUTH_TRUSTED_EMAIL_HEADER=X-User-Email` and passing `X-User-Email: example@example.com` authenticates as that email.

Optional: `WEBUI_AUTH_TRUSTED_NAME_HEADER` sets the name for newly created users. If not set, the email address is used.

### Group Management via Trusted Header

Set `WEBUI_AUTH_TRUSTED_GROUPS_HEADER` to the header name containing a comma-separated list of group names.

- Header value must be comma-separated group names (e.g., `X-User-Groups: admins,editors,users`)
- If header is not present or empty, group memberships are not updated
- User will be unassigned from groups not present in the header
- Group creation via trusted header is not automatic; only existing groups are assigned

### Role Management via Trusted Header

Set `WEBUI_AUTH_TRUSTED_ROLE_HEADER` to the header name containing the desired role.

- Header value must be one of `admin`, `user`, or `pending` (case-insensitive, trimmed)
- When present and valid, the user's role is updated on every sign-in
- Invalid values are ignored with a warning logged
- Missing/empty header leaves the existing role unchanged

**Security:** When configured, this header allows setting admin-level access. Only allow your trusted reverse proxy to set this header.

## Tailscale Serve

Tailscale sets `Tailscale-User-Login` with the email address of the requester.

Tailscale Serve config (`tailscale/serve.json`):

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

Docker Compose with Tailscale sidecar:

```yaml
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

If Tailscale runs in the same network context as Open WebUI, users can directly reach Open WebUI without going through the Serve proxy. Use Tailscale ACLs to restrict access to only port 443.

## Cloudflare Tunnel with Cloudflare Access

Cloudflare sets `Cf-Access-Authenticated-User-Email` with the authenticated user's email.

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    volumes:
      - open-webui:/app/backend/data
    environment:
      - WEBUI_AUTH_TRUSTED_EMAIL_HEADER=Cf-Access-Authenticated-User-Email
    restart: unless-stopped
  cloudflared:
    image: cloudflare/cloudflared:latest
    environment:
      - TUNNEL_TOKEN=${TUNNEL_TOKEN}
    command: tunnel run
    restart: unless-stopped
volumes:
  open-webui: {}
```

## oauth2-proxy

oauth2-proxy is an authenticating reverse proxy that implements social OAuth providers and OIDC support.

Example with Google OAuth:

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    volumes:
      - open-webui:/app/backend/data
    environment:
      - 'WEBUI_AUTH_TRUSTED_EMAIL_HEADER=X-Forwarded-Email'
      - 'WEBUI_AUTH_TRUSTED_NAME_HEADER=X-Forwarded-User'
    restart: unless-stopped
  oauth2-proxy:
    image: quay.io/oauth2-proxy/oauth2-proxy:v7.6.0
    environment:
      OAUTH2_PROXY_HTTP_ADDRESS: 0.0.0.0:4180
      OAUTH2_PROXY_UPSTREAMS: http://open-webui:8080/
      OAUTH2_PROXY_PROVIDER: google
      OAUTH2_PROXY_CLIENT_ID: REPLACEME_OAUTH_CLIENT_ID
      OAUTH2_PROXY_CLIENT_SECRET: REPLACEME_OAUTH_CLIENT_ID
      OAUTH2_PROXY_EMAIL_DOMAINS: REPLACEME_ALLOWED_EMAIL_DOMAINS
      OAUTH2_PROXY_REDIRECT_URL: REPLACEME_OAUTH_CALLBACK_URL
      OAUTH2_PROXY_COOKIE_SECRET: REPLACEME_COOKIE_SECRET
      OAUTH2_PROXY_COOKIE_SECURE: "false"
    restart: unless-stopped
    ports:
      - 4180:4180/tcp
```

## Authentik

Redirect URI: `<open-webui>/oauth/oidc/callback`

```
ENABLE_OAUTH_SIGNUP=true
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true
OAUTH_PROVIDER_NAME=Authentik
OPENID_PROVIDER_URL=https://<authentik-url>/application/o/<App-name>/.well-known/openid-configuration
OAUTH_CLIENT_ID=<Client-ID>
OAUTH_CLIENT_SECRET=<Client-Secret>
OAUTH_SCOPES=openid email profile
OPENID_REDIRECT_URI=https://<open-webui>/oauth/oidc/callback
```

## Authelia

Authelia can return a header for trusted header authentication. See Authelia documentation for configuration details.
