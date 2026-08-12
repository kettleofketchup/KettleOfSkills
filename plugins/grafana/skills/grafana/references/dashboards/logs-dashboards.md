# Log Dashboards and App-Specific Log Queries

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
{namespace="traefik"} | json | DownstreamStatus >= 500
  | line_format "{{.RequestMethod}} {{.RequestPath}} -> {{.DownstreamStatus}} ({{.ServiceName}})"
{namespace="traefik"} | json | Duration > 5000000000  # Slow requests
sum by (ServiceName) (rate({namespace="traefik"} | json | DownstreamStatus >= 500 [$__auto]))
quantile_over_time(0.99, {namespace="traefik"} | json | unwrap Duration | __error__="" [5m]) by (RequestHost) / 1000000
```

### CNPG PostgreSQL Logs
```logql
{namespace="authentik", pod=~".*-pg-.*"} | json | logger="postgres" | record_error_severity=~"ERROR|FATAL|PANIC"
  | line_format "{{.record_error_severity}}: {{.record_message}} | db={{.record_database_name}}"
{namespace="nextcloud", pod=~".*-pg-.*"} | json | logger=~"barman-cloud-wal-archive" | level="error"
{namespace="authentik", pod=~".*-pg-.*"} | json | logger="postgres" |= "deadlock detected"
```

### ArgoCD and Authentik Logs
```logql
# ArgoCD sync failures
{namespace="argocd", container="argocd-application-controller"} | json | level="error" |= "sync"
{namespace="argocd", container="argocd-repo-server"} | json | level="error" |~ "git|clone|fetch"

# Authentik auth failures
{namespace="authentik", container="server"} |= "login" |~ "fail|denied"
{namespace="authentik", container="server"} |= "flow" | json | level="error"
{namespace="authentik", container="worker"} | json | level="error"
```

### Ceph and K8s Events
```logql
{namespace=~"rook-ceph.*"} |= "HEALTH_WARN" or |= "HEALTH_ERR"
{namespace=~"rook-ceph.*"} |= "SLOW_OPS" or |= "slow request"
{namespace="rook-ceph", container="rook-ceph-operator"} | json | level="error"
{job="eventrouter"} |= "CrashLoopBackOff"
{job="eventrouter"} |= "OOMKilling"
{job="eventrouter"} |= "FailedScheduling"
```

## Dashboard Variables

```json
{ "name": "namespace", "type": "query", "datasource": "loki", "query": { "type": 1, "label": "namespace" } },
{ "name": "pod", "type": "query", "datasource": "loki", "query": { "type": 1, "label": "pod", "stream": "{namespace=~\"$namespace\"}" } },
{ "name": "search", "type": "textbox" },
{ "name": "level", "type": "custom", "query": "info,warn,error,debug,fatal", "multi": true, "includeAll": true }
```

Layout: Log Volume (h=6) → Error Rate + Throughput (h=6, side-by-side) → Log Lines (h=18)

For Loki Ruler alerting rules and trace correlation config, see [logs-alerting.md](logs-alerting.md).
