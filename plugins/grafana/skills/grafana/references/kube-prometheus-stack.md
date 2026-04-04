# kube-prometheus-stack Deployment

## Helm Chart

- Chart: `prometheus-community/kube-prometheus-stack`
- Repo: `https://prometheus-community.github.io/helm-charts`
- Includes: Grafana, Prometheus, Alertmanager, node-exporter, kube-state-metrics, Prometheus Operator

## ArgoCD Application (App-of-Apps)

### Pattern: Helm + Git Overlay

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
          # --- CRDs ---
          crds:
            enabled: true
          # --- Grafana ---
          grafana:
            enabled: true
            adminPassword: "" # set via secret or Authentik SSO
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
          # --- Prometheus ---
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
          # --- Alertmanager ---
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

### Grafana Sidecar

Automatic dashboard/datasource discovery via sidecar:

```yaml
grafana:
  sidecar:
    dashboards:
      enabled: true
      searchNamespace: ALL      # scan all namespaces
      folderAnnotation: grafana_folder  # organize by annotation
      provider:
        foldersFromFilesStructure: true
    datasources:
      enabled: true
      searchNamespace: ALL
```

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

## Git Overlay (apps/monitoring/)

Kustomize overlay for IngressRoute, additional dashboards, datasources:

```yaml
# apps/monitoring/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ingressroute.yaml
  - dashboards/          # ConfigMap-based dashboards
  - datasources/         # Additional datasource ConfigMaps
components:
  - ../_components/domain
replacements:
  - source:
      kind: ConfigMap
      name: cluster-config
      fieldPath: data.grafana_host
    targets:
      - select:
          kind: IngressRoute
          name: grafana
        fieldPaths:
          - spec.routes.0.match
        options:
          delimiter: "`"
          index: 1
```

### IngressRoute

```yaml
# apps/monitoring/ingressroute.yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: grafana
  namespace: monitoring
spec:
  entryPoints:
    - websecure
  routes:
    - match: Host(`DOMAIN`)
      kind: Rule
      services:
        - name: kube-prometheus-stack-grafana
          port: 80
  tls:
    secretName: wildcard-tls
```
