---
last_updated: 2026-03-08
---

# Grafana Tempo + Grafana

> **Cross-reference:** For Grafana deployment (kube-prometheus-stack), dashboards, datasource provisioning, ServiceMonitors, and Authentik OIDC — see the `grafana` skill.

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

See [tempo-panels.md](tempo-panels.md) for TraceQL slowdown queries, Grafana panel types, and troubleshooting.
See [tempo-metrics.md](tempo-metrics.md) for OTEL Collector to Tempo config, Metrics Generator, and span metrics.
