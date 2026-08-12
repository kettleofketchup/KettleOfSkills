---
last_updated: 2026-03-08
---

# Log Correlation: Grafana and OTEL Collector Pipeline

## Grafana: Logs-to-Traces

### Loki Datasource Config

```yaml
datasources:
  - name: Loki
    type: loki
    url: http://loki.observability.svc:3100
    jsonData:
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: "trace_id=(\\w+)"
          name: TraceID
          url: "$${__value.raw}"
```

### Query Workflow

1. **Start from logs**: query Loki for errors: `{app="my-service"} |= "error"`
2. **Click trace ID link**: jumps to full trace in Tempo
3. **Or start from trace**: view span, click "Logs", filtered Loki query

## OTEL Collector Log Pipeline

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert

exporters:
  # Loki v3+ supports native OTLP ingestion — use otlphttp, not the deprecated loki exporter
  otlphttp/loki:
    endpoint: http://loki.observability.svc:3100/otlp

service:
  pipelines:
    logs:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [otlphttp/loki]
```
