---
name: opentelemetry
description: OpenTelemetry (OTEL) distributed tracing, metrics, and log correlation. Use when instrumenting Go, Python (Django, FastAPI), or Node.js (Express, NestJS) applications with tracing/spans, instrumenting HTTP handlers or database queries, deploying OTEL Collector on Kubernetes, configuring Jaeger or Tempo/Grafana backends, identifying performance slowdowns via span analysis, correlating logs with trace context, setting up metrics with exemplars, or adding OTEL to Gin/Echo/Chi/Fiber frameworks.
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
- SDK setup, TracerProvider, SpanProcessor → [references/languages/go.md](references/languages/go.md)
- Creating spans, attributes, events, status → [references/languages/go.md](references/languages/go.md)
- HTTP/gRPC middleware, database tracing → [references/languages/go.md](references/languages/go.md)

### Trace Backends
- Jaeger deployment, UI, query patterns → [references/backends/jaeger.md](references/backends/jaeger.md)
- Tempo + Grafana + TraceQL queries → [references/backends/tempo-grafana.md](references/backends/tempo-grafana.md)

### Observability Pillars
- Spans, context propagation, sampling, perf analysis → [references/observability/tracing.md](references/observability/tracing.md)
- Metrics SDK, custom metrics, exemplars → [references/observability/metrics.md](references/observability/metrics.md)
- Structured logging with trace/span IDs → [references/observability/log-correlation.md](references/observability/log-correlation.md)

### Framework Instrumentation
- Django auto/manual instrumentation, ORM tracing → [references/frameworks/django.md](references/frameworks/django.md)
- FastAPI instrumentation, SQLAlchemy, async patterns → [references/frameworks/fastapi.md](references/frameworks/fastapi.md)
- Go frameworks: Gin, Echo, Chi, Fiber middleware → [references/frameworks/gin.md](references/frameworks/gin.md)
- Node.js: Express, NestJS, Fastify, Prisma → [references/frameworks/express.md](references/frameworks/express.md)

### Collector Infrastructure
- OTEL Collector on Kubernetes (DaemonSet/Sidecar) → [references/collector/setup.md](references/collector/setup.md)
- Pipeline config (receivers, processors, exporters) → [references/collector/setup.md](references/collector/setup.md)

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
