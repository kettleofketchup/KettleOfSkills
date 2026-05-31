# Wails / webkit2gtk Fixes for Sway

Wails apps (Go + GTK3 + webkit2gtk) commonly show a **blank window** under Sway on integrated graphics. Root cause: WebKitGTK 2.42+ enabled the **DMA-BUF renderer** by default, which is unstable on:

- NVIDIA proprietary drivers (white screen, EGL DMABuf failures)
- Intel iGPUs running outside a logged-in seat (`KMS: DRM_IOCTL_MODE_CREATE_DUMB failed: Permission denied`)
- Some Wayland compositors with limited dmabuf support
- Sandboxed/flatpak/containerized contexts

## Confirmed errors (wailsapp/wails#2977)

```
KMS: DRM_IOCTL_MODE_CREATE_DUMB failed: Permission denied
Failed to create GBM buffer ... Permission denied
Failed to create EGL images for DMABufs with file descriptors -1, -1 and -1
```

## The full env var set

Apply via `programs.sway.extraSessionCommands` (preferred — runs in the Sway wrapper) OR `environment.sessionVariables`:

```nix
extraSessionCommands = ''
  # Primary fix: disable WebKit's DMA-BUF renderer
  export WEBKIT_DISABLE_DMABUF_RENDERER=1
  # Secondary fix if still blank
  export WEBKIT_DISABLE_COMPOSITING_MODE=1

  # GDK fallback chain (try wayland, then x11)
  export GDK_BACKEND="wayland,x11"

  # Qt
  export QT_QPA_PLATFORM=wayland-egl
  export QT_WAYLAND_DISABLE_WINDOWDECORATION=1

  # Mozilla / Chromium / Electron
  export MOZ_ENABLE_WAYLAND=1
  export NIXOS_OZONE_WL=1

  # Java AWT (Android Studio etc.)
  export _JAVA_AWT_WM_NONREPARENTING=1

  export XDG_CURRENT_DESKTOP=sway
  export XDG_SESSION_TYPE=wayland
  export SDL_VIDEODRIVER=wayland
'';
```

## Setting per-app from inside Wails Go code

Set in `init()` BEFORE `wails.Run` — webkit2gtk reads them at startup:

```go
func init() {
    if runtime.GOOS == "linux" {
        os.Setenv("WEBKIT_DISABLE_DMABUF_RENDERER", "1")
        os.Setenv("WEBKIT_DISABLE_COMPOSITING_MODE", "1")
    }
}
```

## Wails-side GPU policy (already default-off on Linux)

Wails v2 PR #3027 already defaults `WebviewGpuPolicy = Never` on Linux when `options.Linux` is `nil`. To override:

```go
import "github.com/wailsapp/wails/v2/pkg/options/linux"

err := wails.Run(&options.App{
    Linux: &linux.Options{
        WebviewGpuPolicy: linux.WebviewGpuPolicyAlways,    // re-enable GPU
        // or: linux.WebviewGpuPolicyOnDemand
        // or: linux.WebviewGpuPolicyNever (default)
        ProgramName: "myapp",
    },
})
```

The env vars remain useful even with `Never` because the dmabuf path is sometimes still reached via XWayland.

## Last-resort CPU rendering fallback

```nix
environment.sessionVariables = {
  LIBGL_ALWAYS_SOFTWARE = "1";
  WLR_RENDERER          = "pixman";    # wlroots CPU compositor
  GDK_DEBUG             = "gl-disable";
  WEBKIT_FORCE_SANDBOX  = "0";          # some webkit2gtk builds need sandbox off w/ software GL
};
```

Slow but always works. Use for CI/headless or known-broken iGPUs.

## libsoup2 vs libsoup3 / webkit2gtk-4.0 vs 4.1

- `webkit2gtk-4.0` uses **libsoup 2.4** (deprecated)
- `webkit2gtk-4.1` uses **libsoup 3** (current)
- The two libsoup versions **cannot coexist** in the same process — runtime error: `Using libsoup2 and libsoup3 in the same process is not supported`.
- **NixOS only ships `webkitgtk_4_1`** (the unified package), not `webkit2gtk-4.0`. **You must build Wails with `webkit2_41`:**

```bash
wails build -tags webkit2_41
wails dev   -tags webkit2_41
```

Or pin in `wails.json`:
```json
{ "tags": "webkit2_41" }
```

Without the tag, builds fail with `Package webkit2gtk-4.0 was not found`.

## Wails dev shell

See `references/flake-example.md` for the complete `devShells.default` block. Key inputs: `go nodejs_20 pkg-config wails gtk3 webkitgtk_4_1 libsoup_3`. Set `WEBKIT_DISABLE_DMABUF_RENDERER=1` in `shellHook`.

## Debugging a blank window

```bash
# 1. Confirm env vars actually inherited
cat /proc/$(pidof yourapp)/environ | tr '\0' '\n' | grep -i webkit

# 2. Check renderer errors
journalctl --user -b | grep -i webkit

# 3. Force X11 per-app (NOT session-wide)
GDK_BACKEND=x11 wails dev -tags webkit2_41

# 4. Try CPU rendering
LIBGL_ALWAYS_SOFTWARE=1 wails dev -tags webkit2_41

# 5. Verify webkit2gtk version
pkg-config --modversion webkit2gtk-4.1
```

## Issue tracker references

- wailsapp/wails#2977 — primary "Blank window" tracking issue + DMA-BUF errors
- wailsapp/wails#4174 — Wayland blank screen confirmation
- wailsapp/wails#3345 — WebKit2-GTK 4.1 support discussion
- wailsapp/wails#3027 — PR defaulting GPU policy to Never on Linux
- wailsapp/wails#3465 — `webkit2_41` build tag PR
- wailsapp/wails#1420 — Wayland support tracking
- wailsapp/wails#1156 — Discussion: building v2 apps on NixOS
- WebKit Bug 228268 — DMA-BUF / NVIDIA
- WebKit Bug 261874 — DMA-BUF rendering
