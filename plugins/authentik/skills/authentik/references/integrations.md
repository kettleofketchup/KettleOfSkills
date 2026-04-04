# Application Integrations

Per-app integration guides in `references/integrations/`:

| App | Auth Type | File |
|-----|-----------|------|
| ArgoCD | SAML via Dex | [integrations/argocd.md](integrations/argocd.md) |
| Grafana | OAuth2/OIDC | Below |
| Gitea | OAuth2/OIDC | Below |
| MinIO | OpenID Connect | Below |
| Generic SAML | SAML | Below |

---

## Grafana (OAuth2/OIDC)

### Authentik Setup
1. Create **OAuth2/OIDC Provider**
2. Redirect URI: `https://grafana.example.com/login/generic_oauth`
3. Scopes: `openid`, `profile`, `email`

### Grafana Config (`grafana.ini`)
```ini
[auth.generic_oauth]
enabled = true
name = authentik
client_id = <client-id>
client_secret = <client-secret>
scopes = openid profile email
auth_url = https://auth.example.com/application/o/authorize/
token_url = https://auth.example.com/application/o/token/
api_url = https://auth.example.com/application/o/userinfo/
role_attribute_path = contains(groups[*], 'Grafana Admins') && 'Admin' || contains(groups[*], 'Grafana Editors') && 'Editor' || 'Viewer'
```

---

## Gitea (OAuth2/OIDC)

### Authentik Setup
1. Create **OAuth2/OIDC Provider**
2. Redirect URI: `https://gitea.example.com/user/oauth2/authentik/callback`
3. Scopes: `openid`, `profile`, `email`

### Gitea Setup
Admin → Authentication Sources → Add:
- Type: OAuth2
- Provider: OpenID Connect
- Client ID/Secret from Authentik
- Discovery URL: `https://auth.example.com/application/o/<slug>/.well-known/openid-configuration`

---

## MinIO (OpenID Connect)

### Authentik Setup
1. Create **OAuth2/OIDC Provider**
2. Redirect URI: `https://minio-console.example.com/oauth_callback`
3. Add scope mapping for `minio` claim with policy attribute

### Custom Scope Mapping (Python expression)
```python
# Map groups to MinIO policies
if ak_is_group_member(request.user, name="MinIO Admins"):
    return {"policy": "consoleAdmin"}
return {"policy": "readonly"}
```

### MinIO Environment
```
MINIO_IDENTITY_OPENID_CONFIG_URL=https://auth.example.com/application/o/<slug>/.well-known/openid-configuration
MINIO_IDENTITY_OPENID_CLIENT_ID=<client-id>
MINIO_IDENTITY_OPENID_CLIENT_SECRET=<client-secret>
MINIO_IDENTITY_OPENID_SCOPES=openid,profile,email,minio
MINIO_IDENTITY_OPENID_CLAIM_NAME=policy
```

---

## Generic SAML App Template

### Authentik SAML Provider
| Setting | Value |
|---------|-------|
| ACS URL | App's SAML callback URL |
| Issuer | `https://auth.example.com` |
| Audience | App's entity ID |
| NameID | Email (most common) |
| Signing Certificate | authentik Self-signed Certificate |

### App Configuration
- IdP SSO URL: `https://auth.example.com/application/saml/<slug>/sso/binding/post/`
- IdP Certificate: download from authentik admin
- IdP Entity ID: `https://auth.example.com`

**Always use `/sso/binding/post/`** — the redirect binding is NOT csrf_exempt.

### Blueprint Pattern
```yaml
- model: authentik_providers_saml.samlprovider
  identifiers:
    name: <app>-saml
  id: provider-<app>
  attrs:
    authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
    acs_url: https://<app>.example.com/<saml-callback>
    issuer: https://auth.example.com
    sp_binding: post
    signing_kp: !Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]
- model: authentik_core.application
  identifiers:
    slug: <app>
  attrs:
    name: <App Name>
    provider: !KeyOf provider-<app>
```
