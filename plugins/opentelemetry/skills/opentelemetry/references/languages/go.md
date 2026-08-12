---
last_updated: 2026-03-08
---

# Go OpenTelemetry Instrumentation

## SDK Setup

### Dependencies

```bash
go get go.opentelemetry.io/otel \
    go.opentelemetry.io/otel/sdk \
    go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc \
    go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc \
    go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp
```

### TracerProvider Initialization

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.34.0"
)

func InitTracer(ctx context.Context, serviceName, endpoint string) (func(context.Context) error, error) {
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint(endpoint),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, fmt.Errorf("creating trace exporter: %w", err)
    }

    res, _ := resource.Merge(resource.Default(), resource.NewWithAttributes(
        semconv.SchemaURL,
        semconv.ServiceNameKey.String(serviceName),
        semconv.ServiceVersionKey.String("1.0.0"),
    ))

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.AlwaysSample()), // Change for production
    )
    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{}, propagation.Baggage{},
    ))
    return tp.Shutdown, nil
}

// In main():
// shutdown, err := telemetry.InitTracer(ctx, "my-service", "otel-collector:4317")
// defer shutdown(ctx)
```

## Creating Spans

### Basic Span

```go
tracer := otel.Tracer("my-service/handler")

func handleRequest(ctx context.Context) error {
    ctx, span := tracer.Start(ctx, "handleRequest")
    defer span.End()

    result, err := processData(ctx, input)
    if err != nil {
        span.RecordError(err)
        span.SetStatus(codes.Error, err.Error())
        return err
    }

    span.SetAttributes(
        attribute.String("request.id", reqID),
        attribute.Int("result.count", len(result)),
    )
    return nil
}
```

### Span Events and Status

```go
span.AddEvent("cache.miss", trace.WithAttributes(
    attribute.String("cache.key", key),
))

// Only set Error status — Ok is implicit on success
span.SetStatus(codes.Error, "database connection failed")

// Record error with stack trace
span.RecordError(err, trace.WithStackTrace(true))
```

## HTTP Middleware (otelhttp)

```go
import "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"

// Server — wrap mux, creates span per request with HTTP attributes
handler := otelhttp.NewHandler(mux, "server",
    otelhttp.WithMessageEvents(otelhttp.ReadEvents, otelhttp.WriteEvents),
)

// Client — auto-creates spans and injects traceparent headers
client := &http.Client{Transport: otelhttp.NewTransport(http.DefaultTransport)}
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := client.Do(req)
```

## gRPC Instrumentation (StatsHandler)

```go
import "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"

// Server — use StatsHandler (interceptors are deprecated)
server := grpc.NewServer(
    grpc.StatsHandler(otelgrpc.NewServerHandler()),
)

// Client
conn, err := grpc.NewClient(target,
    grpc.WithStatsHandler(otelgrpc.NewClientHandler()),
)
```

See [go-advanced.md](go-advanced.md) for database tracing, context propagation rules, and semantic conventions.
