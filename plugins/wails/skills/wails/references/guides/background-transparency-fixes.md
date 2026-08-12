---
last_updated: 2026-04-18
wails_version: v2.9+
source: https://github.com/wailsapp/wails (v2/internal/frontend/desktop/linux/window.go, window.c)
---

# Background Transparency: Fixes & Common Gotchas

## Achieving Visual Parity

### 1. Match backgrounds exactly
Set `BackgroundColour` RGB values to match your CSS `--background` variable exactly. This eliminates the color shift before the frontend paints.

### 2. Use full-viewport solid backgrounds
Don't rely on the webview's background color showing through. Cover the viewport with a CSS background (`fixed inset-0`) so the webview background is never visible during normal operation.

### 3. Test with the correct GPU policy
If your Wails app uses `WebviewGpuPolicyNever` (software rendering), test the browser version with software rendering too. In Chrome: `--disable-gpu`. In Firefox: set `layers.acceleration.disabled` to true.

### 4. Prefer CSS features supported since webkit2gtk 2.30+
- `backdrop-filter: blur()` -- works, but rendering quality may differ from Chromium
- `filter: blur()` with large radii (60px+) -- may look slightly different at edges
- `-webkit-` prefixed properties -- use unprefixed; webkit2gtk 2.30+ supports them

### 5. Check WebKit environment variables
These env vars change rendering behavior in Wails but not in browsers:
- `WEBKIT_DISABLE_DMABUF_RENDERER=1` -- disables DMA-BUF, may affect compositing quality
- `WEBKIT_DISABLE_COMPOSITING_MODE=1` -- disables accelerated compositing entirely

### 6. Handle software rendering gracefully

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

Use this to disable expensive effects when running in software mode.

## Common Gotchas

1. **"My transparent areas look wrong in Wails"** -- Your `BackgroundColour` alpha is 255 (opaque). Semi-transparent CSS composites against this color, not white. Either match the color to your theme or set `WindowIsTranslucent: true` to force alpha=0.

2. **"backdrop-filter works in Chrome but not Wails"** -- Check webkit2gtk version (must be >= 2.30.0). Also check if `WEBKIT_DISABLE_COMPOSITING_MODE` is set.

3. **"WebGL canvas is opaque in Wails"** -- Ensure `gl.alpha = true` and `style={{ background: "transparent" }}`. If using `WebviewGpuPolicy: Never`, WebGL alpha compositing should still work but through software paths.

4. **"Colors look slightly different"** -- WebKit and Blink have different color management pipelines. Avoid relying on color interpolation for brand-critical colors; use solid colors where precision matters.

5. **"WindowIsTranslucent doesn't work"** -- Requires a compositing window manager. On bare X11 without a compositor, the flag is silently ignored. On Wayland compositors (Sway, Hyprland), it works.

6. **"I set BackgroundColour with alpha=128 but it's fully opaque on Windows"** -- Windows WebView2 treats any non-zero alpha as 255. Use `WebviewIsTransparent: true` in `windows.Options` instead.
