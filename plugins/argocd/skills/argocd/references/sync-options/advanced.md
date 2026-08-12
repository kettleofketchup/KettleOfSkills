# ArgoCD Sync Options - Advanced

## Selective Sync

Sync specific resources only:

```bash
# Sync single resource
argocd app sync myapp --resource apps:Deployment:nginx

# Sync by label
argocd app sync myapp --label app=frontend

# Sync with prune
argocd app sync myapp --prune

# Force sync (delete and recreate)
argocd app sync myapp --force
```

## Skip Reconciliation

Pause syncing for a resource:

```yaml
metadata:
  annotations:
    argocd.argoproj.io/compare-options: IgnoreExtraneous
```

Or exclude from app entirely:
```yaml
metadata:
  annotations:
    argocd.argoproj.io/tracking-id: ""  # Remove from tracking
```

## Create Namespace with Metadata

```yaml
spec:
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
    managedNamespaceMetadata:
      labels:
        env: production
      annotations:
        owner: platform-team
```
