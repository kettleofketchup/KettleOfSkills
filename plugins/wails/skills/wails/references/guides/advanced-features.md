---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Advanced Features

## Frameless Windows

Remove window chrome, implement custom drag regions via CSS:

```go
err := wails.Run(&options.App{
    Frameless: true,
    // ...
})
```

### CSS Drag Regions

Use `--wails-draggable` CSS property to make regions draggable (acts as title bar):

```css
/* Make header draggable */
.titlebar {
    --wails-draggable: drag;
    height: 30px;
    user-select: none;
}

/* Exclude buttons within draggable area */
.titlebar button {
    --wails-draggable: no-drag;
}
```

Alternative: use `data-wails-no-drag` HTML attribute to exclude elements:

```html
<div style="--wails-draggable: drag">
    <button data-wails-no-drag>Close</button>
</div>
```

## Single Instance Lock

Prevent multiple app instances. Second launch triggers callback:

```go
err := wails.Run(&options.App{
    SingleInstanceLock: &options.SingleInstanceLock{
        UniqueId: "e3984e08-28dc-4e3d-b70a-45e961589cdc",
        OnSecondInstanceLaunch: func(data options.SecondInstanceData) {
            // data.Args contains CLI args from second launch
            // data.WorkingDirectory is second instance's cwd
            runtime.WindowUnminimise(app.ctx)
            runtime.Show(app.ctx)
            // handle file open if args contain file path
            if len(data.Args) > 1 {
                app.OpenFile(data.Args[1])
            }
        },
    },
})
```

`UniqueId` must be a unique string (UUID recommended). Same ID = same lock.

## Dynamic Assets / Custom API Routes

Use `AssetServer.Handler` to serve dynamic content alongside static frontend:

```go
type APIRouter struct {
    db *sql.DB
}

func (r *APIRouter) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    switch {
    case strings.HasPrefix(req.URL.Path, "/api/users"):
        r.handleUsers(w, req)
    case strings.HasPrefix(req.URL.Path, "/api/config"):
        r.handleConfig(w, req)
    default:
        w.WriteHeader(http.StatusNotFound) // fallback to embedded assets
    }
}

// In options:
AssetServer: &assetserver.Options{
    Assets:  assets,
    Handler: &APIRouter{db: db},
},
```

Frontend fetches like standard HTTP:

```js
const response = await fetch('/api/users');
const users = await response.json();
```

## File Association

Associate app with file types so OS opens files with your app:

```go
// wails.json or build config
{
    "info": {
        "fileAssociations": [
            {
                "ext": "myext",
                "name": "My File Type",
                "description": "My Application File",
                "iconName": "myFileIcon",
                "role": "Editor"
            }
        ]
    }
}
```

Handle file opens via `SingleInstanceLock.OnSecondInstanceLaunch` - file path arrives in `data.Args`. On first launch, file path is in `os.Args`.

```go
func (a *App) startup(ctx context.Context) {
    a.ctx = ctx
    if len(os.Args) > 1 {
        a.OpenFile(os.Args[1])
    }
}
```

## Notifications

Send system notifications:

```go
runtime.SendNotification(ctx, &runtime.NotificationOptions{
    Title:    "Download Complete",
    Subtitle: "file.zip",
    Body:     "Your file has finished downloading.",
})
```

## Mouse Button Handling

Handle forward/back mouse buttons (mouse4/mouse5):

```go
// In options:
EnableDefaultContextMenu: false,
OnMouseDown: func(button int) {
    switch button {
    case 3: // back
        runtime.EventsEmit(app.ctx, "navigate:back")
    case 4: // forward
        runtime.EventsEmit(app.ctx, "navigate:forward")
    }
},
```

## Obfuscated Builds

Use [garble](https://github.com/burrowers/garble) to obfuscate Go binary:

```bash
wails build -obfuscated
```

Requires garble installed: `go install mvdan.cc/garble@latest`

Obfuscates Go symbols, strings, and package paths. Does NOT obfuscate frontend code (use frontend bundler minification for that).

## Overscroll Prevention

Prevent rubber-band/bounce scrolling on macOS and overscroll glow on Windows:

```css
html, body {
    overflow: hidden;
    height: 100%;
}

/* Or target specific containers */
.app-container {
    overflow: auto;
    overscroll-behavior: none;
}
```

`overscroll-behavior: none` prevents pull-to-refresh and bounce effects while allowing normal scroll within containers.
