# Sway Env Var Matrix per GPU Vendor

Sway uses shell-style exports — env vars go in `programs.sway.extraSessionCommands` (or `wayland.windowManager.sway.extraSessionCommands` in home-manager), NOT in `env =` lines like Hyprland.

## Universal (always set, regardless of GPU)

```nix
programs.sway.extraSessionCommands = ''
  export XDG_CURRENT_DESKTOP=sway
  export XDG_SESSION_TYPE=wayland
  export XDG_SESSION_DESKTOP=sway
  export GDK_BACKEND="wayland,x11"
  export QT_QPA_PLATFORM="wayland;xcb"
  export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
  export QT_AUTO_SCREEN_SCALE_FACTOR=1
  export SDL_VIDEODRIVER=wayland
  export CLUTTER_BACKEND=wayland
  export MOZ_ENABLE_WAYLAND=1
  export NIXOS_OZONE_WL=1                  # Electron/Chromium/CEF
  export ELECTRON_OZONE_PLATFORM_HINT=auto
  export _JAVA_AWT_WM_NONREPARENTING=1
'';
```

## Intel-only

```bash
export LIBVA_DRIVER_NAME=iHD          # i965 for pre-Broadwell
export VDPAU_DRIVER=va_gl
```

## AMD-only

```bash
export LIBVA_DRIVER_NAME=radeonsi
export VDPAU_DRIVER=radeonsi
export AMD_VULKAN_ICD=RADV            # force Mesa RADV over amdvlk
```

## NVIDIA (discrete or hybrid)

The two essentials:

```bash
export LIBVA_DRIVER_NAME=nvidia
export __GLX_VENDOR_LIBRARY_NAME=nvidia
```

Optional additions:

```bash
export GBM_BACKEND=nvidia-drm
export NVD_BACKEND=direct                          # only with nvidia-vaapi-driver
export __GL_GSYNC_ALLOWED=1                         # G-Sync monitors
export __GL_VRR_ALLOWED=0                           # avoid game flicker

# wlroots-specific GPU pinning on hybrid (Sway equivalent of Hyprland's AQ_DRM_DEVICES)
export WLR_DRM_DEVICES=/dev/dri/by-path/pci-0000:00:02.0-card
```

`WLR_DRM_DEVICES` accepts a colon-separated list. The first device is used as the primary render/scanout device.

For older NVIDIA drivers (pre-555), the legacy workarounds — see `references/sway-nvidia.md` for whether they're still needed:

```bash
# Historical — verify if still needed on driver 555+
export WLR_NO_HARDWARE_CURSORS=1
export WLR_DRM_NO_ATOMIC=1
export WLR_DRM_NO_MODIFIERS=1
```

## Generation strategy in the unified module

```nix
{ config, lib, pkgs, ... }:
let
  gpu = config.mySystem.gpu.vendor;

  universal = ''
    export XDG_CURRENT_DESKTOP=sway
    export XDG_SESSION_TYPE=wayland
    export GDK_BACKEND="wayland,x11"
    export QT_QPA_PLATFORM="wayland;xcb"
    export NIXOS_OZONE_WL=1
    export MOZ_ENABLE_WAYLAND=1
    export _JAVA_AWT_WM_NONREPARENTING=1
  '';

  intel = ''
    export LIBVA_DRIVER_NAME=iHD
    export VDPAU_DRIVER=va_gl
  '';

  amd = ''
    export LIBVA_DRIVER_NAME=radeonsi
    export VDPAU_DRIVER=radeonsi
    export AMD_VULKAN_ICD=RADV
  '';

  nvidia = ''
    export LIBVA_DRIVER_NAME=nvidia
    export __GLX_VENDOR_LIBRARY_NAME=nvidia
    export GBM_BACKEND=nvidia-drm
  '';

  vendor =
    if gpu == "intel" then intel
    else if gpu == "amd" then amd
    else if gpu == "nvidia" then nvidia
    else nvidia;  # hybrid → emit NVIDIA so offloaded apps work
in
{
  programs.sway.extraSessionCommands = universal + vendor;
}
```

## Where env vars actually need to be set

Sway runs as `sway` started by a display manager (greetd/SDDM/gdm) or TTY. The env propagation chain:

1. **PAM session** loads `environment.sessionVariables` from NixOS — set system-wide vars here for portability.
2. **Display manager wrapper** runs the sway binary inside a wrapped script generated from `programs.sway.extraSessionCommands` (sway's `wrapperFeatures.base = true`).
3. **Sway itself** does NOT have an `env =` directive — only `set $var value` for sway-internal substitution.

For NVIDIA env vars in particular, prefer `programs.sway.extraSessionCommands` because it runs LATE (just before exec sway) and is guaranteed to be in sway's environment. `environment.sessionVariables` works but is loaded earlier and may be overridden.

## Sources

- `nixpkgs/nixos/modules/programs/wayland/sway.nix` (extraSessionCommands handling)
- `nixpkgs/nixos/modules/programs/wayland/wayland-session.nix`
- https://wiki.nixos.org/wiki/Sway
- https://wiki.archlinux.org/title/Sway
