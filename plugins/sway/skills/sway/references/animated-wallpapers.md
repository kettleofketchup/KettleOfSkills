# Animated Wallpapers on Sway

Sway uses wlroots — same `wlr-layer-shell` protocol as Hyprland — so all wlroots-based wallpaper tools (mpvpaper, awww, swaybg, linux-wallpaperengine) work identically. Three approaches: standalone tools, a Wails app controlling them, or a Wails app patched to be a layer-shell window itself.

## NixOS package survey (verified against nixpkgs 2026-04)

| Tool | Renders | NixOS attr | Notes |
|------|---------|------------|-------|
| `swaybg` | Static images only | `pkgs.swaybg` | Sway baseline; can be set via `output * bg <path> fill` in sway config |
| **`awww`** (was `swww`) | GIF, animated PNG/WebP, transitions | `pkgs.awww` | **`pkgs.swww` removed** in nixpkgs PR #459649 (March 2026) — upstream archived, forked to codeberg as `awww`. Compat shims preserve `swww`/`swww-daemon` commands |
| `mpvpaper` | Anything mpv plays (mp4/mkv/webm) | `pkgs.mpvpaper` | Best for video wallpapers; uses libmpv |
| `linux-wallpaperengine` | Wallpaper Engine `.pkg` (Steam Workshop), scenes, video, web | `pkgs.linux-wallpaperengine` | Bundles CEF; ~150MB RSS |
| `wpaperd` | Static images, multi-output rotation | `pkgs.wpaperd` | Per-output schedules |
| `gtk-layer-shell` | n/a (library) | `pkgs.gtk-layer-shell` | GTK3 layer-shell binding for Wails v2 |
| `gtk4-layer-shell` | n/a (library) | `pkgs.gtk4-layer-shell` | GTK4; for Wails v3+ when it lands |

## wlr-layer-shell protocol basics

`wlr-layer-shell-unstable-v1` lets a Wayland client bind a `wl_surface` to one of four layers:

- `background = 0`
- `bottom = 1`
- (regular xdg_toplevel windows)
- `top = 2`
- `overlay = 3`

For a wallpaper: `layer = background`, `exclusive_zone = 0`, anchor to all four edges, `keyboard_interactivity = none`. swaybg/mpvpaper/awww all use this configuration.

## Approach 1: swaybg (built-in static wallpaper)

The simplest path for static images. Sway natively understands `output ... bg ...`:

```
# ~/.config/sway/config
output * bg ~/wallpapers/static.jpg fill
output eDP-1 bg ~/wallpapers/laptop.png fit
output HDMI-A-1 bg #1a1b26 solid_color
```

Sway invokes `swaybg` automatically. No `exec swaybg` needed.

## Approach 2 (recommended for video): mpvpaper + Wails controller

Wails app shells out to `mpvpaper`, controls playback via mpv's JSON IPC socket.

### Sway config

```
# ~/.config/sway/config
exec mpvpaper -p -o "no-audio --loop-playlist --panscan=1.0 hwdec=auto-safe input-ipc-server=/tmp/mpv-socket" '*' ~/wallpapers/space.mp4
```

Flags:
- `-p` = pause-on-fullscreen (saves battery/GPU)
- `'*'` = render on every connected output (Sway uses `*`, Hyprland uses `ALL`)
- `hwdec=auto-safe` = hardware decode (vaapi for Intel/AMD, nvdec for NVIDIA)
- `input-ipc-server=/tmp/mpv-socket` = control socket

### Wails Go controller

```go
package main

import (
    "encoding/json"
    "net"
    "os/exec"
)

func StartWallpaper(videoPath string) error {
    cmd := exec.Command("mpvpaper", "-p",
        "-o", "no-audio --loop-playlist --panscan=1.0 hwdec=auto-safe input-ipc-server=/tmp/mpv-socket",
        "*", videoPath)
    return cmd.Start()
}

func sendMpvCommand(args ...interface{}) error {
    conn, err := net.Dial("unix", "/tmp/mpv-socket")
    if err != nil { return err }
    defer conn.Close()
    payload, _ := json.Marshal(map[string]interface{}{"command": args})
    _, err = conn.Write(append(payload, '\n'))
    return err
}

func TogglePause()  { sendMpvCommand("cycle", "pause") }
func NextVideo()    { sendMpvCommand("playlist-next") }
func Seek(s float64){ sendMpvCommand("seek", s, "absolute") }
```

