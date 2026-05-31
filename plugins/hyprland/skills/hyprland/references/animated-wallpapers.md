# Animated Wallpapers on Hyprland

Three approaches: standalone tools (mpvpaper/awww), a Wails app controlling them, or a Wails app patched to be a layer-shell window itself.

## NixOS package survey (verified against nixpkgs 2026-04)

| Tool | Renders | NixOS attr | Notes |
|------|---------|------------|-------|
| `hyprpaper` | Static images only | `pkgs.hyprpaper` | Baseline; no animation support |
| `swaybg` | Static images only | `pkgs.swaybg` | Static only |
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

For a wallpaper: `layer = background`, `exclusive_zone = 0`, anchor to all four edges (`top|bottom|left|right`), `keyboard_interactivity = none`. swaybg/hyprpaper/mpvpaper/awww all use this exact configuration.

## Approach 1 (recommended): mpvpaper + Wails controller

The simplest path. Wails app shells out to `mpvpaper`, controls playback via mpv's JSON IPC socket.

### Hyprland config

```ini
# hyprland.conf
exec-once = mpvpaper -p -o "no-audio --loop-playlist --panscan=1.0 hwdec=auto-safe input-ipc-server=/tmp/mpv-socket" ALL ~/wallpapers/space.mp4
```

Flags:
- `-p` = pause-on-fullscreen (saves battery/GPU when any window goes fullscreen)
- `ALL` = render on every connected output
- `hwdec=auto-safe` = hardware video decode (vaapi for Intel/AMD, nvdec for NVIDIA)
- `input-ipc-server=/tmp/mpv-socket` = control socket for the Wails app

### Wails Go controller

```go
package main

import (
    "encoding/json"
    "net"
    "os/exec"
)

// Launch wallpaper
func StartWallpaper(videoPath string) error {
    cmd := exec.Command("mpvpaper", "-p",
        "-o", "no-audio --loop-playlist --panscan=1.0 hwdec=auto-safe input-ipc-server=/tmp/mpv-socket",
        "ALL", videoPath)
    return cmd.Start()
}

// Send IPC command via Unix socket
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

The Wails frontend (Svelte/React) provides the wallpaper library UI. Bind these methods via the standard Wails `Bind` mechanism.

## Approach 2 (recommended for animated images): awww

```bash
swww-daemon &              # legacy alias still works
awww-daemon &              # new binary name
swww img ~/wp/animated.gif --transition-type wipe --transition-duration 1
swww img --outputs eDP-1 ~/laptop-wp.webp
swww query                  # current wallpaper info
swww kill                   # stop daemon
```

Hyprland integration:
```ini
exec-once = swww-daemon
exec-once = sleep 1 && swww img ~/wallpapers/animated.gif --transition-type center --transition-fps 60
```

Caches decoded animation frames in RAM after first loop — much cheaper than equivalent video, but a 60-frame 4K GIF can hold ~1GB of decoded frames.

## Approach 3 (advanced): Wails-as-wallpaper via gtk-layer-shell

The Go binding `github.com/diamondburned/gotk4-layer-shell` (despite the "gtk4" in the package name, it binds GTK3's gtk-layer-shell library). MPL-2.0, last published 2024.

```go
import gls "github.com/diamondburned/gotk4-layer-shell/pkg/gtklayershell"

// Must be called BEFORE the GtkWindow is realized
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

1. **Fork-and-patch Wails** — add a CGo hook in `window.go` between `gtk_application_window_new` and `gtk_widget_show_all` calling the gtk-layer-shell C functions directly. Vendor via `replace` in `go.mod`. This is the cleanest path because the timing requirement (init must precede realize) lines up with where Wails creates the window.
2. **Walk active GTK windows** — after `wails.Run`, call `gtk_window_list_toplevels` from CGo and match by namespace, then `gls.InitForWindow`. Fragile because the window may already be realized.
3. **GTK4 path** — wait for Wails v3 GTK4/WebKitGTK 6 support, then use `pkgs.gtk4-layer-shell` (1.3.0, actively developed).

### NixOS dev shell additions

```nix
buildInputs = with pkgs; [
  go gcc pkg-config
  gtk3 webkitgtk_4_1
  gtk-layer-shell           # GTK3 layer-shell library
  libsoup_3
];
```

**Status**: There is no public prior art for a Wails-as-wallpaper app. Closed Wails issue #3668 ("How to make wails App display between the wallpaper and the desktop?") exists but its accepted answer points to a different approach (controller pattern, not layer-shell).

## Approach 4 (fallback hack): Hyprland windowrulev2

If gtk-layer-shell patching is too much, a `windowrulev2` stack approximates wallpaper behavior:

```ini
windowrulev2 = float, class:^(wails-wallpaper)$
windowrulev2 = pin, class:^(wails-wallpaper)$
windowrulev2 = noborder, class:^(wails-wallpaper)$
windowrulev2 = noshadow, class:^(wails-wallpaper)$
windowrulev2 = noblur, class:^(wails-wallpaper)$
windowrulev2 = nofocus, class:^(wails-wallpaper)$
windowrulev2 = move 0 0, class:^(wails-wallpaper)$
windowrulev2 = size 100% 100%, class:^(wails-wallpaper)$
```

**Caveat**: the window sits in the regular layer — visually wallpaper-like but other floats may render below it depending on stacking. Not a true layer-shell solution.

## Performance & power notes

- Hardware video decode is **mandatory** for video wallpapers on laptops. Software 1080p60 = 10-25W CPU draw, ~2hr battery life.
- `mpvpaper -p` (pause-on-fullscreen) is essential — saves ~90% of GPU cycles when an app goes fullscreen.
- awww caches decoded frames in RAM after first loop (cheap GIFs) but a large 4K animation can hold ~1GB.
- linux-wallpaperengine bundles CEF (~150MB RSS) even for trivial scenes.
- Hyprland `misc:vfr = true` doesn't help during active wallpaper playback because mpvpaper posts new frames every video frame.

## Sources

- https://github.com/GhostNaN/mpvpaper
- https://github.com/LGFae/swww (archived) → https://codeberg.org/LGFae/awww
- https://github.com/NixOS/nixpkgs/pull/459649 (swww → awww rename)
- https://github.com/wmww/gtk-layer-shell
- https://github.com/diamondburned/gotk4-layer-shell
- https://github.com/Almamu/linux-wallpaperengine
- https://wayland.app/protocols/wlr-layer-shell-unstable-v1
- https://github.com/wailsapp/wails/issues/3668
