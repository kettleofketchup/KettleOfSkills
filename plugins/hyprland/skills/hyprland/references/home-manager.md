# home-manager: wayland.windowManager.hyprland

Source: `home-manager/modules/services/window-managers/hyprland.nix`

## Options

| Option | Type | Notes |
|--------|------|-------|
| `enable` | bool | Master switch. Still enable `programs.hyprland.enable` at NixOS level. |
| `package` | nullable package | Set to `null` if NixOS already installs Hyprland. Use `inputs.hyprland.packages.${system}.hyprland` for flake. |
| `portalPackage` | nullable package | Same null-or-override pattern. |
| `plugins` | list of package or path | Hyprland plugins to load. |
| `xwayland.enable` | bool (default true) | |
| `systemd.enable` | bool (default true) | Wires `hyprland-session.target`, imports env vars to systemd user. |
| `systemd.variables` | list of str | Default = 5 standard vars. Use `[ "--all" ]` to import everything. |
| `systemd.extraCommands` | list of str | Restarts target after activation by default. |
| `systemd.enableXdgAutostart` | bool | Enables `systemd-xdg-autostart-generator`. |
| `settings` | attrs | Hyprland config in Nix. Recursive (bool/int/float/str/path/attrs/list). Same-key entries should be lists. |
| `submaps` | attrs of submodule | Declarative submap definitions. |

## Pattern: package=null when NixOS installs Hyprland

The cleanest split for NixOS users: NixOS installs the binary, home-manager only manages config.

```nix
{ inputs, pkgs, ... }:
{
  imports = [ inputs.hyprland.homeManagerModules.default ];

  wayland.windowManager.hyprland = {
    enable          = true;
    package         = null;  # NixOS already provides Hyprland
    portalPackage   = null;
    xwayland.enable = true;
    systemd = {
      enable = true;
      variables = [ "--all" ];
    };

    settings = {
      "$mod" = "SUPER";
      monitor = [ ",preferred,auto,1" ];

      env = [
        "WEBKIT_DISABLE_DMABUF_RENDERER,1"
        "WEBKIT_DISABLE_COMPOSITING_MODE,1"
        "GDK_BACKEND,wayland,x11"
        "NIXOS_OZONE_WL,1"
        "XCURSOR_SIZE,24"
        "HYPRCURSOR_SIZE,24"
      ];

      exec-once = [
        "waybar"
        "hyprpaper"
        "mako"
        "wl-paste --type text  --watch cliphist store"
        "wl-paste --type image --watch cliphist store"
        "${pkgs.polkit_gnome}/libexec/polkit-gnome-authentication-agent-1"
      ];

      general = {
        gaps_in = 5;
        gaps_out = 10;
        border_size = 2;
        "col.active_border"   = "rgba(33ccffee) rgba(00ff99ee) 45deg";
        "col.inactive_border" = "rgba(595959aa)";
        layout = "dwindle";
        allow_tearing = false;
      };

      decoration = {
        rounding = 8;
        blur = { enabled = true; size = 3; passes = 1; };
        shadow = { enabled = true; range = 4; render_power = 3; color = "rgba(1a1a1aee)"; };
      };

      animations = {
        enabled = true;
        bezier = [ "myBezier, 0.05, 0.9, 0.1, 1.05" ];
        animation = [
          "windows,    1, 7,  myBezier"
          "windowsOut, 1, 7,  default, popin 80%"
          "border,     1, 10, default"
          "fade,       1, 7,  default"
          "workspaces, 1, 6,  default"
        ];
      };

      input = {
        kb_layout = "us";
        follow_mouse = 1;
        touchpad.natural_scroll = true;
      };

      bind = [
        "$mod, Q, exec, kitty"
        "$mod, C, killactive,"
        "$mod, M, exit,"
        "$mod, V, togglefloating,"
        "$mod, R, exec, rofi -show drun"
        "$mod SHIFT, W, exec, kitty -e wails dev"
        "$mod, 1, workspace, 1"
        "$mod, 2, workspace, 2"
        "$mod SHIFT, 1, movetoworkspace, 1"
        "$mod SHIFT, 2, movetoworkspace, 2"
      ];

      bindm = [
        "$mod, mouse:272, movewindow"
        "$mod, mouse:273, resizewindow"
      ];

      # Float Wails DevTools so it doesn't fight tiling
      windowrulev2 = [
        "float, class:^(wails-dev)$"
        "float, title:^(DevTools)"
      ];
    };
  };
}
```

## Pattern: package = inputs.hyprland (flake-managed without NixOS module)

For non-NixOS systems (Ubuntu via home-manager standalone, etc.):

```nix
wayland.windowManager.hyprland = {
  enable = true;
  package = inputs.hyprland.packages.${pkgs.system}.hyprland;
  portalPackage = inputs.hyprland.packages.${pkgs.system}.xdg-desktop-portal-hyprland;
};
```

## Source URL

- https://github.com/nix-community/home-manager/blob/master/modules/services/window-managers/hyprland.nix
