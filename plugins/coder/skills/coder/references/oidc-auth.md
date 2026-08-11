# Coder OIDC Authentication

All values are set as `coder.env` entries in the Helm chart. Put the client secret in a Kubernetes Secret and
reference it with `valueFrom.secretKeyRef` — never inline.

## Core Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `CODER_OIDC_ISSUER_URL` | IdP issuer (must serve `/.well-known/openid-configuration`) | `https://auth.example.com/application/o/coder/` |
| `CODER_OIDC_CLIENT_ID` | OAuth client ID | — |
| `CODER_OIDC_CLIENT_SECRET` | OAuth client secret | from Secret |
| `CODER_OIDC_SCOPES` | Requested scopes | `openid,profile,email,offline_access` |
| `CODER_OIDC_SIGN_IN_TEXT` | Login button label | `Sign in with Authentik` |
| `CODER_OIDC_ICON_URL` | Login button icon | `https://auth.example.com/static/dist/assets/icons/icon.png` |

Redirect/callback URL to register at the IdP: `https://coder.example.com/api/v2/users/oidc/callback`

## Claim Mapping

| Variable | Default | Notes |
|----------|---------|-------|
| `CODER_OIDC_EMAIL_FIELD` | `email` | Claim carrying the address |
| `CODER_OIDC_USERNAME_FIELD` | `preferred_username` | Must be stable — a changing value creates duplicate users |
| `CODER_OIDC_NAME_FIELD` | `name` | Display name |
| `CODER_OIDC_EMAIL_DOMAIN` | unset | Comma-separated allowlist, e.g. `example.com,corp.example.com` |
| `CODER_OIDC_IGNORE_EMAIL_VERIFIED` | `false` | Set `true` when the IdP omits `email_verified` |
| `CODER_OIDC_IGNORE_USERINFO` | `false` | `true` = trust ID token only, skip the UserInfo endpoint |

If a claim you need is missing, it is usually absent from the ID token rather than misnamed. Either add it to
the IdP's scope mapping or set `CODER_OIDC_IGNORE_USERINFO=false` so Coder fetches UserInfo.

## Group & Role Claims

Configured here, consumed by IdP sync (→ `idp-sync-rbac.md`):

```
CODER_OIDC_GROUP_FIELD=groups
CODER_OIDC_GROUP_AUTO_CREATE=true
CODER_OIDC_GROUP_REGEX_FILTER=^coder-.*$
CODER_OIDC_GROUP_MAPPING='{"idp-group-name":"coder-group-name"}'
CODER_OIDC_ALLOWED_GROUPS=coder-users        # hard gate: no membership, no login
CODER_OIDC_USER_ROLE_FIELD=roles             # Premium
CODER_OIDC_USER_ROLE_MAPPING='{"TemplateAuthor":["template-admin"]}'
```

`CODER_OIDC_ALLOWED_GROUPS` is the cleanest way to restrict who may log in at all — enforce authorization at
the IdP too, but this gives a second gate that survives IdP policy mistakes.

## Extra Auth Parameters

```
CODER_OIDC_AUTH_URL_PARAMS='{"access_type":"offline","prompt":"consent"}'
```

Needed for providers (notably Google) that only return a refresh token when explicitly asked. Without
`offline_access` / `access_type=offline`, long-lived sessions break when the access token expires.

## Hardening

```
CODER_DISABLE_PASSWORD_AUTH=true                      # SSO only
CODER_OAUTH2_GITHUB_DEFAULT_PROVIDER_ENABLE=false     # kill the default GitHub button
CODER_SESSION_DURATION=24h
CODER_DISABLE_SESSION_EXPIRY_REFRESH=false
```

Create at least one owner account and confirm it can log in via OIDC *before* setting
`CODER_DISABLE_PASSWORD_AUTH=true` — otherwise a broken OIDC config locks everyone out. Recovery requires
flipping the env var back and restarting the deployment.

## Custom CA / mTLS to the IdP

```
CODER_TLS_CLIENT_CERT_FILE=/certs/tls.crt
CODER_TLS_CLIENT_KEY_FILE=/certs/tls.key
```

For a private CA signing the IdP's certificate, mount the bundle via `coder.volumes`/`coder.volumeMounts` and
set `SSL_CERT_FILE=/etc/ssl/certs/ca.crt`. trust-manager can distribute the bundle into the `coder` namespace.

## Troubleshooting

Dump the claims Coder actually received:

```yaml
- name: CODER_LOG_FILTER
  value: ".*got oidc claims.*"
```

```bash
kubectl logs -n coder deploy/coder -f | grep -i "oidc claims"
```

| Symptom | Cause |
|---------|-------|
| `redirect_uri` mismatch | Callback at IdP ≠ `<CODER_ACCESS_URL>/api/v2/users/oidc/callback` |
| Login loops back to sign-in | Cookie domain wrong — `CODER_ACCESS_URL` must match the browser URL exactly (scheme included) |
| "email not verified" | Set `CODER_OIDC_IGNORE_EMAIL_VERIFIED=true` or fix the IdP claim |
| Duplicate users each login | `CODER_OIDC_USERNAME_FIELD` points at a mutable claim |
| Groups always empty | Claim missing from ID token; add the scope/property mapping at the IdP |
| Session drops after ~1h | No refresh token — add `offline_access` to `CODER_OIDC_SCOPES` |
