# ArgoCD Troubleshooting - Advanced

## Cluster Connectivity

### Test from ArgoCD Pod

```bash
kubectl exec -n argocd deployment/argocd-application-controller -- \
  argocd admin cluster kubeconfig https://kubernetes.default.svc

kubectl exec -n argocd deployment/argocd-application-controller -- \
  kubectl --kubeconfig=/tmp/kubeconfig get nodes
```

### Network Policy Issues

Ensure argocd-application-controller can reach target cluster API servers.

## Resource Issues

### Out of Memory

Increase limits:
```yaml
# argocd-repo-server deployment
resources:
  limits:
    memory: 2Gi
```

## Redis Issues

### Rotate Redis Secret

```bash
kubectl delete secret -n argocd argocd-redis
kubectl rollout restart -n argocd deployment/argocd-redis
kubectl rollout restart -n argocd deployment/argocd-server
kubectl rollout restart -n argocd deployment/argocd-repo-server
kubectl rollout restart -n argocd deployment/argocd-application-controller
```

## Performance Issues

### Slow Sync

1. Enable selective sync: `ApplyOutOfSyncOnly=true`
2. Increase parallelism:
```yaml
data:
  controller.resource.parallelism.limit: "50"
```

### Too Many Applications

Use ApplicationSets instead of individual Applications for large deployments.

### GitLab 301 Redirect

Add `.git` suffix to URL:
```bash
argocd repo add https://gitlab.example.com/org/repo.git
```

## OIDC/SSO Issues

Check argocd-server logs:
```bash
kubectl logs -n argocd deployment/argocd-server | grep -i oidc
```
