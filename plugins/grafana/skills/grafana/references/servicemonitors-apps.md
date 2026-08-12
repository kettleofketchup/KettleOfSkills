# ServiceMonitors — CloudNativePG, ArgoCD, Authentik

## CloudNativePG (PostgreSQL)

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

Community dashboard: `20417`

## ArgoCD

ArgoCD configures ServiceMonitors when Prometheus is detected:

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

## Authentik

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

## Importing Community Dashboards

Download from grafana.com and wrap in a ConfigMap:

```bash
curl -sL https://grafana.com/api/dashboards/<id>/revisions/latest/download -o dashboard.json
```

Then create a ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-cnpg
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
  annotations:
    grafana_folder: "Applications"
data:
  cnpg.json: |-
    # paste dashboard.json content here
```

Or use kustomize `configMapGenerator` pointing at the JSON file — see [dashboard-provisioning.md](../dashboard-provisioning.md).
