# Copyparty Deployment

## Installation Methods

### SFX (Self-Extracting, Recommended)

```bash
# Download and run - that's it
python3 copyparty-sfx.py

# English-only (smaller)
python3 copyparty-en.py

# Using uv
uv tool run copyparty
```

Download from: https://github.com/9001/copyparty/releases/latest/download/copyparty-sfx.py
Mirror: https://copyparty.eu/py

### PyPI

```bash
python3 -m pip install --user -U copyparty
```

### Windows EXE

Download `copyparty.exe` (win8+) or `copyparty32.exe` (win7+) from GitHub releases. Comes with Pillow built-in; only needs FFmpeg for media tags/video thumbnails.

### Zipapp (Emergency Fallback)

```bash
# No temp files extracted, requires Python 3.7+
python3 copyparty.pyz
```

### Arch Linux

```bash
pacman -S copyparty
# Comes with systemd service
systemctl start --user copyparty
# Or as specific user
systemctl start copyparty@bob
```

### Homebrew (macOS)

```bash
brew install copyparty ffmpeg
```

### Nix Package

```bash
nix profile install github:9001/copyparty
```

## Docker

### Quick Start

```bash
docker run --rm -it -u 1000 -p 3923:3923 -v /mnt/nas:/w -v $PWD/cfgdir:/cfg copyparty/ac
```

- `/w` = path inside container shared by default
- `/cfg` = optional folder with `*.conf` config files
- For rootless podman, remove `-u 1000`
- For SELinux, append `:z` to all `-v` args

### Docker Image Editions

| Edition | Size (gz) | Features |
|---------|-----------|----------|
| `min` | 20 MB | Copyparty only |
| `im` | 25 MB | + Pillow thumbnails, Mutagen tags |
| `ac` | 56 MB | + FFmpeg video/audio thumbs, transcoding (recommended) |
| `iv` | 73 MB | + libvips for faster HEIF/AVIF/JXL thumbnails |
| `dj` | 104 MB | + beatroot/keyfinder for BPM/key detection |

Available from Docker Hub (`copyparty/ac`) or GitHub (`ghcr.io/9001/copyparty-ac`).

Architecture support: x86, x86_64, armhf, aarch64, ppc64le, s390x (varies by edition).

### Docker Compose

```yaml
version: "3"
services:
  copyparty:
    image: copyparty/ac
    user: "1000"
    ports:
      - "3923:3923"
    volumes:
      - /mnt/nas:/w
      - ./cfgdir:/cfg
```

### Docker Configuration

```yaml
# cfgdir/copyparty.conf
[global]
  e2dsa, e2ts    # indexing
  hist: /cfg/hists/  # keep db/thumbs in config volume

[accounts]
  ed: hunter2

[/]
  /w
  accs:
    r: *
    rw: ed
```

### Docker FTP Server

FTP in Docker requires extra port config:

```yaml
[global]
  ftp: 3921
  ftp-nat: 192.168.1.100  # external IP of server (required for Docker)
  ftp-pr: 12000-12099      # passive port range (expose in Docker)
```

### Docker Performance Tips

- `hist: /cfg/hists/` in `[global]` keeps indexes tidy and performant
- `LD_PRELOAD=/usr/lib/libmimalloc-secure.so.2` makes zip 3x faster, indexing 1.5x faster (doubles RAM)

## Systemd Service

```ini
# /etc/systemd/system/copyparty.service
# See contrib/systemd/copyparty.service for full example
```

Service files provided:
- `contrib/systemd/copyparty.service` - run sfx normally
- `contrib/systemd/prisonparty.service` - run in chroot
- `contrib/openrc/copyparty` - Alpine/Gentoo
- `contrib/rc/copyparty` - FreeBSD
- `contrib/podman-systemd/` - Podman container as systemd service

Config reload without restart:
```bash
systemctl reload copyparty
# Or: kill -s USR1 <pid>
# Or: click [reload cfg] in control panel (admin only)
# Note: [global] section changes require full restart
```

## NixOS Module

