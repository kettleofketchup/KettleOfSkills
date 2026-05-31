# home-manager: wayland.windowManager.sway

Source: `home-manager/modules/services/window-managers/i3-sway/sway.nix`

## Key options

| Option | Type | Notes |
|--------|------|-------|
| `enable` | bool | Master switch. Still set `programs.sway.enable` at NixOS level. |
| `package` | nullable package | Set `null` if NixOS already installs Sway. |
| `systemd.enable` | bool (default true on Linux) | Enables `sway-session.target`. |
| `systemd.variables` | list of str | Defaults: `DISPLAY WAYLAND_DISPLAY SWAYSOCK XDG_CURRENT_DESKTOP XDG_SESSION_TYPE NIXOS_OZONE_WL XCURSOR_THEME XCURSOR_SIZE`. |
| `xwayland` | bool (default true) | |
| `wrapperFeatures.base` | bool (default true) | |
| `wrapperFeatures.gtk` | bool (default false) | **Set to `true` for Wails.** |
| `extraSessionCommands` | lines | Same as NixOS module. |
| `extraOptions` | list of str | Sway CLI args. |
| `config` | submodule | `modifier`, `terminal`, `menu`, `input`, `output`, `keybindings`, `bars`, `gaps`, `floating`, `window`, `startup`, etc. |
| `checkConfig` | bool (default true) | Validates with xvfb-run. Disable if outputs reference home files. |
| `extraConfig` | lines | Raw lines appended to `~/.config/sway/config`. |
| `extraConfigEarly` | lines | Raw lines prepended. |

## Output format (sway-output(5) keys as attrset)

Identify outputs at runtime: `swaymsg -t get_outputs`.

```nix
wayland.windowManager.sway.config.output = {
  "eDP-1" = {
    mode = "1920x1080@60Hz";
    pos = "0 0";
    scale = "1.0";
    bg = "~/wallpapers/laptop.png fill";
    adaptive_sync = "off";
  };
  "DP-1" = {
    mode = "2560x1440@144Hz";
    pos = "1920 0";
    scale = "1.25";
    scale_filter = "smart";
    adaptive_sync = "on";
  };
};
```

## Pattern: package = null when NixOS owns the binary

The cleanest split: NixOS installs sway, home-manager only manages config.

```nix
{ config, pkgs, lib, ... }:
{
  wayland.windowManager.sway = {
    enable = true;
    package = null;                # use system sway from programs.sway
    systemd.enable = true;
    xwayland = true;
    wrapperFeatures.gtk = true;    # Wails / GTK
    checkConfig = false;

    extraSessionCommands = ''
      export GDK_BACKEND="wayland,x11"
      export QT_QPA_PLATFORM=wayland-egl
      export NIXOS_OZONE_WL=1
      export _JAVA_AWT_WM_NONREPARENTING=1
      export XDG_CURRENT_DESKTOP=sway
      export WEBKIT_DISABLE_DMABUF_RENDERER=1
    '';

    config = {
      modifier = "Mod4";
      terminal = "foot";
      menu     = "wofi --show drun";
      defaultWorkspace = "workspace number 1";

      input = {
        "*" = {
          xkb_layout  = "us";
          xkb_options = "ctrl:nocaps";
        };
        "type:touchpad" = {
          tap = "enabled";
          natural_scroll = "enabled";
          dwt = "enabled";
        };
      };

      output."eDP-1" = {
        mode = "1920x1080@60Hz";
        pos  = "0 0";
        scale = "1.0";
        bg = "~/wallpapers/bg.png fill";
      };

      bars = [{ command = "${pkgs.waybar}/bin/waybar"; }];

      gaps = {
        inner = 8;
        outer = 4;
        smartBorders = "on";
        smartGaps = true;
      };

      window = { border = 2; titlebar = false; };
      floating = { border = 2; titlebar = true; };

      keybindings = lib.mkOptionDefault {
        "Mod4+Return"  = "exec foot";
        "Mod4+d"       = "exec wofi --show drun";
        "Mod4+Shift+q" = "kill";
        "Mod4+Shift+e" = "exec swaymsg exit";
        "XF86AudioRaiseVolume"  = "exec pamixer -i 5";
        "XF86AudioLowerVolume"  = "exec pamixer -d 5";
        "XF86AudioMute"         = "exec pamixer -t";
        "XF86MonBrightnessUp"   = "exec brightnessctl set +5%";
        "XF86MonBrightnessDown" = "exec brightnessctl set 5%-";
        "Print"      = "exec grim -g \"$(slurp)\" - | wl-copy";
        "Mod4+Print" = "exec grim - | wl-copy";
      };

      startup = [
        { command = "mako"; }
        { command = "wl-paste --watch cliphist store"; }
        { command = "swayidle -w timeout 300 'swaylock -f' timeout 600 'swaymsg \"output * dpms off\"' resume 'swaymsg \"output * dpms on\"' before-sleep 'swaylock -f'"; }
      ];
    };

    extraConfig = ''
      # CRITICAL: load NixOS sway module's auto-installed config snippets
      include /etc/sway/config.d/*
    '';
  };
}
```

## Source URL

- https://github.com/nix-community/home-manager/blob/master/modules/services/window-managers/i3-sway/sway.nix
