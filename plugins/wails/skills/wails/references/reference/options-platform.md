---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference
---

# Options: Platform-Specific

## Windows-Specific Options

Under `Windows: &windows.Options{...}`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `WebviewIsTransparent` | `bool` | `false` | Transparent webview background (use with `BackgroundColour` A=0) |
| `WindowIsTranslucent` | `bool` | `false` | Enable acrylic backdrop |
| `DisableWindowIcon` | `bool` | `false` | Remove icon from title bar |
| `WebviewUserDataPath` | `string` | `""` | Custom WebView2 user data dir |
| `WebviewBrowserPath` | `string` | `""` | Custom WebView2 browser runtime path |
| `Theme` | `windows.Theme` | `SystemDefault` | `SystemDefault`, `Dark`, `Light` |
| `ResizeDebounceMS` | `uint16` | `0` | Debounce resize events (ms) |
| `OnSuspend` | `func()` | `nil` | Called when Windows suspends |
| `OnResume` | `func()` | `nil` | Called when Windows resumes |
| `WebviewGpuIsDisabled` | `bool` | `false` | Disable GPU hardware acceleration |

## Mac-Specific Options

Under `Mac: &mac.Options{...}`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `TitleBar` | `*mac.TitleBar` | Default | Titlebar appearance config |
| `Appearance` | `mac.AppearanceType` | `DefaultAppearance` | `NSAppearanceNameAqua`, `NSAppearanceNameDarkAqua`, etc. |
| `WebviewIsTransparent` | `bool` | `false` | Transparent webview background |
| `About` | `*mac.AboutInfo` | `nil` | "About" menu info: `Title`, `Message`, `Icon` ([]byte) |
| `Preferences` | `*mac.Preferences` | `nil` | `TabFocusesLinks`, `TextInteractionEnabled`, `FullscreenEnabled` |

### TitleBar options

```go
TitleBar: &mac.TitleBar{
    TitlebarAppearsTransparent: true,
    HideTitle:                 true,
    HideTitleBar:              false,
    FullSizeContent:           true,
    UseToolbar:                false,
    HideToolbarSeparator:      true,
}
```

Preset: `mac.TitleBarHiddenInset()` -- hidden title, inset traffic lights, full-size content.

## Linux-Specific Options

Under `Linux: &linux.Options{...}`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `Icon` | `[]byte` | `nil` | Window icon (PNG/JPEG bytes) |
| `WindowIsTranslucent` | `bool` | `false` | Transparent window background. Requires compositing WM. Forces `BackgroundColour` alpha to 0.0. |
| `WebviewGpuPolicy` | `linux.WebviewGpuPolicy` | `WebviewGpuPolicyAlways` | GPU acceleration for webkit2gtk. `Always`, `OnDemand`, `Never`. |
| `ProgramName` | `string` | `""` | Sets `g_set_prgname()`, used as Wayland xdg-shell `app_id`. |

**Important:** Linux does NOT have `WebviewIsTransparent`. Use `WindowIsTranslucent` instead. When `Linux:` is nil (omitted), Wails defaults `WebviewGpuPolicy` to `Never` for safety.

See [Background Transparency guide](../guides/background-transparency.md) for rendering differences.
