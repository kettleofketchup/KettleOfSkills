# kube-prometheus-stack — Git Overlay and IngressRoute

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

## IngressRoute

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

## Grafana Sidecar Configuration

Automatic dashboard/datasource discovery:

```yaml
grafana:
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
```

The sidecar watches all namespaces for ConfigMaps with label `grafana_dashboard: "1"` (dashboards) or `grafana_datasource: "1"` (datasources) and auto-loads them into Grafana without a restart.

## Namespace Configuration

All kube-prometheus-stack components deploy to the `monitoring` namespace by default. When using ArgoCD with a Git overlay (second source), the overlay path also targets `monitoring` namespace to keep all ConfigMaps co-located.

Dashboard ConfigMaps can be in any namespace when `searchNamespace: ALL` is set — the sidecar discovers them cluster-wide.

## Upgrading kube-prometheus-stack

CRDs are not automatically upgraded by Helm. Before upgrading across major versions:

```bash
# Check current version
helm list -n monitoring

# Pre-upgrade: apply CRDs manually or use --set crds.enabled=true
kubectl apply --server-side -f https://raw.githubusercontent.com/prometheus-community/helm-charts/main/charts/kube-prometheus-stack/charts/crds/crds/...

# Then upgrade
helm upgrade kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring -f values.yaml --set crds.enabled=true
```

Always check the chart's `CHANGELOG.md` for breaking changes before upgrading.
