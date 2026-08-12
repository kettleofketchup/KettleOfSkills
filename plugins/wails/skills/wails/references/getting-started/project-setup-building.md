---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs
---

# Building & wails.json Config

## Building

```bash
# Default build for current platform
wails build

# Production optimized (strips debug, compresses)
wails build -clean -upx

# Platform-specific
wails build -platform windows/amd64
wails build -platform darwin/universal    # macOS universal (amd64+arm64)
wails build -platform linux/amd64

# NSIS installer (Windows)
wails build -nsis

# With webkit2_41 tag (Ubuntu 24.04+)
wails build -tags webkit2_41

# Skip frontend build (if already built)
wails build -s
```

Build flags:
| Flag | Purpose |
|------|---------|
| `-clean` | Clean build directory first |
| `-upx` | Compress binary with UPX (must be installed) |
| `-nsis` | Generate NSIS installer (Windows) |
| `-platform OS/ARCH` | Cross-compile target |
| `-tags TAG` | Go build tags (e.g., `webkit2_41`) |
| `-trimpath` | Remove file system paths from binary |
| `-race` | Build with Go race detector |
| `-s` | Skip frontend build |
| `-ldflags FLAGS` | Pass additional ldflags to Go compiler |
| `-o FILENAME` | Output filename |
| `-webview2 embed/browser/download` | WebView2 install strategy (Windows) |

Output: `build/bin/` directory.

## wails.json Configuration

```json
{
  "$schema": "https://wails.io/schemas/config.v2.json",
  "name": "myapp",
  "outputfilename": "myapp",
  "frontend:install": "npm install",
  "frontend:build": "npm run build",
  "frontend:dev:watcher": "npm run dev",
  "frontend:dev:serverUrl": "auto",
  "frontend:dev:build": "npm run dev",
  "wailsjsdir": "./frontend",
  "author": {
    "name": "Developer",
    "email": "dev@example.com"
  },
  "info": {
    "companyName": "My Company",
    "productVersion": "1.0.0",
    "copyright": "Copyright 2026",
    "comments": "Built with Wails"
  }
}
```

Key fields:
- `frontend:install` - command to install frontend deps (`npm install`)
- `frontend:build` - command to build frontend for production
- `frontend:dev:watcher` - command to run frontend dev server
- `frontend:dev:serverUrl` - `auto` detects Vite URL; set manually if custom port
- `wailsjsdir` - where to generate wailsjs bindings (default: `./frontend`)
- `outputfilename` - binary name (no extension, `.exe` added automatically on Windows)
