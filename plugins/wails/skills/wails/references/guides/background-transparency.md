---
last_updated: 2026-04-18
wails_version: v2.9+
source: https://github.com/wailsapp/wails (v2/internal/frontend/desktop/linux/window.go, window.c)
---

# Background Transparency & Browser vs Wails Rendering

## Why Frontends Look Different in Wails vs a Browser

The same frontend code renders differently in a Wails webview compared to a regular browser (Chrome/Firefox) because of fundamental architectural differences in how the rendering stack is assembled.

### The Rendering Stack

**Browser (Chrome/Firefox via `bun dev` / mock adapter):**
```
Browser chrome → Tab → Blink/Gecko engine → HTML/CSS/WebGL
```
- The browser composites CSS against its own opaque page background (white by default, or your `body` background-color)
- GPU acceleration is typically on by default
- Uses Blink (Chromium) or Gecko (Firefox) rendering engine

**Wails on Linux (webkit2gtk):**
```
GTK Window → #webview-box container → webkit2gtk WebView → HTML/CSS/WebGL
```
- `BackgroundColour` calls `webkit_web_view_set_background_color()` AND applies CSS to `#webview-box`
- Semi-transparent CSS areas composite against `BackgroundColour`, not white
- Uses WebKit rendering engine with TextureMapper compositor
- GPU acceleration controlled by `WebviewGpuPolicy`

### Root Causes of Visual Differences

**1. Different base compositing color:**
Semi-transparent `rgba()` backgrounds, `opacity`, and `backdrop-filter` blend against the underlying color. In a browser, that's the page's white default. In Wails, it's whatever `BackgroundColour` is set to. If your app uses a dark theme with `bg-background` covering the viewport, this matters less -- but any gap where the base shows through will differ.

**2. Different rendering engine (WebKit vs Blink):**
webkit2gtk uses WebKit, not Chromium's Blink. Subtle differences in:
- Blur kernel implementation (`filter: blur()`, `backdrop-filter: blur()`)
- Subpixel rendering and antialiasing
- Font rendering (FreeType vs Skia)
- CSS animation compositing order
- WebGL alpha channel compositing path (TextureMapper vs Viz)

**3. GPU acceleration path:**
If `WebviewGpuPolicy` is `Never` (software rendering), all compositing is software-rendered. CSS blur filters, animations, and WebGL run through different code paths than GPU-accelerated browsers. Visual quality characteristics differ even when pixel output is "correct."

**4. WebKit compositor environment variables:**
If `WEBKIT_DISABLE_DMABUF_RENDERER=1` or `WEBKIT_DISABLE_COMPOSITING_MODE=1` are set (common NVIDIA/Wayland workarounds), the accelerated compositing pipeline is partially or fully disabled. `backdrop-filter` may render with reduced quality or be silently ignored.

**5. webkit2gtk version:**
CSS feature support varies by version:
- `backdrop-filter`: requires webkit2gtk >= 2.30.0 (may need `-webkit-` prefix on older versions)
- Nested `backdrop-filter` on child elements: works in WebKit, silently ignored in Chromium (known Chromium bug)

Check version: `pkg-config --modversion webkit2gtk-4.0` (or `webkit2gtk-4.1`)

## How BackgroundColour Works on Linux

Wails sets the webview background via two mechanisms (C code in `window.c`):

```c
// Layer 1: WebKit webview background (shows behind web content)
webkit_web_view_set_background_color(WEBKIT_WEB_VIEW(webview), &colour);

// Layer 2: GTK container CSS (prevents resize flicker)
gtk_css_provider_load_from_data(cssProvider,
    "#webview-box {background-color: rgba(R, G, B, A/255);}", ...);
```

**Key behaviors:**
- The webview background shows before the frontend loads and behind any transparent CSS areas
- When the page specifies its own CSS background, the page background takes precedence for those areas
- The GTK container CSS was added to prevent black flashing during window resizes (the GTK window and webview are separate layers)

### BackgroundColour Alpha Per Platform

| Platform | Alpha behavior | Semi-transparency |
|----------|---------------|-------------------|
| **Linux** (webkit2gtk) | Full 0-255 range, converted to 0.0-1.0 float for `GdkRGBA` | Yes, true semi-transparency supported |
| **Windows** (WebView2) | Binary: any non-zero alpha → fully opaque (255) | No, only 0 or 255 |
| **macOS** (WKWebView) | Full 0-255 range | Yes, uses `WebviewIsTransparent` for full transparency |

### Matching BackgroundColour to CSS theme

To avoid a visible color shift before the frontend loads, always match `BackgroundColour` to the CSS `background-color` of your root element:

```go
// Go: match your CSS --background variable
BackgroundColour: &options.RGBA{R: 7, G: 0, B: 18, A: 255}, // #070012
```

```css
/* CSS: same color */
:root { --background: #070012; }
body { background-color: var(--background); }
```

## Linux Transparency Options

### WindowIsTranslucent (linux.Options)

Makes the entire window transparent. Available on Linux despite being absent from `options.App` top-level fields:

```go
Linux: &linux.Options{
    WindowIsTranslucent: true,
},
```

