---
last_updated: 2026-03-08
---

# Tempo + Grafana: Slowdown Queries, Panels, and Troubleshooting

## TraceQL: Finding Slowdowns

```traceql
# Traces where total duration > 2s
{ duration > 2s }

# Slow DB queries within a service
{ resource.service.name = "my-service" } >> { span.db.system = "postgresql" && duration > 100ms }

# Find traces slower than usual for an endpoint
{ span.http.route = "/api/users" && duration > 1s }

# Identify which child span is slowest
{ resource.service.name = "my-service" } | max(duration) by(name)
```

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
