# ArgoCD SSO via Authentik: SAML via Dex

Use when OIDC isn't feasible or when SAML property mappings are needed.
For the recommended OIDC approach, see [argocd-oidc.md](argocd-oidc.md).

## Critical: POST Binding

Authentik's redirect binding (`/sso/binding/redirect/`) is NOT `@csrf_exempt`.
The POST binding (`/sso/binding/post/`) IS. **Always use POST binding**:
```
ssoURL: https://auth.example.com/application/saml/argocd/sso/binding/post/
```

## SAML Attribute Names

Authentik sends attributes with specific URIs — match exactly:

| Dex Config | Authentik URI |
|-----------|---------------|
| `usernameAttr` | `http://schemas.goauthentik.io/2021/02/saml/username` |
| `emailAttr` | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` |
| `groupsAttr` | `http://schemas.xmlsoap.org/claims/Group` |

**Common mistake**: `http://schemas.goauthentik.io/2021/02/saml/email` does NOT exist.
Check dex logs for actual attribute names if login fails.

## Authentik SAML Provider Blueprint

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

## ArgoCD Dex Config (`argocd-cm`)

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

## Certificate Validation (caData)

For production, replace `insecureSkipSignatureValidation` with the Authentik
signing cert. Get it from Authentik admin → System → Certificates → download
"authentik Self-signed Certificate":

```yaml
caData: <base64-encoded PEM certificate>
```

Or mount as a file and use `ca: /path/to/cert.pem`.

Note: Authentik's self-signed cert regenerates on fresh deploy. For stable
deployments, export and pin it. For dev/ephemeral, use `insecureSkipSignatureValidation`.

## Troubleshooting (SAML)

| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 CSRF on SAML login | Using `/sso/binding/redirect/` | Change to `/sso/binding/post/` |
| "Login failed" after auth | Wrong `emailAttr` URI | Check dex logs for actual SAML attributes |
| Groups not mapped (SAML) | Missing `property_mappings` | Add all 4 SAML mappings to blueprint |
| Groups not in RBAC | Missing `scopes` in rbac-cm | Add `scopes: '[email,groups]'` |
| CLI login fails (SAML) | SAML doesn't support CLI | Switch to OIDC (see argocd-oidc.md) |
