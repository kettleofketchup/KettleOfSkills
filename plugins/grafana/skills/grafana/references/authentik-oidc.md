# Authentik OIDC Integration for Grafana

Two approaches: **operator-managed** (recommended) or **manual blueprint**.

## Approach 1: Authentik Operator (Recommended)

Use the `authentik-operator` with an `OIDCClient` custom resource. The operator auto-creates the Authentik provider, application, and a K8s Secret with credentials.

### OIDCClient CR

Add to the kube-prometheus-stack Helm chart templates:

```yaml
# templates/oidcclient.yaml
apiVersion: auth.example.com/v1  # Edit: replace with your CRD group
kind: OIDCClient
metadata:
  name: grafana
spec:
  slug: grafana
  name: Grafana
  clientId: grafana
  redirectUris:
    - https://grafana.{{ .Values.global.baseDomain }}/login/generic_oauth
  launchUrl: https://grafana.{{ .Values.global.baseDomain }}
  scopes: [openid, profile, email]
  secretName: grafana-oauth
```

The operator handles creating the OAuth2 provider/application in Authentik, generating credentials in a K8s Secret (`grafana-oauth`), and rotating them if needed.

### Grafana Helm Values (Operator)

```yaml
grafana:
  admin:
    existingSecret: grafana-admin
    userKey: admin-user
    passwordKey: admin-password
  envFromSecrets:
    - name: grafana-oauth
      optional: true
  grafana.ini:
    server:
      root_url: https://grafana.example.com  # Edit: your Grafana URL
    auth:
      signout_redirect_url: "https://auth.example.com/application/o/grafana/end-session/"
      oauth_auto_login: true
    auth.generic_oauth:
      enabled: true
      name: Authentik
      client_id: "${GF_AUTH_GENERIC_OAUTH_CLIENT_ID}"
      client_secret: "${GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET}"
      scopes: openid profile email
      auth_url: https://auth.example.com/application/o/authorize/
      token_url: https://auth.example.com/application/o/token/
      api_url: https://auth.example.com/application/o/userinfo/
      role_attribute_path: "contains(groups[*], 'Grafana Admins') && 'Admin' || contains(groups[*], 'Grafana Editors') && 'Editor' || 'Viewer'"
      allow_assign_grafana_admin: true
```

## Approach 2: Manual Blueprint

For setups without the authentik-operator, create the provider manually.

### Authentik Setup

1. **Providers > Create > OAuth2/OIDC**: Name `Grafana`, client type Confidential, redirect URI `https://grafana.example.com/login/generic_oauth`, scopes `openid profile email`
2. **Applications > Create**: Name `Grafana`, slug `grafana`, provider `Grafana`
3. **Groups**: Create `Grafana Admins`, `Grafana Editors` for role mapping

### Blueprint (Declarative)

```yaml
version: 1
metadata:
  name: Grafana OIDC Provider
entries:
  - model: authentik_providers_oauth2.oauth2provider
    state: present
    identifiers:
      name: Grafana
    id: provider-grafana
    attrs:
      authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
      client_type: confidential
      client_id: grafana
      client_secret: !Env [GRAFANA_OAUTH_SECRET]
      redirect_uris: !Format ["https://%s/login/generic_oauth", !Env [GRAFANA_HOST, grafana.example.com]]
      signing_key: !Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]
      property_mappings:
        - !Find [authentik_providers_oauth2.scopemapping, [scope_name, openid]]
        - !Find [authentik_providers_oauth2.scopemapping, [scope_name, profile]]
        - !Find [authentik_providers_oauth2.scopemapping, [scope_name, email]]
  - model: authentik_core.application
    state: present
    identifiers:
      slug: grafana
    attrs:
      name: Grafana
      provider: !KeyOf provider-grafana
      meta_launch_url: !Format ["https://%s", !Env [GRAFANA_HOST, grafana.example.com]]
```

### Manual Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: grafana-oauth
  namespace: monitoring
type: Opaque
stringData:
  GF_AUTH_GENERIC_OAUTH_CLIENT_ID: "grafana"
  GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET: "client-secret-from-authentik"
```

For role mapping expressions and disabling default admin, see [authentik-oidc-roles.md](authentik-oidc-roles.md).
