---
last_updated: 2026-03-08
---

# Log Correlation with Traces

## Overview

Log correlation injects trace context (trace ID, span ID) into log entries. Enables jumping from a log line to its trace in Jaeger/Tempo, and from a trace span to related logs in Loki/Elasticsearch.

## Go slog Integration

### Bridge Setup

```go
import (
    "log/slog"

    "go.opentelemetry.io/contrib/bridges/otelslog"
    "go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploggrpc"
    sdklog "go.opentelemetry.io/otel/sdk/log"
)

func InitLogger(ctx context.Context, serviceName, collectorEndpoint string) (func(context.Context) error, error) {
    exporter, err := otlploggrpc.New(ctx,
        otlploggrpc.WithEndpoint(collectorEndpoint),
        otlploggrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }

    lp := sdklog.NewLoggerProvider(
        sdklog.WithProcessor(sdklog.NewBatchProcessor(exporter)),
        sdklog.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceNameKey.String(serviceName),
        )),
    )

    // Create slog handler that sends to OTEL
    handler := otelslog.NewHandler("my-service", otelslog.WithLoggerProvider(lp))
    slog.SetDefault(slog.New(handler))

    return lp.Shutdown, nil
}
```

### Usage

```go
// When called within a traced context, trace_id and span_id are auto-injected
func handleRequest(ctx context.Context, userID string) {
    ctx, span := tracer.Start(ctx, "handleRequest")
    defer span.End()

    slog.InfoContext(ctx, "processing request",
        "user_id", userID,
    )

    result, err := processOrder(ctx)
    if err != nil {
        slog.ErrorContext(ctx, "order processing failed",
            "error", err,
            "user_id", userID,
        )
    }
}
```

Output includes trace context automatically:
```json
{
    "level": "INFO",
    "msg": "processing request",
    "user_id": "u123",
    "trace_id": "abc123def456...",
    "span_id": "1234567890abcdef"
}
```

## Manual Trace Context Extraction

If not using the OTEL slog bridge, extract trace context manually:

```go
import "go.opentelemetry.io/otel/trace"

func logWithTrace(ctx context.Context, msg string, args ...any) {
    spanCtx := trace.SpanContextFromContext(ctx)
    if spanCtx.IsValid() {
        args = append(args,
            "trace_id", spanCtx.TraceID().String(),
            "span_id", spanCtx.SpanID().String(),
        )
    }
    slog.Info(msg, args...)
}
```

## Structured Logging Best Practices

### Always Use Context

```go
// Good -- trace context flows through
slog.InfoContext(ctx, "user authenticated", "user_id", id)

// Bad -- no trace correlation possible
slog.Info("user authenticated", "user_id", id)
```

### Log at Span Boundaries

```go
func processOrder(ctx context.Context, order Order) error {
    ctx, span := tracer.Start(ctx, "processOrder")
    defer span.End()

    slog.InfoContext(ctx, "order processing started",
        "order_id", order.ID,
        "item_count", len(order.Items),
    )

    if err != nil {
        // Log AND record on span -- logs for searching, span for trace view
        slog.ErrorContext(ctx, "order validation failed",
            "order_id", order.ID,
            "error", err,
        )
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return err
    }
    return nil
}
```

### Avoid Redundancy

Don't duplicate info already in span attributes (otelhttp records method, path, status). Log only business-relevant context:

```go
slog.InfoContext(ctx, "order created", "order_id", order.ID, "total", order.Total)
```

## Grafana: Logs-to-Traces

### Loki Datasource Config

```yaml
datasources:
  - name: Loki
    type: loki
    url: http://loki.observability.svc:3100
    jsonData:
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: "trace_id=(\\w+)"
          name: TraceID
          url: "$${__value.raw}"
```

### Query Workflow

1. **Start from logs**: query Loki for errors: `{app="my-service"} |= "error"`
2. **Click trace ID link**: jumps to full trace in Tempo
3. **Or start from trace**: view span, click "Logs", filtered Loki query

## OTEL Collector Log Pipeline

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert

exporters:
  # Loki v3+ supports native OTLP ingestion — use otlphttp, not the deprecated loki exporter
  otlphttp/loki:
    endpoint: http://loki.observability.svc:3100/otlp

service:
  pipelines:
    logs:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [otlphttp/loki]
```
