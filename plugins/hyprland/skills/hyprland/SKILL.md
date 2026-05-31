---
name: hyprland
description: Hyprland Wayland compositor on NixOS. This skill should be used when configuring programs.hyprland, GPU rendering (Intel/AMD/NVIDIA), Wails/webkit2gtk fixes, xdg portals, home-manager, or wallpapers.
---

# Hyprland on NixOS

## Overview

Configure Hyprland (dynamic tiling Wayland compositor) on NixOS. Optimized for running webkit2gtk-based desktop apps (Wails, Tauri) on integrated graphics. Covers both nixpkgs and flake-input install paths.

## Quick Reference

| Task | Where |
|------|-------|
| NixOS module options | `references/nixos-module.md` |
| Flake input + cachix setup | `references/flake-setup.md` |
| Integrated graphics (Intel/AMD) | `references/integrated-graphics.md` |
| **Multi-GPU (Intel/AMD/NVIDIA) smart defaults** | `references/multi-gpu.md` |
| **Multi-GPU unified module (`mySystem.gpu`)** | `references/multi-gpu-module.md` |
| **Per-vendor Hyprland env var matrix** | `references/multi-gpu-env-vars.md` |
| Wails blank-screen webkit2gtk fix | `references/wails-webkit-fixes.md` |
| **Animated wallpapers (mpvpaper, awww, gtk-layer-shell)** | `references/animated-wallpapers.md` |
| home-manager hyprland module | `references/home-manager.md` |
| Sample `hyprland.conf` | `references/hyprland-conf.md` |
| Complete `flake.nix` example | `references/flake-example.md` |
| Ecosystem packages (hypr*, waybar) | `references/ecosystem-packages.md` |

For NixOS-level concerns (flakes, modules, packaging, devShells, home-manager), see the sibling `nixos` skill: `~/.claude/skills/nixos/`. Cross-references: `flakes.md`, `nixos-modules.md`, `home-manager.md`, `packaging.md`, `devshells.md`.

## Core Setup

Two install paths — pick one:

**A. Pure nixpkgs** (simpler, slightly older):
```nix
programs.hyprland = {
  enable = true;
  xwayland.enable = true;
  withUWSM = true;  # 25.11+ systemd-managed session
};
xdg.portal.extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
```

**B. Hyprland flake input** (recommended, newest):
```nix
inputs.hyprland.url = "github:hyprwm/Hyprland";
# DO NOT set inputs.hyprland.inputs.nixpkgs.follows — breaks cachix
```
Then import `hyprland.nixosModules.default` and override `programs.hyprland.package = inputs.hyprland.packages.${system}.hyprland;`. See `references/flake-setup.md`.

## Critical Wails / webkit2gtk Fix

Wails apps show a **blank window** on Hyprland + integrated graphics. Fix by setting these env vars (system-wide, in `hyprland.conf`, or in Go code):

```nix
environment.sessionVariables = {
  WEBKIT_DISABLE_DMABUF_RENDERER = "1";   # primary fix
  WEBKIT_DISABLE_COMPOSITING_MODE = "1";  # secondary fix
  GDK_BACKEND     = "wayland,x11";
  NIXOS_OZONE_WL  = "1";
  QT_QPA_PLATFORM = "wayland;xcb";
};
```

Build Wails apps with `wails build -tags webkit2_41` (NixOS ships `webkitgtk_4_1`, not 4.0). Full env list and per-app fallback in `references/wails-webkit-fixes.md`.

## Integrated Graphics (24.11+)

`hardware.opengl.*` was renamed to `hardware.graphics.*` in NixOS 24.11.

```nix
hardware.graphics = {
  enable = true;
  enable32Bit = true;
  extraPackages = with pkgs; [
    intel-media-driver  # Intel Broadwell+ (iHD)
    intel-vaapi-driver  # older Intel (i965)
    vpl-gpu-rt          # 12th gen / Arc oneVPL
    libvdpau-va-gl      # VDPAU shim
  ];
};
```

For AMD APU: mesa RADV is built in — only add `rocmPackages.clr.icd` for OpenCL. Avoid mixing `amdvlk` with RADV. See `references/integrated-graphics.md`.

## Multi-GPU & NVIDIA (2025/2026)

