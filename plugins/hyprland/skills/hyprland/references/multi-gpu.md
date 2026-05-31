# Multi-GPU Smart Defaults (Intel / AMD / NVIDIA)

A single NixOS config that handles all three vendor paths via a `mySystem.gpu.vendor` option. Built on `nixos-hardware` and the upstream Hyprland NVIDIA wiki.

## State of the art (2025/2026)

NVIDIA on Hyprland is dramatically simpler than the old guides suggest:
- **`--unsupported-gpu` is gone** — flag removed from Hyprland.
- **`cursor:no_hardware_cursors`, `render:explicit_sync`, `WLR_NO_HARDWARE_CURSORS` are no longer needed on driver 555+**. Explicit sync negotiates via `syncobj` Wayland protocol automatically. Drop these from any config you copy from older guides.
- **`nvidia-drm.modeset=1` is auto-set by NixOS** for driver ≥ 535. Don't add it manually.
- **`hardware.nvidia.open` has NO default for driver ≥ 560** — must set explicitly. NVIDIA 50xx-series **requires** `open = true`.
- **PRIME sync / reverseSync are X11-only** — Wayland/Hyprland MUST use `prime.offload`.
- **`hardware.opengl.*` renamed to `hardware.graphics.*`** in NixOS 24.11.

## nixos-hardware GPU modules

Add the input and import the matching module:

```nix
inputs.nixos-hardware.url = "github:NixOS/nixos-hardware/master";

# Per host:
modules = [ inputs.nixos-hardware.nixosModules.common-gpu-intel ];
# or:
modules = [ inputs.nixos-hardware.nixosModules.common-gpu-amd ];
# or:
modules = [ inputs.nixos-hardware.nixosModules.common-gpu-nvidia ];
# or hybrid:
modules = [
  inputs.nixos-hardware.nixosModules.common-gpu-intel
  inputs.nixos-hardware.nixosModules.common-gpu-nvidia-prime
];
```

The repo also has per-architecture submodules: `ada-lovelace`, `ampere`, `blackwell`, `turing`, plus per-laptop profiles (e.g. `dell-xps-15-9520-nvidia`).

## NVIDIA-specific NixOS config

```nix
{ config, pkgs, ... }:
{
  services.xserver.videoDrivers = [ "nvidia" ];

  hardware.graphics = {
    enable = true;
    enable32Bit = true;
    extraPackages = with pkgs; [
      nvidia-vaapi-driver   # pair with env NVD_BACKEND=direct
      libvdpau-va-gl libva libva-utils vdpauinfo
    ];
  };

  hardware.nvidia = {
    modesetting.enable = true;          # REQUIRED for Wayland
    open = false;                        # MUST set explicitly on driver ≥ 560
                                         # Set true for 50xx-series (REQUIRED)
    powerManagement.enable = true;       # fixes suspend/resume blank screen
    powerManagement.finegrained = false; # only with prime.offload
    nvidiaSettings = true;
    package = config.boot.kernelPackages.nvidiaPackages.stable;
    # Alternatives: .beta .production .latest .vulkan_beta .legacy_470 .legacy_390
  };

  # Preserve VRAM on suspend (avoids blank screen on resume for big GPUs)
  boot.kernelParams = [
    "nvidia.NVreg_PreserveVideoMemoryAllocations=1"
    "nvidia.NVreg_TemporaryFilePath=/var/tmp"
  ];
}
```

## PRIME hybrid laptops (Intel + NVIDIA)

For Wayland/Hyprland use **offload only** (not sync/reverseSync):

```nix
hardware.nvidia.prime = {
  offload = {
    enable = true;
    enableOffloadCmd = true;     # adds `nvidia-offload` wrapper script
  };
  intelBusId  = "PCI:0@0:2:0";   # find with: lspci -D -d ::03xx
  nvidiaBusId = "PCI:1@0:0:0";   # convert hex → decimal
  # amdgpuBusId = "PCI:5@0:0:0"; # use INSTEAD on AMD+NVIDIA hybrid
};
hardware.nvidia.powerManagement.finegrained = true;  # Turing+ only
```

**Find PCI bus IDs**: `nix shell nixpkgs#pciutils -c lspci -D -d ::03xx`. Convert hex → decimal then format as `PCI:<bus>@<domain>:<device>:<func>`. So `0000:01:00.0` → `PCI:1@0:0:0`.

Run a specific app on the dGPU: `nvidia-offload <cmd>`.

## Reference files

| File | Topic |
|------|-------|
| `multi-gpu-module.md` | Complete `mySystem.gpu` smart-defaults module |
| `multi-gpu-env-vars.md` | Hyprland env var matrix per GPU vendor |
| `multi-gpu-flake.md` | Sample flake.nix with intel/amd/nvidia/hybrid hosts |

## Sources

- https://wiki.hypr.land/Nvidia/
- https://wiki.hypr.land/Configuring/Multi-GPU/
- https://wiki.hypr.land/Configuring/Environment-variables/
- https://wiki.nixos.org/wiki/NVIDIA
- https://github.com/NixOS/nixos-hardware
- https://github.com/NixOS/nixpkgs/blob/nixos-unstable/nixos/modules/hardware/video/nvidia.nix
- https://github.com/JaKooLit/NixOS-Hyprland/tree/main/modules
