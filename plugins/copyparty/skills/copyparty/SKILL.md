---
name: copyparty
description: Copyparty portable file server with resumable uploads, dedup, WebDAV, SFTP, FTP, TFTP, SMB, zeroconf, media indexer, and thumbnails. Use when deploying copyparty file servers (Docker, pip, sfx, NixOS), configuring volumes and permissions, setting up accounts and access control, writing copyparty.conf config files, enabling protocols (HTTP/WebDAV/FTP/SFTP/TFTP/SMB), configuring reverse proxies (nginx/traefik/caddy), setting up file indexing and search, configuring upload rules and deduplication, enabling thumbnails and media playback, writing event hooks, using the HTTP API, or integrating with identity providers (Authelia/authentik/Tailscale) via header-based forward-auth with dynamic per-user/per-group volumes.
---

# Copyparty File Server

Portable file server with resumable uploads, dedup, WebDAV, SFTP, FTP, TFTP, SMB/CIFS, zeroconf, media indexer, and thumbnails -- all in one file. Server only needs Python (2 or 3), all dependencies optional.

## References

- [deployment.md](references/deployment.md) - Installation methods, Docker images, systemd, NixOS module, Synology DSM
- [accounts-volumes.md](references/accounts-volumes.md) - Users, groups, permissions, volumes, config file format, volflags
- [protocols.md](references/protocols.md) - HTTP/HTTPS, WebDAV, FTP/FTPS, SFTP, TFTP, SMB/CIFS configuration
- [http-api.md](references/http-api.md) - REST/HTTP API endpoints for read, write, admin, search
- [features.md](references/features.md) - Upload rules, dedup, thumbnails, media player, search, indexing, event hooks
- [reverse-proxy.md](references/reverse-proxy.md) - Nginx, Traefik, Caddy, Apache, Cloudflare tunnel, real-IP, XFF
- [idp-auth.md](references/idp-auth.md) - Authelia/authentik/Tailscale integration, header auth, dynamic volumes, group filters
- [security.md](references/security.md) - Safety profiles, CORS, filekeys, password hashing, HTTPS, bans, sandboxing

## Quick Start

```bash
# Just run the sfx - that's it
python3 copyparty-sfx.py

# Or install via pip
python3 -m pip install --user -U copyparty

# Or Docker
docker run --rm -it -u 1000 -p 3923:3923 -v /mnt/nas:/w copyparty/ac

# With accounts and indexing
python3 copyparty-sfx.py -a ed:hunter2 -v /srv::r:rw,ed -e2dsa -e2ts
```

## Config File Format

Config files use `-c copyparty.conf` or env `PRTY_CONFIG=copyparty.conf`. Format is pseudo-YAML with sections:

```yaml
[global]
  e2dsa        # enable filesystem indexing
  e2ts         # enable media tag indexing
  p: 3923      # port (default)

[accounts]
  ed: hunter2  # username: password

[groups]
  admins: ed, alice

[/]            # volume at URL /
  /srv/files   # mapped to this filesystem path
  accs:
    r: *       # read for everyone
    rw: ed     # read-write for ed
  flags:
    e2d        # per-volume volflag
```

## Key CLI Arguments

| Argument | Purpose |
|----------|---------|
| `-p PORT` | Listen port (default 3923) |
| `-a user:pass` | Create account |
| `-v src:dst:perms:flags` | Create volume |
| `-c file.conf` | Load config file |
| `-e2dsa` | Enable full filesystem indexing |
| `-e2ts` | Enable media tag indexing |
| `--ftp PORT` | Enable FTP server |
| `--sftp PORT` | Enable SFTP server |
| `--smb` | Enable SMB server (read-only) |
| `-z` | Enable zeroconf (mDNS + SSDP) |
| `--qr` | Show QR code on startup |
| `-q` | Quiet (disable stdout logging) |
| `-j N` | CPU cores (0=all, 1=default) |
| `--dedup` | Symlink-based deduplication |

## Permissions

| Perm | Meaning |
|------|---------|
| `r` | Read: browse, download, zip/tar |
| `w` | Write: upload, move files in |
| `m` | Move: move files/folders out |
| `d` | Delete: delete files/folders |
| `.` | Dots: see dotfiles in listings |
| `g` | Get: download only, no browse |
| `G` | Upget: upload + see own filekeys |
| `h` | HTML: like `g` but serves index.html |
| `a` | Admin: see IPs, upload times, reload |
| `A` | All: same as `rwmda.` |

## Default Port Map

| Port | Protocol |
|------|----------|
| 3923 | HTTP/HTTPS |
| 3921 | FTP |
| 3922 | SFTP |
| 3945 | SMB |
| 3969 | TFTP |
| 3990 | FTPS |
| 5353 | mDNS |
| 1900 | SSDP |
