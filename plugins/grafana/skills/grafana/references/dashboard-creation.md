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

### Stat (single value)
```json
{
  "type": "stat",
  "title": "Total Pods",
  "targets": [{ "expr": "count(kube_pod_info{namespace=\"$namespace\"})" }],
  "fieldConfig": { "defaults": { "unit": "short" } }
}
```

### Gauge (percentage/bounded value)
```json
{
  "type": "gauge",
  "title": "Memory Usage %",
  "targets": [{ "expr": "node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes" }],
  "fieldConfig": {
    "defaults": {
      "unit": "percentunit", "min": 0, "max": 1,
      "thresholds": { "steps": [
        { "value": 0, "color": "green" },
        { "value": 0.7, "color": "yellow" },
        { "value": 0.9, "color": "red" }
      ]}
    }
  }
}
```

### Table
```json
{
  "type": "table",
  "title": "Pod Status",
  "targets": [{ "expr": "kube_pod_status_phase{namespace=\"$namespace\"}", "format": "table", "instant": true }],
  "transformations": [{ "id": "organize", "options": { "excludeByName": { "__name__": true } } }]
}
```

### Logs (Loki)
```json
{
  "type": "logs",
  "title": "Application Logs",
  "datasource": { "type": "loki", "uid": "loki" },
  "targets": [{ "expr": "{namespace=\"$namespace\", pod=~\"$pod.*\"}" }]
}
```

## Template Variables

Define in `templating.list`.

### Datasource Variables (preferred over hardcoded UIDs)

Decouple dashboards from specific datasource UIDs for portability:

```json
{
  "name": "datasource_prometheus",
  "type": "datasource",
  "query": "prometheus",
  "current": { "text": "default", "value": "default" }
}
```

Then reference in panels: `"datasource": {"type": "prometheus", "uid": "${datasource_prometheus}"}`.

For multi-signal dashboards, define one per datasource type:
- `datasource_prometheus` (type: `datasource`, query: `prometheus`)
- `datasource_loki` (type: `datasource`, query: `loki`)
- `datasource_tempo` (type: `datasource`, query: `tempo`)

### Query Variables

```json
{
  "name": "namespace",
  "type": "query",
  "datasource": { "type": "prometheus", "uid": "${datasource_prometheus}" },
  "query": "label_values(kube_pod_info, namespace)",
  "refresh": 2,
  "includeAll": true,
  "multi": true,
  "sort": 1
}
```

Common variables: `namespace`, `pod`, `node`, `instance`, `job`, `device`, `interface`, `mountpoint`.

Use `$variable` in queries: `{namespace="$namespace"}`.

## Row Organization

Group panels into collapsible rows:

```json
{
  "type": "row",
  "title": "CPU Metrics",
  "collapsed": false,
  "gridPos": { "h": 1, "w": 24, "x": 0, "y": 0 },
  "panels": []
}
```

### Collapsed vs Open Rows

- `collapsed: false` — child panels follow the row in the top-level `panels` array
- `collapsed: true` — child panels go inside the row's `panels` array

Default the most-viewed rows to open, secondary investigation rows to collapsed.

### Multi-Signal Dashboard Pattern (Metrics/Logs/Traces)

For service dashboards with all three observability signals, use collapsible rows:
- **Row 1: Metrics** (collapsed: false) — Prometheus panels (request rate, latency, error rate)
- **Row 2: Logs** (collapsed: true) — Loki log stream + log volume
- **Row 3: Traces** (collapsed: true) — Tempo trace search + duration histogram

Each row uses its own datasource variable. This pattern keeps everything for one service in a single dashboard URL while avoiding visual overload.

## Provisioning via ConfigMap (Sidecar)

Create ConfigMap with label `grafana_dashboard: "1"`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dashboard-cluster-health
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
  annotations:
    grafana_folder: "Kubernetes"
data:
  cluster-health.json: |
    { "title": "Cluster Health", "uid": "k8s-cluster-health", ... }
```

### Folder Organization
Use `grafana_folder` annotation to organize:
- `Kubernetes` - cluster-level dashboards
- `Storage` - Ceph/PV dashboards
- `Networking` - Traefik/ingress dashboards
- `Applications` - app-specific dashboards

### Helm Chart Delivery (`.Files.Get`)

For dedicated dashboard charts, store JSON in `dashboards/` and embed via Helm:

```yaml
# templates/cluster-overview.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-cluster-overview
  labels:
    grafana_dashboard: "1"
  annotations:
    grafana_folder: "Custom"  # Edit: replace with your folder name
data:
  cluster-overview.json: |-
    {{ .Files.Get "dashboards/cluster-overview.json" | nindent 4 }}
```

Hardcode the filename per template — do NOT nest `{{ }}` inside `.Files.Get`.

Benefits: separate ArgoCD Application for dashboards means faster syncs, dashboards change without touching chart dependencies.

### Large Dashboards
ConfigMaps have 1MB limit. Typical dashboard JSONs are 30-80KB. For very large dashboards, split into multiple ConfigMaps.

## Provisioning via Git (ArgoCD)

Store dashboard JSON files in `apps/monitoring/dashboards/`:

```yaml
# apps/monitoring/dashboards/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
configMapGenerator:
  - name: dashboard-cluster-health
    namespace: monitoring
    files:
      - cluster-health.json
    options:
      labels:
        grafana_dashboard: "1"
      annotations:
        grafana_folder: "Kubernetes"
      disableNameSuffixHash: true
```

## Domain-Specific Panels & Queries

For detailed panel layouts, PromQL/LogQL queries, and metric references per domain, see:
- [dashboards/cluster-health.md](dashboards/cluster-health.md) - K8s nodes, pods, workloads, PVCs
- [dashboards/ceph-storage.md](dashboards/ceph-storage.md) - Ceph health, IOPS, OSD, pools
- [dashboards/traefik-networking.md](dashboards/traefik-networking.md) - requests, latency, services
- [dashboards/applications.md](dashboards/applications.md) - CNPG, ArgoCD, Authentik
- [dashboards/logs-logql.md](dashboards/logs-logql.md) - LogQL syntax reference
- [dashboards/logs-dashboards.md](dashboards/logs-dashboards.md) - log panels, alerting, app queries
