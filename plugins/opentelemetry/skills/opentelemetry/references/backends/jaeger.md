---
last_updated: 2026-03-08
---

# Jaeger Trace Backend

## Overview

Jaeger is an open-source distributed tracing platform. Jaeger v2 (current default, built on OTEL Collector) provides trace collection, storage, and a web UI. Jaeger v1 reached end-of-life on December 31, 2025.

## Kubernetes Deployment

### All-in-One (Dev/Testing)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
  namespace: observability
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/jaeger:2
          ports:
            - containerPort: 16686  # UI
            - containerPort: 4317   # OTLP gRPC
            - containerPort: 4318   # OTLP HTTP
---
apiVersion: v1
kind: Service
metadata:
  name: jaeger
  namespace: observability
spec:
  selector:
    app: jaeger
  ports:
    - name: ui
      port: 16686
    - name: otlp-grpc
      port: 4317
    - name: otlp-http
      port: 4318
```

## Ports Reference

| Port | Protocol | Purpose |
|------|----------|---------|
| 4317 | gRPC | OTLP trace receiver |
| 4318 | HTTP | OTLP trace receiver |
| 16686 | HTTP | Web UI |

Jaeger v2 uses OTLP natively -- prefer ports 4317/4318. Legacy ports (14250, 14268) are no longer needed.

## Connecting OTEL Collector to Jaeger

```yaml
exporters:
  otlp/jaeger:
    endpoint: jaeger.observability.svc:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      exporters: [otlp/jaeger]
```

## Direct SDK Export (No Collector)

```go
exporter, err := otlptracegrpc.New(ctx,
    otlptracegrpc.WithEndpoint("jaeger.observability.svc:4317"),
    otlptracegrpc.WithInsecure(),
)
```

## UI Query Patterns

### Finding Slow Traces

1. **Service dropdown**: select target service
2. **Operation dropdown**: filter specific endpoint
3. **Tags**: `http.status_code=500` or `error=true`
4. **Min Duration**: `500ms` to find slow requests
5. **Lookback**: time range for search

### Trace Comparison

Compare two traces side-by-side to identify differences in span timing. Select two traces from results, then use the "Compare" button.

### Dependency Graph

System Architecture tab shows service-to-service call graph with edge latencies.

### Useful Search Tags

| Tag | Example | Purpose |
|-----|---------|---------|
| `error=true` | Find failed requests | Error analysis |
| `http.status_code=500` | Server errors | Error drill-down |
| `http.method=POST` | Write operations | Mutation tracing |
| `db.system=postgresql` | Database spans | DB performance |
| `span.kind=client` | Outbound calls | Dependency analysis |

See [jaeger-storage.md](jaeger-storage.md) for storage backends, Jaeger v2 config, and troubleshooting.
