---
last_updated: 2026-03-09
---
# Helm Charts in Kustomize

Inflate Helm charts directly within kustomize. Requires `--enable-helm` flag (or ArgoCD's `kustomize.buildOptions: --enable-helm`).

## helmCharts

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

helmCharts:
  - name: ingress-nginx
    repo: https://kubernetes.github.io/ingress-nginx
    version: 4.8.3
    releaseName: ingress-nginx
    namespace: ingress-nginx
    valuesFile: values.yaml        # Relative path to values file
    valuesInline:                  # Inline values (merged with valuesFile)
      controller:
        replicaCount: 2
    includeCRDs: true              # Include CRDs in output (default false)
    skipTests: true                # Skip test resources (default false)
```

### Multiple charts
```yaml
helmCharts:
  - name: cert-manager
    repo: https://charts.jetstack.io
    version: v1.14.0
    namespace: cert-manager
    valuesInline:
      installCRDs: true
  - name: traefik
    repo: https://traefik.github.io/charts
    version: 28.0.0
    namespace: traefik
    valuesFile: traefik-values.yaml
```

## helmGlobals

Shared settings for all helmCharts entries:

```yaml
helmGlobals:
  chartHome: charts/              # Local directory for downloaded charts
  configHome: helm-config/        # Helm config directory
```

`chartHome` is useful when charts are vendored locally rather than fetched from a repo at build time.

## Build

```bash
# Must enable Helm
kustomize build --enable-helm .

# Charts are rendered, then patches/transformers/replacements apply normally
kustomize build --enable-helm . | kubectl apply -f -
```

## Combining with Patches

Helm-inflated resources can be patched like any other kustomize resource:

```yaml
helmCharts:
  - name: nginx
    repo: https://charts.bitnami.com/bitnami
    version: 15.1.0
    releaseName: nginx
    namespace: web
    valuesFile: values.yaml

patches:
  - target:
      kind: Deployment
      name: nginx
    patch: |-
      - op: replace
        path: /spec/replicas
        value: 3

namespace: web
```

## ArgoCD Integration

Enable Helm inflation in ArgoCD by setting build options in `argocd-cm`:

```yaml
# argocd-cm ConfigMap
data:
  kustomize.buildOptions: --enable-helm
```

For more ArgoCD-specific kustomize integration, see the **argocd** skill.