## Approach 3 (recommended for animated images): awww

```bash
swww-daemon &              # legacy alias still works
awww-daemon &              # new binary name
swww img ~/wp/animated.gif --transition-type wipe --transition-duration 1
swww img --outputs eDP-1 ~/laptop-wp.webp
swww query                  # current wallpaper info
swww kill                   # stop daemon
```

Sway integration:
```
# ~/.config/sway/config
exec swww-daemon
exec sleep 1 && swww img ~/wallpapers/animated.gif --transition-type center --transition-fps 60
```

awww caches decoded animation frames in RAM after first loop — much cheaper than equivalent video, but a 60-frame 4K GIF can hold ~1GB of decoded frames.

## Approach 4 (advanced): Wails-as-wallpaper via gtk-layer-shell

The Go binding `github.com/diamondburned/gotk4-layer-shell` (despite the "gtk4" in the package name, it binds GTK3's gtk-layer-shell library). MPL-2.0.

```go
import gls "github.com/diamondburned/gotk4-layer-shell/pkg/gtklayershell"

// MUST be called BEFORE the GtkWindow is realized
gls.InitForWindow(window)
gls.SetLayer(window, gls.LayerShellLayerBackground)
gls.SetAnchor(window, gls.LayerShellEdgeLeft,   true)
gls.SetAnchor(window, gls.LayerShellEdgeRight,  true)
gls.SetAnchor(window, gls.LayerShellEdgeTop,    true)
gls.SetAnchor(window, gls.LayerShellEdgeBottom, true)
gls.SetExclusiveZone(window, 0)
gls.SetKeyboardMode(window, gls.LayerShellKeyboardModeNone)
gls.SetNamespace(window, "wallpaper")
```

**The hard part**: Wails v2's `v2/internal/frontend/desktop/linux/window.go` creates the GtkWindow inside CGo and does NOT expose it. Three viable approaches:

1. **Fork-and-patch Wails** — add a CGo hook in `window.go` between `gtk_application_window_new` and `gtk_widget_show_all`. Vendor via `replace` in `go.mod`.
2. **Walk active GTK windows** — call `gtk_window_list_toplevels` from CGo post-Run. Fragile (window may already be realized).
3. **GTK4 path** — wait for Wails v3 GTK4/WebKitGTK 6 support, use `pkgs.gtk4-layer-shell`.

### NixOS dev shell additions

```nix
buildInputs = with pkgs; [
  go gcc pkg-config gtk3 webkitgtk_4_1
  gtk-layer-shell           # GTK3 layer-shell library
  libsoup_3
];
```

## Approach 5 (fallback hack): Sway windowrules

```
# ~/.config/sway/config
for_window [app_id="wails-wallpaper"] floating enable
for_window [app_id="wails-wallpaper"] border none
for_window [app_id="wails-wallpaper"] move position 0 0
for_window [app_id="wails-wallpaper"] resize set 100 ppt 100 ppt
for_window [app_id="wails-wallpaper"] sticky enable
no_focus [app_id="wails-wallpaper"]
```

Caveat: window sits in regular layer — not a true wallpaper.

## Performance & power notes

- Hardware video decode is **mandatory** for video wallpapers on laptops. Software 1080p60 = 10-25W CPU draw.
- `mpvpaper -p` (pause-on-fullscreen) saves ~90% of GPU cycles when an app fullscreens.
- awww caches decoded frames in RAM after first loop (cheap GIFs) but a large 4K animation can hold ~1GB.
- linux-wallpaperengine bundles CEF (~150MB RSS) even for trivial scenes.

## Sources

- https://github.com/GhostNaN/mpvpaper
- https://github.com/LGFae/swww (archived) → https://codeberg.org/LGFae/awww
- https://github.com/NixOS/nixpkgs/pull/459649 (swww → awww rename)
- https://github.com/wmww/gtk-layer-shell
- https://github.com/diamondburned/gotk4-layer-shell
- https://github.com/Almamu/linux-wallpaperengine
- https://wayland.app/protocols/wlr-layer-shell-unstable-v1
- https://github.com/swaywm/swaybg
