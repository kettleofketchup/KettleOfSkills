---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/reference/runtime
---

# Window Runtime API

All functions take `ctx context.Context` as first parameter (from `wails.Run` callback).
JS equivalents use `window.runtime.<MethodName>(...)` with no ctx.

## Title & Reload

| Go | JS | Description |
|---|---|---|
| `WindowSetTitle(ctx, title string)` | `WindowSetTitle(title)` | Set window title |
| `WindowReload(ctx)` | `WindowReload()` | Reload frontend (dev reload) |
| `WindowReloadApp(ctx)` | `WindowReloadApp()` | Reload app (full restart of frontend) |
| `WindowExecJS(ctx, js string)` | — | Execute arbitrary JS in window |

## Show / Hide

| Go | JS |
|---|---|
| `WindowShow(ctx)` | `WindowShow()` |
| `WindowHide(ctx)` | `WindowHide()` |

## Size

| Go | JS | Description |
|---|---|---|
| `WindowSetSize(ctx, width, height int)` | `WindowSetSize(width, height)` | Set window width/height in logical pixels |
| `WindowGetSize(ctx) (int, int)` | `WindowGetSize() : Size` | Returns current width, height |
| `WindowSetMinSize(ctx, width, height int)` | `WindowSetMinSize(width, height)` | Set minimum window size |
| `WindowSetMaxSize(ctx, width, height int)` | `WindowSetMaxSize(width, height)` | Set maximum window size |

## Position

| Go | JS | Description |
|---|---|---|
| `WindowCenter(ctx)` | `WindowCenter()` | Center window on current monitor |
| `WindowSetPosition(ctx, x, y int)` | `WindowSetPosition(x, y)` | Set window position in screen coordinates |
| `WindowGetPosition(ctx) (int, int)` | `WindowGetPosition() : Position` | Get current window position |

## Fullscreen

| Go | JS | Description |
|---|---|---|
| `WindowFullscreen(ctx)` | `WindowFullscreen()` | Make window fullscreen |
| `WindowUnfullscreen(ctx)` | `WindowUnfullscreen()` | Restore from fullscreen |
| `WindowIsFullscreen(ctx) bool` | `WindowIsFullscreen() : bool` | Check if fullscreen |

## Maximise / Minimise

| Go | JS | Description |
|---|---|---|
| `WindowMaximise(ctx)` | `WindowMaximise()` | Maximise window |
| `WindowUnmaximise(ctx)` | `WindowUnmaximise()` | Restore from maximised |
| `WindowToggleMaximise(ctx)` | `WindowToggleMaximise()` | Toggle maximise state |
| `WindowMinimise(ctx)` | `WindowMinimise()` | Minimise window |
| `WindowUnminimise(ctx)` | `WindowUnminimise()` | Restore from minimised |

## State Queries

| Go | JS | Returns |
|---|---|---|
| `WindowIsNormal(ctx) bool` | `WindowIsNormal()` | True if not min/max/fullscreen |
| `WindowIsMinimised(ctx) bool` | `WindowIsMinimised()` | True if minimised |
| `WindowIsMaximised(ctx) bool` | `WindowIsMaximised()` | True if maximised |
| `WindowIsFullscreen(ctx) bool` | `WindowIsFullscreen()` | True if fullscreen |

## Theme

| Go | JS | Description |
|---|---|---|
| `WindowSetSystemDefaultTheme(ctx)` | `WindowSetSystemDefaultTheme()` | Use OS theme |
| `WindowSetLightTheme(ctx)` | `WindowSetLightTheme()` | Force light theme |
| `WindowSetDarkTheme(ctx)` | `WindowSetDarkTheme()` | Force dark theme |

## Misc

| Go | JS | Description |
|---|---|---|
| `WindowSetAlwaysOnTop(ctx, b bool)` | `WindowSetAlwaysOnTop(b)` | Pin/unpin window on top |
| `WindowSetBackgroundColour(ctx, R, G, B, A uint8)` | `WindowSetBackgroundColour(R, G, B, A)` | Set window background RGBA |
| `WindowPrint(ctx)` | `WindowPrint()` | Open native print dialog for window content |

## Usage Example (Go)

```go
func (a *App) startup(ctx context.Context) {
    a.ctx = ctx
    runtime.WindowSetTitle(ctx, "My App")
    runtime.WindowCenter(ctx)
    runtime.WindowSetSize(ctx, 1024, 768)
    runtime.WindowSetMinSize(ctx, 400, 300)
}
```

## Usage Example (JS)

```js
window.runtime.WindowSetTitle("My App");
window.runtime.WindowCenter();
window.runtime.WindowSetSize(1024, 768);
```
