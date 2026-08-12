---
last_updated: 2026-04-03
wails_version: v2.9
source: https://github.com/wailsapp/wails/tree/master/website/docs/guides
---

# AssetServer & Middleware

## Embedded Static Assets

Default: embed frontend build output via `embed.FS`:

```go
//go:embed all:frontend/dist
var assets embed.FS

// In options:
AssetServer: &assetserver.Options{
    Assets: assets,
},
```

## Custom http.Handler for Dynamic Routes

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

## Middleware Chain

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
