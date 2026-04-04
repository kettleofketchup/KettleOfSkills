---
name: grafana
last_updated: 2026-03-23
description: "Grafana observability stack for self-hosted Kubernetes using kube-prometheus-stack. This skill should be used when deploying Grafana/Prometheus/Alertmanager via Helm, creating Grafana dashboards (JSON models, panels, variables, PromQL/LogQL queries), provisioning dashboards via ConfigMap sidecars or Git/ArgoCD, configuring datasources (Prometheus, Loki, Tempo, PostgreSQL), creating ServiceMonitors/PodMonitors for scraping app metrics, building cluster health dashboards, Ceph storage monitoring, Traefik ingress metrics, app-specific dashboards, integrating Grafana authentication with Authentik OAuth2/OIDC, designing multi-signal dashboards with collapsible rows (metrics/logs/traces), configuring bidirectional Loki-Tempo cross-signal correlation, setting up OTEL Collector spanmetrics connectors for trace-derived RED metrics, using datasource template variables for portable dashboards, or delivering dashboards via dedicated Helm charts with .Files.Get."
---

# Grafana Observability Stack

Full observability stack for self-hosted Kubernetes via `kube-prometheus-stack` Helm chart. Bundles Grafana, Prometheus, Alertmanager, node-exporter, kube-state-metrics, and default recording/alerting rules.

## Deployment

### kube-prometheus-stack

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -f values.yaml -n monitoring --create-namespace
```

For ArgoCD app-of-apps pattern, Helm values structure, CRD management, and namespace configuration, see [kube-prometheus-stack.md](references/kube-prometheus-stack.md).

### Additional Stack Components

Loki (logs), Tempo (traces) deploy as separate Helm charts in the same namespace:
- `grafana/loki` - log aggregation (Promtail/Alloy as agent)
- `grafana/tempo` - distributed tracing
- See [datasources.md](references/datasources.md) for configuration

## Task Reference

### Dashboard Creation
Build Grafana dashboards: JSON model structure, panel types (timeseries, stat, gauge, table, logs, heatmap), template variables, PromQL/LogQL query patterns.
- Provisioning via ConfigMap sidecar (label: `grafana_dashboard: "1"`)
- Git-based provisioning via ArgoCD kustomize overlay
- See [dashboard-creation.md](references/dashboard-creation.md)

### Datasource Configuration
Configure Prometheus, Loki, Tempo, and PostgreSQL datasources.
- Provisioned via Helm values (`additionalDataSources`) or ConfigMap sidecar
- Tempo-to-Prometheus exemplar linking, Loki derived fields for trace correlation
- See [datasources.md](references/datasources.md)

### ServiceMonitors & PodMonitors
Expose application metrics for Prometheus scraping.
- ServiceMonitor for Service-backed endpoints (Traefik, ArgoCD, CNPG, Rook-Ceph)
- PodMonitor for direct pod scraping
- PrometheusRule for custom alerting/recording rules
- See [servicemonitors.md](references/servicemonitors.md)

### Authentik OIDC Integration
SSO login via Authentik OAuth2/OIDC provider.
- Grafana `auth.generic_oauth` configuration via Helm values
- Role mapping: Authentik groups to Grafana roles (Admin/Editor/Viewer)
- See [authentik-oidc.md](references/authentik-oidc.md)

## Domain-Specific Dashboards

Detailed panel layouts, PromQL/LogQL queries, and metric references per domain:

| Dashboard | Reference |
|-----------|-----------|
| Kubernetes cluster health | [dashboards/cluster-health.md](references/dashboards/cluster-health.md) |
| Ceph storage monitoring | [dashboards/ceph-storage.md](references/dashboards/ceph-storage.md) |
| Traefik ingress/networking | [dashboards/traefik-networking.md](references/dashboards/traefik-networking.md) |
| CNPG, ArgoCD, Authentik | [dashboards/applications.md](references/dashboards/applications.md) |
| LogQL syntax reference | [dashboards/logs-logql.md](references/dashboards/logs-logql.md) |
| Log dashboards, alerting, app queries | [dashboards/logs-dashboards.md](references/dashboards/logs-dashboards.md) |

## Key Patterns

- kube-prometheus-stack CRDs must sync before the chart — use `ServerSideApply=true` and separate CRD app or `crds.enabled: true`
- Dashboard ConfigMaps must have label `grafana_dashboard: "1"` for sidecar pickup
- Datasource ConfigMaps need label `grafana_datasource: "1"`
- Cross-namespace ServiceMonitor scraping requires `prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues: false`
- Grafana persistent storage: use `persistence.enabled: true` with appropriate StorageClass for sqlite DB (dashboards provisioned from ConfigMaps survive restarts regardless)
