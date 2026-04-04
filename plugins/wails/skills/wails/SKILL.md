---
name: wails
description: Wails v2 Go desktop application framework with web frontend. Use when creating Go desktop apps with web UI (Svelte/React/Vue/Preact/Lit), binding Go methods to JavaScript, using wails CLI (init/dev/build/generate), configuring wails.json project settings, working with application options (window size/title/frameless/translucent), handling lifecycle callbacks (OnStartup/OnShutdown/OnDomReady/OnBeforeClose), setting up native menus and dialogs, using the runtime API (window/events/clipboard/dialog/screen/notifications/drag-drop), building cross-platform (Windows/macOS/Linux), creating NSIS installers, code signing, Mac App Store submission, or troubleshooting WebView2/webkit2gtk issues.
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs
---

# Wails v2 - Go Desktop Apps with Web UI

## Quick Start

```bash
# Install CLI
go install github.com/wailsapp/wails/v2/cmd/wails@latest

# Check dependencies
wails doctor

# Create project (default: svelte)
wails init -n myapp -t svelte-ts

# Development with hot-reload
cd myapp && wails dev

# Production build
wails build
```

## Architecture

```
┌─────────────────────────────────────┐
│          Desktop Window             │
│  ┌───────────────────────────────┐  │
│  │   WebView (webkit2gtk/WebView2)│  │
│  │   ┌─────────────────────────┐ │  │
│  │   │  Frontend (Svelte/React │ │  │
│  │   │  /Vue/Preact/Lit/Vanilla│ │  │
│  │   └──────────┬──────────────┘ │  │
│  └──────────────┼────────────────┘  │
│                 │ IPC (JSON-RPC)     │
│  ┌──────────────┴────────────────┐  │
│  │  Go Backend                   │  │
│  │  - Bound methods → JS funcs  │  │
│  │  - Runtime API               │  │
│  │  - Lifecycle callbacks       │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Method binding**: Go structs with exported methods → `wails.Bind()` → auto-generated TypeScript in `frontend/wailsjs/`. Frontend calls Go methods as async JS functions. Structs used as params/returns get TS models generated.

**Runtime API**: `runtime` package provides window control, events (emit/on), dialogs (open/save/message), clipboard, screen info, notifications, drag-drop, browser open, environment, log, menu updates.

**Lifecycle callbacks**: `OnStartup(ctx)` → `OnDomReady(ctx)` → app runs → `OnBeforeClose(ctx) bool` → `OnShutdown(ctx)`. Context from OnStartup used for runtime calls.

## Project Layout

```
myapp/
├── main.go              # Entry point, wails.Run() with options
├── app.go               # App struct with bound methods
├── wails.json           # Project config (name, frontend:build/install, author)
├── go.mod
├── frontend/
│   ├── src/             # Frontend source (framework-specific)
│   ├── index.html
│   ├── package.json
│   └── wailsjs/         # Auto-generated bindings (DO NOT EDIT)
│       ├── go/          # Go method wrappers as JS
│       └── runtime/     # Runtime API TS definitions
├── build/
│   ├── appicon.png      # App icon
│   ├── darwin/          # macOS-specific (Info.plist)
│   ├── windows/         # Windows-specific (wails.exe.manifest, NSIS config)
│   └── bin/             # Build output
```

## Application Options (main.go)

```go
wails.Run(&options.App{
    Title:            "My App",
    Width:            1024,
    Height:           768,
    MinWidth:         400,
    MinHeight:        300,
    Frameless:        false,
    StartHidden:      false,
    AlwaysOnTop:      false,
    BackgroundColour: &options.RGBA{R: 27, G: 38, B: 54, A: 1},
    OnStartup:        app.startup,
    OnShutdown:       app.shutdown,
    OnDomReady:       app.domReady,
    OnBeforeClose:    app.beforeClose,
    Bind:             []interface{}{app},
    // Platform-specific
    Windows: &windows.Options{},
    Mac:     &mac.Options{},
    Linux:   &linux.Options{},
})
```

## wails.json Config

```json
{
  "name": "myapp",
  "outputfilename": "myapp",
  "frontend:install": "npm install",
  "frontend:build": "npm run build",
  "frontend:dev:watcher": "npm run dev",
  "frontend:dev:serverUrl": "auto",
  "author": { "name": "Dev", "email": "dev@example.com" }
}
```

## Key CLI Commands

| Command | Purpose |
|---------|---------|
| `wails init -n NAME -t TEMPLATE` | Create new project |
| `wails dev` | Dev mode with hot-reload |
| `wails build` | Production build |
| `wails build -nsis` | Windows NSIS installer |
| `wails build -platform darwin/universal` | macOS universal binary |
| `wails build -tags webkit2_41` | Ubuntu 24.04+ webkit support |
| `wails generate module` | Regenerate frontend bindings |
| `wails doctor` | Check system dependencies |

## References

- [Installation & Dependencies](references/getting-started/installation.md)
- [Project Setup & Templates](references/getting-started/project-setup.md)
