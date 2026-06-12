# Animated Wallpapers (Advanced) — Wails Layer-Shell & Fallbacks

Advanced approaches continued from `animated-wallpapers.md`.

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
- https://github.com/LGFae/swww (archived) — https://codeberg.org/LGFae/awww
- https://github.com/NixOS/nixpkgs/pull/459649 (swww to awww rename)
- https://github.com/wmww/gtk-layer-shell
- https://github.com/diamondburned/gotk4-layer-shell
- https://github.com/Almamu/linux-wallpaperengine
- https://wayland.app/protocols/wlr-layer-shell-unstable-v1
- https://github.com/swaywm/swaybg
