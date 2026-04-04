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
  # Application settings
  slug: grafana
  name: Grafana
  # OAuth2 provider settings
  clientId: grafana
  redirectUris:
    - https://grafana.{{ .Values.global.baseDomain }}/login/generic_oauth
  launchUrl: https://grafana.{{ .Values.global.baseDomain }}
  scopes: [openid, profile, email]
  # Output: creates K8s Secret "grafana-oauth" with client_id, client_secret keys
  secretName: grafana-oauth
```

The operator handles:

1. Creating the OAuth2 provider in Authentik
2. Creating the Application in Authentik
3. Generating and storing credentials in a K8s Secret (`grafana-oauth`)
4. Rotating credentials if needed

### Grafana Helm Values (Operator)

```yaml
grafana:
  # Admin credentials from separate secret
  admin:
    existingSecret: grafana-admin
    userKey: admin-user
    passwordKey: admin-password
  # OIDC credentials from operator-managed secret
  envFromSecrets:
    - name: grafana-oauth
      optional: true
  grafana.ini:
    server:
      root_url: https://grafana.example.com  # Edit: your Grafana URL
    auth:
      signout_redirect_url: "https://auth.example.com/application/o/grafana/end-session/"  # Edit: your Authentik URL
      oauth_auto_login: true
    auth.generic_oauth:
      enabled: true
      name: Authentik
      client_id: "${GF_AUTH_GENERIC_OAUTH_CLIENT_ID}"
      client_secret: "${GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET}"
      scopes: openid profile email
      auth_url: https://auth.example.com/application/o/authorize/  # Edit: your Authentik URL
      token_url: https://auth.example.com/application/o/token/
      api_url: https://auth.example.com/application/o/userinfo/
      role_attribute_path: "contains(groups[*], 'Grafana Admins') && 'Admin' || contains(groups[*], 'Grafana Editors') && 'Editor' || 'Viewer'"
      allow_assign_grafana_admin: true
```

The `envFromSecrets` injects the operator-managed secret as env vars. Grafana reads `${GF_AUTH_GENERIC_OAUTH_CLIENT_ID}` and `${GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET}` from the secret.

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
  GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET: "<client-secret-from-authentik>"
```

## Role Mapping Expression

The `role_attribute_path` uses JMESPath:

```
contains(groups[*], 'Grafana Admins') && 'Admin' || contains(groups[*], 'Grafana Editors') && 'Editor' || 'Viewer'
```

Evaluation order: Admin first, then Editor, fallback Viewer.

To also grant Grafana Server Admin to the Admins group:
```
contains(groups[*], 'Grafana Admins') && 'GrafanaAdmin' || contains(groups[*], 'Grafana Editors') && 'Editor' || 'Viewer'
```

Requires `allow_assign_grafana_admin: true` in `auth.generic_oauth`.

## Disable Default Admin

Once OIDC works, optionally disable built-in login:

```yaml
grafana:
  grafana.ini:
    auth:
      disable_login_form: true
    auth.generic_oauth:
      oauth_auto_login: true
```
