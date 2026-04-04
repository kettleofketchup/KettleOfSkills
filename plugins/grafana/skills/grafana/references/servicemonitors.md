# ServiceMonitors & PodMonitors

## ServiceMonitor

Tells Prometheus to scrape metrics from a Kubernetes Service's endpoints.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: <app>-metrics
  namespace: <app-namespace>    # or monitoring
  labels:
    release: kube-prometheus-stack  # optional if nilUsesHelmValues=false
spec:
  selector:
    matchLabels:
      app: <app-label>          # must match Service labels
  namespaceSelector:
    matchNames:
      - <target-namespace>
  endpoints:
    - port: metrics             # must match Service port name
      interval: 30s
      path: /metrics
```

### Cross-Namespace Scraping

Prometheus must have `serviceMonitorSelectorNilUsesHelmValues: false` to discover ServiceMonitors outside `monitoring` namespace.

Place ServiceMonitor in either:
- The app's namespace (co-located) - simpler, discovered by `namespaceSelector: any: true`
- The `monitoring` namespace - centralized, use `namespaceSelector.matchNames`

## PodMonitor

Scrape pods directly (no Service needed):

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: <app>-pods
  namespace: <namespace>
spec:
  selector:
    matchLabels:
      app: <app-label>
  podMetricsEndpoints:
    - port: metrics
      interval: 30s
```

## PrometheusRule

Custom alerting and recording rules:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: <app>-alerts
  namespace: monitoring
spec:
  groups:
    - name: <app>.rules
      rules:
        - alert: HighErrorRate
          expr: rate(http_requests_total{code=~"5.."}[5m]) > 0.1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High error rate on {{ $labels.instance }}"
```

## App-Specific ServiceMonitors

### Traefik

Traefik already has metrics enabled (`metrics.prometheus.enabled: true` in Helm values).

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: traefik
  namespace: traefik
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: traefik
  endpoints:
    - port: metrics
      interval: 15s
```

Key metrics: `traefik_entrypoint_requests_total`, `traefik_router_requests_total`, `traefik_service_requests_total`, `traefik_entrypoint_request_duration_seconds_bucket`

### Rook-Ceph

Enable Ceph Prometheus module in rook-ceph-cluster Helm values:

```yaml
monitoring:
  enabled: true
  createPrometheusRules: true
```

This creates ServiceMonitor automatically. Key metrics: `ceph_health_status`, `ceph_osd_up`, `ceph_osd_stat_bytes_used`, `ceph_pool_stored_raw`, `ceph_pg_active`

Ceph dashboard JSON IDs (import from grafana.com):
- `2842` - Ceph Cluster
- `5336` - Ceph OSD
- `5342` - Ceph Pools

### CloudNativePG (PostgreSQL)

CNPG exports metrics on pod port `9187` by default.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: cnpg-metrics
  namespace: monitoring
spec:
  namespaceSelector:
    any: true
  selector:
    matchLabels:
      cnpg.io/podRole: instance
  podMetricsEndpoints:
    - port: metrics
```

Key metrics: `cnpg_collector_up`, `cnpg_collector_pg_stat_activity_count`, `cnpg_collector_pg_replication_lag`, `cnpg_collector_pg_database_size_bytes`

CNPG dashboard from grafana.com: `20417`

### ArgoCD

ArgoCD already configures ServiceMonitors when Prometheus is detected:

```yaml
# In ArgoCD Helm values
controller:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
server:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
repoServer:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
applicationSet:
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
```

Key metrics: `argocd_app_info`, `argocd_app_sync_total`, `argocd_app_health_status`, `argocd_git_request_total`

### Authentik

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: authentik
  namespace: authentik
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: authentik
      app.kubernetes.io/component: server
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

Key metrics: `authentik_login_total`, `authentik_flows_total`, `authentik_outpost_connection`, `django_http_requests_total`

## Community Dashboards

Import from grafana.com: `curl -sL https://grafana.com/api/dashboards/<id>/revisions/latest/download -o dashboard.json`, then wrap in ConfigMap with `grafana_dashboard: "1"` label (see dashboard-creation.md).
