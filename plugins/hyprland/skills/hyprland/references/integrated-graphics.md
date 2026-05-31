# Integrated Graphics on NixOS (24.11+)

`hardware.opengl.*` was renamed to `hardware.graphics.*` in NixOS 24.11. Use the new names.

## Intel iGPU

```nix
{ pkgs, ... }:
{
  hardware.graphics = {
    enable = true;
    enable32Bit = true;       # 32-bit OpenGL (Steam, Wine)
    extraPackages = with pkgs; [
      intel-media-driver       # iHD VA-API: Broadwell (2014) and newer
      intel-vaapi-driver       # i965 VA-API: pre-Broadwell
      libvdpau-va-gl           # VDPAU → VA-API shim
      vpl-gpu-rt               # oneVPL runtime: 12th gen Core / Arc / newer
    ];
    extraPackages32 = with pkgs.driversi686Linux; [
      intel-media-driver
      intel-vaapi-driver
      libvdpau-va-gl
    ];
  };

  environment.sessionVariables = {
    LIBVA_DRIVER_NAME = "iHD";    # use "i965" for pre-Broadwell Intel
    VDPAU_DRIVER      = "va_gl";  # only if libvdpau-va-gl installed
  };
}
```

## AMD iGPU / APU

Mesa RADV (Vulkan) and radeonsi (OpenGL) are pulled in by `hardware.graphics.enable`. Only add packages for OpenCL or extras.

```nix
{ pkgs, ... }:
{
  boot.initrd.kernelModules = [ "amdgpu" ];
  services.xserver.videoDrivers = [ "amdgpu" ];  # only matters under XWayland

  hardware.graphics = {
    enable = true;
    enable32Bit = true;
    extraPackages = with pkgs; [
      # Mesa RADV is the default — no extra package needed.
      # Add amdvlk only if you specifically want AMD's Vulkan ICD alongside RADV.
      # amdvlk

      rocmPackages.clr.icd  # OpenCL
      # VA-API is provided by mesa already.
    ];
  };

  # Defensive: force RADV if amdvlk is co-installed
  environment.sessionVariables.AMD_VULKAN_ICD = "RADV";
}
```

⚠ Don't mix `amdvlk` with RADV unless you set `AMD_VULKAN_ICD = "RADV"`. Vulkan apps will pick the wrong ICD otherwise. (Confirmed in NixOS Discourse: "24.11 & AMD GPU: How to use Mesa RADV instead of amdvlk")

## CPU / software rendering fallback

When the iGPU is broken, blacklisted, or you're in a VM with no virtio-gpu:

```nix
environment.sessionVariables = {
  LIBGL_ALWAYS_SOFTWARE = "1";   # Mesa software rasterizer (llvmpipe)
  WLR_RENDERER = "pixman";        # wlroots CPU renderer (Sway uses this; Hyprland=GLES2)
};
```

For Hyprland specifically, force GLES2 software rendering by also setting `LIBGL_ALWAYS_SOFTWARE=1` — Hyprland's renderer is GLES2-only and will use llvmpipe under software mode.

## User groups

Users need `video` (and usually `render`) group access for direct DRM:

```nix
users.users.kettle = {
  extraGroups = [ "wheel" "video" "render" "input" "audio" ];
};
```

## Validation

```bash
# OpenGL renderer check
nix-shell -p mesa-demos --run "glxinfo | grep 'OpenGL renderer'"
# Expected: "Mesa Intel(R) UHD Graphics ..." or "AMD Radeon ..."

# VA-API check
nix-shell -p libva-utils --run vainfo
# Expected: list of supported profiles

# Vulkan check
nix-shell -p vulkan-tools --run "vulkaninfo | grep deviceName"
# Expected: Intel/AMD device, NOT llvmpipe (unless software fallback)

# DRM device permissions
ls -l /dev/dri/
# Expected: card0 / renderD128 owned by group video / render
```

## Source URLs

- NixOS Wiki Intel: https://wiki.nixos.org/wiki/Intel_Graphics
- NixOS Wiki AMD: https://wiki.nixos.org/wiki/AMD_GPU
- NixOS Wiki Graphics: https://wiki.nixos.org/wiki/Graphics
- Accelerated Video Playback: https://wiki.nixos.org/wiki/Accelerated_Video_Playback
