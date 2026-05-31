---
name: sway
description: Sway tiling Wayland compositor on NixOS. This skill should be used when configuring programs.sway, GPU rendering (Intel/AMD/NVIDIA), Wails/webkit2gtk fixes, xdg portals, home-manager, or wallpapers.
---

# Sway on NixOS

## Overview

Configure Sway (i3-compatible tiling Wayland compositor) on NixOS. Optimized for running webkit2gtk-based desktop apps (Wails, Tauri) on integrated graphics. The NixOS `programs.sway` module already wires XDG portals, polkit, dbus, swaylock PAM, and the GTK FileChooser portal — focus on the Wails-specific tweaks.

## Quick Reference

| Task | Where |
|------|-------|
| NixOS module options | `references/nixos-module.md` |
| What `programs.sway.enable` auto-wires | `references/auto-wired.md` |
| Integrated graphics (Intel/AMD) | `references/integrated-graphics.md` |
| **Multi-GPU (Intel/AMD/NVIDIA) smart defaults** | `references/multi-gpu.md` |
| **Multi-GPU unified module (`mySystem.gpu`)** | `references/multi-gpu-module.md` |
| **Per-vendor Sway env var matrix** | `references/multi-gpu-env-vars.md` |
| **Sway-specific NVIDIA quirks (`--unsupported-gpu`, WLR_*)** | `references/sway-nvidia.md` |
| Wails blank-screen webkit2gtk fix | `references/wails-webkit-fixes.md` |
| **Animated wallpapers (mpvpaper, awww, gtk-layer-shell)** | `references/animated-wallpapers.md` |
| home-manager sway module | `references/home-manager.md` |
| Complete `flake.nix` example | `references/flake-example.md` |
| Ecosystem packages (waybar, etc.) | `references/ecosystem-packages.md` |

For NixOS-level concerns (flakes, modules, packaging, devShells), see the sibling `nixos` skill: `~/.claude/skills/nixos/`. Cross-references: `flakes.md`, `nixos-modules.md`, `home-manager.md`, `packaging.md`, `devshells.md`.

## Core Setup

```nix
programs.sway = {
  enable = true;
  wrapperFeatures.gtk = true;   # CRITICAL for Wails / GTK3 / webkit2gtk
  xwayland.enable = true;        # default true; keep for fallback
  extraSessionCommands = ''
    export GDK_BACKEND="wayland,x11"
    export QT_QPA_PLATFORM=wayland-egl
    export NIXOS_OZONE_WL=1
    export _JAVA_AWT_WM_NONREPARENTING=1
    export XDG_CURRENT_DESKTOP=sway
    export WEBKIT_DISABLE_DMABUF_RENDERER=1   # Wails fix
  '';
  extraPackages = with pkgs; [
    waybar wofi mako wl-clipboard slurp swappy
    swaylock-effects pavucontrol playerctl
    qt5.qtwayland qt6.qtwayland polkit_gnome
  ];
};
```

The `programs.sway.enable` module **already configures** `xdg.portal`, `xdg-desktop-portal-wlr`, `xdg-desktop-portal-gtk`, `security.polkit`, `security.pam.services.swaylock`, dbus session, and GTK as the default FileChooser backend. **Do NOT re-enable these manually.** See `references/auto-wired.md`.

## Critical: wrapperFeatures.gtk

`wrapperFeatures.gtk = true` runs Sway through `wrapGAppsHook`, which injects `XDG_DATA_DIRS`, `GDK_PIXBUF_MODULE_FILE`, and other GTK environment variables that Wails / webkit2gtk apps need to render correctly. **Without this, Wails windows show missing icons, broken file pickers, and rendering glitches.**

## Critical: Wails / webkit2gtk Fix

Wails apps show **blank windows** on Sway + integrated graphics due to the webkit2gtk DMA-BUF renderer regression. Fix via `extraSessionCommands` (above) or `environment.sessionVariables`:

```nix
environment.sessionVariables = {
  WEBKIT_DISABLE_DMABUF_RENDERER = "1";   # primary fix
  WEBKIT_DISABLE_COMPOSITING_MODE = "1";  # secondary fix if still blank
};
```

Build Wails apps with `wails build -tags webkit2_41` (NixOS only ships `webkitgtk_4_1`/libsoup3, not 4.0). Full env list and per-app fallback in `references/wails-webkit-fixes.md`. Note: Wails v2 PR #3027 already defaults `WebviewGpuPolicy = Never` on Linux, but the env vars still help when the dmabuf path is reached via XWayland.

## Integrated Graphics (24.11+)

`hardware.opengl.*` was renamed to `hardware.graphics.*` in NixOS 24.11.

