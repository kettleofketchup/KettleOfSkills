# ArgoCD Helm Integration

ArgoCD uses `helm template` for rendering; Helm doesn't manage releases.

## Basic Helm Application

### From Helm Repository

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: nginx
  namespace: argocd
spec:
  project: default
  source:
    chart: nginx
    repoURL: https://charts.bitnami.com/bitnami
    targetRevision: 15.1.0  # Chart version
    helm:
      releaseName: nginx
  destination:
    server: https://kubernetes.default.svc
    namespace: nginx
```

### From Git Repository

```yaml
spec:
  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: HEAD
    path: charts/myapp  # Path to chart in repo
    helm:
      releaseName: myapp
```

## Values Configuration

Precedence (lowest to highest): values.yaml → valueFiles → values → valuesObject → parameters

### Inline Values (valuesObject)

```yaml
spec:
  source:
    helm:
      valuesObject:
        replicaCount: 3
        image:
          repository: nginx
          tag: "1.25"
        ingress:
          enabled: true
          hosts:
            - host: myapp.example.com
              paths:
                - path: /
                  pathType: Prefix
```

### Values Files

```yaml
spec:
  source:
    helm:
      valueFiles:
        - values.yaml
        - values-prod.yaml
      ignoreMissingValueFiles: true  # Don't fail if file missing
```

### External Values File (from another repo)

```yaml
spec:
  sources:
    - repoURL: https://charts.bitnami.com/bitnami
      chart: nginx
      targetRevision: 15.1.0
      helm:
        valueFiles:
          - $values/nginx/values-prod.yaml
    - repoURL: https://github.com/org/config.git
      targetRevision: main
      ref: values  # Reference name for $values
```

### Parameter Overrides

```yaml
spec:
  source:
    helm:
      parameters:
        - name: replicaCount
          value: "3"
        - name: image.tag
          value: "1.25"
      fileParameters:
        - name: config
          path: files/config.json
```

## OCI Registry

```yaml
spec:
  source:
    chart: myapp
    repoURL: registry-1.docker.io/myorg  # No oci:// prefix
    targetRevision: 1.0.0
```

## CLI Commands

```bash
# Create Helm app
argocd app create myapp \
  --repo https://charts.bitnami.com/bitnami \
  --helm-chart nginx \
  --revision 15.1.0 \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace nginx

# Set Helm values
argocd app set myapp --helm-set replicaCount=3
argocd app set myapp --helm-set-string image.tag=1.25
argocd app set myapp --helm-set-file config=config.json
argocd app set myapp --values values-prod.yaml

# Show rendered manifests
argocd app manifests myapp
```

## Add Helm Repository

```bash
argocd repo add https://charts.bitnami.com/bitnami --type helm --name bitnami
argocd repo add https://charts.example.com \
  --type helm --username admin --password secret
```
See [helm/options.md](helm/options.md) for Helm options, random values handling, and hook mapping.
