# Copyparty Security Reference

## Safety Profiles

### `-s` (Basic Safety)

Alias for: `--dotpart --no-thumb --no-mtag-ff --no-robots --force-js`

- Disables thumbnails and audio transcoding (stops FFmpeg/Pillow/VIPS from processing uploads)
- Uses mutagen instead of FFmpeg for tags (safer, faster)
- Hides partial uploads from listings
- Makes life harder for crawlers

### `-ss` (Increased Safety)

Alias for: `-s --unpost=0 --no-del --no-mv --hardlink --vague-403 -nih`

- Everything in `-s` plus:
- Disables all move/delete support
- Uses hardlinks for dedup (less maintenance)
- Returns 404 instead of 401 (security through ambiguity)
- Removes hostname from directory listings

### `-sss` (Maximum Safety)

Alias for: `-ss --no-dav --no-logues --no-readme -lo cpp-%Y-%m%d-%H%M%S.txt.xz --ls **,*,ln,p,r`

- Everything in `-ss` plus:
- Disables WebDAV support
- Disables README/prologue/epilogue rendering
- Enables logging to disk
- Scans for dangerous symlinks on startup

## XSS Prevention

### Volume-Level Protection

```yaml
flags:
  nohtml     # return HTML/SVG as plaintext, disable markdown rendering
  noscript   # prevent JS execution via CSP headers (most browsers)
```

`nohtml` is the nuclear option (always works). `noscript` relies on CSP headers.

### Script Injection Vectors

Users can inject `<script>` via:
- Uploading `README.md` -- prevent with `--no-readme`
- Renaming files to `.epilogue.html` -- prevent with `--no-logues` or `--no-dot-ren`
- Markdown documents can contain HTML/scripts -- prevent with `nohtml` volflag

Directory listing embeds are sandboxed. Markdown editor is not 100% safe without `nohtml`.

## CORS Configuration

By default, non-GET/HEAD requests must:
- Not contain an `Origin` header, OR
- Have `Origin` matching the server domain, OR
- Include the `PW` header with password

```yaml
[global]
  acao: *               # Access-Control-Allow-Origin (default: * without cookies)
  acam: GET,HEAD        # Access-Control-Allow-Methods (default)
  allow-csrf            # disable ALL CORS protections (not recommended)
```

## Filekeys (Prevent Filename Bruteforcing)

```yaml
flags:
  fk: 4        # 4-character filekeys for all files
  fka          # weaker filekeys (won't change if file edited)
```

- Users with `r` permission see URLs with `?k=...` appended
- Users with `g` permission must provide correct filekey or get 404
- `wG` (upget) lets uploaders receive their own filekeys

Filekey generation: `salt + filesystem-path + file-size + inode` (default) or `salt + path` (with `fka`).

## Dirkeys (Share Specific Folders)

```yaml
flags:
  dk          # generate per-directory accesskeys
  dks         # dirkeys work in subfolders + enable zip/tar
  dky         # disable key check (just hide subfolders)
```

- Grant read-access to specific folders for users with `g` permission
- Generated from `--dk-salt + filesystem-path`
- Key doesn't change when folder contents modified

## Password Hashing

```yaml
[global]
  ah-alg: argon2        # enable (argon2 / scrypt / sha2 / none)
  ah-salt: custom-salt  # optional (auto-generated if not set)
  ah-cli                # interactive mode (never writes plaintext)
```

Uses ~0.4 sec and 256 MiB RAM per password hash.

Notes:
- Static salt for all passwords (because APIs authenticate by password only, username unknown)
- Plaintext passwords printed as hashed versions on startup for replacement
- For Docker/systemd: ensure same `--ah-salt` in both CLI and service environments
- With `--usernames`: hash `username:password` format

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

  early-ban            # reject banned connections ASAP (bad behind cloudflare)
  loris: 60            # ban slowloris after 60 min
  aclose: 10           # downgrade keep-alive for connection-hogging clients
```

Disable specific bans: `ban-404: no`, `ban-403: no`, etc.

## HTTPS Configuration

Both HTTP and HTTPS accepted by default on the same port.

```yaml
[global]
  # If cfssl installed, auto-generates CA + server cert
  # Certs written to --crt-dir
  # Self-signed: install ca.pem into browsers
```

Better: use reverse proxy for TLS termination.

Install cfssl on Windows:
1. Download `cfssl_windows_amd64.exe`, `cfssljson_windows_amd64.exe`, `cfssl-certinfo_windows_amd64.exe`
2. Rename to `cfssl.exe`, `cfssljson.exe`, `cfssl-certinfo.exe`
3. Place in PATH

## Identity Provider (IdP)

Replace copyparty passwords with external auth. See [accounts-volumes.md](accounts-volumes.md) for full IdP config.

Supported: Authelia, authentik, Tailscale, any header-based auth.

```yaml
[global]
  idp-h-usr: X-Authentik-Username    # required
  idp-h-grp: X-Authentik-Groups     # optional
  idp-h-key: shared-secret           # recommended
  xff-src: 10.88.0.0/24             # trust proxy subnet
```

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

## Hidden Services

```yaml
[global]
  no-robots         # HTTP + HTML noindex headers
  force-js          # disable plain HTML listing
  nih               # remove hostname from listings
  nb                # remove copyparty branding
```

## Gotchas

- Users without read-access can still see `.prologue.html`/`README.md` content
- Users can submit auto-running `<script>` via README.md or .epilogue.html
- Markdown documents can contain HTML and scripts (use `nohtml` volflag)
- `--og` (OpenGraph) disables hotlinking
- Files named with `.` ending cannot be accessed on Windows
- `up2k.db` on samba/network disk = unpredictable behavior during outages

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

## Security Contacts

- GitHub: https://github.com/9001/copyparty/security/advisories
- Discord: https://discord.gg/25J8CdTT6G (announcements channel)
