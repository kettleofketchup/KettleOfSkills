---
last_updated: 2026-03-08
---

# Go OTEL: Database Tracing, Context, and Semantic Conventions

## Database Tracing

### Manual Span Wrapping

```go
func (r *repo) GetUser(ctx context.Context, id string) (*User, error) {
    ctx, span := tracer.Start(ctx, "db.GetUser", trace.WithAttributes(
        semconv.DBSystemPostgreSQL,
        semconv.DBQueryTextKey.String("SELECT * FROM users WHERE id = $1"),
    ))
    defer span.End()

    var user User
    if err := r.db.QueryRowContext(ctx, "SELECT ...", id).Scan(&user); err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, "query failed")
        return nil, err
    }
    return &user, nil
}
```

### With otelsql (Auto-Instrumented)

```go
import "github.com/XSAM/otelsql"

// Four ways to instrument: Open, OpenDB, Register, WrapDriver
db, err := otelsql.Open("postgres", dsn,
    otelsql.WithAttributes(semconv.DBSystemPostgreSQL),
)
// All queries automatically traced
otelsql.RegisterDBStatsMetrics(db, otelsql.WithAttributes(semconv.DBSystemPostgreSQL))
```

## Context Propagation Rules

1. **Always pass ctx** -- never use `context.Background()` mid-request
2. **Start child spans from parent ctx** -- `tracer.Start(ctx, "child")` returns new ctx
3. **HTTP clients inject headers** -- use `otelhttp.NewTransport` for automatic propagation
4. **Goroutines need ctx** -- pass ctx, or span ends before goroutine completes

```go
// Correct goroutine pattern
ctx, span := tracer.Start(ctx, "parallel-work")
defer span.End()

g, gCtx := errgroup.WithContext(ctx)
g.Go(func() error {
    return doWork(gCtx) // Uses group context
})
```

## Semantic Conventions

Use `semconv` package (`v1.34.0`+) for standard attribute names:

| Convention | Usage |
|-----------|-------|
| `semconv.HTTPRequestMethodKey` | HTTP method (GET, POST) |
| `semconv.HTTPResponseStatusCodeKey` | HTTP status code |
| `semconv.DBSystemPostgreSQL` | Database system type |
| `semconv.DBQueryTextKey` | Database query text (replaces `DBStatementKey`) |
| `semconv.RPCSystemGRPC` | gRPC system |
| `semconv.ServiceNameKey` | Service identifier |

Always prefer semconv attributes over custom strings -- backends can index and query these.
