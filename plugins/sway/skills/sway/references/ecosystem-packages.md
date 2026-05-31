# Sway Ecosystem Packages

Companion utilities for a complete Sway session. Add to `programs.sway.extraPackages` (so they run inside the wrapped Sway session) or `environment.systemPackages` (system-wide).

## Already in `programs.sway.extraPackages` defaults

```
brightnessctl  foot  grim  pulseaudio  swayidle  swaylock  wmenu
```

The defaults give a barely-functional session — add the rest below.

## Status bar

| Package | Notes |
|---------|-------|
| `waybar` | Most popular; rich modules; CSS theming |
| `i3status-rust` | Rust rewrite of i3status |
| `eww` | Custom dashboards (Lisp-like config) |

## Launcher / runner

| Package | Notes |
|---------|-------|
| `wofi` | Wayland-native dmenu/drun |
| `rofi-wayland` | Rofi fork with Wayland support |
| `fuzzel` | Fast minimal Wayland launcher |
| `bemenu` | dmenu rewrite that works under wlroots |

## Notifications

| Package | Notes |
|---------|-------|
| `mako` | Lightweight, recommended for sway minimalists |
| `dunst` | Featureful, X11-origin but works on Wayland |
| `swaync` | Notification center with control panel |

## Screenshot / clipboard

| Package | Purpose |
|---------|---------|
| `grim` | Take screenshot (in defaults) |
| `slurp` | Region selection |
| `swappy` | Interactive screenshot annotator |
| `wl-clipboard` | wl-copy / wl-paste |
| `cliphist` | Clipboard history |
| `wf-recorder` | Screen recording |

Common bind: `grim -g "$(slurp)" - | wl-copy`

## Lock / idle

| Package | Notes |
|---------|-------|
| `swaylock` | In defaults |
| `swaylock-effects` | Fancier fork with blur, screenshots, clock |
| `swayidle` | In defaults; idle timer daemon |

`swayidle` example:
```
exec swayidle -w \
  timeout 300 'swaylock -f' \
  timeout 600 'swaymsg "output * dpms off"' \
  resume      'swaymsg "output * dpms on"' \
  before-sleep 'swaylock -f'
```

## Hardware control

```nix
brightnessctl       # backlight (in defaults)
playerctl           # MPRIS media player control
pavucontrol         # PulseAudio/PipeWire volume GUI
pamixer             # CLI mixer
networkmanagerapplet # nm-applet tray icon
blueman             # Bluetooth manager
```

## Qt Wayland support

```nix
qt5.qtwayland
qt6.qtwayland
libsForQt5.qt5ct
qt6ct
```

Required for Qt apps to render natively on Wayland — without these they fall back to xcb (XWayland).

## Polkit authentication agent

GUI sudo prompts need a polkit agent. Pick ONE:

```nix
polkit_gnome
# or
kdePackages.polkit-kde-agent-1
# or
lxqt.lxqt-policykit
```

Launch as a systemd user service (see `references/auto-wired.md`) or via `~/.config/sway/config`:
```
exec /run/current-system/sw/libexec/polkit-gnome-authentication-agent-1
```

## Fonts

```nix
fonts.packages = with pkgs; [
  noto-fonts
  noto-fonts-emoji
  noto-fonts-cjk-sans
  nerd-fonts.jetbrains-mono   # 25.11+ syntax
  # Older nixpkgs:
  # (nerdfonts.override { fonts = [ "JetBrainsMono" ]; })
];
```

## Recommended bundle for Wails dev workstation

```nix
programs.sway.extraPackages = with pkgs; [
  # Bar / launcher / notifications
  waybar wofi mako
  # Screenshots / clipboard
  grim slurp swappy wl-clipboard cliphist
  # Lock / idle
  swaylock-effects swayidle
  # Hardware
  brightnessctl playerctl pavucontrol pamixer
  networkmanagerapplet
  # Qt
  qt5.qtwayland qt6.qtwayland
  # Polkit
  polkit_gnome
  # Misc
  xdg-utils libnotify
];

environment.systemPackages = with pkgs; [
  # Fonts handled in fonts.packages
  # Wails build deps
  go gcc pkg-config gtk3 webkitgtk_4_1 nodejs_20 wails
];
```
