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
| `ClipboardGetText(ctx) (string, error)` | `window.runtime.ClipboardGetText()` | Read clipboard text |
| `ClipboardSetText(ctx, text string) error` | `window.runtime.ClipboardSetText(text)` | Write text to clipboard |

## Logging

All log functions: `ctx context.Context, message string`. JS equivalents via `window.runtime.Log*`.

| Go | JS | Level |
|---|---|---|
| `LogTrace(ctx, message)` | `LogTrace(message)` | 1 - Trace |
| `LogDebug(ctx, message)` | `LogDebug(message)` | 2 - Debug |
| `LogInfo(ctx, message)` | `LogInfo(message)` | 3 - Info |
| `LogWarning(ctx, message)` | `LogWarning(message)` | 4 - Warning |
| `LogError(ctx, message)` | `LogError(message)` | 5 - Error |
| `LogFatal(ctx, message)` | `LogFatal(message)` | Logs then calls `os.Exit(1)` |

Go-only: `LogPrint`, `LogPrintln`, `LogSetLogLevel(ctx, level logger.LogLevel)`.

## Screen

```go
func ScreenGetAll(ctx context.Context) ([]Screen, error)
```

JS: `window.runtime.ScreenGetAll() : Promise<Screen[]>`

Screen struct fields: `ID` (string), `Name` (string), `Size` ({Width, Height int}), `PhysSize` ({Width, Height int}), `IsCurrent` (bool), `IsPrimary` (bool), `Rotation` (float32).

## Notification

```go
func SendNotification(ctx context.Context, opts NotificationOptions) error
```

NotificationOptions fields: `Title` (string), `Subtitle` (string, macOS only), `Body` (string).

## Drag and Drop

Enable in app config: `DragAndDrop: &options.DragAndDrop{EnableFileDrop: true, CSSDropProperty: "--wails-drop-target", CSSDropValue: "drop"}`.

| Go | JS |
|---|---|
| `OnFileDrop(ctx, callback func(x, y int, paths []string))` | `window.runtime.OnFileDrop(callback, useDropTarget)` |
| `OnFileDropOff(ctx)` | `window.runtime.OnFileDropOff()` |

CSS elements with `--wails-drop-target: drop` become valid drop targets.

## Environment

```go
func Environment(ctx context.Context) EnvironmentInfo
```

EnvironmentInfo fields: `BuildType` ("dev"/"production"/"debug"), `Platform` ("windows"/"linux"/"darwin"), `Arch` ("amd64"/"arm64"/etc).

## Show / Hide (Application)

Application-level visibility (distinct from `WindowShow`/`WindowHide`).

| Go | JS |
|---|---|
| `Show(ctx)` | `window.runtime.Show()` |
| `Hide(ctx)` | `window.runtime.Hide()` |

## Quit

| Go | JS |
|---|---|
| `Quit(ctx)` | `window.runtime.Quit()` |

Triggers `OnBeforeClose` callback if configured, allowing cancellation.
