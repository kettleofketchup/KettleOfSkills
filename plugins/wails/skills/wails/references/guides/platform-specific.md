---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Platform-Specific Guides

## Windows

### WebView2 Runtime

Windows apps use Microsoft Edge WebView2. Pre-installed on Windows 11 and recent Windows 10 updates. For older systems, control behavior with `-webview2` flag:

```bash
wails build -webview2 download    # download installer at runtime (default)
wails build -webview2 embed       # embed ~140MB bootstrap into binary
wails build -webview2 browser     # open download page in browser
wails build -webview2 error       # error if not installed
```

Programmatic control in options:

```go
windows.Options{
    WebviewIsTransparent: false,
    WindowIsTranslucent:  false,
    WebviewGpuIsDisabled: false,
}
```

### NSIS Installer

Generate Windows installer:

```bash
wails build -nsis
```

Requires NSIS installed (`choco install nsis` or `winget install NSIS.NSIS`). Produces `.exe` installer alongside the app binary.

### Dark/Light Theme

```go
windows.Options{
    Theme: windows.SystemDefault,  // follows system
    // or: windows.Dark, windows.Light
    CustomTheme: &windows.ThemeSettings{
        DarkModeTitleBar:   windows.RGB(30, 30, 30),
        DarkModeTitleText:  windows.RGB(255, 255, 255),
        LightModeTitleBar:  windows.RGB(245, 245, 245),
        LightModeTitleText: windows.RGB(20, 20, 20),
    },
}
```

### Windows Console

Keep console window visible (useful for CLI hybrid apps):

```bash
wails build -windowsconsole
```

## macOS

### Code Signing

Sign for distribution:

```bash
# Sign the app bundle
codesign --deep --force --verbose --sign "Developer ID Application: Your Name (TEAMID)" \
    build/bin/MyApp.app

# Notarize
xcrun notarytool submit build/bin/MyApp.zip \
    --apple-id "your@email.com" \
    --team-id "TEAMID" \
    --password "app-specific-password" \
    --wait

# Staple
xcrun stapler staple build/bin/MyApp.app
```

### Mac App Store

Requires additional entitlements and provisioning profile:

**entitlements.plist** (App Sandbox required for MAS):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
```

Sign with provisioning profile:

```bash
codesign --deep --force --options runtime \
    --sign "3rd Party Mac Developer Application: ..." \
    --entitlements entitlements.plist \
    build/bin/MyApp.app

productbuild --sign "3rd Party Mac Developer Installer: ..." \
    --component build/bin/MyApp.app /Applications \
    MyApp.pkg
```

### TitleBar Customization

```go
Mac: &mac.Options{
    TitleBar: &mac.TitleBar{
        TitlebarAppearsTransparent: true,
        HideTitle:                  true,
        HideTitleBar:              false,
        FullSizeContent:           true,
        UseToolbar:                true,
        HideToolbarSeparator:      true,
    },
    Appearance: mac.NSAppearanceNameDarkAqua,
    // Options: NSAppearanceNameAqua, NSAppearanceNameDarkAqua,
    //          NSAppearanceNameVibrantLight, NSAppearanceNameVibrantDark,
    //          NSAppearanceNameAccessibilityHighContrastAqua,
    //          NSAppearanceNameAccessibilityHighContrastDarkAqua
    WebviewIsTransparent: true,
    WindowIsTranslucent:  true,
    About: &mac.AboutInfo{
        Title:   "My App",
        Message: "Version 1.0",
    },
}
```

Toolbar + transparent titlebar enables "inset" traffic light style common in modern macOS apps.

## Linux

### Dependencies

Required system packages:

```bash
# Debian/Ubuntu
sudo apt install libgtk-3-dev libwebkit2gtk-4.0-dev

# Fedora
sudo dnf install gtk3-devel webkit2gtk4.0-devel

# Arch
sudo pacman -S gtk3 webkit2gtk-4.1
```

### webkit2gtk Version

Default: webkit2gtk-4.0. For newer distros shipping only 4.1 (e.g., Arch, Fedora 38+):

```bash
# Build with webkit2gtk-4.1
wails build -tags webkit2_41
wails dev -tags webkit2_41
```

Or set in `wails.json`:

```json
{
  "wailsjsdir": "./frontend",
  "tags": "webkit2_41"
}
```

### Distribution Support

Supported: Ubuntu 20.04+, Fedora 36+, Arch, openSUSE, Debian 11+. Requires X11 or Wayland with XWayland. Wayland native support depends on webkit2gtk version.

## Cross-Platform Builds

Use `-platform` flag for cross-compilation:

```bash
# Windows targets
wails build -platform windows/amd64
wails build -platform windows/arm64

# macOS targets (requires macOS host for CGo)
wails build -platform darwin/amd64
wails build -platform darwin/arm64
wails build -platform darwin/universal   # fat binary

# Linux targets
wails build -platform linux/amd64
wails build -platform linux/arm64
```

**Limitations:**
- macOS builds require macOS host (CGo dependency)
- Windows cross-compile from Linux possible with `x86_64-w64-mingw32-gcc`
- Linux cross-compile requires matching architecture libs
- Universal macOS binary combines amd64 + arm64 into single file
