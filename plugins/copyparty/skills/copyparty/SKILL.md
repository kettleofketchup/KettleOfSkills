---
name: copyparty
description: Copyparty portable file server (HTTP/WebDAV/FTP/SFTP/SMB). This skill should be used when deploying via Docker/pip/NixOS, configuring accounts/volumes, indexer, hooks, or forward-auth IdP integration.
---

# Copyparty File Server

Portable file server with resumable uploads, dedup, WebDAV, SFTP, FTP, TFTP, SMB/CIFS, zeroconf, media indexer, and thumbnails -- all in one file. Server only needs Python (2 or 3), all dependencies optional.

## References

- [deployment.md](references/deployment.md) - Installation methods: SFX, pip, Arch, Homebrew, Nix, Android, iOS, optional deps
- [deployment-docker.md](references/deployment-docker.md) - Docker images, Compose, systemd, NixOS module, Synology DSM
- [accounts-volumes.md](references/accounts-volumes.md) - Users, groups, permissions, volumes, config file format, password hashing
- [volflags.md](references/volflags.md) - Per-volume flags: indexing, dedup, upload rules, display, filesystem, tag parsers
- [protocols.md](references/protocols.md) - HTTP/HTTPS, WebDAV, rclone, zeroconf, QR code, client tools
- [protocols-ftp-sftp-smb.md](references/protocols-ftp-sftp-smb.md) - FTP/FTPS, SFTP, TFTP, SMB/CIFS configuration
- [http-api.md](references/http-api.md) - Read endpoints: listing, download, archive, search, thumbnails, Prometheus
- [http-api-write.md](references/http-api-write.md) - Write endpoints: upload, file ops, shares, up2k protocol, curl examples
- [features.md](references/features.md) - Indexing, search, dedup, zip downloads, performance tuning, special files
- [features-upload-media.md](references/features-upload-media.md) - Upload rules, thumbnails, media player, event hooks, shares, misc features
- [reverse-proxy.md](references/reverse-proxy.md) - Real-IP config, nginx, unix socket, copyparty config, troubleshooting
- [reverse-proxy-other.md](references/reverse-proxy-other.md) - Caddy, Traefik, Apache, HAProxy, Cloudflare tunnel, performance benchmarks
- [idp-auth.md](references/idp-auth.md) - Header auth config, dynamic volumes, group filters, idp-store, security
- [idp-auth-integrations.md](references/idp-auth-integrations.md) - Authelia, authentik, Tailscale integration examples
- [security.md](references/security.md) - Safety profiles (-s/-ss/-sss), XSS, CORS, filekeys, dirkeys, password hashing
- [security-access.md](references/security-access.md) - Ban system, IP access control, session management, sandbox options

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
| `h` | HTML: like `g` but serves index.html (only for users **without** `r` — see below) |
| `a` | Admin: see IPs, upload times, reload |
| `A` | All: same as `rwmda.` |

### Serving a folder as a static site (index.html)

`h` makes a folder behave like a plain webserver: a bare folder URL (`/help/`)
serves `index.html` instead of copyparty's directory-listing UI.

**Gotcha — `h` only applies to users that lack `r`.** A user who has read
(`r`, and therefore `rwmda` / `A` / admin) always gets the *file listing*, never
the rendered page, because browsing wins. `h` is defined as "like `g`" (get-only,
no browse). So for a **true** static site where *everyone* — including the
logged-in operator — sees the rendered page, grant **only `h`** and give **no one
`r`** on that volume:

```yaml
[/site]
  /srv/data/site
  accs:
    h: *          # everyone (incl. admins) gets index.html, nobody browses
    rw: ci        # an upload account can still push content (it never browses)
```

If instead you keep `rwmda: admin`, admins will see the file listing and only
anonymous visitors get the rendered page — preview it in a logged-out/incognito
window. Manage the underlying files via SSH (or a non-shadowed volume), since a
pure-`h` volume has no browse UI.

Mounting `[/site]` on a subfolder of an existing `[/]` volume *shadows* it: the
URL resolves to the most-specific volume, so `[/]`'s `r` does not leak the
listing back in at `/site/`.

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
