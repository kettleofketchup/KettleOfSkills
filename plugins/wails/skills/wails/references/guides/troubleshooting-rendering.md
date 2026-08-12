---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Troubleshooting: Rendering & Dev Mode

## Transparency & Rendering Issues

**Symptom:** Frontend looks different in Wails than in browser.

**Root cause:** Wails uses webkit2gtk (WebKit engine), not Chromium. Different compositing, font rendering, blur implementations.

**Fixes:**

1. **Match `BackgroundColour` to CSS theme:**
   ```go
   BackgroundColour: &options.RGBA{R: 7, G: 0, B: 18, A: 255}, // must match CSS --background
   ```

2. **Cover the viewport with a solid CSS background** -- don't rely on the webview background. Use `fixed inset-0` with your theme color.

3. **Check GPU policy** -- software rendering (`WebviewGpuPolicyNever`) changes blur filter and animation quality. Ensure `Linux: &linux.Options{}` is set (even empty) to avoid the `Never` default.

4. **Check webkit2gtk version** -- `backdrop-filter` requires >= 2.30.0:
   ```bash
   pkg-config --modversion webkit2gtk-4.0  # or webkit2gtk-4.1
   ```

5. **Check WebKit env vars** -- `WEBKIT_DISABLE_COMPOSITING_MODE=1` disables accelerated compositing, changing backdrop-filter behavior.

See [Background Transparency guide](background-transparency.md) for detailed analysis.

**Symptom:** `WindowIsTranslucent` doesn't work (window is still opaque).

**Fix:** Requires a compositing window manager. On bare X11 without a compositor, the flag is silently ignored. On Wayland compositors (Sway, Hyprland), it should work.

**Symptom:** Resize causes black/white flashing behind webview.

**Cause:** GTK window background doesn't match webview background. Fixed in Wails by PR #2853 which applies `BackgroundColour` to both the webview and the `#webview-box` GTK container. Ensure you're on Wails >= v2.6.

## NSIS Not Found (Windows Installer)

```bash
choco install nsis
# or
winget install NSIS.NSIS

# Verify
makensis -VERSION
```

## Dev Mode Issues

**Hot reload not working:**
- Check `frontend:dev:watcher` in `wails.json` runs framework dev server
- Ensure `frontend:dev:serverUrl` is `"auto"` or correct URL
- Verify Vite/webpack HMR websocket not blocked

**Go changes not rebuilding:**
- `wails dev` watches `.go` files. Ensure you're saving files
- Check `-reloaddirs` flag if Go code is outside root

```bash
wails dev -reloaddirs "./pkg,./internal"
```

**Slow dev startup:**
- Frontend install runs every time. Use `frontend:dev:install` to customize or set to empty string to skip
