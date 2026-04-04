---
last_updated: 2026-03-08
---

# OpenTelemetry Go Web Framework Instrumentation

OTEL middleware for Gin, Echo, Chi, Fiber. All examples assume tracer provider initialized.

---

## Gin (otelgin) — Primary

Package: `go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin`

### Setup and Configuration

```go
import "go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"

r := gin.Default()
r.Use(otelgin.Middleware("my-service",
    otelgin.WithSpanNameFormatter(func(r *http.Request) string {
        return fmt.Sprintf("%s %s", r.Method, r.URL.Path)
    }),
    otelgin.WithFilter(func(r *http.Request) bool {
        return r.URL.Path != "/healthz" // false = skip tracing
    }),
    otelgin.WithMetricAttributeFn(func(r *http.Request) []attribute.KeyValue {
        return []attribute.KeyValue{attribute.String("http.client_ip", r.RemoteAddr)}
    }),
    // gin.Context version — overrides MetricAttributeFn on key collision
    otelgin.WithGinMetricAttributeFn(func(c *gin.Context) []attribute.KeyValue {
        return []attribute.KeyValue{attribute.String("user.id", c.GetString("userID"))}
    }),
    otelgin.WithTracerProvider(tp),
    otelgin.WithMeterProvider(mp),
    otelgin.WithPropagators(propagation.TraceContext{}),
))
```

### Route Params and Custom Spans

Span name defaults to route template (`/users/:id`). Extract context from `c.Request.Context()`:

```go
r.GET("/users/:id", func(c *gin.Context) {
    ctx := c.Request.Context()

    // Add attributes to middleware span
    span := trace.SpanFromContext(ctx)
    span.SetAttributes(attribute.String("user.id", c.Param("id")))

    // Create child span
    ctx, dbSpan := otel.Tracer("my-service").Start(ctx, "db.getUser")
    defer dbSpan.End()

    user, err := db.FindUser(ctx, c.Param("id"))
    if err != nil {
        dbSpan.RecordError(err)
        dbSpan.SetStatus(codes.Error, err.Error())
        c.JSON(500, gin.H{"error": "internal"})
        return
    }
    c.JSON(200, user)
})
```

Auto-collected metrics: `http.server.request.duration`, `http.server.request.body.size`, `http.server.response.body.size`

---

## Echo (otelecho)

Package: `go.opentelemetry.io/contrib/instrumentation/github.com/labstack/echo/otelecho`

```go
import "go.opentelemetry.io/contrib/instrumentation/github.com/labstack/echo/otelecho"

e := echo.New()
e.Use(otelecho.Middleware("my-service",
    otelecho.WithSkipper(func(c echo.Context) bool {
        return c.Path() == "/healthz"
    }),
    otelecho.WithTracerProvider(tp),
    otelecho.WithMeterProvider(mp),
    otelecho.WithMetricAttributeFn(func(r *http.Request) []attribute.KeyValue {
        return []attribute.KeyValue{attribute.String("http.client_ip", r.RemoteAddr)}
    }),
))
```

Context: `c.Request().Context()`. Span name defaults to route template.

---

## Chi (otelchi)

Package: `github.com/riandyrn/otelchi` (community package)

```go
import "github.com/riandyrn/otelchi"

r := chi.NewRouter()
r.Use(otelchi.Middleware("my-service",
    otelchi.WithChiRoutes(r),                    // route patterns in span names
    otelchi.WithFilter(func(r *http.Request) bool {
        return r.URL.Path != "/healthz"          // true = trace, false = skip
    }),
    otelchi.WithRequestMethodInSpanName(true),   // useful for Elastic/New Relic
    otelchi.WithTracerProvider(tp),
    otelchi.WithPropagators(propagation.TraceContext{}),
))
```

Context: `r.Context()`. Route params: `chi.URLParam(r, "id")`.

**Important**: Without `WithChiRoutes(r)`, span names show raw paths (`/users/123`)
instead of patterns (`/users/{id}`). Must be called after routes are defined.

---

## Fiber (otelfiber)

Package: `github.com/gofiber/contrib/otelfiber/v2`

**Fiber uses fasthttp, not net/http.** Use `c.UserContext()` not `http.Request.Context()`.

```go
import "github.com/gofiber/contrib/otelfiber/v2"

app := fiber.New()
app.Use(otelfiber.Middleware(
    otelfiber.WithNext(func(c *fiber.Ctx) bool {
        return c.Path() == "/healthz" // true = skip
    }),
    otelfiber.WithSpanNameFormatter(func(c *fiber.Ctx) string {
        return fmt.Sprintf("%s %s", c.Method(), c.Path())
    }),
    otelfiber.WithCustomAttributes(func(c *fiber.Ctx) []attribute.KeyValue {
        return []attribute.KeyValue{attribute.String("http.client_ip", c.IP())}
    }),
    otelfiber.WithTracerProvider(tp),
    otelfiber.WithMeterProvider(mp),
))
```

Handler context extraction:

```go
func handler(c *fiber.Ctx) error {
    ctx := c.UserContext()  // NOT c.Context() — that returns fasthttp.RequestCtx
    ctx, span := otel.Tracer("svc").Start(ctx, "op")
    defer span.End()
    // pass ctx downstream
}
```

Metrics: `http.server.duration`, `http.server.request.size`, `http.server.response.size`, `http.server.active_requests`

---

## Common Patterns

### Error Recording

```go
span.RecordError(err)                     // adds error event with stack trace
span.SetStatus(codes.Error, err.Error())  // marks span as failed
```

Always call both. `RecordError` alone does not set span status.

### Custom Child Spans

```go
ctx, span := otel.Tracer("service").Start(ctx, "operation.name")
defer span.End()
span.SetAttributes(attribute.String("key", "value"), attribute.Int("count", 42))
```

Always propagate `ctx` to downstream calls for trace hierarchy.

### Span Naming

| Framework | Default Span Name | Example |
|-----------|------------------|---------|
| Gin       | Route template   | `/users/:id` |
| Echo      | Route template   | `/users/:id` |
| Chi       | Route pattern (needs `WithChiRoutes`) | `/users/{id}` |
| Fiber     | Route template   | `/users/:id` |

### Context Extraction

| Framework | Get `context.Context` |
|-----------|----------------------|
| Gin       | `c.Request.Context()` |
| Echo      | `c.Request().Context()` |
| Chi       | `r.Context()` |
| Fiber     | `c.UserContext()` |
