---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference/runtime
---

# Miscellaneous Runtime APIs

Smaller runtime APIs: Browser, Clipboard, Log, Screen, Notification, Drag & Drop, Environment, Show/Hide, Quit.

## Browser

Open URL in the user's default browser.

| Go | JS |
|---|---|
| `BrowserOpenURL(ctx, url string)` | `window.runtime.BrowserOpenURL(url)` |

## Clipboard

| Go | JS | Description |
|---|---|---|
| `ClipboardGetText(ctx) (string, error)` | `window.runtime.ClipboardGetText() : Promise<string>` | Read clipboard text |
| `ClipboardSetText(ctx, text string) error` | `window.runtime.ClipboardSetText(text)` | Write text to clipboard |

## Logging

All log functions: `ctx context.Context, message string`. JS equivalents via `window.runtime.Log*`.

### Log Functions

| Go | JS | Level |
|---|---|---|
| `LogTrace(ctx, message)` | `LogTrace(message)` | 1 - Trace |
| `LogDebug(ctx, message)` | `LogDebug(message)` | 2 - Debug |
| `LogInfo(ctx, message)` | `LogInfo(message)` | 3 - Info |
| `LogWarning(ctx, message)` | `LogWarning(message)` | 4 - Warning |
| `LogError(ctx, message)` | `LogError(message)` | 5 - Error |
| `LogFatal(ctx, message)` | `LogFatal(message)` | Logs then calls `os.Exit(1)` |

### Additional Log Functions (Go only)

| Go | Description |
|---|---|
| `LogPrint(ctx, message string)` | Print without level prefix |
| `LogPrintln(ctx, message string)` | Print with newline, no level prefix |
| `LogSetLogLevel(ctx, level logger.LogLevel)` | Set minimum log level at runtime |

### Log Levels

```go
const (
    TRACE   LogLevel = 1
    DEBUG   LogLevel = 2
    INFO    LogLevel = 3
    WARNING LogLevel = 4
    ERROR   LogLevel = 5
)
```

## Screen

```go
func ScreenGetAll(ctx context.Context) ([]Screen, error)
```

JS: `window.runtime.ScreenGetAll() : Promise<Screen[]>`

### Screen Struct

| Field | Type | Description |
|---|---|---|
| `ID` | `string` | Monitor identifier |
| `Name` | `string` | Monitor name |
| `Size` | `Size` | Logical size `{Width, Height int}` |
| `PhysSize` | `Size` | Physical size `{Width, Height int}` |
| `IsCurrent` | `bool` | Window's current monitor |
| `IsPrimary` | `bool` | Primary display |
| `Rotation` | `float32` | Screen rotation in degrees |

## Notification

```go
func SendNotification(ctx context.Context, opts NotificationOptions) error
```

### NotificationOptions

| Field | Type | Description |
|---|---|---|
| `Title` | `string` | Notification title |
| `Subtitle` | `string` | Subtitle (macOS only) |
| `Body` | `string` | Notification body text |

## Drag and Drop

### Go Functions

| Go | Description |
|---|---|
| `OnFileDrop(ctx, callback func(x, y int, paths []string))` | Register file drop handler with coordinates and paths |
| `OnFileDropOff(ctx)` | Unregister file drop handler |

### JS Functions

| JS | Description |
|---|---|
| `window.runtime.OnFileDrop(callback, useDropTarget)` | Register file drop handler |
| `window.runtime.OnFileDropOff()` | Unregister file drop handler |

Enable drag and drop in app config via `DragAndDrop` options:

```go
app := wails.Run(&options.App{
    DragAndDrop: &options.DragAndDrop{
        EnableFileDrop:       true,
        DisableWebViewDrop:   false,
        CSSDropProperty:      "--wails-drop-target",
        CSSDropValue:         "drop",
    },
})
```

CSS elements with `--wails-drop-target: drop` become valid drop targets.

## Environment

```go
func Environment(ctx context.Context) EnvironmentInfo
```

### EnvironmentInfo

| Field | Type | Values |
|---|---|---|
| `BuildType` | `string` | `"dev"`, `"production"`, `"debug"` |
| `Platform` | `string` | `"windows"`, `"linux"`, `"darwin"` |
| `Arch` | `string` | `"amd64"`, `"arm64"`, etc. |

## Show / Hide (Application)

Application-level visibility (distinct from `WindowShow`/`WindowHide`).

| Go | JS |
|---|---|
| `Show(ctx)` | `window.runtime.Show()` |
| `Hide(ctx)` | `window.runtime.Hide()` |

## Quit

Gracefully quit the application.

| Go | JS |
|---|---|
| `Quit(ctx)` | `window.runtime.Quit()` |

Triggers `OnBeforeClose` callback if configured in app options, allowing cancellation.
