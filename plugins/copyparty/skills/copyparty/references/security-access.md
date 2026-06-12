# Copyparty Security: Access Control and Sandboxing

## Ban System

```yaml
[global]
  # More than N incidents in W minutes = ban for B minutes
  ban-pw: 9,60,1440      # wrong passwords (default: 9 in 1h = 24h ban)
  ban-pwc: 5,60,1440     # password changes
  ban-404: 50,60,1440    # 404 errors (only for g/G/h users)
  ban-403: 9,2,1440      # 403 errors
  ban-422: 9,2,1440      # invalid requests / exploits
  ban-url: 9,2,1440      # suspicious URLs

  # Suspicious URL patterns
  sus-urls: \.php$|(^|/)wp-(admin|content|includes)/
  nonsus-urls: ^(favicon\.ico|robots\.txt)$|^apple-touch-icon|^\.well-known

  early-ban            # reject banned connections ASAP
  loris: 60            # ban slowloris after 60 min
  aclose: 10           # downgrade keep-alive for connection-hogging clients
```

Disable specific bans: `ban-404: no`, `ban-403: no`, etc.

## HTTPS Configuration

Both HTTP and HTTPS accepted by default on the same port.

If `cfssl` is installed, auto-generates CA + server cert.
Better: use reverse proxy for TLS termination.

## IP-Based Access Control

```yaml
[global]
  # Only accept connections from these CIDRs
  ipa: 10.89.0.0/16, 192.168.33.0/24

  # Auto-login by IP
  ipu: 192.168.123.0/24=spartacus

  # Restrict user to IPs
  ipr: 192.168.123.0/24=spartacus
```

## Session Management

```yaml
[global]
  logout: 8086        # session timeout in hours (default)
  usernames           # require username:password format everywhere
```

## Filesystem Security

```yaml
[global]
  xvol              # don't follow symlinks leaving volume
  xdev              # stay within volume filesystem
  no-dot-mv         # disallow moving dotfiles
  no-dot-ren        # disallow renaming to dotfiles
```

## Version Checker

```yaml
[global]
  vc-url: https://api.copyparty.eu/advisories
  vc-age: 3         # check every 3 hours
  vc-exit            # emergency exit if vulnerable
```

## Environment Variable Chickenbits

| Env Var | Effect |
|---------|--------|
| `PRTY_NO_TLS` | Disable native HTTPS |
| `PRTY_NO_SQLITE` | Disable all database functionality |
| `PRTY_NO_MP` | Disable multiprocessing |
| `PRTY_NO_CTYPES` | No external library features |
| `PRTY_NO_IFADDR` | No IP/NIC discovery |
| `PRTY_UNSAFE_STATE` | Allow secrets in fallback locations |

## Feature Beefybits (Force-Enable)

| Env Var | Effect |
|---------|--------|
| `PRTY_FORCE_MP` | Force multiprocessing on macOS |
| `PRTY_FORCE_MAGIC` | Force python-magic on Windows (will segfault) |

## Sandbox Options

- **prisonparty**: `bin/prisonparty.sh` creates a minimal chroot (very portable)
- **bubbleparty**: `bin/bubbleparty.sh` wraps in bubblewrap (better isolation)
- Docker containers provide natural isolation

## GDPR Compliance

```yaml
[global]
  forget-ip: 43200   # forget uploader IPs after 30 days
  # Also: configure log rotation with -lo
```

## Security Contacts

- GitHub: https://github.com/9001/copyparty/security/advisories
- Discord: https://discord.gg/25J8CdTT6G (announcements channel)