```nix
{
  inputs.copyparty.url = "github:9001/copyparty";

  outputs = { self, nixpkgs, copyparty }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        copyparty.nixosModules.default
        ({ pkgs, ... }: {
          nixpkgs.overlays = [ copyparty.overlays.default ];
          services.copyparty = {
            enable = true;
            user = "copyparty";
            group = "copyparty";
            settings = {
              i = "0.0.0.0";
              p = [ 3923 ];
              no-reload = true;
            };
            accounts = {
              ed.passwordFile = "/run/keys/copyparty/ed_password";
            };
            volumes = {
              "/" = {
                path = "/srv/copyparty";
                access = {
                  r = "*";
                  rw = [ "ed" ];
                };
                flags = {
                  e2d = true;
                  fk = 4;
                  scan = 60;
                };
              };
            };
            openFilesLimit = 8192;
          };
        })
      ];
    };
  };
}
```

## Synology DSM (NAS)

Use Docker/Container Manager on Synology:
1. Install Container Manager (DSM 7.2+) or Docker (older DSM)
2. Search registry for `copyparty/ac`
3. Create container with port 3923 mapped
4. Mount config folder to `/cfg` and data folders to `/w`

Recommended Synology config:
```yaml
[global]
  e2d, e2t
  rss, daw, ver
  hist: /cfg/hist
  unlist: ^@eaDir  # hide synology metadata folders
  name: synology

[accounts]
  ed: wark

[/]
  /w
  accs:
    A: ed
```

## Android (Termux)

```bash
yes | pkg upgrade && termux-setup-storage && \
yes | pkg install python termux-api && \
python -m ensurepip && \
python -m pip install --user -U copyparty
# Then run: copyparty --qr
```

For thumbnails: `pkg install ffmpeg && python3 -m pip install --user -U pillow`

## iOS (a-Shell)

```bash
curl -L https://github.com/9001/copyparty/raw/refs/heads/hovudstraum/contrib/setup-ashell.sh | sh
```

Known limitation: cannot run in background; needs to be on-screen.

## Optional Dependencies

Enable bonus features by installing:

| Feature | Package |
|---------|---------|
| Hashed passwords | `argon2-cffi` |
| FTP server | `pyftpdlib` (built into SFX) |
| FTP + TLS | `pyftpdlib pyopenssl` |
| SFTP server | `paramiko` |
| Music tags (fast) | `mutagen` |
| Music tags (accurate) | `ffprobe` |
| Image thumbnails | `Pillow` and/or `pyvips` |
| Video/audio thumbnails | `ffmpeg` + `ffprobe` in PATH |
| HEIF images | `pyvips` or `pillow-heif` |
| RAW images | `rawpy` |
| ZeroMQ hooks | `pyzmq` |
| SMB server | `impacket==0.13.0` |

Platform-specific thumbnail deps:
- **Alpine:** `apk add py3-pillow ffmpeg`
- **Debian:** `apt install --no-install-recommends python3-pil ffmpeg`
- **Fedora:** rpmfusion + `dnf install python3-pillow ffmpeg --allowerasing`
- **macOS:** `brew install pillow ffmpeg`
- **Windows:** `python -m pip install --user -U Pillow` + install FFmpeg manually

## Environment Variable Chickenbits

Disable features with env vars:

| Env Var | Effect |
|---------|--------|
| `PRTY_NO_SQLITE` | Disable all database functionality |
| `PRTY_NO_TLS` | Disable native HTTPS |
| `PRTY_NO_MP` | Disable multiprocessing |
| `PRTY_NO_FFMPEG` | No FFmpeg-based thumbnails/transcoding |
| `PRTY_NO_PIL` | No Pillow thumbnails |
| `PRTY_NO_VIPS` | No libvips thumbnails |
| `PRTY_NO_MUTAGEN` | No mutagen tag reading |
| `PRTY_NO_PARAMIKO` | No SFTP server |
| `PRTY_NO_PYFTPD` | No FTP server |
| `PRTY_NO_PARTFTPY` | No TFTP server |

Dependency unvendoring:

| Env Var | Effect |
|---------|--------|
| `PRTY_SYS_ALL` | Use all system modules |
| `PRTY_SYS_DNSLIB` | System dnslib |
| `PRTY_SYS_IFADDR` | System ifaddr |
| `PRTY_MODSPEC=1` | Debug: show module sources |
