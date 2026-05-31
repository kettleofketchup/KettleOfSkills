# What `programs.sway.enable` Auto-Wires

Setting `programs.sway.enable = true` in NixOS triggers a chain of auto-config that handles 80% of a working Wayland session. **Do not duplicate these settings manually** — they cause conflicts.

## Set automatically

| What | By |
|------|----|
| `xdg.portal.enable = true` | wayland-session.nix |
| `xdg.portal.wlr.enable = true` | wayland-session.nix |
| `xdg.portal.extraPortals = [ xdg-desktop-portal-gtk ]` | wayland-session.nix |
| `xdg.portal.config.sway` (gtk default, wlr screencast/screenshot) | sway.nix |
| `security.polkit.enable = true` | wayland-session.nix |
| `security.pam.services.swaylock = { }` | wayland-session.nix |
| `programs.dconf.enable = true` | wayland-session.nix (mkDefault) |
| `programs.xwayland.enable = true` | wayland-session.nix (mkDefault) |
| `services.graphical-desktop.enable = true` | wayland-session.nix |
| `services.xserver.desktopManager.runXdgAutostartIfNone = true` | wayland-session.nix (mkDefault) |
| `/etc/sway/config.d/nixos.conf` (dbus + systemd user session) | sway.nix |

## What you still need to add manually

These are NOT set by `programs.sway.enable`. Add them yourself:

### Display manager

Sway is a session entry but no display manager is enabled by default:

```nix
# Option A: greetd + tuigreet (lightweight, terminal-based)
services.greetd = {
  enable = true;
  settings.default_session = {
    command = "${pkgs.greetd.tuigreet}/bin/tuigreet --time --cmd sway";
    user = "greeter";
  };
};

# Option B: SDDM with Wayland support
services.displayManager.sddm = {
  enable = true;
  wayland.enable = true;
};
```

### Audio

```nix
security.rtkit.enable = true;
services.pipewire = {
  enable = true;
  alsa = { enable = true; support32Bit = true; };
  pulse.enable = true;
  wireplumber.enable = true;
};
```

PipeWire is **strongly recommended over PulseAudio** because screen-sharing portals require it.

### Polkit GUI agent

A polkit agent must be running for GUI sudo prompts. The sway module enables `security.polkit` but doesn't auto-launch an agent:

```nix
systemd.user.services.polkit-gnome-authentication-agent-1 = {
  description = "polkit-gnome-authentication-agent-1";
  wantedBy = [ "graphical-session.target" ];
  wants    = [ "graphical-session.target" ];
  after    = [ "graphical-session.target" ];
  serviceConfig = {
    Type      = "simple";
    ExecStart = "${pkgs.polkit_gnome}/libexec/polkit-gnome-authentication-agent-1";
    Restart   = "on-failure";
  };
};
```

Or launch from `~/.config/sway/config`:
```
exec /run/current-system/sw/libexec/polkit-gnome-authentication-agent-1
```

### User groups

```nix
users.users.dev = {
  isNormalUser = true;
  extraGroups  = [ "wheel" "networkmanager" "video" "render" "audio" "input" ];
};
```

`video` and `render` are required for direct DRM access (compositor needs them).

### Fonts

```nix
fonts.packages = with pkgs; [
  noto-fonts noto-fonts-emoji noto-fonts-cjk-sans
  nerd-fonts.jetbrains-mono   # 25.11+ syntax
];
```

## Don't double-configure

Common mistake: copying snippets from generic NixOS guides that re-enable portals.

```nix
# ❌ DON'T - already set by programs.sway
xdg.portal = {
  enable = true;
  wlr.enable = true;
  extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
};

# ✅ DO - only override the parts you need
xdg.portal.config.sway."org.freedesktop.impl.portal.FileChooser" = [ "gtk" ];
```
