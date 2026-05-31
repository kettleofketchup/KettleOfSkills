# Sway-Specific NVIDIA Quirks

Sway differs from Hyprland in three places: the `--unsupported-gpu` startup flag, env var placement (shell exports in `extraSessionCommands` instead of `env =` lines), and the wlroots `WLR_*` env vars used for GPU pinning. The hardware-side NixOS config (`hardware.graphics`, `hardware.nvidia`, `prime.offload`) is identical — see `references/multi-gpu.md`.

## The `--unsupported-gpu` flag (Sway 1.10+ behavior)

Sway 1.10 changed behavior: Sway no longer refuses to start on unsupported GPUs. It now prints an informational warning that can be silenced via the `--unsupported-gpu` CLI flag or the `SWAY_UNSUPPORTED_GPU=1` environment variable.

```nix
programs.sway = {
  enable = true;
  wrapperFeatures.gtk = true;
  extraOptions = [ "--unsupported-gpu" ];   # silences NVIDIA warning
};
```

Pre-1.10 behavior was a hard refusal — that's gone. The historical name `--my-next-gpu-wont-be-nvidia` was removed in Sway 1.7 and replaced by `--unsupported-gpu`.

## NixOS module's NVIDIA warning

`nixpkgs/nixos/modules/programs/wayland/sway.nix` (release-25.11) ships an NVIDIA-aware warning: if `nvidia` is in `services.xserver.videoDrivers` AND the NVIDIA package version is `<= 550`, NixOS prints:

```
Using Sway with Nvidia driver version <= 550 may result in a broken system…
```

The NixOS module does **not** automatically pass `--unsupported-gpu` — users must opt in via `programs.sway.extraOptions = [ "--unsupported-gpu" ];`.

## Sway's official position (softened in practice)

The combative "I will never accept NVIDIA patches" FAQ has been overtaken by reality. Sway 1.10 + wlroots 0.18 detect NVIDIA proprietary via `drmGetVersion()` and degrade gracefully rather than refuse. Community consensus: driver **555+ recommended**, pass `--unsupported-gpu`, set `WLR_NO_HARDWARE_CURSORS=1` and `WLR_RENDERER=vulkan`, it works.

## Env var placement

Sway uses shell-style exports, NOT `env = KEY,VAL` lines. Place NVIDIA env vars in `programs.sway.extraSessionCommands` — runs in the sway-wrapper before `exec sway`:

```nix
programs.sway.extraSessionCommands = ''
  # Wayland session
  export XDG_SESSION_TYPE=wayland
  export LIBVA_DRIVER_NAME=nvidia
  export __GLX_VENDOR_LIBRARY_NAME=nvidia
  export GBM_BACKEND=nvidia-drm
  export NVD_BACKEND=direct          # only with nvidia-vaapi-driver
  export __GL_GSYNC_ALLOWED=1
  export __GL_VRR_ALLOWED=0

  # wlroots NVIDIA workarounds (still required in 2026)
  export WLR_NO_HARDWARE_CURSORS=1
  export WLR_RENDERER=vulkan         # reduces flickering vs gles2 default
  export XWAYLAND_NO_GLAMOR=1        # XWayland on NVIDIA still benefits
'';
```

Avoid runtime `exec export …` in sway config — that runs in a child shell and doesn't affect sway itself. Use `environment.sessionVariables` only for vars that should also apply to non-sway sessions.

## wlroots NVIDIA quirks — current state (2026)

