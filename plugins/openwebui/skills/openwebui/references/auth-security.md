# Authentication & Security Reference

## SSO (OAuth / OIDC)

### Prerequisites
- `WEBUI_URL` must be set before enabling OAuth
- `WEBUI_SECRET_KEY` is mandatory (especially clustered environments)
- When `ENABLE_OAUTH_PERSISTENT_CONFIG=true` (default), OAuth settings persist in DB; DB values override env vars

### OAuth Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBUI_URL` | -- | **Required.** Public address |
| `ENABLE_OAUTH_PERSISTENT_CONFIG` | `true` | Persist config to DB; `false` for stateless |
| `ENABLE_OAUTH_SIGNUP` | `false` | Allow account creation via OAuth |
| `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` | `false` | Merge by matching email |
| `OAUTH_UPDATE_PICTURE_ON_LOGIN` | `false` | Update profile pics each login |
| `OAUTH_PICTURE_CLAIM` | `picture` | Claim field for profile picture |
| `WEBUI_AUTH_SIGNOUT_REDIRECT_URL` | empty | Redirect URL after signout |
| `WEBUI_SECRET_KEY` | empty | Secret key for sessions |
| `ENABLE_OAUTH_TOKEN_EXCHANGE` | `false` | Token exchange for external apps |
| `OAUTH_MAX_SESSIONS_PER_USER` | `10` | Max concurrent sessions |

### Google OAuth
`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OPENID_PROVIDER_URL=https://accounts.google.com/.well-known/openid-configuration`
Redirect: `<open-webui>/oauth/google/callback`

### Microsoft OAuth
`MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`, `MICROSOFT_CLIENT_TENANT_ID`
Add `offline_access` to `MICROSOFT_OAUTH_SCOPE` for token refresh.
Redirect: `<open-webui>/oauth/microsoft/callback`

### GitHub OAuth
`GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
Redirect: `<open-webui>/oauth/github/callback`

### Generic OIDC
| Variable | Description |
|----------|-------------|
| `OAUTH_CLIENT_ID` | OIDC client ID |
| `OAUTH_CLIENT_SECRET` | OIDC client secret |
| `OPENID_PROVIDER_URL` | **Mandatory.** Well-known URL |
| `OPENID_REDIRECT_URI` | `<open-webui>/oauth/oidc/callback` |
| `OAUTH_PROVIDER_NAME` | Display name (default: `SSO`) |
| `OAUTH_SCOPES` | `openid email profile` |

### OAuth Role Management
`ENABLE_OAUTH_ROLE_MANAGEMENT=true`
| Variable | Description |
|----------|-------------|
| `OAUTH_ROLES_CLAIM` | Claim containing roles (supports nested: `user.roles`) |
| `OAUTH_ALLOWED_ROLES` | Comma-separated roles -> `user` role |
| `OAUTH_ADMIN_ROLES` | Comma-separated roles -> `admin` role |

### OAuth Group Management
`ENABLE_OAUTH_GROUP_MANAGEMENT=true`
| Variable | Default | Description |
|----------|---------|-------------|
| `OAUTH_GROUP_CLAIM` | `groups` | Token claim for groups (supports nested: `user.memberOf`) |
| `ENABLE_OAUTH_GROUP_CREATION` | `false` | JIT group creation |
| `OAUTH_GROUP_DEFAULT_SHARE` | `true` | Default sharing for JIT groups |

---

## Trusted Header Authentication

Reverse proxy passes user details via HTTP headers. Restrict access with network isolation or `HOST=127.0.0.1`.

| Variable | Description |
|----------|-------------|
| `WEBUI_AUTH_TRUSTED_EMAIL_HEADER` | Header with user email |
| `WEBUI_AUTH_TRUSTED_NAME_HEADER` | Header with user name |
| `WEBUI_AUTH_TRUSTED_GROUPS_HEADER` | Comma-separated group list |
| `WEBUI_AUTH_TRUSTED_ROLE_HEADER` | Role: `admin`, `user`, `pending` |

### Tailscale Serve
Header: `Tailscale-User-Login`. Set `WEBUI_AUTH_TRUSTED_EMAIL_HEADER=Tailscale-User-Login`.

### Cloudflare Access
Header: `Cf-Access-Authenticated-User-Email`.

---

## Keycloak SSO
1. Create realm `openwebui`, client `open-webui` (confidential, openid-connect)
2. Enable client auth, copy secret
3. Set `OPENID_PROVIDER_URL=http://localhost:9090/realms/openwebui/.well-known/openid-configuration`

