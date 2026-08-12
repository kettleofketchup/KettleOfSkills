---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference
---

# Wails CLI Reference

## wails init

Scaffolds a new Wails project.

| Flag | Description |
|------|-------------|
| `-n` | Project name (**mandatory**) |
| `-d` | Project directory (default: name flag value) |
| `-g` | Init git repository |
| `-l` | List available templates |
| `-t` | Template name (e.g. `svelte`, `react`, `vue`, `preact`, `lit`, `vanilla`) |
| `-ide` | Generate IDE project files (`vscode`, `goland`) |

```bash
wails init -n myapp -t svelte
wails init -n myapp -t react -ide vscode -g
wails init -l  # list all templates
```

## wails build

Compiles application for production.

| Flag | Description |
|------|-------------|
| `-clean` | Clean build directory |
| `-compiler` | Go compiler path |
| `-debug` | Build with debug info, keep console window |
| `-devtools` | Enable devtools in production build |
| `-dryrun` | Print build command without executing |
| `-f` | Force rebuild of application |
| `-garbleargs` | Args passed to garble (default: `-literals -tiny -seed=random`) |
| `-ldflags` | Additional ldflags passed to compiler |
| `-m` | Skip mod tidy before compile |
| `-nsis` | Generate NSIS installer (Windows only) |
| `-o` | Output filename |
| `-obfuscated` | Obfuscate app using garble |
| `-platform` | Build target `OS/ARCH` |
| `-race` | Build with Go race detector |
| `-s` | Skip frontend build |
| `-tags` | Build tags passed to Go compiler |
| `-trimpath` | Remove all file system paths from executable |
| `-upx` | Compress binary with UPX |
| `-windowsconsole` | Keep console window for Windows builds |
| `-webview2` | WebView2 installer strategy: `download`, `embed`, `browser`, `error` |

Platform targets: `windows/amd64`, `windows/arm64`, `darwin/amd64`, `darwin/arm64`, `darwin/universal`, `linux/amd64`, `linux/arm64`. Cross-compile multiple: `-platform "windows/amd64,darwin/universal,linux/amd64"`

```bash
wails build -clean -trimpath -platform darwin/universal
wails build -obfuscated -upx -nsis -platform windows/amd64
wails build -webview2 embed   # embed WebView2 runtime
```

## wails dev

Development mode with hot-reload.

| Flag | Description |
|------|-------------|
| `-browser` | Open browser to dev server on startup |
| `-debounce` | Debounce time for hot-reload (default: 100ms) |
| `-devserver` | Dev server bind address (default: `localhost:34115`) |
| `-extensions` | File extensions to trigger rebuilds (default: `go`) |
| `-frontenddevserverurl` | URL of frontend dev server (Vite etc.) |
| `-loglevel` | Log level: `Trace`, `Debug`, `Info`, `Warning`, `Error` |
| `-nogen` | Skip code generation |
| `-noreload` | Disable automatic reload on change |
| `-reloaddirs` | Additional directories to watch (comma-separated) |
| `-save` | Save given flags as defaults to `wails.json` |
| `-tags` | Build tags |
| `-wailsjsdir` | Directory to generate wailsjs modules into |

```bash
wails dev
wails dev -browser -loglevel Debug
wails dev -frontenddevserverurl http://localhost:5173
wails dev -extensions "go,html,css" -reloaddirs "./pkg,./internal"
```

## wails doctor

System diagnostics. Checks Go version, Wails version, platform dependencies (gcc, pkg-config, npm, docker, etc.), and WebView2 (Windows). No flags.

## wails generate

### wails generate module

Generates `wailsjs/` modules for bindings in the project.

```bash
wails generate module
```

### wails generate template

Creates a template from an existing project for reuse with `wails init -t`.

```bash
wails generate template -name my-template -frontend ./frontend
```
