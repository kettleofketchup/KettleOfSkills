# Copyparty Protocol Configuration

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

### HTTPS / TLS

If `cfssl` is installed, copyparty auto-creates CA + server cert on startup (self-signed).

```yaml
[global]
  # Certs written to --crt-dir for distribution
  # Install ca.pem into browsers for self-signed
```

Using a reverse proxy for TLS is recommended over native HTTPS.

### Binding Options

See `--help-bind` for full syntax. Key options:
- `--i IP` - bind to specific IPs, unix sockets, or `::` (all)
- `--p PORT` - ports (comma/range: `3923,4001-4005`)
- `--ll` - include link-local IPs in mDNS
- `--reuseaddr` - allow rapid restart on Windows
- `--ign-ebind` - continue if some endpoints fail to bind

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

**Linux (nautilus/gvfs):** Appears automatically if zeroconf enabled

**rclone (recommended):**
```ini
# ~/.config/rclone/rclone.conf
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

- To edit existing files, client needs Delete permission + `daw` volflag (or client sends `x-oc-mtime` header)
- Without `daw`, PUT creates copies like `notes.txt-1771978661.txt`
- `daw` also makes all PUT uploads overwrite if user has delete access
- Login: any username + password, or password-in-username (unless `--usernames` enabled)

## FTP Server

Based on pyftpdlib. Requires dedicated port.

```yaml
[global]
  ftp: 3921           # enable FTP on port 3921
  ftps: 3990          # enable explicit TLS (FTPES)
  ftp-pr: 12000-12099 # passive port range (important for firewalls)
  ftp-nat: 1.2.3.4    # external IP for Docker/NAT (required for Docker)
```

### FTP Firewall Ports

```bash
firewall-cmd --permanent --add-port=3921/tcp        # FTP
firewall-cmd --permanent --add-port=3990/tcp        # FTPS
firewall-cmd --permanent --add-port=12000-12099/tcp # passive range
```

### FTP Client Examples

```bash
# lftp
lftp -u k,wark -p 3921 127.0.0.1 -e ls

# lftp with TLS
lftp -u k,wark -p 3990 127.0.0.1 -e 'set ssl:verify-certificate no; ls'

# curl plaintext
curl ftp://127.0.0.1:3921/

# curl encrypted
curl --ssl-reqd ftp://127.0.0.1:3990/
```

### FTP Notes

- Login: any username + password, or password-in-username field
- Uploads are NOT resumable (delete and restart)
- Active mode by default; use `--ftp-pr` for passive mode
- If enabling both FTP and FTPS, port range is split in half

## SFTP Server

Based on paramiko. SSH-based, uses SSH keys or passwords.

```yaml
[global]
  sftp: 3922                                    # enable SFTP on port 3922
  sftp-key: david ssh-ed25519 AAAAC3NzaC...    # associate SSH key with user
  sftp-pw                                       # enable password login (default: keys only)
  sftp-anon: guest                              # anonymous login as user 'guest'
```

### SFTP Requirements

- Requires `paramiko` package
- Docker editions with SFTP: `ac`, `im`, `iv`, `dj`
- Speed: ~700 MiB/s (slower than WebDAV and FTP)

## TFTP Server

Based on partftpy. Read/write, no accounts.

```yaml
[global]
  tftp: 3969           # enable TFTP
  # tftp-pr: PORT-PORT # optional: reply port range
```

### TFTP Notes

- No accounts: read from world-readable, write to world-writable, overwrite in world-deletable
- Only binary/octet/image mode (no netascii)
- RFC 7440 NOT supported -- extremely slow over WAN
- Speed: ~1100 KiB/s over 100BASE-T, ~400 KiB/s over wifi
- Port 69 requires root; use NAT redirect instead:

```bash
iptables -t nat -A PREROUTING -i eth0 -p udp --dport 69 -j REDIRECT --to-port 3969
```

### TFTP Client Examples

```bash
# curl
curl --tftp-blksize 1428 tftp://127.0.0.1:3969/firmware.bin
curl --tftp-blksize 1428 -T firmware.bin tftp://127.0.0.1:3969/

