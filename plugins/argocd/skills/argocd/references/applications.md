# ArgoCD Applications

## Application Structure

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io  # Cascade delete resources
spec:
  project: default  # AppProject name

  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: HEAD  # Branch, tag, or commit SHA
    path: manifests  # Path within repo

  destination:
    server: https://kubernetes.default.svc  # Or use 'name: cluster-name'
    namespace: myapp

  syncPolicy:
    automated:
      prune: true      # Delete resources removed from Git
      selfHeal: true   # Revert manual changes
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
```

## Source Configuration

### Multiple Sources
```yaml
spec:
  sources:
    - repoURL: https://github.com/org/repo.git
      targetRevision: HEAD
      path: base
    - repoURL: https://github.com/org/config.git
      targetRevision: main
      path: overlays/prod
```

### Directory Source
```yaml
source:
  path: manifests
  directory:
    recurse: true
    include: '*.yaml'
    exclude: 'test-*'
```

## CLI Commands

```bash
# Create application
argocd app create myapp \
  --repo https://github.com/org/repo.git \
  --path manifests \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace myapp \
  --sync-policy automated \
  --auto-prune \
  --self-heal

# Sync operations
argocd app sync myapp
argocd app sync myapp --prune
argocd app sync myapp --force
argocd app sync myapp --resource apps:Deployment:myapp

# Status and info
argocd app get myapp
argocd app list
argocd app history myapp
argocd app diff myapp

# Rollback
argocd app rollback myapp <history-id>

# Delete
argocd app delete myapp
argocd app delete myapp --cascade=false  # Keep resources
```

## App of Apps Pattern

### Directory-Based (Recommended)

Root Application watches a directory of Application YAMLs. Each child app is a standalone file.
Add/remove apps by adding/removing YAML files - no templating, no values, no Helm.

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

### ApplicationSet Alternative

For generating many similar apps (multi-cluster, multi-env), use ApplicationSet with Git directory generator.
More powerful but more complex - prefer directory-based for single-cluster homelab setups.

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

See [applicationsets.md](applicationsets.md) for full generator reference.

## Ignore Differences

```yaml
spec:
  ignoreDifferences:
    # By JSON pointer
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
        - /metadata/annotations

    # By JQ expression
    - group: ""
      kind: ConfigMap
      jqPathExpressions:
        - '.data["config.yaml"]'

    # By managed fields manager
    - group: "*"
      kind: "*"
      managedFieldsManagers:
        - kube-controller-manager
```

## Info Annotations

```yaml
spec:
  info:
    - name: Documentation
      value: https://docs.example.com
    - name: Owner
      value: platform-team
```

## Revision History

```yaml
spec:
  revisionHistoryLimit: 10  # Default is 10
```
