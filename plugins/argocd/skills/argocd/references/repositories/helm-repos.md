# ArgoCD Helm Repositories

## Helm Repositories

```bash
# Public Helm repo
argocd repo add https://charts.bitnami.com/bitnami --type helm --name bitnami

# Private Helm repo
argocd repo add https://charts.example.com \
  --type helm \
  --name private \
  --username admin \
  --password secret

# OCI Helm registry
argocd repo add registry-1.docker.io \
  --type helm \
  --name dockerhub \
  --enable-oci \
  --username myuser \
  --password mytoken
```

## Google Cloud Source

```bash
argocd repo add https://source.developers.google.com/p/project/r/repo \
  --gcp-service-account-key-path service-account.json
```

## Declarative TLS ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-tls-certs-cm
  namespace: argocd
data:
  git.example.com: |
    -----BEGIN CERTIFICATE-----
    ...
    -----END CERTIFICATE-----
```

## Declarative SSH Known Hosts

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-ssh-known-hosts-cm
  namespace: argocd
data:
  ssh_known_hosts: |
    github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmd...
    gitlab.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsj2b...
```
