# Open WebUI Environment Variables: Authentication, OAuth, LDAP & Security

## Security Variables

| Variable | Type | Default | Description |
|---|---|---|---|
| `WEBUI_AUTH` | bool | `True` | Enable/disable authentication. Can only disable on fresh installs with no users. |
| `WEBUI_SECRET_KEY` | str | `t0p-s3cr3t` | Key for JWT and encryption. Docker: randomly generated. **MUST** be set in production. Changing it invalidates all sessions and breaks MCP token decryption. Must be identical across all replicas. |
| `JWT_EXPIRES_IN` | str | `4w` | JWT expiration. Valid units: `s`, `m`, `h`, `d`, `w`. `-1` disables (dangerous in production). PersistentConfig. |
| `WEBUI_SESSION_COOKIE_SAME_SITE` | str | `lax` | SameSite for session cookies: `lax`, `strict`, `none`. Use `lax` with OAuth. |
| `WEBUI_SESSION_COOKIE_SECURE` | bool | `False` | Secure attribute for session cookies. Set `True` for HTTPS. |
| `WEBUI_AUTH_COOKIE_SAME_SITE` | str | `lax` | SameSite for auth cookies. Falls back to session cookie setting. |
| `WEBUI_AUTH_COOKIE_SECURE` | bool | `False` | Secure attribute for auth cookies. Falls back to session cookie setting. |
| `ENABLE_PASSWORD_VALIDATION` | bool | `False` | Enables password complexity validation. |
| `PASSWORD_VALIDATION_REGEX_PATTERN` | str | `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$` | Regex for password validation. |
| `PASSWORD_VALIDATION_HINT` | str | `''` | Custom hint for failed password validation. |
| `ENABLE_WEB_LOADER_SSL_VERIFICATION` | bool | `True` | SSL verification for RAG web fetches. PersistentConfig. |

## Forward User Info Headers

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_FORWARD_USER_INFO_HEADERS` | bool | `False` | Forward user/session info as HTTP headers to APIs, MCP, tool servers. |
| `FORWARD_USER_INFO_HEADER_USER_NAME` | str | `X-OpenWebUI-User-Name` | Header for user display name. |
| `FORWARD_USER_INFO_HEADER_USER_ID` | str | `X-OpenWebUI-User-Id` | Header for user ID. |
| `FORWARD_USER_INFO_HEADER_USER_EMAIL` | str | `X-OpenWebUI-User-Email` | Header for user email. |
| `FORWARD_USER_INFO_HEADER_USER_ROLE` | str | `X-OpenWebUI-User-Role` | Header for user role. |
| `FORWARD_SESSION_INFO_HEADER_CHAT_ID` | str | `X-OpenWebUI-Chat-Id` | Header for chat ID. |
| `FORWARD_SESSION_INFO_HEADER_MESSAGE_ID` | str | `X-OpenWebUI-Message-Id` | Header for message ID. Required for external tool events. |

## OAuth / OIDC

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_OAUTH_SIGNUP` | bool | `False` | Enables OAuth/SSO signup. |
| `ENABLE_OAUTH_PERSISTENT_CONFIG` | bool | `False` | When `False` (default), OAuth env vars always take priority over DB values. |
| `OAUTH_CLIENT_ID` | str | - | OIDC client ID. |
| `OAUTH_CLIENT_SECRET` | str | - | OIDC client secret. |
| `OPENID_PROVIDER_URL` | str | - | OIDC discovery URL (`.well-known/openid-configuration`). Required for OIDC. |
| `OAUTH_PROVIDER_NAME` | str | - | Display name for OAuth provider. |
| `OAUTH_SCOPES` | str | `openid email profile` | OAuth scopes. |
| `OPENID_REDIRECT_URI` | str | - | Callback URL: `https://your-domain/oauth/oidc/callback`. |
| `OAUTH_AUTHORIZE_PARAMS` | str | - | JSON object of extra authorize params (e.g., `{"prompt":"consent"}`). |
| `OAUTH_SESSION_TOKEN_ENCRYPTION_KEY` | str | - | Encryption key for OAuth session tokens. Must be same across all instances. |

## Google OAuth

| Variable | Type | Default | Description |
|---|---|---|---|
| `GOOGLE_CLIENT_ID` | str | - | Google OAuth client ID. |
| `GOOGLE_CLIENT_SECRET` | str | - | Google OAuth client secret. |
| `GOOGLE_OAUTH_AUTHORIZE_PARAMS` | str | - | Extra Google authorize params JSON. |

## Microsoft OAuth

| Variable | Type | Default | Description |
|---|---|---|---|
| `MICROSOFT_CLIENT_ID` | str | - | Microsoft Entra ID client ID. |
| `MICROSOFT_CLIENT_SECRET` | str | - | Microsoft client secret. |
| `MICROSOFT_CLIENT_TENANT_ID` | str | - | Microsoft tenant ID. |
| `MICROSOFT_OAUTH_SCOPE` | str | `openid email profile` | Microsoft OAuth scopes. |
| `MICROSOFT_REDIRECT_URI` | str | - | Callback: `https://your-domain/oauth/microsoft/callback`. |

## OAuth Callback URLs

- OIDC: `https://your-domain/oauth/oidc/callback`
- Microsoft: `https://your-domain/oauth/microsoft/callback`
- Google: `https://your-domain/oauth/google/callback`

## Common OAuth Mistakes

Wrong variable names people use:
- `OIDC_CONFIG` -- use `OPENID_PROVIDER_URL`
- `WEBUI_OIDC_CLIENT_ID` -- use `OAUTH_CLIENT_ID`
- `WEBUI_ENABLE_SSO` -- use `ENABLE_OAUTH_SIGNUP`
- `OPENID_CLIENT_ID` -- use `OAUTH_CLIENT_ID`

## API Key Configuration

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_API_KEYS` | bool | `False` | Enables API key creation. Non-admin users need "API Keys" permission. PersistentConfig. |
| `ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS` | bool | `False` | Enables endpoint restrictions for API keys. PersistentConfig. |
| `API_KEYS_ALLOWED_ENDPOINTS` | str | - | Comma-separated allowed endpoints. PersistentConfig. |

## Model Caching

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_BASE_MODELS_CACHE` | bool | `False` | Caches base model list in memory. Refreshes on restart or Admin Save. PersistentConfig. |
| `MODELS_CACHE_TTL` | int | `1` | Cache TTL (seconds) for model list API responses. Set 300 for production. |

## Pending User Overlay

| Variable | Type | Default | Description |
|---|---|---|---|
| `PENDING_USER_OVERLAY_TITLE` | str | `''` | Custom title for pending user overlay. PersistentConfig. |
| `PENDING_USER_OVERLAY_CONTENT` | str | `''` | Custom content for pending user overlay. PersistentConfig. |

## Community & Evaluation

| Variable | Type | Default | Description |
|---|---|---|---|
| `ENABLE_COMMUNITY_SHARING` | bool | `True` | Controls community sharing buttons and resource discovery. PersistentConfig. |
| `ENABLE_EVALUATION_ARENA_MODELS` | bool | `True` | Enables evaluation arena models. PersistentConfig. |
| `ENABLE_MESSAGE_RATING` | bool | `True` | Enables message rating. PersistentConfig. |
