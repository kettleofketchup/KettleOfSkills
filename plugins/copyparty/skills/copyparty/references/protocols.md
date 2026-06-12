# Copyparty Protocol Configuration: HTTP and WebDAV

## HTTP/HTTPS (Default)

Default port: 3923. Accepts both HTTP and HTTPS simultaneously.

```yaml
[global]
  p: 3923              # default port
  p: 80,443            # listen on standard ports
  i: 0.0.0.0           # listen on all interfaces (default ::)
  i: 192.168.1.1,::1   # specific interfaces
  i: unix:770:www:/dev/shm/party.sock  # unix socket (770 perms, www group)
  nc: 1024             # max clients (default)
```

If `cfssl` is installed, copyparty auto-creates CA + server cert on startup (self-signed). Using a reverse proxy for TLS is recommended over native HTTPS.

## WebDAV Server

Built-in, always available on the same HTTP port. Read-write support.

```yaml
[global]
  daw              # allow WebDAV overwrites (PUT replaces existing)
  dav-auth         # force password auth for all WebDAV clients
  dav-port: 3924   # separate port for WebDAV (optional)
```

### Connecting Clients

**macOS Finder:** Go > Connect to Server > `http://192.168.1.1:3923/`

**Windows:** Right-click My Computer > Map Network Drive > `http://192.168.1.1:3923/`
- Put password in username field for best compatibility
- Windows webdav client has many bugs; rclone is recommended alternative

**rclone (recommended):**
```ini
[cpp-rw]
type = webdav
vendor = owncloud
url = http://127.0.0.1:3923/
headers = Cookie,cppwd=hunter2
pacer_min_sleep = 0.01ms

[cpp-ro]
type = http
url = http://127.0.0.1:3923/
headers = Cookie,cppwd=hunter2
pacer_min_sleep = 0.01ms
```

Mount: `rclone mount --vfs-cache-mode writes cpp-rw: /mnt/copyparty`

The "connect" page at `/?hc` auto-generates rclone config commands.

### WebDAV Notes

- To edit existing files, client needs Delete permission + `daw` volflag
- Without `daw`, PUT creates copies like `notes.txt-1771978661.txt`
- `daw` makes all PUT uploads overwrite if user has delete access
- Login: any username + password, or password-in-username (unless `--usernames` enabled)

## Zeroconf / mDNS / SSDP

```yaml
[global]
  z               # enable all zeroconf (mDNS + SSDP)
  zm              # enable mDNS only
  zs              # enable SSDP only
  z-on: 192.168.0.0/16  # restrict to subnets
  name: partybox  # server name (default: hostname)
```

- **mDNS:** Gives copyparty a `.local` domain; appears in KDE/GNOME/macOS file managers (UDP 5353)
- **SSDP:** Makes copyparty appear in Windows file explorer (UDP 1900)

## QR Code

```yaml
[global]
  qr                          # show http QR code
  qrs                         # show https QR code
  qrl: uploads/?pw=hunter2    # append to URL
  qri: 192.168.               # IP prefix filter
  qr-pin: 1                   # stick QR to bottom of console
  qr-file: qr.png:8:4:333333:ffcc55  # write to file
```

## Client Tools

**u2c.py (Command-Line Uploader):**
```bash
python3 u2c.py --dr /local/folder http://server:3923/remote/
# Features: resumable, parallel, checksummed, folder sync
```

**partyfuse.py (FUSE Client):**
```bash
python3 partyfuse.py http://server:3923/ /mnt/cpp
# Read-only FUSE mount; also works with nginx/IIS directory listings
```

## Authentication Methods

1. URL param `&pw=password`
2. Header `PW: password`
3. Basic auth (username or password field)
4. Cookie `cppwd=password` (HTTP) or `cppws=password` (HTTPS)

With `--usernames` enabled, format is `user:password` everywhere.

See [protocols-ftp-sftp-smb.md](protocols-ftp-sftp-smb.md) for FTP, SFTP, TFTP, and SMB.
