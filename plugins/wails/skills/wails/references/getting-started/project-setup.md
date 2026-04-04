---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs
---

# Project Setup & Templates

## Create New Project

```bash
wails init -n <project-name> -t <template>
```

### Available Templates

| Template | Flag |
|----------|------|
| Svelte + JS | `-t svelte` |
| Svelte + TS | `-t svelte-ts` |
| React + JS | `-t react` |
| React + TS | `-t react-ts` |
| Vue + JS | `-t vue` |
| Vue + TS | `-t vue-ts` |
| Preact + JS | `-t preact` |
| Preact + TS | `-t preact-ts` |
| Lit + JS | `-t lit` |
| Lit + TS | `-t lit-ts` |
| Vanilla + JS | `-t vanilla` |
| Vanilla + TS | `-t vanilla-ts` |

Remote templates also supported: `-t https://github.com/user/repo`

## Project Layout

```
myapp/
├── main.go                  # Entry: wails.Run(&options.App{...})
├── app.go                   # App struct, bound methods, lifecycle callbacks
├── wails.json               # Project configuration
├── go.mod / go.sum
├── frontend/
│   ├── index.html           # HTML entry point
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.ts       # Vite config (all templates use Vite)
│   ├── tsconfig.json        # TypeScript config (TS templates)
│   ├── src/
│   │   ├── App.svelte       # (or App.tsx, App.vue, etc.)
│   │   ├── main.ts          # Frontend entry
│   │   └── style.css
│   └── wailsjs/             # AUTO-GENERATED - do not edit
│       ├── go/
│       │   └── main/
│       │       ├── App.js   # JS wrappers for bound Go methods
│       │       └── App.d.ts # TS declarations
│       └── runtime/
│           └── runtime.d.ts # Runtime API types
├── build/
│   ├── appicon.png          # 1024x1024 app icon
│   ├── darwin/
│   │   └── Info.plist       # macOS app metadata
│   └── windows/
│       ├── icon.ico
│       ├── info.json        # Version info for exe
│       ├── wails.exe.manifest
│       └── installer/       # NSIS installer config
```

## Development Mode

```bash
wails dev
```

Features:
- Frontend hot-reload via Vite dev server
- Go backend rebuilds on .go file changes
- Auto-regenerates TypeScript bindings when Go methods change
- Frontend served at `http://localhost:34115` (also accessible in browser for debugging)
- `-tags webkit2_41` required on Ubuntu 24.04+

Flags:
- `-browser` open app in browser instead of native window
- `-e <ext>` additional file extensions to trigger rebuild (default: go)
- `-reloaddirs <dirs>` additional directories to watch
- `-noreload` disable auto-reload
- `-nogen` disable auto-generation of bindings

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

## Regenerate Bindings

```bash
wails generate module
```

Regenerates `frontend/wailsjs/go/` from current Go bound methods. Run manually if auto-generation misses changes. Bindings auto-generated during `wails dev` and `wails build`.

## Adding Bound Methods

1. Add exported method to bound struct in Go:
```go
func (a *App) MyMethod(name string) (string, error) {
    return "Hello " + name, nil
}
```

2. Bindings auto-generated on next `wails dev` or `wails generate module`

3. Call from frontend:
```typescript
import { MyMethod } from '../wailsjs/go/main/App';
const result = await MyMethod("world");
```

Supported param/return types: primitives, strings, structs (→ TS classes), slices, maps, errors. Struct types generate TS model classes with `createFrom()` factory methods.
