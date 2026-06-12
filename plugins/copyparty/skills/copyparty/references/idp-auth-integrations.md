# Copyparty IdP Integration Examples

## Authelia Integration

### Docker Compose

```yaml
services:
  copyparty:
    image: copyparty/ac:latest
    labels:
      - "traefik.http.routers.cpp.middlewares=authelia@docker"

  authelia:
    image: authelia/authelia:4.39
    labels:
      - "traefik.http.middlewares.authelia.forwardAuth.address=http://authelia:9091/api/authz/forward-auth"
      - "traefik.http.middlewares.authelia.forwardAuth.trustForwardHeader=true"
      - "traefik.http.middlewares.authelia.forwardAuth.authResponseHeaders=Remote-User,Remote-Groups,Remote-Name,Remote-Email"
```

### Copyparty Config

```yaml
[global]
  idp-h-usr: remote-user
  idp-h-grp: remote-groups
  xff-src: lan
```

### Authelia Access Control

```yaml
# authelia configuration.yml
access_control:
  default_policy: deny
  rules:
    - domain: 'files.example.com'
      policy: one_factor
```

### WebDAV/rclone Through Authelia

Authelia requires one_factor policy for the domain. rclone config uses `Proxy-Authorization` header:

```ini
[cpp-dav]
type = webdav
url = https://files.example.com/u/alice/priv/
vendor = owncloud
pacer_min_sleep = 0.01ms
headers = Proxy-Authorization,basic YWxpY2U6cGFzc3dvcmQ=
```

The base64 string is `username:password` encoded. Generate with: `echo -n 'user:pass' | base64`

## Authentik Integration

### Expected Headers

authentik forward-auth proxy provider injects:
- `X-authentik-username`
- `X-authentik-groups` (pipe-separated: `group1|group2`)
- `X-authentik-email`
- `X-authentik-name`

### Copyparty Config

```yaml
[global]
  idp-h-usr: X-authentik-username
  idp-h-grp: X-authentik-groups
  xff-src: lan
  idp-login: /outpost.goauthentik.io/start/?rd={dst}
  idp-logout: /outpost.goauthentik.io/sign_out
```

### Traefik Forward-Auth

```yaml
# traefik dynamic config
http:
  middlewares:
    authentik:
      forwardAuth:
        address: http://authentik-server:9000/outpost.goauthentik.io/auth/traefik
        trustForwardHeader: true
        authResponseHeaders:
          - X-authentik-username
          - X-authentik-groups
          - X-authentik-email
```

## Tailscale Integration

```yaml
[global]
  idp-hm-usr: ^Tailscale-User-Login^alice.m@forest.net^alice
  idp-hm-usr: ^Tailscale-User-Login^bob@corp.net^bob
  xff-src: 100.64.0.0/10  # Tailscale subnet
```

## Generic Header Auth

For any reverse proxy that injects a username header:

```yaml
[global]
  idp-h-usr: x-idp-user
  idp-h-grp: x-idp-group
  idp-h-key: my-shared-secret
  xff-src: lan
  auth-ord: idp,cookie,basic
  idp-cookie: true  # cookie-based session bypass (for slow IdPs)
```
