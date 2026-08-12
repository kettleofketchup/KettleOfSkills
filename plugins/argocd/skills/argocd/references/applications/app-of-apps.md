# ArgoCD App of Apps Pattern

## Directory-Based (Recommended)

Root Application watches a directory of Application YAMLs. Each child app is a standalone file.
Add/remove apps by adding/removing YAML files — no templating, no values, no Helm.

```yaml
# argocd-apps/root.yaml - applied manually once, manages everything else
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: git@github.com:org/repo.git
    targetRevision: HEAD
    path: argocd-apps
    directory:
      recurse: false
      exclude: root.yaml    # Exclude self
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

```
argocd-apps/
  root.yaml          # The root app (excluded from self-management)
  traefik.yaml       # Helm chart app
  metallb.yaml       # Helm chart app
  authentik.yaml     # Multi-source: Helm + kustomize sidecar
  cert-manager.yaml  # Plain manifests app
```

Each child file is a complete Application spec. Helm apps use `helm.valuesObject` inline.

## Multi-Source Sidecar Pattern

Apps needing extra manifests (IngressRoutes, CNPG clusters) use multi-source with a kustomize sidecar:

```yaml
# argocd-apps/myapp.yaml
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
      path: apps/myapp       # kustomization.yaml with extra resources
```

## ApplicationSet Alternative

For generating many similar apps (multi-cluster, multi-env), use ApplicationSet with Git directory generator.
More powerful but more complex — prefer directory-based for single-cluster homelab setups.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: apps
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: git@github.com:org/repo.git
        revision: HEAD
        directories:
          - path: argocd-apps/*
          - path: argocd-apps/root.yaml
            exclude: true
  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      project: default
      source:
        repoURL: git@github.com:org/repo.git
        targetRevision: HEAD
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
```

See [../applicationsets.md](../applicationsets.md) for full generator reference.
