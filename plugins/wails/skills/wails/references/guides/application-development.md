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

Only **public methods** (uppercase) on bound structs are exposed to frontend. Pass struct instances in `Bind` option.

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

Generates:

```typescript
export class Person {
    name: string;
    age: number;
    address: string;

    static createFrom(source: any = {}) {
        return new Person(source);
    }

    constructor(source: any = {}) {
        if ('string' === typeof source) source = JSON.parse(source);
        this.name = source["name"];
        this.age = source["age"];
        this.address = source["address"];
    }
}
```

Use `createFrom` to instantiate from JSON/API responses:

```typescript
import { Person } from '../wailsjs/go/models';

const p = Person.createFrom({ name: "Alice", age: 30 });
```

Fields without json tags are **skipped** in generation.

## AssetServer

### Embedded Static Assets

Default: embed frontend build output via `embed.FS`:

```go
//go:embed all:frontend/dist
var assets embed.FS

// In options:
AssetServer: &assetserver.Options{
    Assets: assets,
},
```

### Custom http.Handler for Dynamic Routes

Serve API routes, dynamic content alongside static assets:

```go
AssetServer: &assetserver.Options{
    Assets:  assets,
    Handler: NewAPIHandler(),
},
```

```go
type APIHandler struct{}

func NewAPIHandler() *APIHandler {
    return &APIHandler{}
}

func (h *APIHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    if strings.HasPrefix(r.URL.Path, "/api/") {
        // handle API routes
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
        return
    }
    // unhandled requests fall through to embedded assets
    w.WriteHeader(http.StatusNotFound)
}
```

Handler receives requests that don't match embedded assets. Return 404 to let Wails handle.

### Middleware Chain

Wrap the entire asset server (both embedded + handler) with middleware:

```go
AssetServer: &assetserver.Options{
    Assets:     assets,
    Handler:    apiHandler,
    Middleware: LoggingMiddleware,
},
```

Middleware signature takes an `http.Handler` (the next handler in chain):

```go
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Printf("%s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}
```

The `next` handler is the complete Wails asset server. Middleware wraps everything - embedded assets, custom handler, all of it. Useful for auth, CORS, logging, request modification.
