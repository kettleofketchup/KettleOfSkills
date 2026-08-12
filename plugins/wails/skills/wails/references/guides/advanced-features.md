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
            runtime.WindowUnminimise(app.ctx)
            runtime.Show(app.ctx)
            if len(data.Args) > 1 {
                app.OpenFile(data.Args[1])
            }
        },
    },
})
```

`UniqueId` must be a unique string (UUID recommended).

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
    default:
        w.WriteHeader(http.StatusNotFound)
    }
}

// In options:
AssetServer: &assetserver.Options{
    Assets:  assets,
    Handler: &APIRouter{db: db},
},
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

Handle file opens via `OnSecondInstanceLaunch` - file path arrives in `data.Args`.

## Notifications

```go
runtime.SendNotification(ctx, &runtime.NotificationOptions{
    Title:    "Download Complete",
    Subtitle: "file.zip",
    Body:     "Your file has finished downloading.",
})
```

See [Advanced Features: Misc](advanced-features-misc.md) for obfuscated builds, overscroll prevention, and mouse button handling.
