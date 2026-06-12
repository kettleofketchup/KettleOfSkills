# Copyparty Protocol Configuration: FTP, SFTP, TFTP, SMB

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
firewall-cmd --permanent --add-port=3921/tcp
firewall-cmd --permanent --add-port=3990/tcp
firewall-cmd --permanent --add-port=12000-12099/tcp  # passive range
```

### FTP Client Examples

```bash
# lftp
lftp -u k,wark -p 3921 127.0.0.1 -e ls

# lftp with TLS
lftp -u k,wark -p 3990 127.0.0.1 -e 'set ssl:verify-certificate no; ls'

# curl
curl ftp://127.0.0.1:3921/
curl --ssl-reqd ftp://127.0.0.1:3990/
```

Notes:
- Login: any username + password, or password-in-username field
- Uploads are NOT resumable (delete and restart)
- If enabling both FTP and FTPS, passive port range is split in half

## SFTP Server

Based on paramiko. SSH-based, uses SSH keys or passwords.

```yaml
[global]
  sftp: 3922                                    # enable SFTP on port 3922
  sftp-key: david ssh-ed25519 AAAAC3NzaC...    # associate SSH key with user
  sftp-pw                                       # enable password login (default: keys only)
  sftp-anon: guest                              # anonymous login as user 'guest'
```

Requires `paramiko` package. Speed: ~700 MiB/s (slower than WebDAV and FTP).

## TFTP Server

Based on partftpy. Read/write, no accounts.

```yaml
[global]
  tftp: 3969           # enable TFTP
```

Notes:
- No accounts: read from world-readable, write to world-writable, overwrite in world-deletable
- RFC 7440 NOT supported -- extremely slow over WAN
- Speed: ~1100 KiB/s over 100BASE-T, ~400 KiB/s over wifi
- Port 69 requires root; use NAT redirect:

```bash
iptables -t nat -A PREROUTING -i eth0 -p udp --dport 69 -j REDIRECT --to-port 3969
```

### TFTP Client Examples

```bash
curl --tftp-blksize 1428 tftp://127.0.0.1:3969/firmware.bin
curl --tftp-blksize 1428 -T firmware.bin tftp://127.0.0.1:3969/
atftp --option "blksize 1428" 127.0.0.1 3969 -p -l firmware.bin -r firmware.bin
```

## SMB/CIFS Server

Based on impacket. **Unsafe, slow, not recommended for WAN.**

```yaml
[global]
  smb              # enable read-only SMB
  smbw             # enable read-write SMB
  smb-port: 3945   # listen on non-privileged port
```

Port 445 is privileged; use NAT redirect:
```bash
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 445 -j REDIRECT --to-port 3945
```

**SMB Warnings:**
- Not confident read-only is truly read-only
- Possible path traversal; use prisonparty/bubbleparty
- Not compatible with password hashing or `--usernames`
- Only sees first ~400 files in large folders
- Python3 only, slow (WebDAV is 5x faster, rclone-WebDAV is 30x faster)
- Requires `impacket==0.13.0`

Login: Username `$username`, password `$password` (or username `$password`, password `k`).
