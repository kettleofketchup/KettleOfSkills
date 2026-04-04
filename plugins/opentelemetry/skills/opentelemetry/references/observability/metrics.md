---
last_updated: 2026-03-08
---

# OpenTelemetry Metrics

## MeterProvider Setup

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc"
    sdkmetric "go.opentelemetry.io/otel/sdk/metric"
    semconv "go.opentelemetry.io/otel/semconv/v1.34.0"
)

func InitMeter(ctx context.Context, serviceName, endpoint string) (func(context.Context) error, error) {
    exporter, err := otlpmetricgrpc.New(ctx,
        otlpmetricgrpc.WithEndpoint(endpoint), otlpmetricgrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }
    res, _ := resource.Merge(resource.Default(), resource.NewWithAttributes(
        semconv.SchemaURL, semconv.ServiceNameKey.String(serviceName),
    ))
    mp := sdkmetric.NewMeterProvider(
        sdkmetric.WithReader(sdkmetric.NewPeriodicReader(exporter)),
        sdkmetric.WithResource(res),
    )
    otel.SetMeterProvider(mp)
    return mp.Shutdown, nil
}
```

## Instrument Types

| Instrument | Type | Use Case |
|-----------|------|----------|
| Counter | Monotonic sum | Request count, bytes sent |
| UpDownCounter | Non-monotonic sum | Active connections, queue depth |
| Histogram | Distribution | Request latency, response size |
| Gauge | Current value | CPU usage, temperature |

## Creating Metrics

### Counter

```go
meter := otel.Meter("my-service/metrics")

requestCounter, _ := meter.Int64Counter("http.requests.total",
    metric.WithDescription("Total HTTP requests"),
    metric.WithUnit("{request}"),
)

requestCounter.Add(ctx, 1,
    metric.WithAttributes(
        attribute.String("http.method", "GET"),
        attribute.String("http.route", "/api/users"),
        attribute.Int("http.status_code", 200),
    ),
)
```

### Histogram (Latency)

```go
requestDuration, _ := meter.Float64Histogram("http.request.duration",
    metric.WithDescription("HTTP request duration"),
    metric.WithUnit("s"),
    metric.WithExplicitBucketBoundaries(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

start := time.Now()
// ... handle request
duration := time.Since(start).Seconds()
requestDuration.Record(ctx, duration,
    metric.WithAttributes(attribute.String("http.route", "/api/users")),
)
```

### UpDownCounter

```go
activeConnections, _ := meter.Int64UpDownCounter("connections.active",
    metric.WithDescription("Number of active connections"),
)
activeConnections.Add(ctx, 1)   // Increment
activeConnections.Add(ctx, -1)  // Decrement
```

### Gauge (Observable)

```go
meter.Float64ObservableGauge("system.memory.usage",
    metric.WithDescription("Memory usage in bytes"),
    metric.WithFloat64Callback(func(_ context.Context, o metric.Float64Observer) error {
        var m runtime.MemStats
        runtime.ReadMemStats(&m)
        o.Observe(float64(m.Alloc))
        return nil
    }),
)
```

## Exemplars

Exemplars link specific metric measurements to the trace that generated them. When viewing a latency spike in Grafana, click the exemplar dot to jump directly to the trace.

### How They Work

```go
// When recording metrics inside a traced request, exemplars are automatic
func handleRequest(ctx context.Context) {
    ctx, span := tracer.Start(ctx, "handleRequest")
    defer span.End()

    start := time.Now()
    // ... work
    duration := time.Since(start).Seconds()

    // If ctx has an active span, the SDK attaches trace_id/span_id as exemplar
    requestDuration.Record(ctx, duration,
        metric.WithAttributes(attribute.String("http.route", "/api/users")),
    )
}
```

### Exemplar Filter Config

```go
import "go.opentelemetry.io/otel/sdk/metric/exemplar"

mp := sdkmetric.NewMeterProvider(
    sdkmetric.WithExemplarFilter(exemplar.AlwaysOnFilter),
    // Other options:
    //   exemplar.TraceBasedFilter  (default — only sampled spans)
    //   exemplar.AlwaysOffFilter   (disable exemplars)
)
// Or set via env: OTEL_METRICS_EXEMPLAR_FILTER=always_on|trace_based|always_off
```

## RED Metrics Pattern

| Metric | Instrument | What It Measures |
|--------|-----------|------------------|
| **R**ate | Counter | Requests per second |
| **E**rrors | Counter | Failed requests per second |
| **D**uration | Histogram | Request latency distribution |

```go
func instrumentedHandler(ctx context.Context) {
    start := time.Now()
    requestCounter.Add(ctx, 1, metric.WithAttributes(attrs...))

    err := handleRequest(ctx)

    duration := time.Since(start).Seconds()
    requestDuration.Record(ctx, duration, metric.WithAttributes(attrs...))

    if err != nil {
        errorCounter.Add(ctx, 1, metric.WithAttributes(attrs...))
    }
}
```

## Views (Customizing Aggregation)

```go
// Custom histogram buckets for specific metric
view := sdkmetric.NewView(
    sdkmetric.Instrument{Name: "http.request.duration"},
    sdkmetric.Stream{
        Aggregation: sdkmetric.AggregationExplicitBucketHistogram{
            Boundaries: []float64{0.01, 0.05, 0.1, 0.5, 1.0, 5.0},
        },
    },
)

mp := sdkmetric.NewMeterProvider(
    sdkmetric.WithView(view),
)
```

## Prometheus Compatibility

```go
import "go.opentelemetry.io/otel/exporters/prometheus"

promExporter, _ := prometheus.New()
mp := sdkmetric.NewMeterProvider(
    sdkmetric.WithReader(promExporter),
)

// Expose /metrics endpoint
http.Handle("/metrics", promhttp.Handler())
```
