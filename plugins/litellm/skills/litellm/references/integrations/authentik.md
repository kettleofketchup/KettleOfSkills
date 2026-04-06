# Authentik Integration

LiteLLM supports Authentik as an identity provider through two mechanisms:
1. **SSO for Admin UI** - Users log into LiteLLM's admin dashboard via Authentik
2. **JWT Token Auth** - API requests authenticated with Authentik-issued JWTs

## SSO Setup (Admin UI Login)

Uses LiteLLM's Generic OIDC provider. Authentik acts as the OAuth2/OIDC identity provider.

### Authentik Side

1. Create an OAuth2/OIDC Provider in Authentik
2. Set redirect URI to `https://<litellm-proxy>/sso/callback`
3. Note the client ID, client secret, and endpoints

### LiteLLM Side

Environment variables:
```
GENERIC_CLIENT_ID="<authentik-app-client-id>"
GENERIC_CLIENT_SECRET="<authentik-app-client-secret>"
GENERIC_AUTHORIZATION_ENDPOINT="https://authentik.example.com/application/o/authorize/"
GENERIC_TOKEN_ENDPOINT="https://authentik.example.com/application/o/token/"
GENERIC_USERINFO_ENDPOINT="https://authentik.example.com/application/o/userinfo/"
GENERIC_SCOPE="openid profile email"
PROXY_BASE_URL="https://litellm.example.com"
```

### Attribute Mapping

Map Authentik user fields to LiteLLM:
```
GENERIC_USER_ID_ATTRIBUTE="sub"
GENERIC_USER_EMAIL_ATTRIBUTE="email"
GENERIC_USER_DISPLAY_NAME_ATTRIBUTE="name"
GENERIC_USER_ROLE_ATTRIBUTE="groups"
```

### Access Restrictions

```
ALLOWED_EMAIL_DOMAINS="company.com"
PROXY_ADMIN_ID="<authentik-user-id>"    # Set first admin after SSO login
```

Debug SSO: navigate to `/sso/debug/login`.
Fallback login: `/fallback/login` when SSO is misconfigured.

## JWT Token Auth (API Requests)

For programmatic access where clients present Authentik-issued JWTs directly to LiteLLM API endpoints (bypassing UI SSO).

### Config

```yaml
general_settings:
  enable_jwt_auth: True
  master_key: sk-1234
```

```
JWT_PUBLIC_KEY_URL="https://authentik.example.com/application/o/<app-slug>/jwks/"
```

### Claim Mapping

```yaml
litellm_jwtauth:
  user_id_jwt_field: "sub"
  user_email_jwt_field: "email"
  team_id_jwt_field: "client_id"
  roles_jwt_field: "groups"
  enforce_rbac: true
  role_mappings:
    - role: "litellm-admins"           # Authentik group name
      internal_role: "proxy_admin"
    - role: "litellm-users"
      internal_role: "internal_user"
  user_allowed_email_domain: "company.com"
```

### Scope-Based Model Access

```yaml
litellm_jwtauth:
  enforce_scope_based_access: true
  scope_mappings:
    - scope: litellm.tier1
      models: ["gpt-3.5-turbo", "claude-3-haiku"]
    - scope: litellm.tier2
      models: ["gpt-4", "claude-3-opus"]
```

## Combined SSO + JWT

Both can be enabled simultaneously:
- SSO handles admin UI login
- JWT handles programmatic API access
- Same Authentik application can serve both (different endpoints)
