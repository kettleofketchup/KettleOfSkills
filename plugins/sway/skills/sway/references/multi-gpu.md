# Multi-GPU Smart Defaults (Intel / AMD / NVIDIA)

A single NixOS config that handles all three vendor paths via a `mySystem.gpu.vendor` option. Built on `nixos-hardware`. NixOS-level config (`hardware.graphics`, `hardware.nvidia`, `prime.offload`) is compositor-agnostic and applies identically to Sway and Hyprland — only env var placement differs.

For NixOS-specific concerns (flakes, modules, packaging), see the sibling `nixos` skill: `~/.claude/skills/nixos/references/{flakes,nixos-modules,packaging}.md`.

## State of the art (2025/2026)

- **`hardware.opengl.*` renamed to `hardware.graphics.*`** in NixOS 24.11.
- **`hardware.nvidia.open` has NO default** for driver ≥ 560 — must set explicitly. NVIDIA 50xx-series **requires** `open = true`.
- **PRIME sync / reverseSync are X11-only** — Wayland MUST use `prime.offload`.
- **Sway-specific**: see `references/sway-nvidia.md` for whether `--unsupported-gpu` is still needed and which `WLR_*` env vars are still required.
- **Modern NVIDIA driver 555+** supports explicit sync via `syncobj` Wayland protocol natively. Older `WLR_NO_HARDWARE_CURSORS=1` workarounds may no longer be required.

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
      nvidia-vaapi-driver   # pair with NVD_BACKEND=direct
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

For Wayland/Sway use **offload only** (not sync/reverseSync):

```nix
hardware.nvidia.prime = {
  offload = {
    enable = true;
    enableOffloadCmd = true;     # adds `nvidia-offload` wrapper
  };
  intelBusId  = "PCI:0@0:2:0";   # find: lspci -D -d ::03xx
  nvidiaBusId = "PCI:1@0:0:0";   # convert hex → decimal
  # amdgpuBusId = "PCI:5@0:0:0"; # use INSTEAD on AMD+NVIDIA hybrid
};
hardware.nvidia.powerManagement.finegrained = true;  # Turing+ only
```

**Find PCI bus IDs**: `nix shell nixpkgs#pciutils -c lspci -D -d ::03xx`. Convert hex → decimal then format as `PCI:<bus>@<domain>:<device>:<func>`. So `0000:01:00.0` → `PCI:1@0:0:0`.

Run a specific app on the dGPU: `nvidia-offload <cmd>`.

For sway-specific GPU pinning (`WLR_DRM_DEVICES`), see `references/sway-nvidia.md`.

## Reference files

| File | Topic |
|------|-------|
| `multi-gpu-module.md` | Complete `mySystem.gpu` smart-defaults module (sway version) |
| `multi-gpu-env-vars.md` | Sway env var matrix per GPU vendor (extraSessionCommands placement) |
| `sway-nvidia.md` | Sway-specific NVIDIA quirks: `--unsupported-gpu`, `WLR_*` vars |

## Sources

- https://wiki.nixos.org/wiki/NVIDIA
- https://wiki.nixos.org/wiki/Sway
- https://github.com/NixOS/nixos-hardware
- https://github.com/NixOS/nixpkgs/blob/nixos-unstable/nixos/modules/hardware/video/nvidia.nix
- https://github.com/swaywm/sway/wiki
