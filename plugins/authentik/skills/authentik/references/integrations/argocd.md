# ArgoCD SSO via Authentik

Two approaches: OIDC via Dex (official, supports CLI) or SAML via Dex.

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

---

## Option B: SAML via Dex

Use when OIDC isn't feasible or when SAML property mappings are needed.

### Critical: POST Binding

Authentik's redirect binding (`/sso/binding/redirect/`) is NOT `@csrf_exempt`.
The POST binding (`/sso/binding/post/`) IS. **Always use POST binding**:
```
ssoURL: https://auth.example.com/application/saml/argocd/sso/binding/post/
```

### SAML Attribute Names

Authentik sends attributes with specific URIs — match exactly:

| Dex Config | Authentik URI |
|-----------|---------------|
| `usernameAttr` | `http://schemas.goauthentik.io/2021/02/saml/username` |
| `emailAttr` | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` |
| `groupsAttr` | `http://schemas.xmlsoap.org/claims/Group` |

**Common mistake**: `http://schemas.goauthentik.io/2021/02/saml/email` does NOT exist.
Check dex logs for actual attribute names if login fails.

### Authentik SAML Provider Blueprint

```yaml
- model: authentik_providers_saml.samlprovider
  identifiers:
    name: argocd-saml
  id: saml-provider
  attrs:
    authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
    invalidation_flow: !Find [authentik_flows.flow, [slug, default-provider-invalidation-flow]]
    acs_url: https://argocd.example.com/api/dex/callback
    issuer: https://auth.example.com
    audience: https://argocd.example.com/api/dex/callback
    sp_binding: post
    signing_kp: !Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]
    sign_assertion: true
    sign_response: true
    name_id_mapping: !Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/email]]
    property_mappings:
      - !Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/email]]
      - !Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/name]]
      - !Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/username]]
      - !Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/uid]]
- model: authentik_core.application
  identifiers:
    slug: argocd
  attrs:
    name: ArgoCD
    provider: !KeyOf saml-provider
```

### ArgoCD Dex Config (`argocd-cm`)

```yaml
url: https://argocd.example.com
dex.config: |
  connectors:
    - type: saml
      id: authentik
      name: Authentik
      config:
        ssoURL: https://auth.example.com/application/saml/argocd/sso/binding/post/
        redirectURI: https://argocd.example.com/api/dex/callback
        entityIssuer: https://argocd.example.com/api/dex/callback
        ssoIssuer: https://auth.example.com
        usernameAttr: http://schemas.goauthentik.io/2021/02/saml/username
        emailAttr: http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress
        groupsAttr: http://schemas.xmlsoap.org/claims/Group
        insecureSkipSignatureValidation: true
```

### Certificate Validation (caData)

For production, replace `insecureSkipSignatureValidation` with the Authentik
signing cert. Get it from Authentik admin → System → Certificates → download
"authentik Self-signed Certificate":

```yaml
caData: <base64-encoded PEM certificate>
```

Or mount as a file and use `ca: /path/to/cert.pem`.

Ref: [ArgoCD SAML docs](https://argo-cd.readthedocs.io/en/stable/operator-manual/user-management/okta/#saml-with-dex)

Note: Authentik's self-signed cert regenerates on fresh deploy. For stable
deployments, export and pin it. For dev/ephemeral, use `insecureSkipSignatureValidation`.

---

## RBAC (both options)

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

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 CSRF on SAML login | Using `/sso/binding/redirect/` | Change to `/sso/binding/post/` |
| "Login failed" after auth | Wrong `emailAttr` URI | Check dex logs for actual SAML attributes |
| Groups not mapped (OIDC) | Missing `insecureEnableGroups` | Add `insecureEnableGroups: true` |
| Groups not mapped (SAML) | Missing `property_mappings` | Add all 4 SAML mappings to blueprint |
| Groups not in RBAC | Missing `scopes` in rbac-cm | Add `scopes: '[email,groups]'` |
| `unsupported protocol scheme ""` | Empty `url` in argocd-cm | Set `url: https://argocd.example.com` |
| No login button | Empty `dex.config` | Check argocd-cm, restart dex server |
| CLI login fails (SAML) | SAML doesn't support CLI | Switch to OIDC (Option A) |
