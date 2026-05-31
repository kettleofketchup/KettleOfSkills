# NixOS programs.sway Module Options

Source: `nixpkgs/nixos/modules/programs/wayland/sway.nix` (release-25.11)

## Options

| Option | Type | Default | Notes |
|--------|------|---------|-------|
| `programs.sway.enable` | bool | false | Master switch. Auto-wires portals, polkit, dbus, swaylock PAM, dconf. |
| `programs.sway.package` | nullable package | `pkgs.sway` | Set `null` if installing via home-manager. |
| `programs.sway.wrapperFeatures.base` | bool | true | Runs `extraSessionCommands` and prepends `dbus-run-session`. |
| `programs.sway.wrapperFeatures.gtk` | bool | false | **Set to `true` for Wails / GTK3 / webkit2gtk.** Wraps via `wrapGAppsHook`. |
| `programs.sway.extraSessionCommands` | lines | "" | Shell commands run just before Sway starts. Requires `wrapperFeatures.base`. |
| `programs.sway.extraOptions` | list of str | [] | Sway CLI args (e.g. `["--unsupported-gpu"]`). |
| `programs.sway.xwayland.enable` | bool | true | Compiles with XWayland support. |
| `programs.sway.extraPackages` | list of pkg | (defaults below) | Extra packages installed in the sway session. |

## Default `extraPackages`

```nix
[ brightnessctl foot grim pulseaudio swayidle swaylock wmenu ]
```

The defaults give a barely-functional session — you'll typically add waybar, wofi/rofi-wayland, mako, slurp, wl-clipboard, qt5/6.qtwayland, polkit_gnome.

## Module-provided portal config

The module auto-sets:

```nix
xdg.portal.config.sway = {
  default = [ "gtk" ];
  "org.freedesktop.impl.portal.ScreenCast" = "wlr";
  "org.freedesktop.impl.portal.Screenshot" = "wlr";
  "org.freedesktop.impl.portal.Inhibit" = "none";
};
```

**This means GTK is the default FileChooser portal — exactly what Wails needs.** The screencast/screenshot interfaces route to `xdg-desktop-portal-wlr`.

## Auto-imported wayland-session.nix

The module imports `wayland-session.nix`, which sets:

```nix
security.polkit.enable = true;
security.pam.services.swaylock = { };
programs.dconf.enable = lib.mkDefault true;
programs.xwayland.enable = lib.mkIf enableXWayland (lib.mkDefault true);
services.graphical-desktop.enable = true;
xdg.portal.wlr.enable = true;
xdg.portal.extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
services.xserver.desktopManager.runXdgAutostartIfNone = lib.mkDefault true;
```

**Do NOT re-enable any of these manually — `programs.sway.enable = true` does it.**

## Auto-installed `/etc/sway/config.d/nixos.conf`

```
exec dbus-update-activation-environment --systemd DISPLAY WAYLAND_DISPLAY SWAYSOCK XDG_CURRENT_DESKTOP
exec "systemctl --user import-environment {,WAYLAND_}DISPLAY SWAYSOCK; systemctl --user start sway-session.target"
exec swaymsg -t subscribe '["shutdown"]' && systemctl --user stop sway-session.target
```

Custom Sway configs **must** include `/etc/sway/config.d/*` or replicate these `exec` lines, otherwise XDG portals, screen sharing, and the systemd user session break.

## Minimal config for Wails dev

```nix
{ pkgs, ... }:
{
  programs.sway = {
    enable = true;
    wrapperFeatures.gtk = true;
    xwayland.enable = true;
    extraSessionCommands = ''
      export GDK_BACKEND="wayland,x11"
      export QT_QPA_PLATFORM=wayland-egl
      export NIXOS_OZONE_WL=1
      export _JAVA_AWT_WM_NONREPARENTING=1
      export XDG_CURRENT_DESKTOP=sway
      export WEBKIT_DISABLE_DMABUF_RENDERER=1
    '';
    extraPackages = with pkgs; [
      waybar wofi mako slurp wl-clipboard swappy
      swaylock-effects pavucontrol playerctl brightnessctl
      qt5.qtwayland qt6.qtwayland polkit_gnome
      networkmanagerapplet xdg-utils
    ];
  };
}
```

## Source URL

- https://github.com/NixOS/nixpkgs/blob/release-25.11/nixos/modules/programs/wayland/sway.nix
- https://github.com/NixOS/nixpkgs/blob/release-25.11/nixos/modules/programs/wayland/wayland-session.nix
