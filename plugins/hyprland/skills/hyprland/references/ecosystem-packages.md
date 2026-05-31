# Hyprland Ecosystem Packages

Companion utilities for a complete Hyprland desktop. Add to `environment.systemPackages` (system-wide) or `home.packages` (per-user).

## Hypr* family (from hyprwm)

| Package | Purpose |
|---------|---------|
| `hyprpaper` | Wallpaper daemon |
| `hyprlock` | Screen locker (PAM-aware) |
| `hypridle` | Idle daemon (calls hyprlock, dpms off) |
| `hyprcursor` | Cursor theme manager |
| `hyprpicker` | Color picker |
| `hyprshot` | Screenshot wrapper (alternative to grim+slurp) |

## Status bar

| Package | Notes |
|---------|-------|
| `waybar` | Most popular; rich modules; CSS theming |
| `eww` | Elkowar's wacky widgets (Lisp-like config); for custom dashboards |

## Launcher / runner

| Package | Notes |
|---------|-------|
| `rofi-wayland` | Rofi fork with native Wayland support |
| `wofi` | Wayland-only launcher |
| `fuzzel` | Fast minimal Wayland launcher |
| `tofi` | Tiny dmenu replacement |

## Notifications

| Package | Notes |
|---------|-------|
| `mako` | Lightweight, recommended for minimalists |
| `dunst` | Featureful, X11 history; works on Wayland |
| `swaynotificationcenter` | Rich notification center with control panel |

## Screenshot / clipboard

| Package | Purpose |
|---------|---------|
| `grim` | Take screenshot |
| `slurp` | Region selection |
| `swappy` | Interactive screenshot annotator |
| `wl-clipboard` | wl-copy / wl-paste |
| `cliphist` | Clipboard history |
| `satty` | Modern annotation tool (alternative to swappy) |

## Hardware control

```nix
brightnessctl       # backlight
playerctl           # MPRIS media player control
pavucontrol         # PulseAudio volume control GUI
pamixer             # PulseAudio CLI mixer
networkmanagerapplet # nm-applet tray icon
blueman             # Bluetooth manager
```

## Qt Wayland support

```nix
qt5.qtwayland
qt6.qtwayland
libsForQt5.qt5ct    # Qt5 settings GUI
qt6ct               # Qt6 settings GUI
```

Required for Qt-based apps to render natively on Wayland instead of falling back to xcb.

## Polkit authentication agent

GUI sudo prompts need a polkit agent. Pick ONE:

```nix
polkit_gnome
# or
kdePackages.polkit-kde-agent-1
# or
lxqt.lxqt-policykit
```

Launch from `exec-once` in hyprland.conf:
```
exec-once = /run/current-system/sw/libexec/polkit-gnome-authentication-agent-1
```

## Fonts

```nix
noto-fonts            # broad Unicode coverage
noto-fonts-emoji      # color emoji
noto-fonts-cjk-sans   # CJK
nerd-fonts.jetbrains-mono  # 25.11+ syntax for nerd fonts
# Older nixpkgs:
# (nerdfonts.override { fonts = [ "JetBrainsMono" ]; })
```

## Lock / idle / audio

`hyprlock` requires PAM: `security.pam.services.hyprlock = { };`

`hypridle` config (`~/.config/hypr/hypridle.conf`):

```
general {
    lock_cmd = pidof hyprlock || hyprlock
    before_sleep_cmd = loginctl lock-session
    after_sleep_cmd  = hyprctl dispatch dpms on
}
listener { timeout = 300; on-timeout = brightnessctl -s set 10; on-resume = brightnessctl -r }
listener { timeout = 600; on-timeout = loginctl lock-session }
listener { timeout = 660; on-timeout = hyprctl dispatch dpms off; on-resume = hyprctl dispatch dpms on }
```

PipeWire audio:
```nix
security.rtkit.enable = true;
services.pipewire = {
  enable = true;
  alsa = { enable = true; support32Bit = true; };
  pulse.enable = true;
};
```

## Recommended bundle for Wails dev workstation

```nix
environment.systemPackages = with pkgs; [
  # Hypr ecosystem
  hyprpaper hyprlock hypridle hyprcursor hyprpicker hyprshot
  # Bar / launcher / notifications
  waybar rofi-wayland mako
  # Screenshots / clipboard
  grim slurp swappy wl-clipboard cliphist
  # Hardware
  brightnessctl playerctl pavucontrol pamixer
  networkmanagerapplet
  # Qt
  qt5.qtwayland qt6.qtwayland
  # Polkit
  polkit_gnome
  # Fonts
  noto-fonts noto-fonts-emoji
  # Wails build deps
  go gcc pkg-config gtk3 webkitgtk_4_1 nodejs
];
```
