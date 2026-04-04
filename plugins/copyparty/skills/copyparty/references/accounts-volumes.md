# Copyparty Accounts, Volumes, and Configuration

## Account and Volume CLI Syntax

```bash
# Create account
-a username:password

# Create volume: -v localpath:urlpath:permissions:flags
-v /srv::r                           # share /srv at webroot, read-only for all
-v /mnt/music:music:r,u1,u2:rw,u3   # read for u1/u2, read-write for u3
-v /mnt/inc:inc:w,u1:rm,u2          # write-only for u1, read-move for u2
-v /mnt/ss:i:rw,u1:g:c,fk=4        # rw for u1, get-only for all, 4-char filekeys
-v .::wG:c,e2d,fk=4                 # anonymous upget with filekeys
```

## Permissions Reference

| Permission | Name | Description |
|------------|------|-------------|
| `r` | read | Browse folder contents, download files, zip/tar, see filekeys/dirkeys |
| `w` | write | Upload files, move/copy files INTO this folder |
| `m` | move | Move files/folders FROM this folder |
| `d` | delete | Delete files/folders |
| `.` | dots | User can see dotfiles in directory listings |
| `g` | get | Download files only, cannot browse or zip/tar |
| `G` | upget | Same as `g` but uploaders see their own filekeys |
| `h` | html | Same as `g` but folders serve index.html, no filekey needed for index.html |
| `a` | admin | See upload time, uploader IPs, config-reload |
| `A` | all | Shortcut for `rwmda.` |

### Permission Combinations

```bash
-v .::r:rw,ed         # everyone reads, ed read-writes
-v .::r,*,-@acct      # read for unauthenticated only
-v .::r,@acct         # read for all logged-in users
-v .::r,@admins,-james  # read for admins group, excluding james
```

### Special Groups

- `*` = everyone (including anonymous)
- `@acct` = all known/logged-in users
- Custom groups defined in config `[groups]` section

## Config File Format

Config files loaded with `-c copyparty.conf` or env `PRTY_CONFIG=copyparty.conf`.

```yaml
# Not actually YAML, but similar syntax
# Inline comments need 2 spaces before the #

[global]
  p: 8086, 3939  # listen on multiple ports
  e2dsa          # filesystem indexing
  e2ts           # media tag indexing
  z, qr          # zeroconf and QR code

[accounts]
  ed: 123        # username: password
  k: k

[groups]
  g1: ed, k      # group with members

[/]              # volume at URL "/"
  .              # maps to current directory
  accs:
    r: *         # everyone reads
    rw: ed       # ed read-writes

[/priv]          # volume at URL "/priv"
  ./priv         # relative path
  accs:
    r: k
    rw: ed

[/music]         # volume at URL "/music"
  /home/ed/Music # absolute path
  accs:
    r: *

[/dump]          # write-only drop folder
  /home/ed/inc
  accs:
    w: *
  flags:
    e2d          # uploads database
    nodupe       # reject duplicate uploads

[/sharex]        # sharex-style upload folder
  /home/ed/inc/sharex
  accs:
    wG: *        # write-upget for everyone
    rwmd: ed, k  # full access for ed and k
  flags:
    e2d, d2t, fk: 4  # db, no media parse, 4-char filekeys
```

### Config File Includes

```yaml
# Include another config file (space after % is important)
% copyparty.d

# Include from absolute path
% /etc/copyparty.d

# copyparty.d is a directory: includes all *.conf files inside (non-recursive, alphabetical order)
# Max include depth: 64
```

### Equivalent CLI vs Config

The config above is equivalent to:
```bash
-u ed:123 -u k:k \
-v .::r:a,ed \
-v priv:priv:r,k:rw,ed \
-v /home/ed/Music:music:r \
-v /home/ed/inc:dump:w:c,e2d,nodupe \
-v /home/ed/inc/sharex:sharex:wG:c,e2d,d2t,fk=4
```

## Volflags (Per-Volume Configuration)

Volflags are set in CLI with `:c,flagname=value` or in config under `flags:`. Many global options can also be volflags, and vice versa. Full list at `--help-flags` or https://copyparty.eu/cli/#flags-help-page

### Common Volflags

