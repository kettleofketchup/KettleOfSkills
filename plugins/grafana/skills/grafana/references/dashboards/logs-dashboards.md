# Log Dashboards & Alerting

## Log Panel Types

### Logs Panel (type: logs)
```json
{
  "type": "logs",
  "datasource": { "type": "loki", "uid": "${DS_LOKI}" },
  "targets": [{ "expr": "{namespace=\"$namespace\"} |= \"$search\" | json | level=~\"$level\"", "maxLines": 500 }],
  "options": { "showTime": true, "wrapLogMessage": true, "prettifyLogMessage": true, "enableLogDetails": true, "sortOrder": "Descending" }
}
```

### Log Volume Histogram (type: timeseries, stacked bars)
```logql
sum by (level) (count_over_time({namespace="$namespace"} | json | keep level [$__auto]))
```
Color overrides: error=red, warn=yellow, info=green, debug=blue

### Error Rate from Logs (type: stat)
```logql
sum(rate({namespace="$namespace"} |= "error" [$__auto]))
  / sum(rate({namespace="$namespace"} [$__auto])) * 100
```

## App-Specific Log Queries

### Traefik Access Logs (JSON)
```logql
# 5xx errors with detail
{namespace="traefik"} | json | DownstreamStatus >= 500
  | line_format "{{.RequestMethod}} {{.RequestPath}} -> {{.DownstreamStatus}} ({{.ServiceName}})"

# Slow requests (Duration in nanoseconds)
{namespace="traefik"} | json | Duration > 5000000000

# Error rate by service
sum by (ServiceName) (rate({namespace="traefik"} | json | DownstreamStatus >= 500 [$__auto]))

# Request rate by host
sum by (RequestHost) (rate({namespace="traefik"} | json [$__auto]))

# P99 latency by host (ns to ms)
quantile_over_time(0.99, {namespace="traefik"} | json | unwrap Duration | __error__="" [5m]) by (RequestHost) / 1000000
```

### CNPG PostgreSQL Logs (JSON, nested record)
```logql
# PostgreSQL errors
{namespace="authentik", pod=~".*-pg-.*"} | json | logger="postgres" | record_error_severity=~"ERROR|FATAL|PANIC"

# Formatted output
  | line_format "{{.record_error_severity}}: {{.record_message}} | db={{.record_database_name}}"

# WAL archiving errors
{namespace="nextcloud", pod=~".*-pg-.*"} | json | logger=~"barman-cloud-wal-archive" | level="error"

# Deadlock detection
{namespace="authentik", pod=~".*-pg-.*"} | json | logger="postgres" |= "deadlock detected"
```

### ArgoCD Logs (logfmt/JSON)
```logql
# Sync failures
{namespace="argocd", container="argocd-application-controller"} | json | level="error" |= "sync"

# Git errors
{namespace="argocd", container="argocd-repo-server"} | json | level="error" |~ "git|clone|fetch"

# OutOfSync detection
{namespace="argocd", container="argocd-application-controller"} |= "OutOfSync"
```

### Authentik Logs (JSON)
```logql
# Auth failures
{namespace="authentik", container="server"} |= "login" |~ "fail|denied"

# Flow errors
{namespace="authentik", container="server"} |= "flow" | json | level="error"

# Worker task failures
{namespace="authentik", container="worker"} | json | level="error"
```

### Ceph Logs
```logql
# Health warnings/errors
{namespace=~"rook-ceph.*"} |= "HEALTH_WARN" or |= "HEALTH_ERR"

# Slow OSD operations
{namespace=~"rook-ceph.*"} |= "SLOW_OPS" or |= "slow request"

# OSD down events
{namespace=~"rook-ceph.*"} |= "marked down"

# Rook operator errors
{namespace="rook-ceph", container="rook-ceph-operator"} | json | level="error"
```

### K8s Events (via eventrouter)
```logql
{job="eventrouter"} |= "CrashLoopBackOff"
{job="eventrouter"} |= "OOMKilling"
{job="eventrouter"} |= "FailedScheduling"
{job="eventrouter"} |= "Failed to pull image"
{job="eventrouter"} |= "FailedMount" or |= "FailedAttachVolume"
{job="eventrouter"} |= "Unhealthy" |~ "Liveness|Readiness"
```

## Log-Based Alerting (Loki Ruler)

Enable in Loki Helm values:
```yaml
loki:
  rulerConfig:
    alertmanager_url: http://alertmanager.monitoring.svc:9093
    storage: { type: local, local: { directory: /etc/loki/rules } }
    enable_api: true
```

### Alert Rules
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

## Split-View Dashboard Variables

```json
{ "name": "namespace", "type": "query", "datasource": "loki", "query": { "type": 1, "label": "namespace" } },
{ "name": "pod", "type": "query", "datasource": "loki", "query": { "type": 1, "label": "pod", "stream": "{namespace=~\"$namespace\"}" } },
{ "name": "search", "type": "textbox" },
{ "name": "level", "type": "custom", "query": "info,warn,error,debug,fatal", "multi": true, "includeAll": true }
```

Layout: Log Volume (h=6) -> Error Rate + Throughput (h=6, side-by-side) -> Log Lines (h=18)
