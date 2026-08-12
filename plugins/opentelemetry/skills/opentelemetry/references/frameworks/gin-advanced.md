---
last_updated: 2026-03-08
---

# Go Web Framework OTEL: Echo, Chi, Fiber, and Patterns

## Echo (otelecho)

Package: `go.opentelemetry.io/contrib/instrumentation/github.com/labstack/echo/otelecho`

```go
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

## Chi (otelchi)

Package: `github.com/riandyrn/otelchi` (community package)

```go
r := chi.NewRouter()
r.Use(otelchi.Middleware("my-service",
    otelchi.WithChiRoutes(r),                    // route patterns in span names
    otelchi.WithFilter(func(r *http.Request) bool {
        return r.URL.Path != "/healthz"
    }),
    otelchi.WithRequestMethodInSpanName(true),
    otelchi.WithTracerProvider(tp),
    otelchi.WithPropagators(propagation.TraceContext{}),
))
```

Context: `r.Context()`. **Important**: Without `WithChiRoutes(r)`, span names show raw paths (`/users/123`) instead of patterns (`/users/{id}`). Must be called after routes are defined.

## Fiber (otelfiber)

Package: `github.com/gofiber/contrib/otelfiber/v2`

**Fiber uses fasthttp, not net/http.** Use `c.UserContext()` not `http.Request.Context()`.

```go
app := fiber.New()
app.Use(otelfiber.Middleware(
    otelfiber.WithNext(func(c *fiber.Ctx) bool { return c.Path() == "/healthz" }),
    otelfiber.WithSpanNameFormatter(func(c *fiber.Ctx) string {
        return fmt.Sprintf("%s %s", c.Method(), c.Path())
    }),
    otelfiber.WithTracerProvider(tp),
    otelfiber.WithMeterProvider(mp),
))

func handler(c *fiber.Ctx) error {
    ctx := c.UserContext()  // NOT c.Context() — that returns fasthttp.RequestCtx
    ctx, span := otel.Tracer("svc").Start(ctx, "op")
    defer span.End()
    return nil
}
```

## Common Patterns

### Error Recording

```go
span.RecordError(err)                     // adds error event with stack trace
span.SetStatus(codes.Error, err.Error())  // marks span as failed
```

Always call both. `RecordError` alone does not set span status.

### Span Naming and Context Extraction

| Framework | Default Span Name | Get context.Context |
|-----------|------------------|---------------------|
| Gin | Route template `/users/:id` | `c.Request.Context()` |
| Echo | Route template `/users/:id` | `c.Request().Context()` |
| Chi | Pattern needs `WithChiRoutes` | `r.Context()` |
| Fiber | Route template `/users/:id` | `c.UserContext()` |
