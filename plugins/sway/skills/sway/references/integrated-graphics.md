# Integrated Graphics on NixOS (24.11+)

`hardware.opengl.*` was renamed to `hardware.graphics.*` in NixOS 24.11. Use the new names.

| Old (≤24.05) | New (24.11+) |
|--------------|--------------|
| `hardware.opengl.enable` | `hardware.graphics.enable` |
| `hardware.opengl.driSupport32Bit` | `hardware.graphics.enable32Bit` |
| `hardware.opengl.extraPackages` | `hardware.graphics.extraPackages` |
| `hardware.opengl.extraPackages32` | `hardware.graphics.extraPackages32` |

## Intel iGPU (Broadwell+: Xe / Iris / UHD / Arc)

```nix
{ pkgs, ... }:
{
  hardware.graphics = {
    enable = true;
    enable32Bit = true;
    extraPackages = with pkgs; [
      intel-media-driver        # iHD VA-API (Broadwell+)
      vpl-gpu-rt                # oneVPL/QSV (12th gen+, replaces deprecated intel-media-sdk)
      libvdpau-va-gl            # VDPAU→VA-API bridge
      intel-compute-runtime     # OpenCL NEO (Gen8+)
      vulkan-loader
      vulkan-validation-layers
    ];
    extraPackages32 = with pkgs.pkgsi686Linux; [
      intel-media-driver
      libvdpau-va-gl
    ];
  };

  environment.sessionVariables = {
    LIBVA_DRIVER_NAME = "iHD";       # iHD = modern intel-media-driver
    VDPAU_DRIVER      = "va_gl";     # VDPAU through VA-API
  };

  services.xserver.videoDrivers = [ "modesetting" ];  # do NOT use legacy intel DDX
  boot.initrd.kernelModules = [ "i915" ];
}
```

**Notes:**
- For pre-Broadwell (Haswell, Ivy Bridge): use `intel-vaapi-driver`, set `LIBVA_DRIVER_NAME = "i965"`.
- `intel-media-sdk` is **deprecated** (CVEs) → always use `vpl-gpu-rt`.
- `vaapiIntel` and `vaapiVdpau` are legacy aliases → renamed to `intel-vaapi-driver` and `libvdpau-va-gl`.

## AMD iGPU / APU (Vega APU, Ryzen 7000/8000G RDNA)

```nix
{ pkgs, ... }:
{
  boot.initrd.kernelModules = [ "amdgpu" ];
  services.xserver.videoDrivers = [ "amdgpu" ];

  hardware.graphics = {
    enable = true;
    enable32Bit = true;
    extraPackages = with pkgs; [
      # mesa is included by default (RADV Vulkan + radeonsi OpenGL/VAAPI)
      rocmPackages.clr.icd     # OpenCL via ROCm (replaces rocm-opencl-icd)
      libva
      libvdpau-va-gl
      vulkan-loader
      # amdvlk  ← DEPRECATED. Only add if RADV breaks for your GPU.
    ];
    extraPackages32 = with pkgs.pkgsi686Linux; [
      libvdpau-va-gl
    ];
  };

  environment.sessionVariables = {
    LIBVA_DRIVER_NAME = "radeonsi";
    VDPAU_DRIVER      = "radeonsi";
    # If amdvlk is co-installed, force RADV:
    # AMD_VULKAN_ICD = "RADV";
  };
}
```

**AMD notes:**
- `mesa` provides RADV (Vulkan), `radeonsi` (OpenGL/VAAPI), `r600` (legacy). Auto-enabled with `hardware.graphics.enable`.
- **`amdvlk` is being deprecated.** Stick with RADV unless you have a specific known breakage.
- For older GCN1.0/1.1 cards: `boot.kernelParams = [ "radeon.si_support=0" "radeon.cik_support=0" "amdgpu.si_support=1" "amdgpu.cik_support=1" ];`

## CPU / software rendering fallback

When the iGPU is broken, blacklisted, or you're in a VM with no virtio-gpu:

```nix
environment.sessionVariables = {
  LIBGL_ALWAYS_SOFTWARE = "1";   # Mesa llvmpipe rasterizer
  WLR_RENDERER          = "pixman"; # wlroots CPU renderer (Sway uses wlroots)
};
```

Sway uses wlroots, so `WLR_RENDERER=pixman` is the proper way to force CPU compositing. Slow but always works.

## User groups

```nix
users.users.dev = {
  extraGroups = [ "wheel" "video" "render" "input" "audio" ];
};
```

`video` and `render` are required for direct DRM access by the compositor.

## Validation

```bash
nix-shell -p mesa-demos --run "glxinfo | grep 'OpenGL renderer'"
# → "Mesa Intel(R) UHD Graphics ..." or "AMD Radeon ..."

nix-shell -p libva-utils --run vainfo
# → list of supported VA-API profiles

nix-shell -p vulkan-tools --run "vulkaninfo | grep deviceName"
# → real device, NOT llvmpipe (unless software fallback)

ls -l /dev/dri/
# → card0 / renderD128 owned by group video / render
```

## Source URLs

- NixOS Wiki Intel: https://wiki.nixos.org/wiki/Intel_Graphics
- NixOS Wiki AMD: https://wiki.nixos.org/wiki/AMD_GPU
- NixOS Wiki Graphics: https://wiki.nixos.org/wiki/Graphics
- Accelerated Video Playback: https://wiki.nixos.org/wiki/Accelerated_Video_Playback
