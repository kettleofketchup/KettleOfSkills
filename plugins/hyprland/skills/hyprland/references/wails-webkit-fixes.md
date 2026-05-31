# Wails / webkit2gtk Fixes for Hyprland

Wails apps (Go + GTK3 + webkit2gtk) commonly show a **blank window** under Hyprland on integrated graphics. Two known regressions in webkit2gtk 2.42+:
1. DMA-BUF renderer blank screen on most Wayland compositor + iGPU combos
2. GPU compositing crash on the XWayland-fallback path

Both fix via env vars.

## The full env var set

```nix
environment.sessionVariables = {
  # PRIMARY FIX: disable WebKit's DMA-BUF renderer
  WEBKIT_DISABLE_DMABUF_RENDERER = "1";

  # SECONDARY FIX: disable GPU compositing in WebKit (covers XWayland fallback)
  WEBKIT_DISABLE_COMPOSITING_MODE = "1";

  # GDK: prefer Wayland, fall back to X11 (XWayland)
  GDK_BACKEND = "wayland,x11";

  # Qt deps Wails sometimes pulls
  QT_QPA_PLATFORM = "wayland;xcb";
  QT_WAYLAND_DISABLE_WINDOWDECORATION = "1";

  # Electron / Chromium → Wayland (for any bundled subprocesses)
  NIXOS_OZONE_WL = "1";

  # Java GUI under tiling WMs
  _JAVA_AWT_WM_NONREPARENTING = "1";

  XDG_CURRENT_DESKTOP = "Hyprland";
  XDG_SESSION_TYPE    = "wayland";
  XDG_SESSION_DESKTOP = "Hyprland";
};
```

## Setting in hyprland.conf instead

```
env = WEBKIT_DISABLE_DMABUF_RENDERER,1
env = WEBKIT_DISABLE_COMPOSITING_MODE,1
env = GDK_BACKEND,wayland,x11
env = NIXOS_OZONE_WL,1
env = QT_QPA_PLATFORM,wayland;xcb
```

## Setting per-app from inside Wails Go code

```go
package main

import (
    "os"
    "runtime"
)

func init() {
    if runtime.GOOS == "linux" {
        os.Setenv("WEBKIT_DISABLE_DMABUF_RENDERER", "1")
        os.Setenv("WEBKIT_DISABLE_COMPOSITING_MODE", "1")
    }
}
```

Set these in `init()` BEFORE `wails.Run` — webkit2gtk reads them at startup.

## Last-resort CPU rendering fallback

If the window still won't paint after env vars are set:

```nix
environment.sessionVariables = {
  LIBGL_ALWAYS_SOFTWARE = "1";
  WEBKIT_FORCE_SANDBOX  = "0";  # some webkit2gtk builds need sandbox off w/ software GL
};
```

Slow but always works. Use this for CI/headless environments or known-broken iGPUs.

## webkit2gtk 4.1 build tag

NixOS ships `webkitgtk_4_1` (not 4.0). Wails needs the matching build tag:

```bash
wails build -tags webkit2_41
wails dev   -tags webkit2_41
```

Or persist in `wails.json`:
```json
{ "tags": "webkit2_41" }
```

Without this tag, builds fail with `Package webkit2gtk-4.0 was not found`.

## Required build inputs (for `nix-shell` / devShell)

```nix
pkgs.mkShell {
  buildInputs = with pkgs; [
    go gcc pkg-config gtk3 webkitgtk_4_1 nodejs
  ];
  shellHook = ''
    export WEBKIT_DISABLE_DMABUF_RENDERER=1
    export WEBKIT_DISABLE_COMPOSITING_MODE=1
    export GDK_BACKEND=wayland,x11
    export CGO_ENABLED=1
    export PKG_CONFIG_PATH="${pkgs.webkitgtk_4_1.dev}/lib/pkgconfig:${pkgs.gtk3.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
  '';
}
```

## Debugging a blank window

```bash
# 1. Confirm env vars actually inherited by the process
cat /proc/$(pidof yourapp)/environ | tr '\0' '\n' | grep -i webkit

# 2. Check renderer errors in journal
journalctl --user -b | grep -i webkit

# 3. Try forcing X11 per-app (NOT session-wide)
GDK_BACKEND=x11 wails dev -tags webkit2_41

# 4. Try CPU rendering
LIBGL_ALWAYS_SOFTWARE=1 wails dev -tags webkit2_41

# 5. Verify webkit2gtk version present
pkg-config --modversion webkit2gtk-4.1
```

## Issue tracker references

- wailsapp/wails#2977 — primary "Blank window" tracking issue
- wailsapp/wails#4174 — Wayland blank screen confirmation
- wailsapp/wails#3345 — WebKit2-GTK 4.1 support discussion (`-tags webkit2_41`)
- hyprwm/Hyprland#1352 — `legacyRenderer posts blank screen`
- tauri-apps/tauri#9394 — sibling framework, same root cause

The combination `WEBKIT_DISABLE_DMABUF_RENDERER=1` + `WEBKIT_DISABLE_COMPOSITING_MODE=1` is the safe default for any Wails-on-Wayland deployment.
