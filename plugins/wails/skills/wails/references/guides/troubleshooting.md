---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Troubleshooting

## wails doctor

First diagnostic step. Checks all dependencies and reports issues:

```bash
wails doctor
```

Output includes: Go version, Wails version, platform info, WebView2/webkit2gtk status, npm/node versions, build tools (gcc/pkg-config). Fix anything marked with `[x]` or `[!]`.

## WebView2 Missing (Windows)

**Symptom:** App crashes on launch or shows "WebView2 Runtime not found" error.

**Fix:**
- Install Edge WebView2 Runtime from https://developer.microsoft.com/en-us/microsoft-edge/webview2/
- Or embed runtime in build: `wails build -webview2 embed`
- Or auto-download at launch: `wails build -webview2 download` (default)
- Windows 11 always has WebView2. Problem mostly affects Windows 10 LTSC/Server.

## webkit2gtk Not Found (Linux)

**Fix for webkit2gtk-4.0 distros (Ubuntu, Debian):**

```bash
sudo apt install libwebkit2gtk-4.0-dev libgtk-3-dev
```

**Fix for webkit2gtk-4.1 distros (Arch, Fedora 38+):**

```bash
# Arch
sudo pacman -S webkit2gtk-4.1 gtk3
# Fedora
sudo dnf install webkit2gtk4.1-devel gtk3-devel
```

Then build with tag: `wails build -tags webkit2_41` or set `{ "tags": "webkit2_41" }` in `wails.json`.

## Blank Screen

**Common causes:**

1. **Frontend not built** - run `wails dev` not just `go run .`
2. **Wrong embed path** - verify `//go:embed all:frontend/dist` matches actual build output dir
3. **Frontend build error** - check `frontend/` builds independently: `cd frontend && npm run build`
4. **Port conflict in dev mode** - Vite dev server port already in use

Debug: `wails dev -devtools` or:

```go
Debug: options.Debug{
    OpenInspectorOnStartup: true,
},
```

5. **GPU issues on Windows** - try disabling GPU acceleration:

```go
Windows: &windows.Options{
    WebviewGpuIsDisabled: true,
},
```

## Asset Loading Failures

1. **Missing `all:` prefix in embed directive:**
   ```go
   //go:embed all:frontend/dist    // correct - includes dotfiles
   ```

2. **Base path mismatch** - Vite/webpack must use relative or `/` base path:
   ```js
   export default { base: './' }   // vite.config.js
   ```

3. **Custom handler swallowing requests** - ensure handler returns 404 for unmatched paths.

## Build Errors

### CGo Compiler Not Found

Install gcc: `sudo apt install build-essential` (Linux), Xcode CLI tools (macOS), MinGW-w64 (Windows).

### Missing pkg-config

```bash
sudo apt install pkg-config    # Ubuntu/Debian
brew install pkg-config        # macOS
sudo dnf install pkgconf-pkg-config  # Fedora
```

### Go Module Errors

```bash
go clean -modcache && go mod tidy
```

### Frontend Build Failures

```bash
rm -rf frontend/node_modules frontend/package-lock.json
cd frontend && npm install
```

See [Troubleshooting: Rendering & Dev Mode](troubleshooting-rendering.md) for transparency issues and hot-reload problems.
