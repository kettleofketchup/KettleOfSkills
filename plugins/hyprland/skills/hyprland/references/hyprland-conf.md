# Sample hyprland.conf

Minimal Wails-friendly `~/.config/hypr/hyprland.conf`. Trimmed from upstream `example/hyprland.conf` (`hyprwm/Hyprland` main branch).

Use this when writing the file directly instead of via `wayland.windowManager.hyprland.settings`.

```conf
# Monitors
monitor = ,preferred,auto,1

# Programs
$terminal    = kitty
$fileManager = thunar
$menu        = rofi -show drun

# Env vars - cursor + Wails/webkit2gtk fixes
env = XCURSOR_SIZE,24
env = HYPRCURSOR_SIZE,24
env = WEBKIT_DISABLE_DMABUF_RENDERER,1
env = WEBKIT_DISABLE_COMPOSITING_MODE,1
env = GDK_BACKEND,wayland,x11
env = NIXOS_OZONE_WL,1
env = QT_QPA_PLATFORM,wayland;xcb
env = XDG_CURRENT_DESKTOP,Hyprland
env = XDG_SESSION_TYPE,wayland

# Autostart
exec-once = waybar
exec-once = hyprpaper
exec-once = mako
exec-once = wl-paste --type text  --watch cliphist store
exec-once = wl-paste --type image --watch cliphist store
exec-once = /run/current-system/sw/libexec/polkit-gnome-authentication-agent-1

general {
    gaps_in = 5
    gaps_out = 10
    border_size = 2
    col.active_border = rgba(33ccffee) rgba(00ff99ee) 45deg
    col.inactive_border = rgba(595959aa)
    resize_on_border = false
    allow_tearing = false
    layout = dwindle
}

decoration {
    rounding = 8
    rounding_power = 2
    active_opacity = 1.0
    inactive_opacity = 1.0

    shadow {
        enabled = true
        range = 4
        render_power = 3
        color = rgba(1a1a1aee)
    }

    blur {
        enabled = true
        size = 3
        passes = 1
        vibrancy = 0.1696
    }
}

animations {
    enabled = yes
    bezier  = easeOutQuint, 0.23, 1, 0.32, 1
    animation = windows,    1, 4.79, easeOutQuint
    animation = windowsIn,  1, 4.10, easeOutQuint, popin 87%
    animation = windowsOut, 1, 1.49, default,      popin 87%
    animation = border,     1, 5.39, easeOutQuint
    animation = fade,       1, 3.03, easeOutQuint
    animation = workspaces, 1, 1.94, easeOutQuint, fade
}

dwindle { pseudotile = true; preserve_split = true }

misc {
    force_default_wallpaper = 0
    disable_hyprland_logo   = true
}

input {
    kb_layout = us
    follow_mouse = 1
    sensitivity = 0
    touchpad { natural_scroll = true }
}

# Keybinds
$mainMod = SUPER

bind = $mainMod, Q, exec, $terminal
bind = $mainMod, C, killactive,
bind = $mainMod, M, exit,
bind = $mainMod, E, exec, $fileManager
bind = $mainMod, V, togglefloating,
bind = $mainMod, R, exec, $menu
bind = $mainMod, P, pseudo,
bind = $mainMod, J, togglesplit,

bind = $mainMod, left,  movefocus, l
bind = $mainMod, right, movefocus, r
bind = $mainMod, up,    movefocus, u
bind = $mainMod, down,  movefocus, d

# Workspaces 1-5 (extend as needed)
bind = $mainMod, 1, workspace, 1
bind = $mainMod, 2, workspace, 2
bind = $mainMod, 3, workspace, 3
bind = $mainMod SHIFT, 1, movetoworkspace, 1
bind = $mainMod SHIFT, 2, movetoworkspace, 2

bindm = $mainMod, mouse:272, movewindow
bindm = $mainMod, mouse:273, resizewindow

# Volume / brightness / media
bindel = ,XF86AudioRaiseVolume,  exec, wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+
bindel = ,XF86AudioLowerVolume,  exec, wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
bindel = ,XF86AudioMute,         exec, wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
bindel = ,XF86MonBrightnessUp,   exec, brightnessctl -e4 -n2 set 5%+
bindel = ,XF86MonBrightnessDown, exec, brightnessctl -e4 -n2 set 5%-
bindl  = ,XF86AudioPlay,         exec, playerctl play-pause
bindl  = ,XF86AudioNext,         exec, playerctl next
bindl  = ,XF86AudioPrev,         exec, playerctl previous

# Window rules — float Wails DevTools so it doesn't fight tiling
windowrulev2 = float, title:^(DevTools - .*)$
windowrulev2 = float, class:^(wails-dev)$
```

## Source URL

- https://github.com/hyprwm/Hyprland/blob/main/example/hyprland.conf
