# Log-Based Alerting and Trace Correlation

## Loki Ruler Configuration

Enable in Loki Helm values:
```yaml
loki:
  rulerConfig:
    alertmanager_url: http://alertmanager.monitoring.svc:9093
    storage: { type: local, local: { directory: /etc/loki/rules } }
    enable_api: true
```

## Alert Rules

```yaml
groups:
  - name: log-alerts
    rules:
      - alert: HighHTTPErrorRate
        expr: |
          sum(rate({namespace="traefik"} | json | DownstreamStatus >= 500 [5m]))
          / sum(rate({namespace="traefik"} | json [5m])) > 0.05
        for: 10m
        labels: { severity: critical }
        annotations: { summary: "5xx error rate above 5% for 10 minutes" }

      - alert: PostgreSQLErrors
        expr: |
          sum by (pod) (rate({pod=~".*-pg-.*"} | json | logger="postgres"
            | record_error_severity=~"ERROR|FATAL" [5m])) > 0.1
        for: 10m
        labels: { severity: warning }

      - alert: CephHealthError
        expr: count_over_time({namespace=~"rook-ceph.*"} |= "HEALTH_ERR" [5m]) > 0
        for: 5m
        labels: { severity: critical }

      - alert: ArgoSyncFailed
        expr: count_over_time({namespace="argocd"} |= "Sync operation" |= "Failed" [15m]) > 0
        for: 5m
        labels: { severity: warning }

      - alert: NoLogsFromNamespace
        expr: absent_over_time({namespace="traefik"}[15m])
        for: 15m
        labels: { severity: warning }
```

## Trace Correlation

Loki datasource derived fields for Tempo linking:
```yaml
derivedFields:
  - name: TraceID
    matcherRegex: "(?:traceID|trace_id|traceId)[=: ]\"?([a-fA-F0-9]{16,32})\"?"
    datasourceUid: tempo
    urlDisplayLabel: "View Trace"
    matcherType: regex
```

This adds a clickable "View Trace" link in Loki log lines that contain a trace ID, navigating directly to the Tempo trace explorer.

## Multi-Service Alert Grouping

For Alertmanager routing, group log-based alerts by namespace:

```yaml
# alertmanager.yaml route
route:
  group_by: ['alertname', 'namespace']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'
```

For log panel types and app-specific queries, see [logs-dashboards.md](logs-dashboards.md).
