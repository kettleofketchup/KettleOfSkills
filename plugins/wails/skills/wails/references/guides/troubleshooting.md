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

Check installed version:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -Name pv
```

## webkit2gtk Not Found (Linux)

**Symptom:** Build fails with `Package webkit2gtk-4.0 was not found` or similar.

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

Then build with tag:

```bash
wails build -tags webkit2_41
wails dev -tags webkit2_41
```

Or set permanently in `wails.json`:

```json
{ "tags": "webkit2_41" }
```

## Blank Screen

**Symptom:** App window opens but shows white/blank screen.

**Common causes:**

1. **Frontend not built** - run `wails dev` not just `go run .`
2. **Wrong embed path** - verify `//go:embed all:frontend/dist` matches actual build output dir
3. **Frontend build error** - check `frontend/` builds independently: `cd frontend && npm run build`
4. **Asset path mismatch** - ensure `wails.json` `frontend:build` command produces files in embedded dir
5. **Port conflict in dev mode** - Vite dev server port already in use. Kill other processes or change port

Debug: open DevTools with `wails dev -devtools` or set `Debug` option:

```go
Debug: options.Debug{
    OpenInspectorOnStartup: true,
},
```

6. **GPU issues on Windows** - try disabling GPU acceleration:

```go
Windows: &windows.Options{
    WebviewGpuIsDisabled: true,
},
```

## Asset Loading Failures

**Symptom:** 404 errors for JS/CSS/images in production build.

**Causes:**

1. **Missing `all:` prefix in embed directive:**
   ```go
   //go:embed all:frontend/dist    // correct - includes dotfiles
   //go:embed frontend/dist         // wrong - misses hidden files
   ```

2. **Base path mismatch** - Vite/webpack must use relative or `/` base path:
   ```js
   // vite.config.js
   export default { base: './' }   // or '/'
   ```

3. **Custom handler swallowing requests** - ensure handler returns 404 for unmatched paths so Wails serves embedded assets:
   ```go
   func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
       if !h.canHandle(r) {
           w.WriteHeader(http.StatusNotFound) // let Wails handle
           return
       }
       // ...
   }
   ```

## Build Errors

### CGo Compiler Not Found

```
# runtime/cgo
cgo: C compiler "gcc" not found
```

Install gcc: `sudo apt install build-essential` (Linux), install Xcode CLI tools (macOS), install MinGW-w64 (Windows).

### Missing pkg-config

```
pkg-config: command not found
```

```bash
# Ubuntu/Debian
sudo apt install pkg-config

# macOS
brew install pkg-config

# Fedora
sudo dnf install pkgconf-pkg-config
```

### Go Module Errors

```bash
# Reset module cache
go clean -modcache
go mod tidy
```

### Frontend Build Failures

```bash
# Clear node_modules and reinstall
rm -rf frontend/node_modules frontend/package-lock.json
cd frontend && npm install
```

### NSIS Not Found (Windows Installer)

```bash
# Windows
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
