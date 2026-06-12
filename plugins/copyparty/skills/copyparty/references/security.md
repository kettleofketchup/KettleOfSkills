# Copyparty Security Reference

## Safety Profiles

### `-s` (Basic Safety)

Alias for: `--dotpart --no-thumb --no-mtag-ff --no-robots --force-js`

- Disables thumbnails and audio transcoding
- Uses mutagen instead of FFmpeg for tags (safer, faster)
- Hides partial uploads from listings

### `-ss` (Increased Safety)

Alias for: `-s --unpost=0 --no-del --no-mv --hardlink --vague-403 -nih`

- Everything in `-s` plus:
- Disables all move/delete support
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

```yaml
flags:
  nohtml     # return HTML/SVG as plaintext, disable markdown rendering
  noscript   # prevent JS execution via CSP headers (most browsers)
```

`nohtml` is the nuclear option (always works). `noscript` relies on CSP headers.

Users can inject scripts via:
- Uploading `README.md` -- prevent with `--no-readme`
- Renaming files to `.epilogue.html` -- prevent with `--no-logues` or `--no-dot-ren`
- Markdown documents can contain HTML/scripts -- prevent with `nohtml` volflag

## CORS Configuration

By default, non-GET/HEAD requests must have `Origin` matching the server domain or include the `PW` header.

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

## Dirkeys (Share Specific Folders)

```yaml
flags:
  dk          # generate per-directory accesskeys
  dks         # dirkeys work in subfolders + enable zip/tar
```

## Password Hashing

```yaml
[global]
  ah-alg: argon2        # enable (argon2 / scrypt / sha2 / none)
  ah-salt: custom-salt  # optional (auto-generated if not set)
  ah-cli                # interactive mode (never writes plaintext)
```

Uses ~0.4 sec and 256 MiB RAM per password hash.

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
- `up2k.db` on samba/network disk = unpredictable behavior during outages
- Files named with `.` ending cannot be accessed on Windows

See [security-access.md](security-access.md) for ban system, IP access control, session management, and sandboxing.