```yaml
flags:
  # Indexing
  e2d            # enable uploads database
  e2ds           # scan for new files on startup
  e2dsa          # scan all files including readonly
  e2ts           # scan for media tags
  d2d            # disable all indexing for this volume
  d2t            # disable media tag parsing (safety for untrusted uploads)

  # Dedup
  dedup          # symlink-based deduplication
  hardlinkonly   # use hardlinks instead of symlinks
  reflink        # use CoW/reflinks
  nodupe         # reject duplicate uploads

  # Upload rules
  sz: 1k-3m      # allowed filesize range
  df: 4g         # minimum free disk space
  vmaxb: 1g      # max volume size
  vmaxn: 4k      # max files in volume
  nosub          # no subdirectory uploads
  rotn: 1000,2   # rotate into subfolders (1000 files, 2 levels)
  rotf: %Y/%m/%d # date-based subdirectory structure
  lifetime: 300  # self-destruct uploads after 5 min
  maxn: 250,3600 # rate limit: 250 files per hour per IP
  maxb: 1g,300   # rate limit: 1 GiB per 5 min per IP

  # Thumbnails
  dthumb         # disable all thumbnails
  dvthumb        # disable video thumbnails only
  dathumb        # disable audio spectrograms only
  grid           # default to grid view
  gsel           # enable click-to-select in grid

  # Display
  sort: href     # default sort column
  norobots       # tell search engines to go away
  nohtml         # prevent XSS by returning HTML as plaintext
  og             # enable OpenGraph/Discord embeds

  # Filesystem
  hist: /path    # override .hist location
  dbpath: /path  # override database location
  scan: 60       # rescan every 60 seconds
  xvol           # don't follow symlinks leaving volume
  xdev           # stay within volume filesystem
  nohash: \.iso$ # skip hashing matching files
  noidx: \.log$  # skip indexing matching files

  # Other
  rss            # enable RSS feeds
  opds           # enable OPDS feeds (e-readers)
  fk: 4          # 4-character filekeys
  dk             # enable dirkeys
  dks            # dirkeys work in subfolders too
  dots           # show dotfiles to everyone
  dotsrch        # include dotfiles in search results
  daw            # WebDAV: allow overwrite via PUT
  cachectl: no-cache  # browser caching strategy
  chmod_f: 644   # file permissions
  chmod_d: 755   # directory permissions
  uid: 1000      # chown user
  gid: 573       # chown group

  # Metadata
  mte: title,artist  # tags to index and display
  mth: album         # tags to hide but still index
  mtp: .bpm=f,t30,/mtag/audio-bpm.py  # custom tag parser
```

## Volume Shadowing

Mount volumes on top of subfolders to hide them:

```bash
-v /mnt::r -v /var/empty:web/certs:r
# /mnt is webroot, but /web/certs shows /var/empty instead of /mnt/web/certs
```

Works for single files too -- files can be volumes.

## Dotfiles

Files/folders starting with `.` are hidden from listings by default.

- Global option `-ed` or volflag `dots` lets clients request to see them
- Permission `.` gives specific users the ability
- `dotsrch` volflag includes dotfiles in search results
- `--see-dots` makes dotfiles visible by default

## Password Hashing

```bash
# Enable argon2 hashing
--ah-alg argon2

# Interactive password hashing (never writes plaintext to disk)
--ah-cli

# Show the auto-generated salt
--show-ah-salt
```

Takes ~0.4 sec and 256 MiB RAM per password on decent hardware.

Config:
```yaml
[global]
  ah-alg: argon2
  ah-salt: your-custom-salt  # optional, auto-generated if not set
```

## User-Changeable Passwords

```yaml
[global]
  chpw            # enable password changes in control panel
  chpw-no: admin  # deny changes for specific accounts
  chpw-db: /path/to/chpw.json  # custom storage location
```

## IP-Based Authentication

```yaml
[global]
  # Auto-login based on IP range
  ipu: 192.168.123.0/24=spartacus
  ipu: 10.0.0.0/8=trusted_user

  # Restrict user to IP ranges
  ipr: 192.168.123.0/24,172.16.0.0/16=spartacus
```

## Identity Provider (IdP) Integration

Replace copyparty passwords with external auth (Authelia, authentik, etc.):

```yaml
[global]
  # Required: header containing username
  idp-h-usr: X-Authentik-Username

  # Optional: header containing groups
  idp-h-grp: X-Authentik-Groups

  # Security: header with shared secret
  idp-h-key: my-shared-secret

  # Trust reverse proxy subnet
  xff-src: 10.88.0.0/24

  # Custom login/logout URLs
  idp-login: /idp/login/?redir={dst}
  idp-logout: /idp/logout/

  # IdP volume persistence across restarts
  idp-store: 1  # 1=log only (default), 2=remember users, 3=remember users+groups

  # Auth precedence
  auth-ord: idp,cookie,basic  # default order
```

### Generic Header Auth (Tailscale, etc.)

```yaml
[global]
  idp-hm-usr: ^Tailscale-User-Login^alice.m@forest.net^alice
```

## Dynamic Volumes (IdP)

Volumes with `${u}` or `${g}` in their URL are created dynamically per-user/group:

```yaml
[/home/${u}]
  /srv/homes/${u}
  accs:
    A: ${u}
```

Note: IdP volumes are forgotten on restart unless `idp-store: 2` or higher. Until revived, they inherit parent volume permissions.
