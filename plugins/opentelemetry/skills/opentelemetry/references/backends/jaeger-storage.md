---
last_updated: 2026-03-08
---

# Jaeger Storage, Config, and Troubleshooting

## Storage Options

| Backend | Use Case | Retention |
|---------|----------|-----------|
| In-memory | Dev/testing only | Lost on restart |
| Badger | Single-node, low volume | Local disk |
| Elasticsearch | Production, full-text search | Configurable |
| Cassandra | Production, high write throughput | Configurable |
| ClickHouse | Production, columnar analytics | Configurable |

## Jaeger v2 Config (OTEL Collector-Based)

Jaeger v2 uses OTEL Collector pipeline architecture:

```yaml
# jaeger-v2-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:

exporters:
  jaeger_storage_exporter:
    trace_storage: es-main

extensions:
  jaeger_storage:
    backends:
      es-main:
        elasticsearch:
          server_urls: http://elasticsearch:9200
          index_prefix: jaeger

service:
  extensions: [jaeger_storage]
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [jaeger_storage_exporter]
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| No traces appearing | Wrong exporter endpoint | Verify collector -> jaeger connectivity |
| Missing spans | Context not propagated | Check `ctx` passed through call chain |
| Spans but no service name | Missing resource attributes | Set `service.name` in TracerProvider resource |
| High memory usage | In-memory storage | Switch to persistent storage backend |
