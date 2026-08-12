---
name: opentelemetry
description: Instruments Go, Python (Django, FastAPI), and Node.js (Express, NestJS) with OTEL tracing, metrics, and log correlation. Covers OTEL Collector, Jaeger, Tempo/Grafana, and Gin/Echo/Chi/Fiber.
last_updated: 2026-03-08
---

# OpenTelemetry

Vendor-neutral observability framework for distributed tracing, metrics, and logs. Provides SDKs for application instrumentation and a Collector for receiving, processing, and exporting telemetry data.

## Architecture

```
App (SDK) → OTEL Collector → Backend (Jaeger / Tempo+Grafana)
    ↓              ↓
  Traces       Pipelines:
  Metrics      receivers → processors → exporters
  Logs
```

## Task Reference

### Go Instrumentation
- SDK setup, TracerProvider, HTTP/gRPC middleware → [references/languages/go.md](references/languages/go.md)
- Database tracing, context rules, semconv → [references/languages/go-advanced.md](references/languages/go-advanced.md)

### Trace Backends
- Jaeger deployment, UI, query patterns → [references/backends/jaeger.md](references/backends/jaeger.md)
- Jaeger storage backends, v2 config → [references/backends/jaeger-storage.md](references/backends/jaeger-storage.md)
- Tempo + Grafana + TraceQL queries → [references/backends/tempo-grafana.md](references/backends/tempo-grafana.md)
- Grafana panels, trace-to-logs, troubleshooting → [references/backends/tempo-panels.md](references/backends/tempo-panels.md)

### Observability Pillars
- Spans, context propagation, sampling → [references/observability/tracing.md](references/observability/tracing.md)
- Performance patterns, span best practices → [references/observability/tracing-patterns.md](references/observability/tracing-patterns.md)
- Metrics SDK, custom metrics, exemplars, RED → [references/observability/metrics.md](references/observability/metrics.md)
- Metrics views, Prometheus compatibility → [references/observability/metrics-advanced.md](references/observability/metrics-advanced.md)
- Structured logging with trace/span IDs → [references/observability/log-correlation.md](references/observability/log-correlation.md)
- Grafana Loki config, OTEL log pipeline → [references/observability/log-pipeline.md](references/observability/log-pipeline.md)

### Framework Instrumentation
- Django auto/manual instrumentation, ORM → [references/frameworks/django.md](references/frameworks/django.md)
- Django Celery, DRF, common mistakes → [references/frameworks/django-advanced.md](references/frameworks/django-advanced.md)
- FastAPI instrumentation, SQLAlchemy, async → [references/frameworks/fastapi.md](references/frameworks/fastapi.md)
- FastAPI background tasks, common mistakes → [references/frameworks/fastapi-advanced.md](references/frameworks/fastapi-advanced.md)
- Go frameworks: Gin middleware → [references/frameworks/gin.md](references/frameworks/gin.md)
- Echo, Chi, Fiber, common Go patterns → [references/frameworks/gin-advanced.md](references/frameworks/gin-advanced.md)
- Node.js: Express bootstrap, manual spans → [references/frameworks/express.md](references/frameworks/express.md)
- NestJS, Fastify, DB tracing, common mistakes → [references/frameworks/express-advanced.md](references/frameworks/express-advanced.md)

### Collector Infrastructure
- OTEL Collector on Kubernetes (DaemonSet/Sidecar) → [references/collector/setup.md](references/collector/setup.md)
- Processors, app config, health, troubleshooting → [references/collector/collector-advanced.md](references/collector/collector-advanced.md)

## Quick Start (Go)

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

func initTracer(ctx context.Context) (*sdktrace.TracerProvider, error) {
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint("otel-collector:4317"),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }
    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceNameKey.String("my-service"),
        )),
    )
    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.TraceContext{})
    return tp, nil
}
```

## Identifying Slowdowns

1. Add spans around suspected slow operations (DB queries, HTTP calls, processing loops)
2. Add timing attributes — `span.SetAttributes(attribute.Int64("db.rows", count))`
3. Query in Jaeger/Tempo — filter by `duration > 500ms` or sort by duration
4. Drill into trace waterfall — identify which child span dominates total latency
5. Use exemplars — link slow metric samples directly to the trace that caused them

See [references/observability/tracing.md](references/observability/tracing.md) for detailed span analysis patterns.

## Key Go Packages

| Package | Purpose |
|---------|---------|
| `go.opentelemetry.io/otel` | Core API (tracer, propagation) |
| `go.opentelemetry.io/otel/sdk/trace` | TracerProvider, SpanProcessor |
| `go.opentelemetry.io/otel/sdk/metric` | MeterProvider, metric instruments |
| `go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc` | OTLP gRPC trace exporter |
| `go.opentelemetry.io/otel/exporters/otlp/otlpmetric/otlpmetricgrpc` | OTLP gRPC metric exporter |
| `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp` | HTTP middleware |
| `go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc` | gRPC interceptors |
| `go.opentelemetry.io/otel/semconv/v1.26.0` | Semantic conventions |

## Key Python Packages

| Package | Purpose |
|---------|---------|
| `opentelemetry-api` | Core API |
| `opentelemetry-sdk` | TracerProvider, MeterProvider |
| `opentelemetry-exporter-otlp-proto-grpc` | OTLP gRPC exporter |
| `opentelemetry-instrumentation-django` | Django auto-instrumentation |
| `opentelemetry-instrumentation-fastapi` | FastAPI auto-instrumentation |
| `opentelemetry-instrumentation-sqlalchemy` | SQLAlchemy query tracing |
| `opentelemetry-instrumentation-requests` | requests library tracing |
| `opentelemetry-instrumentation-httpx` | httpx async client tracing |

## Key Node.js Packages

| Package | Purpose |
|---------|---------|
| `@opentelemetry/sdk-node` | Node.js SDK (TracerProvider, etc.) |
| `@opentelemetry/auto-instrumentations-node` | All auto-instrumentations |
| `@opentelemetry/instrumentation-express` | Express middleware |
| `@opentelemetry/instrumentation-nestjs-core` | NestJS interceptors |
| `@opentelemetry/instrumentation-fastify` | Fastify plugin |
| `@opentelemetry/exporter-trace-otlp-grpc` | OTLP gRPC exporter |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting `tp.Shutdown(ctx)` | Defer shutdown in main — flushes pending spans |
| Not propagating context | Always pass `ctx` through call chain, never `context.Background()` |
| Too many spans (span explosion) | Instrument boundaries (HTTP, DB, queue), not every function |
| Missing service.name resource | Always set via `semconv.ServiceNameKey` — required for backend grouping |
| Using `SimpleSpanProcessor` in prod | Use `BatchSpanProcessor` — batches exports, reduces overhead |

## Official Documentation
- [OpenTelemetry Go SDK](https://opentelemetry.io/docs/languages/go/)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/languages/python/)
- [OpenTelemetry JS SDK](https://opentelemetry.io/docs/languages/js/)
- [OTEL Collector](https://opentelemetry.io/docs/collector/)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)

> **Related skill:** For Grafana dashboards, Prometheus, and ServiceMonitors — see the `grafana` skill.
