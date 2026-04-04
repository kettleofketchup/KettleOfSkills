---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs
---

# Installation & Dependencies

## Required

- **Go 1.21+** - `go version` to verify
- **NPM** (Node 15+) - for frontend toolchain

## Platform-Specific Dependencies

### Linux

```bash
# Debian/Ubuntu
sudo apt install gcc libgtk-3-dev libwebkit2gtk-4.0-dev

# Ubuntu 24.04+ (webkit2gtk 4.1 API)
# Must build with tag:
wails build -tags webkit2_41
wails dev -tags webkit2_41

# Fedora
sudo dnf install gcc gtk3-devel webkit2gtk4.0-devel

# Arch
sudo pacman -S gcc pkg-config gtk3 webkit2gtk
```

**Ubuntu 24.04+ note**: Ships webkit2gtk-4.1 instead of 4.0. The `webkit2_41` build tag switches Wails to use the 4.1 API. Required for both `dev` and `build` commands. Without it: build errors referencing missing webkit2gtk-4.0 pkg-config.

### macOS

```bash
# Xcode command line tools (required)
xcode-select --install
```

Requires macOS 10.15+ (Catalina). Xcode CLI tools provide clang compiler and webkit framework headers.

### Windows

- **WebView2 Runtime** - bundled with Windows 11, Windows 10 may need manual install from Microsoft
- Go compiler (MinGW not needed, Wails uses CGo with MSVC toolchain on Windows)
- Optional: NSIS for installer creation (`choco install nsis` or `scoop install nsis`)

**WebView2 troubleshooting**:
- Missing WebView2 → app crashes on launch. Check: `reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"` 
- Embedded install strategy: set `windows.Options{WebviewIsTransparent: false}` and use WebView2 bootstrapper in NSIS script
- Enterprise environments may block WebView2 → use fixed version runtime

## Install Wails CLI

```bash
go install github.com/wailsapp/wails/v2/cmd/wails@latest
```

Installs to `$GOPATH/bin/` (ensure in `$PATH`).

## Verify Installation

```bash
wails doctor
```

Checks:
- Go version ≥ 1.21
- NPM available
- Platform build dependencies present (gcc, pkg-config, gtk3, webkit2gtk on Linux)
- Wails CLI version
- Optional dependency status (NSIS, UPX, docker)

**Common `wails doctor` failures**:
- `pkg-config not found` → install pkg-config package
- `webkit2gtk-4.0 not found` → install libwebkit2gtk-4.0-dev (or use webkit2_41 tag on Ubuntu 24.04+)
- `gcc not found` → install build-essential (Linux) or xcode-select (macOS)

## Updating

```bash
go install github.com/wailsapp/wails/v2/cmd/wails@latest
```

Check current version: `wails version`

## CGo Requirement

Wails requires CGo enabled (`CGO_ENABLED=1`, default). Cross-compilation needs appropriate C cross-compiler toolchain for target platform. Native compilation recommended; use CI matrix for multi-platform builds.
