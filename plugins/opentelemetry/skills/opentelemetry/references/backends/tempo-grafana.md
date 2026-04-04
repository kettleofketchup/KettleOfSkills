---
last_updated: 2026-03-08
---

# Grafana Tempo + Grafana

> **Cross-reference:** For Grafana deployment (kube-prometheus-stack), dashboards, datasource provisioning, ServiceMonitors, and Authentik OIDC — see the `grafana` skill.

## Overview

Tempo is a high-scale, cost-effective trace backend by Grafana Labs. Only indexes trace ID — relies on object storage (S3, GCS, local). Pairs with Grafana for visualization and TraceQL for querying.

## Kubernetes Deployment (Helm)

### Tempo (Distributed Mode)

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install tempo grafana/tempo-distributed \
    --namespace observability --create-namespace \
    -f tempo-values.yaml
```

```yaml
# tempo-values.yaml
global:
  clusterDomain: cluster.local

storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: minio.storage.svc:9000
      access_key: ${S3_ACCESS_KEY}
      secret_key: ${S3_SECRET_KEY}
      insecure: true

traces:
  otlp:
    grpc:
      enabled: true
    http:
      enabled: true

metricsGenerator:
  enabled: true
  remoteWriteUrl: "http://prometheus.observability.svc:9090/api/v1/write"
```

### Tempo (Single Binary — Dev/Small Clusters)

```yaml
# tempo-values.yaml (tempo chart, not tempo-distributed)
tempo:
  storage:
    trace:
      backend: local
      local:
        path: /var/tempo/traces

  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318
```

```bash
helm install tempo grafana/tempo \
    --namespace observability -f tempo-values.yaml
```

## Grafana Datasource Configuration

```yaml
apiVersion: 1
datasources:
  - name: Tempo
    type: tempo
    access: proxy
    url: http://tempo-query-frontend.observability.svc:3100
    jsonData:
      tracesToLogsV2:
        datasourceUid: loki
        filterByTraceID: true
        filterBySpanID: true
      tracesToMetrics:
        datasourceUid: prometheus
        queries:
          - name: Request rate
            query: rate(traces_spanmetrics_calls_total{$$__tags}[5m])
      serviceMap:
        datasourceUid: prometheus
      nodeGraph:
        enabled: true
      lokiSearch:
        datasourceUid: loki
```

## TraceQL Query Language

### Basic Queries

```traceql
# Find traces by service name
{ resource.service.name = "my-service" }

# Find traces with errors
{ status = error }

# Find slow spans (> 500ms)
{ duration > 500ms }

# Find specific HTTP endpoints
{ span.http.route = "/api/users" }

# Combine conditions
{ resource.service.name = "my-service" && span.http.status_code >= 500 }
```

### Structural Queries (Span Relationships)

```traceql
# Parent-child: find DB calls within HTTP handlers
{ span.http.route = "/api/users" } >> { span.db.system = "postgresql" }

# Sibling spans: find parallel operations
{ name = "cache.get" } ~ { name = "db.query" }

# Ancestor (any depth): find DB calls anywhere under HTTP handler
{ span.http.route = "/api/users" } >> { span.db.system = "postgresql" }
```

### Aggregate Queries

```traceql
# Average duration by operation
{ resource.service.name = "my-service" } | avg(duration)

# Count errors by endpoint
{ status = error } | count() by(span.http.route)

# P99 latency
{ resource.service.name = "my-service" } | quantile_over_time(duration, 0.99)
```

### Finding Slowdowns

```traceql
# Traces where total duration > 2s
{ duration > 2s }

# Slow DB queries within a service
{ resource.service.name = "my-service" } >> { span.db.system = "postgresql" && duration > 100ms }

# Compare: find traces slower than usual for an endpoint
{ span.http.route = "/api/users" && duration > 1s }

# Identify which child span is slowest
{ resource.service.name = "my-service" } | max(duration) by(name)
```

## Connecting OTEL Collector to Tempo

```yaml
exporters:
  otlp/tempo:
    endpoint: tempo-distributor.observability.svc:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      exporters: [otlp/tempo]
```

## Metrics Generator (Span Metrics)

Tempo can generate RED metrics (Rate, Errors, Duration) from traces:

```yaml
# In tempo config
metrics_generator:
  processor:
    span_metrics:
      dimensions:
        - service.name
        - http.route
        - http.method
    service_graphs:
      enabled: true
  storage:
    path: /var/tempo/wal
  remote_write:
    - url: http://prometheus:9090/api/v1/write
```

Generated metrics available in Prometheus/Grafana:
- `traces_spanmetrics_calls_total` — request count
- `traces_spanmetrics_latency_bucket` — latency histogram
- `traces_service_graph_request_total` — service graph edges

## Grafana Panels for Traces

> For dashboard JSON model structure, panel types, and provisioning via ConfigMap sidecar — see the `grafana` skill's [dashboard-creation.md](../../grafana/references/dashboard-creation.md).

### Service Map
Enable `serviceMap` datasource — auto-generates topology from trace data.

### Trace-to-Logs
Click span → "View Logs" jumps to Loki logs filtered by trace ID.

### Trace-to-Metrics
Click span → "View Metrics" shows related Prometheus metrics.

### Exemplars
In Grafana metric panels, enable exemplars to show dots on graphs that link directly to traces. Requires metrics with exemplar support.

> For ServiceMonitor setup to scrape app metrics that correlate with traces — see the `grafana` skill's [servicemonitors.md](../../grafana/references/servicemonitors.md).

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No traces in Grafana | Wrong datasource URL | Point to `tempo-query-frontend` service |
| TraceQL returns empty | Traces not yet flushed | Wait for flush interval (default 30s) |
| "trace not found" by ID | Compaction not complete | Retry after compaction cycle |
| Missing span metrics | Metrics generator disabled | Enable `metricsGenerator.enabled: true` |
