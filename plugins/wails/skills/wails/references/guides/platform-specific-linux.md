---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Platform-Specific: Linux & Cross-Platform

## Linux

### Dependencies

Required system packages:

```bash
# Debian/Ubuntu
sudo apt install libgtk-3-dev libwebkit2gtk-4.0-dev

# Fedora
sudo dnf install gtk3-devel webkit2gtk4.0-devel

# Arch
sudo pacman -S gtk3 webkit2gtk-4.1
```

### webkit2gtk Version

Default: webkit2gtk-4.0. For newer distros shipping only 4.1 (e.g., Arch, Fedora 38+):

```bash
wails build -tags webkit2_41
wails dev -tags webkit2_41
```

Or set in `wails.json`:

```json
{
  "wailsjsdir": "./frontend",
  "tags": "webkit2_41"
}
```

### Window Transparency

Linux uses `WindowIsTranslucent` (not `WebviewIsTransparent` which is Mac/Windows-only):

```go
Linux: &linux.Options{
    WindowIsTranslucent: true,  // requires compositing WM
},
```

When enabled, Wails calls `gtk_widget_set_app_paintable(true)` with an RGBA visual, and forces `BackgroundColour` alpha to 0.0. CSS `transparent` areas show through to the desktop. Requires a compositing WM (Sway, Hyprland, KWin, Mutter, Picom); silently ignored without one.

### GPU Policy

Controls webkit2gtk hardware acceleration. Critical for NVIDIA/Wayland stability:

```go
Linux: &linux.Options{
    WebviewGpuPolicy: linux.WebviewGpuPolicyAlways,  // GPU accel (default when Linux opts set)
    // WebviewGpuPolicyOnDemand  // let WebKit decide
    // WebviewGpuPolicyNever     // software rendering (safest for NVIDIA/Wayland)
},
```

When `options.Linux` is nil, Wails defaults to `WebviewGpuPolicyNever` as a safety measure (issue #2977). Setting GPU policy explicitly requires setting `Linux: &linux.Options{...}` -- even an empty struct changes the default from Never to Always.

### BackgroundColour on Linux

`BackgroundColour` sets both the webkit2gtk webview background and the GTK container widget CSS. Match it to your CSS theme's `--background` color:

```go
BackgroundColour: &options.RGBA{R: 7, G: 0, B: 18, A: 255}, // match CSS --background: #070012
```

Linux supports full 0-255 alpha range (unlike Windows which only supports 0 or 255).

See [Background Transparency guide](background-transparency.md) for detailed guidance on visual parity.

### Distribution Support

Supported: Ubuntu 20.04+, Fedora 36+, Arch, openSUSE, Debian 11+. Requires X11 or Wayland with XWayland.

## Cross-Platform Builds

```bash
# Windows targets
wails build -platform windows/amd64
wails build -platform windows/arm64

# macOS targets (requires macOS host for CGo)
wails build -platform darwin/amd64
wails build -platform darwin/arm64
wails build -platform darwin/universal   # fat binary

# Linux targets
wails build -platform linux/amd64
wails build -platform linux/arm64
```

**Limitations:**
- macOS builds require macOS host (CGo dependency)
- Windows cross-compile from Linux possible with `x86_64-w64-mingw32-gcc`
- Universal macOS binary combines amd64 + arm64 into single file
