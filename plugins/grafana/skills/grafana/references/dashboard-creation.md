# Dashboard Creation

## JSON Model Structure

Every Grafana dashboard is a JSON object:

```json
{
  "title": "Dashboard Title",
  "uid": "unique-dashboard-id",
  "tags": ["kubernetes", "monitoring"],
  "timezone": "browser",
  "editable": true,
  "templating": { "list": [] },
  "panels": [],
  "time": { "from": "now-6h", "to": "now" },
  "refresh": "30s"
}
```

`uid` must be unique across the Grafana instance. Use lowercase-kebab-case (e.g., `k8s-cluster-health`).

## Panel Types

### Timeseries (default for metrics)
```json
{
  "type": "timeseries",
  "title": "CPU Usage",
  "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [{
    "expr": "sum(rate(container_cpu_usage_seconds_total{namespace=\"$namespace\"}[5m])) by (pod)",
    "legendFormat": "{{pod}}"
  }],
  "fieldConfig": {
    "defaults": { "unit": "percentunit", "min": 0 }
  }
}
```

### Stat, Gauge, Table, Logs

```json
{ "type": "stat", "title": "Total Pods",
  "targets": [{ "expr": "count(kube_pod_info{namespace=\"$namespace\"})" }],
  "fieldConfig": { "defaults": { "unit": "short" } } }
```

```json
{ "type": "gauge", "title": "Memory Usage %",
  "targets": [{ "expr": "node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes" }],
  "fieldConfig": { "defaults": { "unit": "percentunit", "min": 0, "max": 1,
    "thresholds": { "steps": [
      { "value": 0, "color": "green" }, { "value": 0.7, "color": "yellow" }, { "value": 0.9, "color": "red" }
    ]} }} }
```

```json
{ "type": "table", "title": "Pod Status",
  "targets": [{ "expr": "kube_pod_status_phase{namespace=\"$namespace\"}", "format": "table", "instant": true }],
  "transformations": [{ "id": "organize", "options": { "excludeByName": { "__name__": true } } }] }
```

```json
{ "type": "logs", "datasource": { "type": "loki", "uid": "loki" },
  "targets": [{ "expr": "{namespace=\"$namespace\", pod=~\"$pod.*\"}" }] }
```

## Template Variables

Define in `templating.list`.

### Datasource Variables (preferred over hardcoded UIDs)

```json
{
  "name": "datasource_prometheus",
  "type": "datasource",
  "query": "prometheus",
  "current": { "text": "default", "value": "default" }
}
```

For multi-signal dashboards define one per type: `datasource_prometheus`, `datasource_loki`, `datasource_tempo`.

### Query Variables

```json
{
  "name": "namespace", "type": "query",
  "datasource": { "type": "prometheus", "uid": "${datasource_prometheus}" },
  "query": "label_values(kube_pod_info, namespace)",
  "refresh": 2, "includeAll": true, "multi": true, "sort": 1
}
```

Common: `namespace`, `pod`, `node`, `instance`, `job`, `device`, `interface`, `mountpoint`.

## Row Organization

```json
{ "type": "row", "title": "CPU Metrics", "collapsed": false,
  "gridPos": { "h": 1, "w": 24, "x": 0, "y": 0 }, "panels": [] }
```

- `collapsed: false` — child panels follow row in top-level `panels` array
- `collapsed: true` — child panels go inside row's `panels` array

### Multi-Signal Dashboard Pattern (Metrics/Logs/Traces)

Use collapsible rows: Row 1 Metrics (open), Row 2 Logs (collapsed), Row 3 Traces (collapsed). Each row uses its own datasource variable.

For provisioning via ConfigMap sidecar, Git/ArgoCD, and Helm `.Files.Get` delivery, see [dashboard-provisioning.md](dashboard-provisioning.md).
