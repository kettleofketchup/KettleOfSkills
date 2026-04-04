# Kustomize in ArgoCD

ArgoCD auto-detects kustomize when `kustomization.yaml` exists in the Application's `spec.source.path`.

For general kustomize concepts (bases, overlays, components, replacements, patches, transformers), see the **kustomize** skill.

## ArgoCD Kustomize Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: HEAD
    path: apps/myapp          # Path containing kustomization.yaml
    kustomize:                # Optional ArgoCD-level overrides
      images:
        - name: myapp
          newTag: v2.0.0
      namespace: production
      commonLabels:
        managed-by: argocd
      patches:                # Inline patches from ArgoCD
        - target:
            kind: Deployment
            name: myapp
          patch: |-
            - op: replace
              path: /spec/replicas
              value: 3
```

## Multi-Source: Helm Chart + Kustomize Sidecar

Deploy a Helm chart with additional kustomize-managed manifests (IngressRoutes, extra resources):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  sources:
    - repoURL: https://charts.example.com
      chart: myapp
      targetRevision: v1.0.0
      helm:
        valuesObject:
          key: value
    - repoURL: git@github.com:org/repo.git
      targetRevision: HEAD
      path: apps/myapp        # kustomization.yaml here
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
```

Keeps Helm values as source of truth for chart, kustomize for supplementary resources (ingress, certs, CNPG clusters, etc.).

## Helm Inflation in Kustomize

Render Helm charts within kustomize (requires `--enable-helm` in ArgoCD):

```yaml
# argocd-cm ConfigMap
data:
  kustomize.buildOptions: --enable-helm
```

```yaml
# kustomization.yaml
helmCharts:
  - name: nginx
    repo: https://charts.bitnami.com/bitnami
    version: 15.1.0
    valuesFile: values.yaml
```

## CLI Overrides

```bash
argocd app set myapp --kustomize-image myapp=registry.example.com/myapp:v2
argocd app set myapp --kustomize-common-label env=staging
argocd app set myapp --nameprefix staging-
argocd app manifests myapp   # Show rendered output
```
