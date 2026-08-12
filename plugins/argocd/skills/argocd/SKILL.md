---
name: argocd
description: GitOps CD for Kubernetes with ArgoCD. Use for Applications, ApplicationSets, App of Apps, Helm/Kustomize, kustomize overrides, multi-source apps, sync, RBAC/projects, health checks, or private repos.
---

# ArgoCD

Declarative GitOps continuous delivery for Kubernetes. ArgoCD continuously monitors Git repositories and automatically syncs application state to match desired configuration.

## Quick Start

**Install ArgoCD:**
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**Access UI:**
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Get initial admin password
argocd admin initial-password -n argocd
```

**CLI Login:**
```bash
argocd login localhost:8080 --insecure
```

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Application** | Kubernetes resource tracking a Git repo path to a cluster/namespace |
| **AppProject** | Logical grouping with source/destination restrictions and RBAC |
| **ApplicationSet** | Template for generating multiple Applications from generators |
| **Sync** | Process of applying Git manifests to cluster |
| **Health** | Status assessment of deployed resources |

## Task Reference

### Application Management
- Create, sync, delete Applications → [references/applications.md](references/applications.md)
- App of Apps pattern, multi-source sidecar → [references/applications/app-of-apps.md](references/applications/app-of-apps.md)

### Multi-Cluster & Templating
- List, Cluster, Git, Matrix generators → [references/applicationsets.md](references/applicationsets.md)
- Merge, Pull Request, Go templates, Progressive Syncs → [references/applicationsets/advanced.md](references/applicationsets/advanced.md)

### Manifest Tools
- Helm charts, values, OCI registries → [references/helm.md](references/helm.md)
- Helm options, random values, hook mapping → [references/helm/options.md](references/helm/options.md)
- General kustomize (bases, overlays, components, replacements) → **kustomize** skill
- ArgoCD kustomize overrides, multi-source Helm+kustomize → [references/kustomize.md](references/kustomize.md)

### Sync Configuration
- Sync waves, hooks, phases, retry → [references/sync-options.md](references/sync-options.md)
- Selective sync, skip reconciliation, namespace metadata → [references/sync-options/advanced.md](references/sync-options/advanced.md)

### Operations & Admin
- AppProjects, RBAC policies, roles → [references/operations.md](references/operations.md)
- Health checks, notifications, cluster management → [references/operations/health-notifications.md](references/operations/health-notifications.md)

### Repository Setup
- Private repos, SSH, HTTPS, GitHub App, credential templates → [references/repositories.md](references/repositories.md)
- Helm repos, OCI registries, declarative ConfigMaps → [references/repositories/helm-repos.md](references/repositories/helm-repos.md)

### Troubleshooting
- Sync issues, auth, CLI, resource errors → [references/troubleshooting.md](references/troubleshooting.md)
- Cluster connectivity, Redis, performance → [references/troubleshooting/advanced.md](references/troubleshooting/advanced.md)

## Common CLI Commands

```bash
# Application management
argocd app create <name> --repo <url> --path <path> --dest-server https://kubernetes.default.svc --dest-namespace <ns>
argocd app sync <name>
argocd app get <name>
argocd app delete <name>
argocd app list

# Cluster management
argocd cluster add <context-name>
argocd cluster list

# Repository management
argocd repo add <url> [--ssh-private-key-path | --username/--password]
argocd repo list

# Project management
argocd proj create <name> -d <server>,<namespace> -s <repo-url>
argocd proj list
```

## Minimal Application Example

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: HEAD
    path: manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## Official Documentation
- [ArgoCD Docs](https://argo-cd.readthedocs.io/en/stable/)
- [Application Spec](https://argo-cd.readthedocs.io/en/stable/user-guide/application-specification/)
- [CLI Reference](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd/)