---

## LDAP Authentication

| Variable | Example | Description |
|----------|---------|-------------|
| `ENABLE_LDAP` | `true` | Enable LDAP |
| `LDAP_SERVER_HOST` | `localhost` | Host (no protocol prefix) |
| `LDAP_SERVER_PORT` | `389` | 389=plaintext/StartTLS, 636=LDAPS |
| `LDAP_USE_TLS` | `false` | TLS toggle |
| `LDAP_APP_DN` | `cn=admin,dc=example,dc=org` | Bind DN |
| `LDAP_APP_PASSWORD` | `admin` | Bind password |
| `LDAP_SEARCH_BASE` | `dc=example,dc=org` | Search base |
| `LDAP_ATTRIBUTE_FOR_USERNAME` | `uid` | Username attribute |
| `LDAP_ATTRIBUTE_FOR_MAIL` | `mail` | Email attribute |
| `LDAP_SEARCH_FILTER` | `(memberOf=...)` | Optional filter |

**Note**: Read on first startup only. Use Admin UI for changes unless `ENABLE_PERSISTENT_CONFIG=false`.

---

## SCIM 2.0 Provisioning

| Variable | Description |
|----------|-------------|
| `SCIM_ENABLED` | `false` -- enable SCIM |
| `SCIM_TOKEN` | Bearer token (`openssl rand -base64 32`) |
| `SCIM_AUTH_PROVIDER` | OAuth provider name for externalId |

Base URL: `<your-url>/api/v1/scim/v2/`

Operations: CRUD for Users (`/Users`) and Groups (`/Groups`). Supports filter operators: `eq`, `ne`, `co`, `sw`, `ew`, `pr`, `gt`, `ge`, `lt`, `le`.

---

## RBAC

### Roles

| Role | Description |
|------|-------------|
| Admin | Full system control; bypass most permissions |
| User | Standard user subject to RBAC |
| Pending | Zero access until promoted |

`DEFAULT_USER_ROLE=pending` (options: `pending`, `user`, `admin`)

### Headless Admin
| Variable | Description |
|----------|-------------|
| `WEBUI_ADMIN_EMAIL` | Admin email |
| `WEBUI_ADMIN_PASSWORD` | Admin password |
| `WEBUI_ADMIN_NAME` | Display name |

Only creates on fresh install (empty DB).

### Permissions (Additive -- True takes precedence)

**Workspace**: Models Access/Import/Export, Knowledge Access, Prompts Access/Import/Export, Tools Access/Import/Export, Skills Access

**Sharing**: Share/Public Models, Knowledge, Prompts, Tools, Skills, Notes

**Chat**: Chat Controls, Model Valves, System Prompt, Parameters, File Upload, Delete/Edit/Rate, STT/TTS/Audio Call, Multiple Models, Temporary Chat, Enforced Temporary

**Features**: API Keys, Notes, Channels, Folders, Web Search, Image Generation, Code Interpreter, Direct Tool Servers, Memories

### Groups
Additive permissions. Visibility: Anyone (default), Members, No one.

**Recommended**: Separate permission groups (`[Perms] Image Gen`) from sharing groups (`Team-Engineering`).

---

## Banners

`WEBUI_BANNERS` -- JSON array. Properties: `id`, `type` (`info`/`success`/`warning`/`error`), `title`, `content` (HTML), `dismissible`, `timestamp`.

---

## Webhooks

1. **Admin webhook** (`WEBHOOK_URL`): fires on `new_user` events
2. **User webhook** (`ENABLE_USER_WEBHOOKS`): fires `chat_response` when user not active
3. **Channel webhooks**: POST to `{WEBUI_API_BASE_URL}/channels/webhooks/{id}/{token}` with `{"content": "..."}`

---

## Analytics

Admin Panel > Analytics. Disable: `ENABLE_ADMIN_ANALYTICS=False`.

Tracks: messages, tokens, chats, users. Model usage table, user activity table. Elo-based leaderboard with arena evaluation.

API: `GET /api/v1/analytics/{summary|models|users|messages|daily|tokens}` with `start_date`, `end_date`, `group_id` params.
