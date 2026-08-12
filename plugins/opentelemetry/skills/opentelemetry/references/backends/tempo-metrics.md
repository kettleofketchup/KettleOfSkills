---
last_updated: 2026-03-08
---

# Tempo: Collector Config and Metrics Generator

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