| Variable | Status in 2026 | Notes |
|---|---|---|
| `WLR_NO_HARDWARE_CURSORS=1` | **Still required** for NVIDIA | Hardware cursors via wlroots remain unreliable on NVIDIA even with 555+ explicit sync (sway#3617). |
| `WLR_RENDERER=vulkan` | **Recommended** on NVIDIA | Reduces flickering vs the gles2 default. Sway defaults to gles2. |
| `XWAYLAND_NO_GLAMOR=1` | **Recommended** on NVIDIA | XWayland still benefits even on driver 555+. |
| `WLR_DRM_NO_ATOMIC=1` | **No longer needed** with 555+ | Historical workaround for atomic modesetting. |
| `WLR_DRM_NO_MODIFIERS=1` | **No longer needed** with 555+ | Historical DMA-BUF modifier workaround. |
| `WLR_RENDERER_ALLOW_SOFTWARE=1` | Only for nouveau/llvmpipe fallback | Not for proprietary. |
| `WLR_DRM_DEVICES=/dev/dri/cardN:/dev/dri/cardM` | **GPU selection on hybrid** | Sway-specific equivalent of Hyprland's `AQ_DRM_DEVICES`. First listed = renderer. **Colon**-separated. |
| `WLR_BACKENDS` | Rarely needed | Default DRM backend is correct for hardware sessions. |

## Hybrid PRIME offload from Sway

PRIME sync is X11-only (same as Hyprland). For Wayland hybrid laptops, use `hardware.nvidia.prime.offload.enable = true;` and pin the wlroots renderer to the iGPU via `WLR_DRM_DEVICES`.

**Reverse PRIME (render iGPU → display NVIDIA) is NOT supported on Sway** — wlroots cannot mix renderers across devices (sway#7241, closed as architectural limitation).

```nix
programs.sway.extraSessionCommands = ''
  export WLR_DRM_DEVICES=/dev/dri/by-path/pci-0000:00:02.0-card
'';
```

Use `by-path` rather than `card0`/`card1` because card numbering is not stable across boots. List with `ls /dev/dri/by-path/`.

## Software rendering fallback

For VMs without virtio-gpu or broken iGPUs:

```nix
programs.sway.extraSessionCommands = ''
  export WLR_RENDERER=pixman           # CPU renderer (always works)
  export LIBGL_ALWAYS_SOFTWARE=1
  export WLR_RENDERER_ALLOW_SOFTWARE=1
'';
```

`WLR_RENDERER=pixman` is the wlroots CPU compositor — slow but always works. Alternative: `WLR_RENDERER=vulkan` or `WLR_RENDERER=gles2`.

## Smart-defaults integration

In the unified `mySystem.gpu` module, conditionally append to `extraSessionCommands` and `extraOptions` based on `cfg.vendor`:

```nix
(lib.mkIf (builtins.elem cfg.vendor [ "nvidia" "hybrid-intel-nvidia" "hybrid-amd-nvidia" ]) {
  programs.sway.extraOptions = [ "--unsupported-gpu" ];
  programs.sway.extraSessionCommands = ''
    export WLR_NO_HARDWARE_CURSORS=1
    export WLR_RENDERER=vulkan
    export GBM_BACKEND=nvidia-drm
    export __GLX_VENDOR_LIBRARY_NAME=nvidia
    export LIBVA_DRIVER_NAME=nvidia
    export XWAYLAND_NO_GLAMOR=1
  '';
})

(lib.mkIf (cfg.vendor == "hybrid-intel-nvidia") {
  programs.sway.extraSessionCommands = lib.mkAfter ''
    export WLR_DRM_DEVICES=/dev/dri/by-path/pci-0000:00:02.0-card
  '';
})
```

## Sources

- https://github.com/NixOS/nixpkgs/blob/release-25.11/nixos/modules/programs/wayland/sway.nix (NVIDIA ≤ 550 warning)
- https://github.com/swaywm/sway/releases/tag/1.7 (rename to `--unsupported-gpu`)
- https://github.com/swaywm/sway/releases/tag/1.10 (warning instead of refusal)
- https://github.com/swaywm/sway/issues/3617 (cursor workaround still needed)
- https://github.com/swaywm/sway/issues/7241 (reverse PRIME unsupported)
- https://github.com/swaywm/sway/issues/7887 (`SWAY_UNSUPPORTED_GPU` env var)
- https://github.com/crispyricepc/sway-nvidia/blob/main/wlroots-env-nvidia.sh (canonical env var set)
- https://discourse.nixos.org/t/possible-to-use-sway-with-nvidia-proprietary-driver/46259
- https://discourse.nixos.org/t/screen-flickering-and-tearing-with-nixos-sway-nvidia/49469
- https://bbs.archlinux.org/viewtopic.php?id=291411 (`WLR_RENDERER=vulkan`)
- https://forums.developer.nvidia.com/t/hardware-cursor-is-not-working-on-wayland-drm-sessions/261853