For configs that handle Intel/AMD/NVIDIA from one module, use `nixos-hardware` + a `mySystem.gpu.vendor` enum option. Modern NVIDIA on Hyprland is much simpler than older guides:

- **Drop these obsolete settings** from any older config: `--unsupported-gpu`, `cursor:no_hardware_cursors`, `render:explicit_sync`, `WLR_NO_HARDWARE_CURSORS`. Driver 555+ negotiates explicit sync via `syncobj` automatically.
- **`hardware.nvidia.open` has no default** for driver ≥ 560 — set explicitly. NVIDIA 50xx-series **requires** `open = true`.
- **PRIME sync/reverseSync are X11-only** — Wayland MUST use `prime.offload`.
- **NVIDIA env vars shrunk to two**: `LIBVA_DRIVER_NAME=nvidia` and `__GLX_VENDOR_LIBRARY_NAME=nvidia`.

```nix
inputs.nixos-hardware.url = "github:NixOS/nixos-hardware/master";
modules = [ inputs.nixos-hardware.nixosModules.common-gpu-nvidia-prime ];
```

See `references/multi-gpu.md` for the full smart-defaults pattern, `multi-gpu-module.md` for a paste-ready unified module, and `multi-gpu-env-vars.md` for the env var matrix.

## Animated Wallpapers

Hyprpaper is static-only. For animated/video wallpapers and Wails-controlled wallpaper apps:

| Tool | NixOS attr | Use |
|------|-----------|-----|
| `mpvpaper` | `pkgs.mpvpaper` | Video (mp4/webm), hwdec, mpv IPC socket |
| `awww` (was `swww`) | `pkgs.awww` | Animated GIF/WebP/APNG, transitions |
| `linux-wallpaperengine` | `pkgs.linux-wallpaperengine` | Steam Workshop wallpapers |
| `gtk-layer-shell` | `pkgs.gtk-layer-shell` | Library to make a Wails GTK3 window a wallpaper layer |

**Note**: `pkgs.swww` was removed in nixpkgs PR #459649 (March 2026) — use `pkgs.awww`. Compat shims preserve `swww`/`swww-daemon` commands.

Recommended Wails pattern: app launches `mpvpaper` and controls it via `/tmp/mpv-socket` JSON IPC. Advanced: patch Wails internals to call gtk-layer-shell on the GtkWindow via `github.com/diamondburned/gotk4-layer-shell`. See `references/animated-wallpapers.md` for both paths plus the wlr-layer-shell protocol details.

## XDG Portal

`programs.hyprland.enable` already wires `xdg-desktop-portal-hyprland`. Add the GTK portal for file pickers in Wails apps:

```nix
xdg.portal = {
  enable = true;
  extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
};
```

## Cachix (avoid hours of compile)

```nix
nix.settings = {
  substituters = [ "https://cache.nixos.org" "https://hyprland.cachix.org" ];
  trusted-public-keys = [
    "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
    "hyprland.cachix.org-1:a7pgxzMz7+chwVL3/pzj6jIBMioiJM7ypFP8PwtkuGc="
  ];
};
```

## Validation

```bash
hyprctl version                              # confirms running flake binary
echo $XDG_SESSION_TYPE                       # → wayland
busctl --user list | grep xdg-desktop-portal # portal alive
nix-shell -p libva-utils --run vainfo        # iGPU VA-API
pkg-config --modversion webkit2gtk-4.1       # webkit available
wails doctor                                 # Wails sees deps
```

If a Wails window is still blank after setting env vars: try `LIBGL_ALWAYS_SOFTWARE=1` and verify env inherited via `cat /proc/$(pidof yourapp)/environ | tr '\0' '\n' | grep WEBKIT`.

## Common Traps

- **Don't override `inputs.hyprland.inputs.nixpkgs.follows`** — breaks cachix, forces multi-hour local rebuild.
- **Don't enable `xdg.portal` without an extraPortal** — portal silently fails. Always add `xdg-desktop-portal-gtk`.
- **`hardware.opengl` is deprecated** — use `hardware.graphics` on 24.11+.
- **`wails build` without `-tags webkit2_41`** fails — NixOS has webkitgtk-4.1 only.
- **Setting `package = null`** in home-manager when system already installs Hyprland avoids double-install.
