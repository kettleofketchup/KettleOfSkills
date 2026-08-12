# ArgoCD SSO via Authentik: OIDC (Recommended)

Two approaches: OIDC via Dex (recommended, supports CLI) or SAML via Dex.
For SAML option, see [argocd-saml.md](argocd-saml.md).

## Option A: OIDC via Dex (Official — Recommended)

Source: [goauthentik.io/integrations/infrastructure/argocd](https://integrations.goauthentik.io/infrastructure/argocd/)

Uses Dex as OIDC intermediary — enables both UI and CLI login. This is the
officially documented approach from Authentik.

### Authentik Setup
1. Create **OAuth2/OIDC Provider** (not SAML)
2. Redirect URIs (Strict): `https://argocd.example.com/api/dex/callback`
   and `https://localhost:8085/auth/callback` (CLI)
3. Select signing key
4. Note: Client ID, Client Secret, Application Slug

### Groups
- `ArgoCD Admins` → `role:admin`
- `ArgoCD Viewers` → `role:readonly`

### ArgoCD Secret (`argocd-secret`)
```yaml
data:
  dex.authentik.clientSecret: <base64-encoded-client-secret>
```

### ArgoCD ConfigMap (`argocd-cm`)
```yaml
url: https://argocd.example.com
dex.config: |
  connectors:
  - type: oidc
    id: authentik
    name: Authentik
    config:
      issuer: https://auth.example.com/application/o/<app-slug>/
      clientID: <client-id>
      clientSecret: $dex.authentik.clientSecret
      insecureEnableGroups: true
      scopes:
        - openid
        - profile
        - email
```

### Helm Values
```yaml
configs:
  secret:
    extra:
      dex.authentik.clientSecret: "<client-secret>"
  cm:
    dex.config: |
      connectors:
      - config:
          issuer: https://auth.example.com/application/o/<app-slug>/
          clientID: <client-id>
          clientSecret: $dex.authentik.clientSecret
          insecureEnableGroups: true
          scopes: [openid, profile, email]
        name: authentik
        type: oidc
        id: authentik
  rbac:
    policy.csv: |
      g, ArgoCD Admins, role:admin
      g, ArgoCD Viewers, role:readonly
    scopes: '[email,groups]'
```

## RBAC

```yaml
# argocd-rbac-cm or configs.rbac in Helm
policy.csv: |
  p, role:exec, exec, create, */*, allow
  g, ArgoCD Admins, role:admin
  g, ArgoCD Exec, role:exec
  g, ArgoCD Viewers, role:readonly
scopes: '[email,groups]'
```

## Web Terminal

```yaml
# argocd-cm
exec.enabled: "true"
exec.shells: "bash,sh"
```

## Troubleshooting (OIDC)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Groups not mapped (OIDC) | Missing `insecureEnableGroups` | Add `insecureEnableGroups: true` |
| Groups not in RBAC | Missing `scopes` in rbac-cm | Add `scopes: '[email,groups]'` |
| `unsupported protocol scheme ""` | Empty `url` in argocd-cm | Set `url: https://argocd.example.com` |
| No login button | Empty `dex.config` | Check argocd-cm, restart dex server |
| CLI login fails | Only for SAML (not OIDC) | N/A for OIDC |
