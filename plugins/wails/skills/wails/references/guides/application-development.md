---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# Application Development

## App Struct Pattern

Standard pattern: struct holds context, lifecycle hooks wire it up.

```go
type App struct {
    ctx context.Context
}

func NewApp() *App {
    return &App{}
}

func (a *App) startup(ctx context.Context) {
    a.ctx = ctx // store for runtime calls later
}

func (a *App) shutdown(ctx context.Context) {
    // cleanup: close DB connections, save state
}

func (a *App) domReady(ctx context.Context) {
    // DOM available, safe to emit events
}

func (a *App) beforeClose(ctx context.Context) (prevent bool) {
    // return true to prevent window close
    return false
}
```

Wire hooks in `wails.Run`:

```go
err := wails.Run(&options.App{
    Title:     "MyApp",
    Width:     1024,
    Height:    768,
    OnStartup:     app.startup,
    OnShutdown:    app.shutdown,
    OnDomReady:    app.domReady,
    OnBeforeClose: app.beforeClose,
    Bind: []interface{}{app},
})
```

## Method Binding

Only **public methods** (uppercase) on bound structs are exposed to frontend.

```go
type Greeter struct{}

func (g *Greeter) Hello(name string) string {
    return "Hello " + name
}

// In main:
Bind: []interface{}{
    &Greeter{},
    app,
}
```

### EnumBind

Expose Go constants as enums to frontend:

```go
type Status int

const (
    Active Status = iota
    Inactive
    Pending
)

// In options:
EnumBind: []interface{}{
    []Status{Active, Inactive, Pending},
}
```

## Generated JS Bindings

`wails dev` and `wails build` auto-generate JS/TS bindings in `frontend/wailsjs/`:

```
frontend/wailsjs/
├── go/
│   ├── main/
│   │   ├── App.js          # bound method wrappers
│   │   └── App.d.ts        # TypeScript declarations
│   └── models.ts           # struct type definitions
└── runtime/
    └── runtime.d.ts        # Wails runtime type definitions
```

Call from frontend:

```js
import { Hello } from '../wailsjs/go/main/Greeter';

const result = await Hello("World");
```

All bound methods return Promises.

## Struct to TypeScript Conversion

Go structs become TS classes. **json tags required** for field name mapping:

```go
type Person struct {
    Name    string `json:"name"`
    Age     int    `json:"age"`
    Address string `json:"address,omitempty"`
}
```

Generated TS class includes `createFrom()` factory method. Fields without json tags are **skipped** in generation.

See [AssetServer & Middleware](application-development-assetserver.md) for embedded assets and custom HTTP handlers.
