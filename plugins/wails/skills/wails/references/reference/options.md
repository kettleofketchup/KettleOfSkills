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
| `StartHidden` | `bool` | `false` | Start with window hidden |

## AssetServer Options

| Option | Type | Description |
|--------|------|-------------|
| `Assets` | `embed.FS` | Frontend assets via Go embed; must contain `index.html` |
| `Handler` | `http.Handler` | Custom asset handler; falls back when `Assets` FS has no match |
| `Middleware` | `AssetMiddleware` | Hook into AssetServer HTTP chain |

## Appearance Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `AlwaysOnTop` | `bool` | `false` | Keep window above others |
| `BackgroundColour` | `*options.RGBA` | `White` | Window background RGBA |
| `WindowStartState` | `options.WindowStartState` | `Normal` | `Normal`, `Maximised`, `Minimised`, `Fullscreen` |
| `CSSDragProperty` | `string` | `"--wails-draggable"` | CSS property to identify drag regions |
| `CSSDragValue` | `string` | `"drag"` | Value of CSSDragProperty that enables dragging |

**Alpha behavior per platform:** Linux = full 0-255 range; Windows = binary (0 or 255); macOS = full 0-255 range. Match `BackgroundColour` to CSS theme to avoid flash before frontend loads.

## Lifecycle Callbacks

| Option | Signature | When |
|--------|-----------|------|
| `OnStartup` | `func(ctx context.Context)` | After frontend created, before `index.html` loaded |
| `OnDomReady` | `func(ctx context.Context)` | After `DOMContentLoaded` fires |
| `OnShutdown` | `func(ctx context.Context)` | After application termination |
| `OnBeforeClose` | `func(ctx context.Context) bool` | Before closing; return `true` to prevent close |

## Binding Options

| Option | Type | Description |
|--------|------|-------------|
| `Bind` | `[]interface{}` | Slice of struct instances to expose methods to frontend |
| `EnumBind` | `[]interface{}` | Slice of enum arrays to expose to frontend TS |

## Other Options

| Option | Type | Description |
|--------|------|-------------|
| `Logger` | `logger.Logger` | Custom logger implementation |
| `LogLevel` | `logger.LogLevel` | Dev log level: `Trace`, `Debug`, `Info`, `Warning`, `Error` |
| `SingleInstanceLock` | `*options.SingleInstanceLock` | Restrict to single instance |
| `Debug` | `options.Debug` | `OpenInspectorOnStartup` (bool) |
| `ErrorFormatter` | `func(error) any` | Custom error formatting for bound method errors |
| `DragAndDrop` | `*options.DragAndDrop` | `EnableFileDrop`, `DisableWebViewDrop`, CSS properties |

See [Options: Platform-Specific](options-platform.md) for Windows, Mac, and Linux options.