**How it works internally:**
1. Checks for an RGBA visual (`gdk_screen_get_rgba_visual`)
2. Checks compositor is active (`gdk_screen_is_composited`)
3. Sets `gtk_widget_set_app_paintable(true)` + RGBA visual
4. Forces `BackgroundColour` alpha to 0.0 regardless of what you pass

**Requirements:**
- A compositing window manager (Sway, Hyprland, KWin, Mutter, Picom, etc.)
- Without compositing, the flag is silently ignored and the window is opaque

**Effect:** CSS `transparent` or `rgba(0,0,0,0)` areas will show through to the desktop. The RGB values in `BackgroundColour` become irrelevant.

### Platform-Specific Transparency Comparison

| Option | Windows | macOS | Linux |
|--------|---------|-------|-------|
| `WebviewIsTransparent` | `windows.Options` | `mac.Options` | **Not available** |
| `WindowIsTranslucent` | `windows.Options` (acrylic) | N/A | `linux.Options` |
| Effect | Webview bg transparent | Webview bg transparent | Window bg transparent (forces alpha=0) |

Linux lacks `WebviewIsTransparent` as a separate option -- `WindowIsTranslucent` serves both purposes by making the window and webview backgrounds transparent together.

## WebGL Canvas Transparency

When using a WebGL/Three.js canvas with `alpha: true` overlaid on HTML:

```tsx
<Canvas
  gl={{ alpha: true, ... }}
  style={{ background: "transparent" }}
>
```

The canvas composites over the HTML behind it using pre-multiplied alpha. This should work identically in both webkit2gtk and Chromium per the WebGL spec, but:

- webkit2gtk composites through TextureMapper → GTK window background
- Chromium composites through Viz → browser tab background
- If the canvas has a z-index conflict with other fixed-position elements, DOM order determines paint order (later = on top) and each engine may resolve edge cases differently

**Best practice:** Ensure the solid-color background element (e.g., grid animation) is in DOM before the transparent canvas, both with the same z-index, so later-DOM-order compositing is consistent.

## Achieving Visual Parity

### 1. Match backgrounds exactly
Set `BackgroundColour` RGB values to match your CSS `--background` variable exactly. This eliminates the color shift before the frontend paints.

### 2. Use full-viewport solid backgrounds
Don't rely on the webview's background color showing through. Cover the viewport with a CSS background (`fixed inset-0`) so the webview background is never visible during normal operation.

### 3. Test with the correct GPU policy
If your Wails app uses `WebviewGpuPolicyNever` (software rendering), test the browser version with software rendering too. In Chrome: `--disable-gpu`. In Firefox: set `layers.acceleration.disabled` to true.

### 4. Prefer CSS features supported since webkit2gtk 2.30+
All modern CSS features work, but some edge-case rendering differs:
- `backdrop-filter: blur()` -- works, but rendering quality may differ from Chromium
- `filter: blur()` with large radii (60px+) -- may look slightly different at edges
- `-webkit-` prefixed properties -- use unprefixed; webkit2gtk 2.30+ supports them

### 5. Check WebKit environment variables
These env vars change rendering behavior in Wails but not in browsers:
- `WEBKIT_DISABLE_DMABUF_RENDERER=1` -- disables DMA-BUF, may affect compositing quality
- `WEBKIT_DISABLE_COMPOSITING_MODE=1` -- disables accelerated compositing entirely

### 6. Handle software rendering gracefully
Detect software rendering in the frontend and simplify visual effects:

```typescript
function isSoftwareRenderer(): boolean {
  const canvas = document.createElement("canvas")
  const gl = canvas.getContext("webgl2") || canvas.getContext("webgl")
  if (!gl) return true
  const ext = gl.getExtension("WEBGL_debug_renderer_info")
  if (!ext) return false
  const renderer = (gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) as string).toLowerCase()
  return /llvmpipe|softpipe|swiftshader|software|lavapipe|mesa offscreen/.test(renderer)
}
```

Use this to disable expensive effects (WebGL 3D scenes, large blur filters) when running in software mode.

## Common Gotchas

1. **"My transparent areas look wrong in Wails"** -- Your `BackgroundColour` alpha is 255 (opaque). Semi-transparent CSS composites against this color, not white. Either match the color to your theme or set `WindowIsTranslucent: true` to force alpha=0.

2. **"backdrop-filter works in Chrome but not Wails"** -- Check webkit2gtk version (must be >= 2.30.0). Also check if `WEBKIT_DISABLE_COMPOSITING_MODE` is set.

3. **"WebGL canvas is opaque in Wails"** -- Ensure `gl.alpha = true` and `style={{ background: "transparent" }}`. If using `WebviewGpuPolicy: Never`, WebGL alpha compositing should still work but through software paths.

4. **"Colors look slightly different"** -- WebKit and Blink have different color management pipelines. For exact matches, avoid relying on color interpolation (gradients, blend modes) for brand-critical colors; use solid colors where precision matters.

5. **"WindowIsTranslucent doesn't work"** -- Requires a compositing window manager. On bare X11 without a compositor, the flag is silently ignored. On Wayland compositors (Sway, Hyprland), it works.

6. **"I set BackgroundColour with alpha=128 but it's fully opaque on Windows"** -- Windows WebView2 treats any non-zero alpha as 255. Use `WebviewIsTransparent: true` in `windows.Options` instead.
