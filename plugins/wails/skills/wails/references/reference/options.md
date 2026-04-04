---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference
---

# Application Options

Passed to `wails.Run(&options.App{...})`.

## Window Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `Title` | `string` | `""` | Window title bar text |
| `Width` | `int` | `1024` | Starting window width |
| `Height` | `int` | `768` | Starting window height |
| `MinWidth` | `int` | `0` | Minimum window width |
| `MinHeight` | `int` | `0` | Minimum window height |
| `MaxWidth` | `int` | `0` | Maximum window width (0 = no constraint) |
| `MaxHeight` | `int` | `0` | Maximum window height (0 = no constraint) |
| `DisableResize` | `bool` | `false` | Prevent user resizing |
| `Fullscreen` | `bool` | `false` | Start fullscreen |
| `Frameless` | `bool` | `false` | Remove window frame/title bar |
| `StartHidden` | `bool` | `false` | Start with window hidden; call `runtime.WindowShow()` to reveal |

## AssetServer Options

| Option | Type | Description |
|--------|------|-------------|
| `Assets` | `embed.FS` | Frontend assets via Go embed; must contain `index.html` |
| `Handler` | `http.Handler` | Custom asset handler; falls back to this when `Assets` FS has no match |
| `Middleware` | `AssetMiddleware` | Hook into AssetServer HTTP chain; wraps `http.Handler` |

```go
//go:embed all:frontend/dist
var assets embed.FS

app := &options.App{
    AssetServer: &assetserver.Options{
        Assets:  assets,
        Handler: myCustomHandler,
    },
}
```

## Appearance Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `AlwaysOnTop` | `bool` | `false` | Keep window above others |
| `BackgroundColour` | `*options.RGBA` | `White` | Window background RGBA (shows before frontend loads) |
| `WindowStartState` | `options.WindowStartState` | `Normal` | `Normal`, `Maximised`, `Minimised`, `Fullscreen` |
| `CSSDragProperty` | `string` | `"--wails-draggable"` | CSS property to identify drag regions |
| `CSSDragValue` | `string` | `"drag"` | Value of CSSDragProperty that enables dragging |

```go
BackgroundColour: &options.RGBA{R: 27, G: 38, B: 54, A: 255}
```

CSS drag region usage:
```css
.titlebar { --wails-draggable: drag; }
.titlebar button { --wails-draggable: no-drag; }
```

## Lifecycle Callbacks

| Option | Signature | When |
|--------|-----------|------|
| `OnStartup` | `func(ctx context.Context)` | After frontend created, before `index.html` loaded. Use `ctx` for `runtime.*` calls |
| `OnDomReady` | `func(ctx context.Context)` | After frontend `DOMContentLoaded` fires |
| `OnShutdown` | `func(ctx context.Context)` | After application termination |
| `OnBeforeClose` | `func(ctx context.Context) bool` | Before closing; return `true` to prevent close |

```go
OnStartup: func(ctx context.Context) {
    app.ctx = ctx  // store for later runtime calls
},
OnBeforeClose: func(ctx context.Context) bool {
    // show confirmation dialog
    dialog, _ := runtime.MessageDialog(ctx, runtime.MessageDialogOptions{
        Type:    runtime.QuestionDialog,
        Title:   "Quit?",
        Message: "Are you sure?",
    })
    return dialog != "Yes"  // true = prevent close
},
```

## Binding Options

| Option | Type | Description |
|--------|------|-------------|
| `Bind` | `[]interface{}` | Slice of struct instances to expose methods to frontend |
| `EnumBind` | `[]interface{}` | Slice of enum arrays to expose to frontend TS |

```go
Bind: []interface{}{
    &app,
    &myService,
},
EnumBind: []interface{}{
    AllUserRoles,  // var AllUserRoles = []UserRole{Admin, User, Guest}
},
```

Bound methods callable from frontend via `window.go.main.App.MethodName()` or generated `wailsjs/go/` bindings.

## Windows-Specific Options

Under `Windows: &windows.Options{...}`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `WebviewIsTransparent` | `bool` | `false` | Transparent webview background (use with `BackgroundColour` A=0) |
| `WindowIsTranslucent` | `bool` | `false` | Enable acrylic backdrop |
| `DisableWindowIcon` | `bool` | `false` | Remove icon from title bar |
| `WebviewUserDataPath` | `string` | `""` | Custom WebView2 user data dir (default: `%APPDATA%\[BinaryName]`) |
| `WebviewBrowserPath` | `string` | `""` | Custom WebView2 browser runtime path |
| `Theme` | `windows.Theme` | `SystemDefault` | `SystemDefault`, `Dark`, `Light` |
| `ResizeDebounceMS` | `uint16` | `0` | Debounce resize events (ms) |
| `OnSuspend` | `func()` | `nil` | Called when Windows suspends (sleep/hibernate) |
| `OnResume` | `func()` | `nil` | Called when Windows resumes |
| `WebviewGpuIsDisabled` | `bool` | `false` | Disable GPU hardware acceleration for webview |

## Mac-Specific Options

Under `Mac: &mac.Options{...}`.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `TitleBar` | `*mac.TitleBar` | Default | Titlebar appearance config (see below) |
| `Appearance` | `mac.AppearanceType` | `DefaultAppearance` | `NSAppearanceNameAqua`, `NSAppearanceNameDarkAqua`, `NSAppearanceNameVibrantLight`, etc. |
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
| `WindowIsTranslucent` | `bool` | `false` | Translucent window (compositor-dependent) |
| `WebviewGpuPolicy` | `linux.WebviewGpuPolicy` | `WebviewGpuPolicyAlways` | `WebviewGpuPolicyAlways`, `WebviewGpuPolicyOnDemand`, `WebviewGpuPolicyNever` |

## Other Options

| Option | Type | Description |
|--------|------|-------------|
| `Logger` | `logger.Logger` | Custom logger implementation |
| `LogLevel` | `logger.LogLevel` | Dev log level: `Trace`, `Debug`, `Info`, `Warning`, `Error` |
| `LogLevelProduction` | `logger.LogLevel` | Production log level |
| `SingleInstanceLock` | `*options.SingleInstanceLock` | Restrict to single instance. Fields: `UniqueId` (string), `OnSecondInstanceLaunch` callback |
| `Debug` | `options.Debug` | Debug settings: `OpenInspectorOnStartup` (bool) |
| `ErrorFormatter` | `func(error) any` | Custom error formatting for bound method errors returned to frontend |
| `DragAndDrop` | `*options.DragAndDrop` | Enable drag-and-drop. Fields: `EnableFileDrop` (bool), `DisableWebViewDrop` (bool), `CSSDropProperty`, `CSSDropValue` |

```go
SingleInstanceLock: &options.SingleInstanceLock{
    UniqueId: "e3984e08-28dc-4e3d-b70a-45e961589cdc",
    OnSecondInstanceLaunch: func(data options.SecondInstanceData) {
        runtime.WindowUnminimise(ctx)
        runtime.Show(ctx)
    },
},
DragAndDrop: &options.DragAndDrop{
    EnableFileDrop:     true,
    DisableWebViewDrop: false,
},
```