```nix
hardware.graphics = {
  enable = true;
  enable32Bit = true;
  extraPackages = with pkgs; [
    intel-media-driver  # Intel Broadwell+ (iHD VA-API)
    vpl-gpu-rt          # oneVPL/QSV runtime (12th gen+, replaces deprecated intel-media-sdk)
    libvdpau-va-gl      # VDPAU shim
    intel-compute-runtime # OpenCL NEO (Gen8+)
  ];
};
environment.sessionVariables.LIBVA_DRIVER_NAME = "iHD";
```

For AMD APU: mesa RADV is built in — only add `rocmPackages.clr.icd` for OpenCL. **Avoid `amdvlk`** (being deprecated). For pre-Broadwell Intel: use `intel-vaapi-driver` and `LIBVA_DRIVER_NAME=i965`. See `references/integrated-graphics.md`.

## Multi-GPU & NVIDIA (2025/2026)

For configs that handle Intel/AMD/NVIDIA from one module, use `nixos-hardware` + a `mySystem.gpu.vendor` enum option. NixOS-level config (`hardware.graphics`, `hardware.nvidia`, `prime.offload`) is compositor-agnostic and applies identically to Sway and Hyprland — only env var placement differs.

- **`hardware.nvidia.open` has no default** for driver ≥ 560 — set explicitly. NVIDIA 50xx-series **requires** `open = true`.
- **PRIME sync/reverseSync are X11-only** — Sway MUST use `prime.offload`.
- **Sway-specific NVIDIA quirks** (`--unsupported-gpu`, `WLR_NO_HARDWARE_CURSORS`, `WLR_DRM_NO_ATOMIC`, `WLR_DRM_DEVICES`): see `references/sway-nvidia.md`.
- **Sway env vars** go in `programs.sway.extraSessionCommands` (not `env =` lines).

```nix
inputs.nixos-hardware.url = "github:NixOS/nixos-hardware/master";
modules = [ inputs.nixos-hardware.nixosModules.common-gpu-nvidia-prime ];
```

See `references/multi-gpu.md` for the full pattern, `multi-gpu-module.md` for a paste-ready unified module, `multi-gpu-env-vars.md` for the env var matrix, and `sway-nvidia.md` for Sway-specific NVIDIA workarounds.

## Animated Wallpapers

swaybg is static-only. For animated/video wallpapers and Wails-controlled wallpaper apps:

| Tool | NixOS attr | Use |
|------|-----------|-----|
| `mpvpaper` | `pkgs.mpvpaper` | Video (mp4/webm), hwdec, mpv IPC socket |
| `awww` (was `swww`) | `pkgs.awww` | Animated GIF/WebP/APNG, transitions |
| `linux-wallpaperengine` | `pkgs.linux-wallpaperengine` | Steam Workshop wallpapers |
| `gtk-layer-shell` | `pkgs.gtk-layer-shell` | Library to make a Wails GTK3 window a wallpaper layer |

**Note**: `pkgs.swww` was removed in nixpkgs PR #459649 (March 2026) — use `pkgs.awww`. Compat shims preserve `swww`/`swww-daemon` commands.

Native sway shortcut for static: `output * bg ~/wallpapers/static.jpg fill` in sway config (sway invokes swaybg automatically). For animation, recommended Wails pattern: app launches `mpvpaper` and controls it via `/tmp/mpv-socket` JSON IPC. Advanced: patch Wails internals to call gtk-layer-shell on the GtkWindow. See `references/animated-wallpapers.md` for both paths plus the wlr-layer-shell protocol details.

## Validation

```bash
swaymsg -t get_version                       # confirms running
echo $XDG_SESSION_TYPE                       # → wayland
echo $XDG_CURRENT_DESKTOP                    # → sway
busctl --user list | grep xdg-desktop-portal # portal alive
nix-shell -p libva-utils --run vainfo        # iGPU VA-API
pkg-config --modversion webkit2gtk-4.1       # webkit available
wails doctor                                 # Wails sees deps
```

If a Wails window is still blank: try `LIBGL_ALWAYS_SOFTWARE=1`, verify env inherited via `cat /proc/$(pidof yourapp)/environ | tr '\0' '\n' | grep WEBKIT`, and check `journalctl --user -b | grep -i webkit` for renderer errors.

## Common Traps

- **Forgetting `wrapperFeatures.gtk = true`** — GTK env vars never injected, Wails apps render broken.
- **Manually setting `xdg.portal.enable`** — already set by sway module; double-config causes conflicts.
- **`hardware.opengl` is deprecated** — use `hardware.graphics` on 24.11+.
- **`wails build` without `-tags webkit2_41`** — fails on NixOS (only webkitgtk-4.1/libsoup3 available).
- **Missing `qt5.qtwayland` + `qt6.qtwayland`** — Qt apps fall back to xcb instead of native Wayland.
- **Custom Sway config without `include /etc/sway/config.d/*`** — breaks systemd user session, portals, and screen sharing. The NixOS module ships critical exec lines there.
