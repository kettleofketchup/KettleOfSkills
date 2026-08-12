---
last_updated: 2026-04-18
wails_version: v2.9+
source: https://github.com/wailsapp/wails (v2/internal/frontend/desktop/linux/window.go, window.c)
---

# Background Transparency & Browser vs Wails Rendering

## Why Frontends Look Different in Wails vs a Browser

The same frontend code renders differently in a Wails webview compared to a regular browser because of fundamental architectural differences in how the rendering stack is assembled.

### The Rendering Stack

**Browser (Chrome/Firefox via `bun dev` / mock adapter):**
- The browser composites CSS against its own opaque page background (white by default)
- GPU acceleration typically on by default; uses Blink (Chromium) or Gecko (Firefox)

**Wails on Linux (webkit2gtk):**
- `BackgroundColour` calls `webkit_web_view_set_background_color()` AND applies CSS to `#webview-box`
- Semi-transparent CSS areas composite against `BackgroundColour`, not white
- Uses WebKit rendering engine with TextureMapper compositor
- GPU acceleration controlled by `WebviewGpuPolicy`

### Root Causes of Visual Differences

1. **Different base compositing color:** Semi-transparent `rgba()` backgrounds blend against `BackgroundColour`. In a browser, that's page white.
2. **Different rendering engine (WebKit vs Blink):** Subtle differences in blur kernels, subpixel rendering, font rendering (FreeType vs Skia), WebGL alpha compositing.
3. **GPU acceleration path:** `WebviewGpuPolicyNever` (software rendering) changes CSS blur, animations, WebGL.
4. **WebKit compositor env vars:** `WEBKIT_DISABLE_DMABUF_RENDERER=1` or `WEBKIT_DISABLE_COMPOSITING_MODE=1` disable accelerated compositing.
5. **webkit2gtk version:** `backdrop-filter` requires >= 2.30.0 (may need `-webkit-` prefix on older).

## How BackgroundColour Works on Linux

Wails sets the webview background via two mechanisms:

- `webkit_web_view_set_background_color()` - webview background (shows before frontend loads)
- GTK container CSS on `#webview-box` - prevents resize flicker

**Alpha behavior per platform:**

| Platform | Alpha behavior | Semi-transparency |
|----------|---------------|-------------------|
| **Linux** (webkit2gtk) | Full 0-255 range | Yes, true semi-transparency supported |
| **Windows** (WebView2) | Binary: any non-zero alpha = 255 | No, only 0 or 255 |
| **macOS** (WKWebView) | Full 0-255 range | Yes, uses `WebviewIsTransparent` |

Match `BackgroundColour` to your CSS `--background` variable to avoid flash before frontend loads:

```go
BackgroundColour: &options.RGBA{R: 7, G: 0, B: 18, A: 255}, // #070012
```

## Linux Transparency Options

### WindowIsTranslucent

Makes the entire window transparent on Linux:

```go
Linux: &linux.Options{
    WindowIsTranslucent: true,
},
```

Requires a compositing WM (Sway, Hyprland, KWin, Mutter, Picom). Forces `BackgroundColour` alpha to 0.0. Silently ignored without compositor.

### Platform Comparison

| Option | Windows | macOS | Linux |
|--------|---------|-------|-------|
| `WebviewIsTransparent` | `windows.Options` | `mac.Options` | Not available |
| `WindowIsTranslucent` | `windows.Options` (acrylic) | N/A | `linux.Options` |

Linux lacks `WebviewIsTransparent` — `WindowIsTranslucent` serves both purposes.

## WebGL Canvas Transparency

When using a WebGL/Three.js canvas with `alpha: true` overlaid on HTML, webkit2gtk composites through TextureMapper vs Chromium's Viz compositor. Ensure the solid-color background element is in DOM before the transparent canvas for consistent paint order.

See [Background Transparency: Fixes & Common Gotchas](background-transparency-fixes.md) for achieving visual parity and debugging issues.
