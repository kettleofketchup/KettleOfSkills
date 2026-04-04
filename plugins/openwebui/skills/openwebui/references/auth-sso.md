# SSO (OAuth, OIDC, Trusted Header)

Only one OIDC provider can be configured at a time via `OPENID_PROVIDER_URL`. You cannot have Microsoft and Google as OIDC providers simultaneously. A community workaround exists for dual OAuth — see the Dual OAuth Tutorial.

## OAuth Configuration Overview

| Environment Variable | Default | Description |
|---|---|---|
| `WEBUI_URL` | — | **Required.** Your public WebUI address, e.g., `http://localhost:8080`. |
| `ENABLE_OAUTH_PERSISTENT_CONFIG` | `true` | Persist OAuth config to the database; set to `false` for stateless/containerized environments. |
| `ENABLE_OAUTH_SIGNUP` | `false` | Allows account creation upon OAuth login (separate from `ENABLE_SIGNUP`). |
| `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` | `false` | Merge OAuth logins based on matching email (caution: can be insecure if provider doesn't verify emails). |
| `OAUTH_UPDATE_PICTURE_ON_LOGIN` | `false` | Update user profile pictures from OAuth provider with each login. |
| `OAUTH_PICTURE_CLAIM` | `picture` | Field in the claim containing the profile picture. Set to empty string to disable. |
| `WEBUI_AUTH_SIGNOUT_REDIRECT_URL` | *empty* | Redirect users to this URL after signout. |
| `WEBUI_SECRET_KEY` | *empty* | MUST be set - especially in clustered environments. Otherwise session issues and weird OAuth issues will occur. |
| `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY` | `WEBUI_SECRET_KEY` | A secret key for encrypting OAuth tokens stored on the server. Must be shared across all instances in a cluster. |
| `OAUTH_CLIENT_INFO_ENCRYPTION_KEY` | `WEBUI_SECRET_KEY` | A secret key for encrypting OAuth client information stored on the server - used for OAuth 2.1 authentication for MCP servers. |
| `ENABLE_OAUTH_ID_TOKEN_COOKIE` | `true` | For backward compatibility. Controls if the legacy `oauth_id_token` cookie is set. Recommended to set to `false`. |
| `ENABLE_OAUTH_TOKEN_EXCHANGE` | `false` | Enables the token exchange endpoint for external apps to exchange OAuth tokens for Open WebUI JWTs. |
| `OAUTH_MAX_SESSIONS_PER_USER` | `10` | Maximum concurrent OAuth sessions per user per provider. |

**Critical Configuration Notes:**

1. **WEBUI_URL Must Be Set First**: Configure `WEBUI_URL` in the Admin Panel before enabling OAuth, as it's used for redirect URIs.
2. **Persistent Config Behavior**: When `ENABLE_OAUTH_PERSISTENT_CONFIG=true` (default), OAuth settings are stored in the database after first launch. To change environment variables after initial setup, either set `ENABLE_OAUTH_PERSISTENT_CONFIG=false` to always read from environment variables, or update settings through the Admin Panel.
3. **Required Variables**: Always verify you're using the exact variable names from the environment configuration documentation.

### Server-Side OAuth Session Management

Instead of storing large `access_token` and `id_token` values in browser cookies, the entire token payload is encrypted and stored in the Open WebUI database in an `oauth_session` table. The user's browser gets a small, secure `httponly` cookie named `oauth_session_id`.

- **Multi-Device Support:** Multiple concurrent sessions are supported per user per provider. A configurable limit (`OAUTH_MAX_SESSIONS_PER_USER`, default: 10) prunes the oldest sessions when exceeded.
- **Automatic Refresh:** When a token is required by a downstream service, the backend retrieves tokens via `oauth_session_id`. If expired, it automatically uses the stored `refresh_token` to fetch new ones.

### OAuth Token Exchange for External Applications

Allows external applications to authenticate with Open WebUI by exchanging an OAuth provider's access token for an Open WebUI JWT session token. Enable with `ENABLE_OAUTH_TOKEN_EXCHANGE=true`.

### Google

Redirect URI: `<open-webui>/oauth/google/callback`

Required variables:
1. `GOOGLE_CLIENT_ID` - Google OAuth client ID
2. `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
3. `OPENID_PROVIDER_URL` - Must be set for logout to work properly (usually `https://accounts.google.com/.well-known/openid-configuration`)

Optional:
- `GOOGLE_OAUTH_AUTHORIZE_PARAMS` - JSON object for extra `/authorize` params (e.g., `prompt`, `login_hint`, `hd`).

```bash
GOOGLE_OAUTH_AUTHORIZE_PARAMS={"prompt":"consent","login_hint":"user@example.com","hd":"example.com"}
```

### Microsoft

Redirect URI: `<open-webui>/oauth/microsoft/callback`

Required variables:
1. `MICROSOFT_CLIENT_ID` - Microsoft OAuth client ID
2. `MICROSOFT_CLIENT_SECRET` - Microsoft OAuth client secret
3. `MICROSOFT_CLIENT_TENANT_ID` - Microsoft tenant ID - use `9188040d-6c67-4c5b-b112-36a304b66dad` for personal accounts
4. `MICROSOFT_REDIRECT_URI` - Must be set to `<open-webui>/oauth/microsoft/callback`
5. `OPENID_PROVIDER_URL` - Must be set for logout to work properly

**Token Refresh (`offline_access`):** Add `offline_access` scope to enable automatic token refresh:

```
MICROSOFT_OAUTH_SCOPE=openid email profile offline_access
```

Without `offline_access`, after ~1 hour you may see `WARNING | No refresh token available for session xxx`. Basic chat (using Open WebUI JWT) is not affected, but MCP tool servers using `auth_type: "system_oauth"`, OneDrive/SharePoint file access, and automatic profile picture refresh will fail.

### GitHub

Redirect URI: `<open-webui>/oauth/github/callback`

Required variables:
1. `GITHUB_CLIENT_ID` - GitHub OAuth App Client ID
2. `GITHUB_CLIENT_SECRET` - GitHub OAuth App Client Secret

### OIDC (Generic)

Redirect URI: `<open-webui>/oauth/oidc/callback`. The `email` claim is required. `name` and `picture` claims are used if available.

Required/used variables:
1. `OAUTH_CLIENT_ID` - OIDC client ID
2. `OAUTH_CLIENT_SECRET` - OIDC client secret
3. `OPENID_PROVIDER_URL` - **Required.** OIDC well known URL
4. `OAUTH_PROVIDER_NAME` - Name shown on UI, defaults to SSO
5. `OAUTH_SCOPES` - Scopes to request. Defaults to `openid email profile`
6. `OPENID_REDIRECT_URI` - Must be set to `<open-webui>/oauth/oidc/callback`
7. `OAUTH_AUDIENCE` - Optional `audience` value passed to authorization endpoint

**Common OIDC Mistakes:** Using non-existent variables like `OIDC_CONFIG`, forgetting `OPENID_PROVIDER_URL`, using incorrect redirect URI format.

### OAuth Role Management

Set `ENABLE_OAUTH_ROLE_MANAGEMENT` to `true` to manage roles from OAuth access tokens.

1. `OAUTH_ROLES_CLAIM` - Claim containing roles. Defaults to `roles`. Can be nested (e.g., `user.roles`).
2. `OAUTH_ALLOWED_ROLES` - Comma-separated list of roles allowed to log in (receive role `user`).
3. `OAUTH_ADMIN_ROLES` - Comma-separated list of roles that receive role `admin`.
4. `OAUTH_ROLES_SEPARATOR` - Alternative separator for `OAUTH_*_ROLES` variables.

Users must log out and back in to receive role changes.

### OAuth Group Management

Set `ENABLE_OAUTH_GROUP_MANAGEMENT` to `true` to sync user groups from OAuth tokens on login.

1. `OAUTH_GROUP_CLAIM` - Claim containing group memberships. Defaults to `groups`. Can be nested.
2. `ENABLE_OAUTH_GROUP_CREATION` - If `true`, performs Just-in-Time group creation during OAuth login. Defaults to `false`.
3. `OAUTH_GROUP_DEFAULT_SHARE` - Default sharing permission for JIT-created groups. Defaults to `true`. Set to `members` or `false`.

**Strict Synchronization:** When enabled, users are added to matching groups and removed from any Open WebUI groups not in their OAuth claims. Admin users' group memberships are not automatically updated.
