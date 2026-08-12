# Nextcloud ArgoCD and Storage Configuration

## ArgoCD Application

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nextcloud
  namespace: argocd
spec:
  project: default
  source:
    chart: nextcloud
    repoURL: https://nextcloud.github.io/helm/
    targetRevision: "8.*"
    helm:
      valueFiles:
        - values.yaml  # from git repo
  destination:
    server: https://kubernetes.default.svc
    namespace: nextcloud
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```

## App-of-Apps Multi-Source Pattern

Place values.yaml in the git repo and reference via multi-source:

```yaml
spec:
  sources:
    - repoURL: https://nextcloud.github.io/helm/
      chart: nextcloud
      targetRevision: "8.*"
      helm:
        valueFiles:
          - $values/nextcloud/values.yaml
    - repoURL: git@github.com:kettleofketchup/home.git
      targetRevision: main
      ref: values
```

## Storage Classes (Rook-Ceph)

Ensure these StorageClasses exist before deploying:

| StorageClass | Provisioner | Access | Use |
|-------------|-------------|--------|-----|
| `ceph-block` | rook-ceph.rbd.csi.ceph.com | RWO | PostgreSQL, Redis, Nextcloud app |
| `ceph-filesystem` | rook-ceph.cephfs.csi.ceph.com | RWX | Multi-replica data (if needed) |

Single-replica deployment: use `ceph-block` (RWO) for everything — simpler and better performance.
Multi-replica: `ceph-filesystem` (RWX) for nextcloudData, sticky sessions required.
