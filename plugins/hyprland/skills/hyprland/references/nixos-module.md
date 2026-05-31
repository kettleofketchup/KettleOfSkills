# NixOS programs.hyprland Module Options

Source: `nixpkgs/nixos/modules/programs/wayland/hyprland.nix` (release-25.11)

## Options

| Option | Type | Default | Notes |
|--------|------|---------|-------|
| `programs.hyprland.enable` | bool | false | Master switch. Adds session entry, configures `xdg.portal`, installs Hyprland. |
| `programs.hyprland.package` | package | `pkgs.hyprland` | Override with `inputs.hyprland.packages.${system}.hyprland` for flake. |
| `programs.hyprland.portalPackage` | package | `pkgs.xdg-desktop-portal-hyprland` | Pin to same Hyprland build as `package`. |
| `programs.hyprland.xwayland.enable` | bool | true | Compiles with XWayland support. Keep enabled — Wails benefits from XWayland fallback. |
| `programs.hyprland.withUWSM` | bool | false | Launch via Universal Wayland Session Manager. Recommended on 25.11+; sets `programs.uwsm.enable = true`, registers `wayland-session@Hyprland.target`. |
| `programs.hyprland.systemd.setPath.enable` | bool | auto | Sets systemd user `DefaultEnvironment` PATH so xdg-open works. Auto-enabled on Hyprland < 0.41.2. |

## Removed options (do not use)

- `programs.hyprland.xwayland.hidpi` — REMOVED
- `programs.hyprland.enableNvidiaPatches` — REMOVED
- `programs.hyprland.nvidiaPatches` — REMOVED

## Behavior set automatically by `enable = true`

```nix
xdg.portal = {
  enable = true;
  extraPortals = [ cfg.portalPackage ];   # adds xdg-desktop-portal-hyprland
  configPackages = lib.mkDefault [ cfg.package ];
};
```

So you only need to ADD `xdg-desktop-portal-gtk` (for GTK file pickers in Wails apps) — never enable the Hyprland portal yourself.

## Minimal pure-nixpkgs config

```nix
{ pkgs, ... }:
{
  programs.hyprland = {
    enable = true;
    xwayland.enable = true;
  };

  xdg.portal = {
    enable = true;
    extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
  };

  services.dbus.enable = true;
  security.polkit.enable = true;
}
```

## With UWSM (recommended 25.11+)

```nix
programs.hyprland = {
  enable = true;
  xwayland.enable = true;
  withUWSM = true;
};
```

UWSM properly registers `wayland-session@Hyprland.target` and avoids the "Hyprland was started without start-hyprland" warning. Pair with a display manager:

```nix
services.displayManager.sddm = {
  enable = true;
  wayland.enable = true;
};
```

## Two-module pattern (flake input + nixpkgs)

When importing the Hyprland flake's `nixosModules.default`, both modules coexist:

- nixpkgs module → provides `enable`, `xwayland`, `package`, `portalPackage`, `withUWSM`
- flake module → adds `programs.hyprland.{plugins, settings, extraConfig, topPrefixes, bottomPrefixes}`

Use them together. The flake module *extends* the nixpkgs module, it does not replace it.

## Source URLs

- nixpkgs module: https://github.com/NixOS/nixpkgs/blob/release-25.11/nixos/modules/programs/wayland/hyprland.nix
- Hyprland flake module: https://github.com/hyprwm/Hyprland/blob/main/nix/module.nix
