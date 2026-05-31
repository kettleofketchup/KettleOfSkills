# Multi-GPU Smart Defaults Module (Sway)

A single NixOS module exposing `mySystem.gpu.vendor` that auto-configures Intel, AMD, NVIDIA, or hybrid setups for a Sway session.

The hardware blocks (`hardware.graphics`, `hardware.nvidia`, `prime.offload`) are compositor-agnostic — same as the Hyprland version. The Sway-specific bits live in `programs.sway.extraSessionCommands` (not `env =` lines).

```nix
# modules/hardware/gpu.nix
{ config, lib, pkgs, ... }:
let
  cfg = config.mySystem.gpu;
in
{
  options.mySystem.gpu = {
    vendor = lib.mkOption {
      type = lib.types.enum [ "intel" "amd" "nvidia" "hybrid-intel-nvidia" "hybrid-amd-nvidia" ];
      default = "intel";
    };

    nvidiaOpen = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = ''
        Use NVIDIA open kernel modules (Turing+; REQUIRED for 50xx-series).
      '';
    };

    nvidiaPackage = lib.mkOption {
      type = lib.types.nullOr lib.types.package;
      default = null;
    };

    intelBusId  = lib.mkOption { type = lib.types.str; default = "PCI:0@0:2:0"; };
    amdgpuBusId = lib.mkOption { type = lib.types.str; default = "PCI:5@0:0:0"; };
    nvidiaBusId = lib.mkOption { type = lib.types.str; default = "PCI:1@0:0:0"; };
  };

  config = lib.mkMerge [
    # Universal graphics stack
    {
      hardware.graphics = {
        enable = true;
        enable32Bit = true;
      };
    }

    # Intel
    (lib.mkIf (builtins.elem cfg.vendor [ "intel" "hybrid-intel-nvidia" ]) {
      services.xserver.videoDrivers = lib.mkDefault [ "modesetting" ];
      hardware.graphics.extraPackages = with pkgs; [
        intel-media-driver intel-vaapi-driver libvdpau-va-gl
        vpl-gpu-rt intel-compute-runtime
      ];
    })

    # AMD
    (lib.mkIf (builtins.elem cfg.vendor [ "amd" "hybrid-amd-nvidia" ]) {
      services.xserver.videoDrivers = lib.mkDefault [ "amdgpu" ];
      hardware.amdgpu.initrd.enable = true;
      hardware.graphics.extraPackages = with pkgs; [
        rocmPackages.clr.icd libva libva-utils
      ];
    })

    # NVIDIA (discrete or hybrid)
    (lib.mkIf (builtins.elem cfg.vendor [ "nvidia" "hybrid-intel-nvidia" "hybrid-amd-nvidia" ]) {
      services.xserver.videoDrivers = [ "nvidia" ];
      hardware.graphics.extraPackages = with pkgs; [
        nvidia-vaapi-driver libvdpau-va-gl libva
      ];
      hardware.nvidia = {
        modesetting.enable = true;
        open = cfg.nvidiaOpen;
        powerManagement.enable = true;
        nvidiaSettings = true;
        package =
          if cfg.nvidiaPackage != null
          then cfg.nvidiaPackage
          else config.boot.kernelPackages.nvidiaPackages.stable;
      };
      boot.kernelParams = [
        "nvidia.NVreg_PreserveVideoMemoryAllocations=1"
        "nvidia.NVreg_TemporaryFilePath=/var/tmp"
      ];

      # Sway-specific: see references/sway-nvidia.md for whether this is still needed
      # programs.sway.extraOptions = [ "--unsupported-gpu" ];
    })

    # Intel + NVIDIA Optimus (PRIME offload — Wayland-compatible)
    (lib.mkIf (cfg.vendor == "hybrid-intel-nvidia") {
      services.xserver.videoDrivers = [ "modesetting" "nvidia" ];
      hardware.nvidia.prime = {
        offload = { enable = true; enableOffloadCmd = true; };
        intelBusId  = cfg.intelBusId;
        nvidiaBusId = cfg.nvidiaBusId;
      };
      hardware.nvidia.powerManagement.finegrained = true;  # Turing+ only
      boot.initrd.kernelModules = [ "i915" ];
    })

    # AMD + NVIDIA hybrid
    (lib.mkIf (cfg.vendor == "hybrid-amd-nvidia") {
      services.xserver.videoDrivers = [ "amdgpu" "nvidia" ];
      hardware.nvidia.prime = {
        offload = { enable = true; enableOffloadCmd = true; };
        amdgpuBusId = cfg.amdgpuBusId;
        nvidiaBusId = cfg.nvidiaBusId;
      };
    })
  ];
}
```

## Usage in host config

```nix
{
  imports = [ ./modules/hardware/gpu.nix ];
  mySystem.gpu.vendor = "intel";
  # mySystem.gpu.vendor = "amd";
  # mySystem.gpu.vendor = "nvidia";
  # mySystem.gpu.vendor = "hybrid-intel-nvidia";

  # NVIDIA 50xx-series:
  # mySystem.gpu.nvidiaOpen = true;

  # Hybrid: find with `lspci -D -d ::03xx`
  # mySystem.gpu.intelBusId  = "PCI:0@0:2:0";
  # mySystem.gpu.nvidiaBusId = "PCI:1@0:0:0";
}
```
