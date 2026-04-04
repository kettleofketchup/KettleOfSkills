# Copyparty Identity Provider (IdP) Integration

Replace copyparty passwords with external auth via reverse-proxy header injection.

## Architecture

```
Client → Reverse Proxy → IdP Middleware → Copyparty
                         (injects headers)
```

IdP service (Authelia, authentik, etc.) sits as middleware in the reverse proxy. Authenticated requests get headers injected (username, groups). Copyparty reads those headers instead of using its own password auth.

## Global Configuration

```yaml
[global]
  # Required: header containing authenticated username
  idp-h-usr: Remote-User              # Authelia
  idp-h-usr: X-Authentik-Username     # authentik
  idp-h-usr: x-idp-user               # generic

  # Optional: header containing group membership
  idp-h-grp: Remote-Groups            # Authelia
  idp-h-grp: X-Authentik-Groups       # authentik
  idp-h-grp: x-idp-group              # generic

  # Recommended: shared secret header to prevent header smuggling
  idp-h-key: shangala-bangala

  # Required: trust reverse proxy subnet for XFF headers
  xff-src: lan                         # all private IPs
  xff-src: 10.88.0.0/24               # specific subnet

  # Optional: custom login/logout URLs
  idp-login: /outpost.goauthentik.io/start/?rd={dst}  # authentik
  idp-login: /idp/login/?redir={dst}                   # generic
  idp-logout: /outpost.goauthentik.io/sign_out         # authentik

  # Auth precedence (default: idp,cookie,basic)
  auth-ord: idp,cookie,basic

  # Cookie-based session bypass (for slow IdPs)
  idp-cookie: true
```

## Header-Value Mapping (Tailscale, etc.)

For IdPs that don't map to copyparty usernames directly, use `idp-hm-usr`:

```yaml
[global]
  # Format: ^HeaderName^HeaderValue^CopypartyUsername
  idp-hm-usr: ^Tailscale-User-Login^alice.m@forest.net^alice
  idp-hm-usr: ^Tailscale-User-Login^bob@corp.net^bob
```

Each mapping is a separate `idp-hm-usr` line. The header value is matched exactly.

## Dynamic Volumes (Per-User/Group)

Volumes with `${u}` (username) or `${g}` (group) are created dynamically:

```yaml
# Per-user home directory
[/u/${u}]
  /srv/homes/${u}
  accs:
    rwmd: ${u}

# Per-user private folder (only owner can access)
[/u/${u}/priv]
  /srv/homes/${u}/priv
  accs:
    A: ${u}

# Per-group shared folder
[/lounge/${g}]
  /srv/groups/${g}
  accs:
    rw: ${g}

# Group-filtered user volumes (only for members of "su" group)
[/admin/${u%+su}]
  /srv/admin/${u}
  accs:
    A: ${u}

# Exclude group members (everyone EXCEPT "su" group)
[/public/${u%-su}]
  /srv/public/${u}
  accs:
    rw: ${u}
```

### Group Filter Syntax

| Pattern | Meaning |
|---------|---------|
| `${u}` | All authenticated users |
| `${u%+grp}` | Users who ARE members of "grp" |
| `${u%-grp}` | Users who are NOT members of "grp" |
| `${u%+ga,%+gb}` | Members of BOTH "ga" AND "gb" |
| `${u%-ga,%-gb}` | Not member of "ga" NOR "gb" |
| `${g}` | All groups |
| `${g%+grp}` | Groups matching "grp" |

## Volume Persistence (`idp-store`)

**By default, IdP volumes are forgotten on restart** and revived on first request.

```yaml
[global]
  idp-store: 1    # default: log users but don't remember
  idp-store: 2    # remember usernames across restarts
  idp-store: 3    # remember usernames AND groups
```

Until revived, volumes inherit parent volume permissions. **Security implication:** if parent is world-readable, IdP volumes become world-readable until the owner's first request.

**Strategic parent volumes** prevent this:

```yaml
# Lock down the parent so inherited permissions are safe
[/u]
  /srv/homes
  accs:
    r: @acct       # only authenticated users can browse parent

[/u/${u}]
  /srv/homes/${u}
  accs:
    A: ${u}
```

To remove cached users: Control Panel → "view idp cache" → delete entries.

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

**Status:** Example exists but marked as incomplete upstream.

### Expected Headers

authentik forward-auth proxy provider injects:
- `X-authentik-username`
- `X-authentik-groups` (pipe-separated: `group1|group2`)
- `X-authentik-email`
- `X-authentik-name`
- `X-authentik-uid`

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

## Security Considerations

- **Always set `xff-src`** to the proxy subnet. Without it, clients can forge IdP headers.
- **Use `idp-h-key`** shared secret when possible. The reverse proxy injects a secret header; copyparty rejects requests without it.
- **Parent volume permissions** matter for unrevived IdP volumes. Design volume hierarchy so inheritance is safe.
- **`auth-ord`** controls fallback. Default `idp,cookie,basic` means IdP headers checked first. Set `auth-ord: basic,idp` to allow copyparty passwords to override IdP.
