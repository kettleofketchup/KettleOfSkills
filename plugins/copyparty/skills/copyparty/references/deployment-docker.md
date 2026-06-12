# Copyparty Docker and Systemd Deployment

## Docker Quick Start

```bash
docker run --rm -it -u 1000 -p 3923:3923 -v /mnt/nas:/w -v $PWD/cfgdir:/cfg copyparty/ac
```

- `/w` = path inside container shared by default
- `/cfg` = optional folder with `*.conf` config files
- For rootless podman, remove `-u 1000`
- For SELinux, append `:z` to all `-v` args

## Docker Image Editions

| Edition | Size (gz) | Features |
|---------|-----------|----------|
| `min` | 20 MB | Copyparty only |
| `im` | 25 MB | + Pillow thumbnails, Mutagen tags |
| `ac` | 56 MB | + FFmpeg video/audio thumbs, transcoding (recommended) |
| `iv` | 73 MB | + libvips for faster HEIF/AVIF/JXL thumbnails |
| `dj` | 104 MB | + beatroot/keyfinder for BPM/key detection |

Available from Docker Hub (`copyparty/ac`) or GitHub (`ghcr.io/9001/copyparty-ac`).

Architecture support: x86, x86_64, armhf, aarch64, ppc64le, s390x (varies by edition).

## Docker Compose

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

## Docker Config File

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

## Docker FTP Server

FTP in Docker requires extra port config:

```yaml
[global]
  ftp: 3921
  ftp-nat: 192.168.1.100  # external IP of server (required for Docker)
  ftp-pr: 12000-12099      # passive port range (expose in Docker)
```

Docker performance tips:
- `hist: /cfg/hists/` keeps indexes tidy and performant
- `LD_PRELOAD=/usr/lib/libmimalloc-secure.so.2` makes zip 3x faster, indexing 1.5x faster

## Systemd Service

Service files provided in `contrib/systemd/`:
- `copyparty.service` - run sfx normally
- `prisonparty.service` - run in chroot
- `contrib/openrc/copyparty` - Alpine/Gentoo
- `contrib/rc/copyparty` - FreeBSD
- `contrib/podman-systemd/` - Podman container as systemd service

Config reload without restart:
```bash
systemctl reload copyparty
# Or: kill -s USR1 <pid>
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
            settings = { i = "0.0.0.0"; p = [ 3923 ]; };
            accounts.ed.passwordFile = "/run/keys/copyparty/ed_password";
            volumes."/" = {
              path = "/srv/copyparty";
              access = { r = "*"; rw = [ "ed" ]; };
              flags = { e2d = true; fk = 4; scan = 60; };
            };
            openFilesLimit = 8192;
          };
        })
      ];
    };
  };
}
```

## Synology DSM

Use Docker/Container Manager on Synology:
1. Install Container Manager (DSM 7.2+) or Docker (older DSM)
2. Search registry for `copyparty/ac`
3. Create container with port 3923 mapped
4. Mount config folder to `/cfg` and data folders to `/w`

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
