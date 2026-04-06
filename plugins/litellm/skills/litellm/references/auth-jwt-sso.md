# JWT/OIDC Token Auth & SSO

## JWT Auth Setup

```yaml
general_settings:
  enable_jwt_auth: True
  master_key: sk-1234
```

Set JWKS endpoint: `JWT_PUBLIC_KEY_URL=https://idp.example.com/.well-known/jwks.json`

Multiple providers: comma-separate URLs in `JWT_PUBLIC_KEY_URL`.

## JWT Claim Mapping

```yaml
litellm_jwtauth:
  user_id_jwt_field: "sub"           # nested: "user.sub"
  user_email_jwt_field: "email"
  team_id_jwt_field: "client_id"
  org_id_jwt_field: "org_id"
  end_user_id_jwt_field: "customer_id"
```

## Scope-Based Access

```yaml
litellm_jwtauth:
  admin_jwt_scope: "litellm-proxy-admin"
  enforce_scope_based_access: true
  scope_mappings:
    - scope: litellm.api.consumer
      models: ["anthropic-claude"]
```

## Role Mapping

```yaml
litellm_jwtauth:
  roles_jwt_field: "roles"
  enforce_rbac: true
  role_mappings:
    - role: litellm.api.consumer
      internal_role: "team"
  jwt_litellm_role_map:
    - jwt_role: "ADMIN"
      litellm_role: "proxy_admin"
  sync_user_role_and_teams: true
```

## Advanced JWT Features

- **K8s ServiceAccount tokens**: Map namespace to teams via `team_alias_jwt_field`
- **OIDC UserInfo** for opaque tokens: `oidc_userinfo_enabled: true`
- **Email domain restriction**: `user_allowed_email_domain: "company.com"`
- **Route auth**: `team_allowed_routes: ["openai_routes", "anthropic_routes"]`
- **Public key caching**: `public_key_ttl: 600`

## SSO for Admin UI

Admin UI: `http://<proxy>/ui`. Requires `PROXY_BASE_URL` set.
Redirect URI for all providers: `https://<proxy>/sso/callback`

### Google OAuth 2.0

```
GOOGLE_CLIENT_ID="..."
GOOGLE_CLIENT_SECRET="..."
```

### Microsoft Entra ID (Azure AD)

```
MICROSOFT_CLIENT_ID="..."
MICROSOFT_CLIENT_SECRET="..."
MICROSOFT_TENANT="..."
```

Supports App Roles: `proxy_admin`, `proxy_admin_viewer`, `internal_user`, `internal_user_view_only`

### Generic OIDC (Authentik, Keycloak, Auth0, any OAuth2)

```
GENERIC_CLIENT_ID="..."
GENERIC_CLIENT_SECRET="..."
GENERIC_AUTHORIZATION_ENDPOINT="https://provider/auth"
GENERIC_TOKEN_ENDPOINT="https://provider/token"
GENERIC_USERINFO_ENDPOINT="https://provider/userinfo"
GENERIC_SCOPE="openid profile email"
```

### SSO Attribute Mapping

```
GENERIC_USER_ID_ATTRIBUTE="given_name"
GENERIC_USER_EMAIL_ATTRIBUTE="family_name"
GENERIC_USER_DISPLAY_NAME_ATTRIBUTE="display_name"
GENERIC_USER_ROLE_ATTRIBUTE="given_role"
GENERIC_USER_EXTRA_ATTRIBUTES="department,employee_id"
```

### SSO Admin & Restrictions

```
ALLOWED_EMAIL_DOMAINS="company.com"
PROXY_ADMIN_ID="<user-id>"          # Set admin after first SSO login
PROXY_LOGOUT_URL="https://..."      # Custom logout redirect
DISABLE_ADMIN_UI="True"             # Disable UI entirely
```

Debug: `/sso/debug/login`. Fallback: `/fallback/login` (username/password when SSO enabled).
