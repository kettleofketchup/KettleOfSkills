# Hyprland Env Var Matrix per GPU Vendor

Sourced from `hyprwm/hyprland-wiki/content/Configuring/Environment-variables.md` and `…/Nvidia/_index.md`.

## Universal (always set, regardless of GPU)

```nix
env = [
  "XDG_CURRENT_DESKTOP,Hyprland"
  "XDG_SESSION_TYPE,wayland"
  "XDG_SESSION_DESKTOP,Hyprland"
  "GDK_BACKEND,wayland,x11,*"
  "QT_QPA_PLATFORM,wayland;xcb"
  "QT_WAYLAND_DISABLE_WINDOWDECORATION,1"
  "QT_AUTO_SCREEN_SCALE_FACTOR,1"
  "SDL_VIDEODRIVER,wayland"
  "CLUTTER_BACKEND,wayland"
  "MOZ_ENABLE_WAYLAND,1"
  "NIXOS_OZONE_WL,1"               # Electron / Chromium / CEF
  "ELECTRON_OZONE_PLATFORM_HINT,auto"
  "_JAVA_AWT_WM_NONREPARENTING,1"
];
```

## Intel-only

```nix
env = [
  "LIBVA_DRIVER_NAME,iHD"          # i965 for pre-Broadwell
  "VDPAU_DRIVER,va_gl"
];
```

## AMD-only

```nix
env = [
  "LIBVA_DRIVER_NAME,radeonsi"
  "VDPAU_DRIVER,radeonsi"
  "AMD_VULKAN_ICD,RADV"            # force Mesa RADV over amdvlk
];
```

## NVIDIA (discrete or hybrid)

The Hyprland NVIDIA page now requires only **two** env vars:

```nix
env = [
  "LIBVA_DRIVER_NAME,nvidia"
  "__GLX_VENDOR_LIBRARY_NAME,nvidia"
];
```

Optional additions:

```nix
env = [
  "GBM_BACKEND,nvidia-drm"          # documented but not strictly required
  "NVD_BACKEND,direct"              # only with nvidia-vaapi-driver installed
  "__GL_GSYNC_ALLOWED,1"            # G-Sync monitors
  "__GL_VRR_ALLOWED,0"              # set to 0 to avoid game flicker
  "AQ_DRM_DEVICES,/dev/dri/cardN:/dev/dri/cardM"  # hybrid: force primary
];
```

## Hybrid laptops

Emit the NVIDIA env vars even on `hybrid-intel-nvidia` so that offloaded apps render correctly. The iGPU is primary and doesn't need its own LIBVA override unless you specifically want hardware video decode on the iGPU (in which case set `LIBVA_DRIVER_NAME=iHD` instead — they're mutually exclusive).

For Hyprland to pick the right primary GPU on a hybrid laptop, pin via `AQ_DRM_DEVICES`:

```bash
ls /dev/dri/by-path/
# pci-0000:00:02.0-card → Intel
# pci-0000:01:00.0-card → NVIDIA
```

Then in hyprland.conf:
```ini
env = AQ_DRM_DEVICES,/dev/dri/by-path/pci-0000:00:02.0-card:/dev/dri/by-path/pci-0000:01:00.0-card
```

The first device listed is primary.

## Generation strategy in the unified module

```nix
let
  gpu = config.mySystem.gpu.vendor;
  universalEnv = [ /* ... */ ];
  nvidiaEnv = [ "LIBVA_DRIVER_NAME,nvidia" "__GLX_VENDOR_LIBRARY_NAME,nvidia" ];
  intelEnv  = [ "LIBVA_DRIVER_NAME,iHD"   "VDPAU_DRIVER,va_gl" ];
  amdEnv    = [ "LIBVA_DRIVER_NAME,radeonsi" "VDPAU_DRIVER,radeonsi" "AMD_VULKAN_ICD,RADV" ];

  vendorEnv =
    if gpu == "intel" then intelEnv
    else if gpu == "amd" then amdEnv
    else if gpu == "nvidia" then nvidiaEnv
    else nvidiaEnv;  # hybrid → emit NVIDIA so offloaded apps work

  envLines = lib.concatMapStringsSep "\n"
    (e: "env = ${e}") (universalEnv ++ vendorEnv);
in
{
  environment.etc."hypr/gpu-env.conf".text = envLines;
}
```

User then adds at top of `~/.config/hypr/hyprland.conf`:
```ini
source = /etc/hypr/gpu-env.conf
```

## UWSM caveat

If using `programs.hyprland.withUWSM = true` (recommended on NixOS 24.11+), `env = ...` lines in `hyprland.conf` may NOT be respected. Instead place vars in:

- `~/.config/uwsm/env` — toolkit & general env vars (universal)
- `~/.config/uwsm/env-hyprland` — Hyprland/Aquamarine-specific vars

Example `~/.config/uwsm/env`:
```bash
export LIBVA_DRIVER_NAME=nvidia
export __GLX_VENDOR_LIBRARY_NAME=nvidia
export NIXOS_OZONE_WL=1
export MOZ_ENABLE_WAYLAND=1
```

## Sources

- https://wiki.hypr.land/Configuring/Environment-variables/
- https://wiki.hypr.land/Nvidia/
