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
| `h` | html | Same as `g` but folders serve index.html, no filekey needed. Only applies to users **without** `r` — see static-site note below |
| `a` | admin | See upload time, uploader IPs, config-reload |
| `A` | all | Shortcut for `rwmda.` |

### Static-site serving (`h`) and the read-permission gotcha

`h` serves a folder's `index.html` for bare folder URLs (webserver-style)
*only to users who lack `r`*. Anyone with read (`r`, `A`, admin) still gets the
directory **listing** — browse always wins. For a pure static site where even
the logged-in operator sees the rendered page, grant **only `h`**, no `r`:

```yaml
[/site]
  /srv/data/site
  accs:
    h: *      # everyone (incl. admins) → index.html, nobody browses
    rw: ci    # optional upload account to push content (never browses)
```

Keeping `rwmda: admin` means admins see the listing and only anonymous visitors
get the page (preview logged-out). Manage files via SSH, since pure-`h` has no
browse UI. Mounting `[/site]` over a subfolder of `[/]` shadows it — `[/]`'s `r`
does not re-expose the listing at `/site/`.

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
% copyparty.d   # include directory (space after % is important)
% /etc/copyparty.d
# max include depth: 64
```

### Volume Shadowing

Mount volumes on top of subfolders to hide them:

```bash
-v /mnt::r -v /var/empty:web/certs:r
# /mnt is webroot, but /web/certs shows /var/empty instead of /mnt/web/certs
```

## Password Hashing

```bash
--ah-alg argon2   # enable argon2 hashing
--ah-cli          # interactive (never writes plaintext to disk)
```

Takes ~0.4 sec and 256 MiB RAM per password.

```yaml
[global]
  ah-alg: argon2
  chpw            # enable password changes in control panel
  ipu: 192.168.123.0/24=spartacus  # auto-login by IP
  ipr: 192.168.123.0/24=spartacus  # restrict user to IP ranges
```
