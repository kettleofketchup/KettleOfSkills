# Dashboard Provisioning

## ConfigMap Sidecar

Create a ConfigMap with label `grafana_dashboard: "1"`:

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

Use `grafana_folder` annotation:
- `Kubernetes` — cluster-level dashboards
- `Storage` — Ceph/PV dashboards
- `Networking` — Traefik/ingress dashboards
- `Applications` — app-specific dashboards

### ConfigMap Size Limit

ConfigMaps have a 1MB limit. Typical dashboard JSONs are 30–80KB. For very large dashboards, split across multiple ConfigMaps.

## Helm Chart Delivery (`.Files.Get`)

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

## Domain-Specific Panels and Queries

For detailed panel layouts, PromQL/LogQL queries, and metric references per domain:

- [dashboards/cluster-health.md](dashboards/cluster-health.md) — K8s nodes, pods, workloads, PVCs
- [dashboards/ceph-storage.md](dashboards/ceph-storage.md) — Ceph health, IOPS, OSD, pools
- [dashboards/traefik-networking.md](dashboards/traefik-networking.md) — requests, latency, services
- [dashboards/applications-cnpg-argocd.md](dashboards/applications-cnpg-argocd.md) — CNPG, ArgoCD
- [dashboards/applications-authentik.md](dashboards/applications-authentik.md) — Authentik
- [dashboards/logs-logql.md](dashboards/logs-logql.md) — LogQL syntax reference
- [dashboards/logs-dashboards.md](dashboards/logs-dashboards.md) — log panels, app queries
- [dashboards/logs-alerting.md](dashboards/logs-alerting.md) — Loki alerting rules, trace correlation
