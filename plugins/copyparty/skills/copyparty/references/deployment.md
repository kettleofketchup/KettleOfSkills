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

### PyPI

```bash
python3 -m pip install --user -U copyparty
```

### Windows EXE

Download `copyparty.exe` (win8+) or `copyparty32.exe` (win7+) from GitHub releases. Comes with Pillow built-in; only needs FFmpeg for media tags/video thumbnails.

### Arch Linux

```bash
pacman -S copyparty
systemctl start --user copyparty   # or: systemctl start copyparty@bob
```

### Homebrew (macOS)

```bash
brew install copyparty ffmpeg
```

### Nix Package

```bash
nix profile install github:9001/copyparty
```

### Android (Termux)

```bash
yes | pkg upgrade && termux-setup-storage && \
yes | pkg install python termux-api && \
python -m ensurepip && \
python -m pip install --user -U copyparty
# Then run: copyparty --qr
```

For thumbnails: `pkg install ffmpeg && python3 -m pip install --user -U pillow`

### iOS (a-Shell)

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
| `PRTY_SYS_ALL` | Use all system modules |
