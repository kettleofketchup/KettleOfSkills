---
last_updated: 2026-03-08
---

# Distributed Tracing: Performance Patterns and Span Best Practices

## Performance Analysis Patterns

### Database Query Slowdowns

```go
ctx, span := tracer.Start(ctx, "db.query",
    trace.WithAttributes(
        semconv.DBQueryTextKey.String(query),
        semconv.DBSystemPostgreSQL,
    ),
)
defer span.End()

start := time.Now()
rows, err := db.QueryContext(ctx, query, args...)
queryDuration := time.Since(start)

span.SetAttributes(
    attribute.Float64("db.query_duration_ms", float64(queryDuration.Milliseconds())),
    attribute.Int("db.rows_returned", rowCount),
)
```

### N+1 Query Detection

Look for traces where a parent span has many identical child DB spans:

```
[500ms] GET /api/users
+-- [2ms] SELECT * FROM users
+-- [3ms] SELECT * FROM profiles WHERE user_id = 1
+-- [2ms] SELECT * FROM profiles WHERE user_id = 2
... (50 more)
```

Pattern: parent span with many short, similar children = N+1 problem.

### Concurrent vs Sequential Detection

Span waterfall reveals sequential operations that could be parallelized:

```
Sequential (bad -- 300ms total):
+-- [100ms] fetch-user       -----
+-- [100ms] fetch-orders           -----
+-- [100ms] fetch-preferences            -----

Concurrent (good -- 100ms total):
+-- [100ms] fetch-user       -----
+-- [100ms] fetch-orders     -----
+-- [100ms] fetch-preferences-----
```

## Span Best Practices

### What to Instrument
- HTTP/gRPC handler entry points (auto-instrumented with middleware)
- Database queries
- External HTTP/gRPC client calls
- Message queue publish/consume
- Cache operations
- Significant business logic boundaries

### What NOT to Instrument
- Every function call (span explosion)
- Pure computation without I/O
- Logging statements (use log correlation instead)
- Trivial operations (< 1ms, no failure modes)

### Naming Conventions

| Pattern | Example | Notes |
|---------|---------|-------|
| `{verb}.{noun}` | `get.user`, `process.order` | Business operations |
| `{component}.{operation}` | `db.query`, `cache.get` | Infrastructure operations |
| HTTP routes | `GET /api/users/{id}` | Auto-set by otelhttp, use route not full URL |

### Attributes for Debugging

```go
span.SetAttributes(
    attribute.String("user.id", userID),           // Request identity
    attribute.String("feature.flag", flagName),     // Feature flags
    attribute.Int("batch.size", len(items)),         // Batch sizing
    attribute.String("cache.status", "miss"),        // Cache behavior
    attribute.Float64("queue.lag_ms", lagMs),        // Queue health
)
```
