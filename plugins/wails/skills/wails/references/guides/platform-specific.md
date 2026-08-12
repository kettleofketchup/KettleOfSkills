---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Platform-Specific Guides: Windows & macOS

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
    WebviewIsTransparent: true,
    WindowIsTranslucent:  true,
    About: &mac.AboutInfo{
        Title:   "My App",
        Message: "Version 1.0",
    },
}
```

See [Platform-Specific: Linux & Cross-Platform](platform-specific-linux.md) for Linux options and cross-compilation.
