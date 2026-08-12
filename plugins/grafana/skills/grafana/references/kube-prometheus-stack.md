# kube-prometheus-stack Deployment

## Helm Chart

- Chart: `prometheus-community/kube-prometheus-stack`
- Repo: `https://prometheus-community.github.io/helm-charts`
- Includes: Grafana, Prometheus, Alertmanager, node-exporter, kube-state-metrics, Prometheus Operator

## ArgoCD Application (App-of-Apps)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kube-prometheus-stack
  namespace: argocd
spec:
  project: default
  sources:
    - repoURL: https://prometheus-community.github.io/helm-charts
      chart: kube-prometheus-stack
      targetRevision: "72.*"
      helm:
        valuesObject:
          crds:
            enabled: true
          grafana:
            enabled: true
            adminPassword: ""
            sidecar:
              dashboards:
                enabled: true
                searchNamespace: ALL
                folderAnnotation: grafana_folder
                provider:
                  foldersFromFilesStructure: true
              datasources:
                enabled: true
                searchNamespace: ALL
            persistence:
              enabled: true
              storageClassName: ceph-block
              size: 5Gi
          prometheus:
            prometheusSpec:
              retention: 15d
              storageSpec:
                volumeClaimTemplate:
                  spec:
                    storageClassName: ceph-block
                    resources:
                      requests:
                        storage: 50Gi
              serviceMonitorSelectorNilUsesHelmValues: false
              podMonitorSelectorNilUsesHelmValues: false
              ruleSelectorNilUsesHelmValues: false
              probeSelectorNilUsesHelmValues: false
          alertmanager:
            alertmanagerSpec:
              storage:
                volumeClaimTemplate:
                  spec:
                    storageClassName: ceph-block
                    resources:
                      requests:
                        storage: 5Gi
    - repoURL: git@github.com:org/infra.git  # Edit: replace with your repo URL
      targetRevision: HEAD
      path: apps/monitoring
  destination:
    server: https://kubernetes.default.svc
    namespace: monitoring
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```

### CRD Management

`ServerSideApply=true` required — CRDs are large and exceed annotation size limits. Alternative: separate CRD-only app with `crds.enabled: false` on main chart.

## Essential Helm Values

### Selector Configuration (Cross-Namespace Scraping)

Set all selector values to `false` to scrape ServiceMonitors/PodMonitors from any namespace:

```yaml
prometheus:
  prometheusSpec:
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    ruleSelectorNilUsesHelmValues: false
    probeSelectorNilUsesHelmValues: false
```

Without this, only resources in the `monitoring` namespace with matching labels are scraped.

### Resource Limits (Production)

```yaml
prometheus:
  prometheusSpec:
    resources:
      requests: { cpu: 500m, memory: 2Gi }
      limits: { memory: 4Gi }
grafana:
  resources:
    requests: { cpu: 100m, memory: 256Mi }
    limits: { memory: 512Mi }
alertmanager:
  alertmanagerSpec:
    resources:
      requests: { cpu: 50m, memory: 64Mi }
      limits: { memory: 128Mi }
```

For Git overlay (apps/monitoring/) and IngressRoute setup, see [kube-prometheus-stack-overlay.md](kube-prometheus-stack-overlay.md).