# Windows
tftp -i 127.0.0.1 put firmware.bin

# atftp
atftp --option "blksize 1428" 127.0.0.1 3969 -p -l firmware.bin -r firmware.bin
```

## SMB/CIFS Server

Based on impacket. **Unsafe, slow, not recommended for WAN.**

```yaml
[global]
  smb              # enable read-only SMB
  smbw             # enable read-write SMB
  smb-port: 3945   # listen on non-privileged port
  # smb1           # use SMB1 (faster on Win7, buggy elsewhere)
```

### SMB Port NAT

Port 445 is privileged; use NAT redirect:
```bash
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 445 -j REDIRECT --to-port 3945
```

### SMB Warnings

- Not confident read-only is truly read-only
- Not fully VFS integrated -- possible path traversal; use prisonparty/bubbleparty
- Not compatible with password hashing or `--usernames`
- Only sees first ~400 files in large folders
- Python3 only, slow (WebDAV is 5x faster, rclone-WebDAV is 30x faster)
- Requires `impacket==0.13.0`

### SMB Authentication

- Username `$username`, password `$password`
- Or username `$password`, password `k`

## Zeroconf / mDNS / SSDP

```yaml
[global]
  z               # enable all zeroconf (mDNS + SSDP)
  zm              # enable mDNS only
  zs              # enable SSDP only
  z-on: 192.168.0.0/16  # restrict to subnets
  z-off: 10.0.0.0/8     # exclude subnets
  name: partybox  # server name (default: hostname)
```

### mDNS

- Gives copyparty a `.local` domain (e.g., `partybox.local:3923`)
- All enabled services appear in mDNS-aware file managers (KDE, GNOME, macOS)
- UDP port 5353

### SSDP

- Makes copyparty appear in Windows file explorer
- Doubleclicking opens the "connect" page
- UDP port 1900
- Debug with `--zsv` to see why discovery fails

## QR Code

```yaml
[global]
  qr                          # show http QR code
  qrs                         # show https QR code
  qrl: uploads/?pw=hunter2    # append to URL
  qri: 192.168.               # IP prefix filter
  qr-pin: 1                   # stick QR to bottom of console
  qr-file: qr.png:8:4:333333:ffcc55  # write to file
  qr-file: qr.svg:1:2         # vector QR
```

## Client Tools

### u2c.py (Command-Line Uploader)

```bash
# Download from copyparty: /?hc > u2c.py
python3 u2c.py --help

# Upload with sync
python3 u2c.py --dr /local/folder http://server:3923/remote/

# Features: resumable, parallel, checksummed, folder sync
```

### partyfuse.py (FUSE Client)

```bash
# Read-only FUSE mount
python3 partyfuse.py http://server:3923/ /mnt/cpp

# Also works with nginx/IIS directory listings
```

### curl Examples

```bash
# Upload file (HTML response)
curl -F f=@movie.mkv http://127.0.0.1:3923/?pw=wark

# Upload file (get URL back)
curl -F f=@movie.mkv 'http://127.0.0.1:3923/?want=url&pw=wark'

# PUT upload with random filename
curl -H pw:wark -H rand:8 -T movie.mkv http://127.0.0.1:3923/

# Append to file
curl -H pw:wark -T- http://127.0.0.1:3923/logfile.txt?apnd

# Stream upload
(printf 'PUT /junk?pw=wark HTTP/1.1\r\n\r\n'; cat movie.mkv) | nc 127.0.0.1 3923
```

### Authentication Methods

Clients authenticate via (first non-blank wins):
1. URL param `&pw=password`
2. Header `PW: password`
3. Basic auth (username or password field)
4. Cookie `cppwd=password` (HTTP) or `cppws=password` (HTTPS)

With `--usernames` enabled, format is `user:password` everywhere.
