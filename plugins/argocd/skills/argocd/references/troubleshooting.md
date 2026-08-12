# ArgoCD Troubleshooting

## Application Sync Issues

### OutOfSync After Successful Sync

**Cause:** Field differences between desired and live state.

```yaml
spec:
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
        - /metadata/annotations/kubectl.kubernetes.io~1last-applied-configuration
```

### StatefulSet volumeClaimTemplates Perpetual OutOfSync

**Cause:** Kubernetes strips `apiVersion`/`kind` from `volumeClaimTemplates` entries.

**Solution — Global (recommended):**
```yaml
configs:
  cm:
    resource.customizations.ignoreDifferences.apps_StatefulSet: |
      jqPathExpressions:
        - .spec.volumeClaimTemplates[]?.apiVersion
        - .spec.volumeClaimTemplates[]?.kind
```

**Solution — Per-Application:**
```yaml
spec:
  ignoreDifferences:
    - group: apps
      kind: StatefulSet
      jqPathExpressions:
        - .spec.volumeClaimTemplates[]?.apiVersion
        - .spec.volumeClaimTemplates[]?.kind
```

### Stuck in Progressing

Common causes: Ingress controller not updating status, StatefulSet waiting for PVCs, pods failing to start.

```bash
argocd app get myapp
kubectl describe deployment -n myapp myapp
kubectl get events -n myapp
```

### Sync Failed

```bash
argocd app sync myapp --dry-run
kubectl logs -n argocd deployment/argocd-repo-server
kubectl logs -n argocd deployment/argocd-application-controller
```

## Authentication Issues

### Forgot Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Reset password
argocd account bcrypt --password 'newpassword'
kubectl -n argocd patch secret argocd-secret \
  -p '{"stringData": {"admin.password": "$2a$10$...", "admin.passwordMtime": "'$(date +%FT%T%Z)'"}}'
```

### Disable Admin Account

```yaml
# argocd-cm ConfigMap
data:
  admin.enabled: "false"
```

## Repository Issues

### Permission Denied (SSH)

1. Verify: `ssh -T git@github.com`
2. Permissions: `chmod 600 ~/.ssh/id_rsa`
3. Known hosts: `ssh-keyscan github.com | argocd cert add-ssh --batch`

### Certificate Errors (HTTPS)

```bash
argocd cert add-tls git.example.com --from ca.pem
```

## CLI Issues

### "transport is closing" Error

**Cause:** Proxy incompatible with HTTP/2

```bash
argocd app list --grpc-web
export ARGOCD_OPTS='--grpc-web'
```

## Resource Issues

### "Field not declared in schema"

Use server-side apply: `ServerSideApply=true` or skip validation: `Validate=false`

### Cached Manifest Error

```bash
kubectl rollout restart -n argocd deployment/argocd-repo-server
```

## Debugging Commands

```bash
argocd app get myapp
argocd app diff myapp
argocd app manifests myapp

kubectl logs -n argocd deployment/argocd-server
kubectl logs -n argocd deployment/argocd-repo-server
kubectl logs -n argocd deployment/argocd-application-controller
kubectl get events -n argocd --sort-by='.lastTimestamp'

argocd admin settings rbac can myuser get applications 'default/*'
```

See [troubleshooting/advanced.md](troubleshooting/advanced.md) for cluster connectivity, Redis issues, and performance.
