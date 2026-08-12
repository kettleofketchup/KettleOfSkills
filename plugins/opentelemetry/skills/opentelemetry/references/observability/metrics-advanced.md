---
last_updated: 2026-03-08
---

# OTEL Metrics: Views and Prometheus Compatibility

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
