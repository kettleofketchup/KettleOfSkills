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

See [gin-advanced.md](gin-advanced.md) for Echo, Chi, Fiber middleware setup and common patterns.
