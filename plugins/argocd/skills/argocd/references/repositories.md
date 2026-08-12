# ArgoCD Repository Configuration

## HTTPS Authentication

### Username/Password or Token

```bash
# GitHub/GitLab token (use token as password, any username)
argocd repo add https://github.com/org/repo.git \
  --username git \
  --password ghp_xxxxxxxxxxxx

# Basic auth
argocd repo add https://git.example.com/repo.git \
  --username myuser \
  --password mypassword
```

### Declarative Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-repo
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
type: Opaque
stringData:
  type: git
  url: https://github.com/org/repo.git
  username: git
  password: ghp_xxxxxxxxxxxx
```

## SSH Authentication

```bash
argocd repo add git@github.com:org/repo.git \
  --ssh-private-key-path ~/.ssh/id_rsa
```

### Declarative Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-ssh-repo
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
type: Opaque
stringData:
  type: git
  url: git@github.com:org/repo.git
  sshPrivateKey: |
    -----BEGIN OPENSSH PRIVATE KEY-----
    ...
    -----END OPENSSH PRIVATE KEY-----
```

## GitHub App Authentication

```bash
argocd repo add https://github.com/org/repo.git \
  --github-app-id 12345 \
  --github-app-installation-id 67890 \
  --github-app-private-key-path key.pem

# For GitHub Enterprise
argocd repo add https://github.example.com/org/repo.git \
  --github-app-id 12345 \
  --github-app-installation-id 67890 \
  --github-app-private-key-path key.pem \
  --github-app-enterprise-base-url https://github.example.com/api/v3
```

## Credential Templates

Reusable credentials for URL patterns:

```bash
argocd repocreds add https://github.com/org \
  --username git \
  --password ghp_xxxxxxxxxxxx

argocd repocreds add git@github.com:org \
  --ssh-private-key-path ~/.ssh/id_rsa
```

### Declarative

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: github-creds
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repo-creds
type: Opaque
stringData:
  type: git
  url: https://github.com/org
  username: git
  password: ghp_xxxxxxxxxxxx
```

## TLS Certificates & SSH Known Hosts

```bash
# Self-signed CA
argocd cert add-tls git.example.com --from ~/ca-cert.pem

# Skip TLS (testing only)
argocd repo add https://git.example.com/repo.git \
  --insecure-skip-server-verification

# Add from ssh-keyscan
ssh-keyscan github.com | argocd cert add-ssh --batch
```

## CLI Commands

```bash
argocd repo list
argocd repo get https://github.com/org/repo.git
argocd repo rm https://github.com/org/repo.git
argocd repocreds list
```

## Troubleshooting

**GitLab 301 redirects:** Add `.git` suffix to URL

**Permission denied:** Check SSH key permissions (600) and known hosts

**Certificate errors:** Add CA cert or use `--insecure-skip-server-verification` for testing

See [repositories/helm-repos.md](repositories/helm-repos.md) for Helm repositories and OCI registries.
