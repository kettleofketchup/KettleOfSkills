# Copyparty Identity Provider (IdP) Integration

Replace copyparty passwords with external auth via reverse-proxy header injection.

## Architecture

```
Client → Reverse Proxy → IdP Middleware → Copyparty
                         (injects headers)
```

## Global Configuration

```yaml
[global]
  # Required: header containing authenticated username
  idp-h-usr: Remote-User              # Authelia
  idp-h-usr: X-Authentik-Username     # authentik

  # Optional: header containing group membership
  idp-h-grp: Remote-Groups            # Authelia
  idp-h-grp: X-Authentik-Groups       # authentik

  # Recommended: shared secret to prevent header smuggling
  idp-h-key: shangala-bangala

  # Required: trust reverse proxy subnet
  xff-src: lan                         # all private IPs
  xff-src: 10.88.0.0/24               # specific subnet

  # Optional: custom login/logout URLs
  idp-login: /outpost.goauthentik.io/start/?rd={dst}
  idp-logout: /outpost.goauthentik.io/sign_out

  # Auth precedence (default: idp,cookie,basic)
  auth-ord: idp,cookie,basic
```

## Header-Value Mapping (Tailscale, etc.)

```yaml
[global]
  # Format: ^HeaderName^HeaderValue^CopypartyUsername
  idp-hm-usr: ^Tailscale-User-Login^alice.m@forest.net^alice
  idp-hm-usr: ^Tailscale-User-Login^bob@corp.net^bob
```

## Dynamic Volumes (Per-User/Group)

```yaml
# Per-user home directory
[/u/${u}]
  /srv/homes/${u}
  accs:
    rwmd: ${u}

# Per-group shared folder
[/lounge/${g}]
  /srv/groups/${g}
  accs:
    rw: ${g}

# Group-filtered (only for members of "su" group)
[/admin/${u%+su}]
  /srv/admin/${u}
  accs:
    A: ${u}
```

### Group Filter Syntax

| Pattern | Meaning |
|---------|---------|
| `${u}` | All authenticated users |
| `${u%+grp}` | Users who ARE members of "grp" |
| `${u%-grp}` | Users who are NOT members of "grp" |
| `${u%+ga,%+gb}` | Members of BOTH "ga" AND "gb" |
| `${g}` | All groups |

## Volume Persistence (`idp-store`)

By default, IdP volumes are forgotten on restart and revived on first request.

```yaml
[global]
  idp-store: 1    # default: log users but don't remember
  idp-store: 2    # remember usernames across restarts
  idp-store: 3    # remember usernames AND groups
```

**Security:** Until revived, volumes inherit parent volume permissions. Lock down the parent:

```yaml
[/u]
  /srv/homes
  accs:
    r: @acct       # only authenticated users can browse

[/u/${u}]
  /srv/homes/${u}
  accs:
    A: ${u}
```

## Security Considerations

- **Always set `xff-src`** to the proxy subnet. Without it, clients can forge IdP headers.
- **Use `idp-h-key`** shared secret when possible.
- **Parent volume permissions** matter for unrevived IdP volumes.
- **`auth-ord`** controls fallback. Set `auth-ord: basic,idp` to allow copyparty passwords to override IdP.

See [idp-auth-integrations.md](idp-auth-integrations.md) for Authelia and authentik examples.
