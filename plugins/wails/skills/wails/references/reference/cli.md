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
| `-noPackage` | Skip platform-specific packaging (macOS .app, Windows resource embedding) |
| `-nocolour` | Disable colour output |
| `-nosyncgomod` | Do not sync go.mod with Wails version |
| `-nsis` | Generate NSIS installer (Windows only) |
| `-o` | Output filename |
| `-obfuscated` | Obfuscate app using garble |
| `-platform` | Build target `OS/ARCH` (see table below) |
| `-race` | Build with Go race detector |
| `-s` | Skip frontend build |
| `-skipbindings` | Skip bindings generation |
| `-tags` | Build tags passed to Go compiler (space-separated, quoted) |
| `-trimpath` | Remove all file system paths from executable |
| `-u` | Update project `go.mod` to use same Wails version as CLI |
| `-upx` | Compress binary with UPX |
| `-upxflags` | Flags passed to UPX |
| `-v` | Verbosity level (1=verbose, 2=very verbose) |
| `-windowsconsole` | Keep console window for Windows builds |
| `-webview2` | WebView2 installer strategy: `download` (default), `embed`, `browser`, `error` |

### Platform targets

| Target | Description |
|--------|-------------|
| `windows/amd64` | Windows 64-bit |
| `windows/arm64` | Windows ARM64 |
| `darwin/amd64` | macOS Intel |
| `darwin/arm64` | macOS Apple Silicon |
| `darwin/universal` | macOS Universal binary |
| `linux/amd64` | Linux 64-bit |
| `linux/arm64` | Linux ARM64 |

Cross-compile multiple: `-platform "windows/amd64,darwin/universal,linux/amd64"`

```bash
wails build -clean -trimpath -platform darwin/universal
wails build -obfuscated -upx -nsis -platform windows/amd64
wails build -debug -devtools  # debug build with devtools
wails build -webview2 embed   # embed WebView2 runtime
```

## wails dev

Development mode with hot-reload.

| Flag | Description |
|------|-------------|
| `-appargs` | Args passed to application in shell style |
| `-assetdir` | Serve assets from this directory instead of embed.FS |
| `-browser` | Open browser to dev server on startup |
| `-compiler` | Go compiler path |
| `-debounce` | Debounce time for hot-reload (default: 100ms) |
| `-devserver` | Dev server bind address (default: `localhost:34115`) |
| `-extensions` | File extensions to trigger rebuilds (default: `go`) |
| `-frontenddevserverurl` | URL of frontend dev server (Vite etc.) to use instead of serving assets directly |
| `-ldflags` | Additional ldflags |
| `-loglevel` | Log level: `Trace`, `Debug`, `Info`, `Warning`, `Error` |
| `-nocolour` | Disable colour output |
| `-nogen` | Skip code generation |
| `-noreload` | Disable automatic reload on change |
| `-nosyncgomod` | Do not sync go.mod with Wails version |
| `-race` | Build with Go race detector |
| `-reloaddirs` | Additional directories to watch for reload (comma-separated) |
| `-s` | Skip frontend build |
| `-save` | Save given flags as defaults to `wails.json` |
| `-skipbindings` | Skip bindings generation |
| `-tags` | Build tags (space-separated, quoted) |
| `-v` | Verbosity level |
| `-wailsjsdir` | Directory to generate wailsjs modules into |

```bash
wails dev
wails dev -browser -loglevel Debug
wails dev -frontenddevserverurl http://localhost:5173  # use Vite dev server
wails dev -extensions "go,html,css" -reloaddirs "./pkg,./internal"
wails dev -appargs "--port 8080 --debug"
wails dev -save  # save current flags as defaults
```

## wails doctor

System diagnostics. Checks Go version, Wails version, platform dependencies (gcc, pkg-config, npm, docker, etc.), and WebView2 (Windows). No flags.

```bash
wails doctor
```

## wails generate

### wails generate module

Generates `wailsjs/` modules for bindings in the project.

```bash
wails generate module
```

### wails generate template

Creates a template from an existing project for reuse with `wails init -t`.

| Flag | Description |
|------|-------------|
| `-name` | Template name |
| `-frontend` | Frontend project directory |

```bash
wails generate template -name my-template -frontend ./frontend
```
