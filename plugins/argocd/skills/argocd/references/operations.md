# ArgoCD Operations & Administration

## AppProjects

Logical grouping with access controls.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: myproject
  namespace: argocd
spec:
  description: My project

  # Allowed source repos
  sourceRepos:
    - https://github.com/org/*
    - '!https://github.com/org/denied-repo'  # Deny pattern

  # Allowed destinations
  destinations:
    - namespace: 'myapp-*'
      server: https://kubernetes.default.svc
    - namespace: '*'
      server: https://production.example.com

  # Allowed cluster resources (cluster-scoped require explicit allow)
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
    - group: rbac.authorization.k8s.io
      kind: ClusterRole

  # Denied namespaced resources
  namespaceResourceBlacklist:
    - group: ''
      kind: Secret

  orphanedResources:
    warn: true

  # Project roles
  roles:
    - name: developer
      description: Developer access
      policies:
        - p, proj:myproject:developer, applications, get, myproject/*, allow
        - p, proj:myproject:developer, applications, sync, myproject/*, allow
      groups:
        - my-oidc-group
```

### CLI Commands

```bash
argocd proj create myproject \
  -d https://kubernetes.default.svc,myapp \
  -s https://github.com/org/repo.git

argocd proj add-destination myproject https://kubernetes.default.svc '*'
argocd proj add-source myproject https://github.com/org/*
argocd proj list
```

## RBAC

Configure in `argocd-rbac-cm` ConfigMap.

### Policy Syntax

```
p, <subject>, <resource>, <action>, <object>, <effect>
g, <user/group>, <role>
```

### Built-in Roles

- `role:readonly` - Read-only access
- `role:admin` - Full access

### Example Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-rbac-cm
  namespace: argocd
data:
  policy.default: role:readonly
  policy.csv: |
    # Admins
    g, admin-group, role:admin

    # Developers - specific project access
    p, role:developer, applications, get, */*, allow
    p, role:developer, applications, sync, myproject/*, allow
    p, role:developer, applications, create, myproject/*, allow
    g, dev-group, role:developer

  policy.matchMode: glob
```

### Resources and Actions

| Resource | Actions |
|----------|---------|
| applications | get, create, update, delete, sync, override, action/* |
| applicationsets | get, create, update, delete |
| clusters | get, create, update, delete |
| repositories | get, create, update, delete |
| logs | get |
| exec | create |

### Validate RBAC

```bash
argocd admin settings rbac validate --policy-file policy.csv
argocd admin settings rbac can developer get applications 'default/*'
```

See [operations/health-notifications.md](operations/health-notifications.md) for health checks, notifications, and cluster management.
