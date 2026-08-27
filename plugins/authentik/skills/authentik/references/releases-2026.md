# What Changed in 2026.x

Digest of changes that affect anything documented in this skill. Current
release line: **2026.8** (released Aug 2026). Release cadence moved to
**three months** as of 2026.2, so the line is `2026.2 → 2026.5 → 2026.8 → 2026.11`.

Upstream notes: https://docs.goauthentik.io/releases/2026.8/

## Breaking changes you will actually hit

| Change | Version | What to do |
|---|---|---|
| `blank://blank` replaced by a real `meta_hide` boolean | 2026.5 | Use `meta_hide: true`. Existing `blank://blank` apps are auto-migrated on upgrade. See [hide-from-library.md](hide-from-library.md) |
| `User.ak_groups` deprecated | 2026.2 | Use `user.groups` in property mappings and policy expressions. Legacy use logs a System Task warning (throttled to once per 30 days) |
| Listen default `0.0.0.0` → `[::]` | 2026.5 | IPv4-only clusters may need `AUTHENTIK_LISTEN__HTTP=0.0.0.0:9000` set back explicitly |
| `AUTHENTIK_POSTGRESQL__CONN_OPTIONS` deprecated | 2026.5 | Slated for removal. Move pooler tuning to the `DIRECT` settings below |
| `hash_password` no longer takes a positional password | 2026.8 | Pipe via stdin: `echo "$PW" \| docker compose run --rm server hash_password` (keeps the password out of the process list) |
| WebAuthn "Prevent duplicate device" removed | 2026.8 | No replacement setting; drop it from blueprints |
| SCIM group syncing now filtered by application policies | 2026.2 | Existing group filters are deactivated on upgrade with a config warning — re-select groups |
| `docker-compose.yml` renamed `compose.yml` | 2026.2 | Docker installs only; Helm unaffected |
| Python 3.14 backend | 2026.2 | Custom property-mapping expressions run on 3.14 |

**Outpost versions must match the server version.** Upgrade both together.

## SAML: unified endpoints

2026.x exposes one endpoint that handles SSO *and* SLO for *both* HTTP-POST and
HTTP-Redirect bindings — the operation is detected from the inbound SAML message.

```
Unified SSO + SLO:  /application/saml/<slug>/
IdP-initiated:      /application/saml/<slug>/init/
Metadata:           /application/saml/<slug>/metadata/
```

The binding-specific paths (`/sso/binding/post/`, `/sso/binding/redirect/`,
`/sso/binding/init/`, `/slo/binding/post/`, `/slo/binding/redirect/`) **remain
available** for backward compatibility, and the API still returns them as
`url_sso_post`, `url_sso_redirect`, `url_sso_init`, `url_slo_post`,
`url_slo_redirect` alongside the new `url_unified` / `url_unified_init`.

Existing SP configs pointing at `/sso/binding/post/` keep working — there is no
forced migration. For new integrations the unified URL sidesteps the old
"POST vs Redirect / CSRF" trap entirely, since the binding no longer has to
match the path.

Other SAML changes:
- SAML **sources** gained `force_authn` (bool) — re-authenticate at the IdP even
  when a session exists.
- SAML **providers** honor an inbound `ForceAuthn` flag (2026.8).
- Metadata parser imports SLO endpoints and encryption certificates (2026.2).
- Auto-generated issuer URLs (2026.5) — `issuer_override` is now only needed when
  the SP demands a specific entity ID.
- Ed448 and ED25519 signing keys available for OAuth/OIDC and cert builder.

## PostgreSQL: transaction-mode pooler support (2026.8)

Previously PgBouncer in transaction mode required
`DISABLE_SERVER_SIDE_CURSORS=true` and still broke on LISTEN/NOTIFY and advisory
locks. 2026.8 splits the two connection needs:

- The existing `AUTHENTIK_POSTGRESQL__*` settings carry normal traffic and can
  point at a transaction-mode pooler.
- The new `AUTHENTIK_POSTGRESQL__DIRECT__*` settings point at a direct or
  session-pooled endpoint, used for operations that need a stable session.

`DIRECT` accepts: `HOST`, `PORT`, `NAME`, `USER`, `PASSWORD`, `SSLMODE`,
`SSLROOTCERT`, `SSLCERT`, `SSLKEY`. If unset, it falls back to the primary
settings — so single-database deployments need no change.

## Base URL is becoming mandatory (2026.11)

`AUTHENTIK_WEB__BASE_URL` — the external scheme+host this instance is reachable
at, e.g. `https://authentik.company`. Also settable in the UI under
**System > Settings** (`base_url`) or via the API. **Optional in 2026.8,
required from 2026.11** — set it now.

## New brand fields

| Field | Version | Description |
|---|---|---|
| `branding_map_tiles` | 2026.8 | Vector tile source for the events map. XYZ template with `{z}/{x}/{y}`, or a `pmtiles://` archive URL. Empty = bundled hexworld basemap (no external requests — relevant for airgapped). **Served to unauthenticated clients — never embed an API key here.** |
| `flow_user_switch` | 2026.8 | Flow used when switching between signed-in accounts |
| `flow_request` | 2026.8 | Flow used for access requests (PAM) |
| `flow_lockdown` | 2026.5 | Flow used by account lockdown |

## New in 2026.8 (feature surface)

- **OpenID Certified™** — Basic, Implicit, Hybrid, Config and Form Post OP
  profiles, plus RP-Initiated, Front-Channel and Back-Channel logout.
- **OAuth 2.0 Token Exchange** (RFC 8693) — trade a token from a trusted
  provider/source for an authentik access token for the same user; includes
  on-behalf-of (OBO) delegation.
- **Dynamic Client Registration (DCR)** — `/providers/oauth2-dcr/`; the OAuth2
  provider setup surfaces a `dcr_registration` URL.
- **Key-bound ID tokens** — binds the ID token to a key to blunt token theft.
- **Access Requests / PAM** (Enterprise) — users request access to applications
  and entitlements; approvers grant/deny; approved access auto-expires.
  API: `/requests/grant-requests/`, `/requests/rules/`, `/requests/rule-bindings/`,
  `/requests/rule-child-bindings/`.
- **Agent Accounts** (Enterprise) — service accounts that act on behalf of a
  parent user. API: `/agents/agents/`.
- **User switching** — multiple accounts signed in per browser, switched from the
  account menu. API: `/core/users/switch/`.
- **User offboarding** (Enterprise) — schedule deactivation/deletion with optional
  session and token revocation. API: `/lifecycle/user_offboarding/`.
- **Object Attributes** — declared custom text/number/bool fields with regex
  validation on users, groups and application entitlements.
  API: `/core/object_attributes/`.
- **Nested LDAP group sync** — "Sync Group Parents" preserves directory hierarchy.
- **Expiring bindings** — policy, group and user bindings take `expires` /
  `expiring`, so temporary access self-revokes.
- **Rust rewrite** — the server request entrypoint and the **proxy outpost** moved
  from Go to Rust. Described upstream as a 1-to-1 functional match: the
  `/outpost.goauthentik.io/auth/traefik` and `/auth/nginx` endpoints, the
  `X-authentik-*` headers, and the forward-auth token behavior are unchanged.
  The Django core is untouched. Note `AUTHENTIK_LISTEN__DEBUG` (9900) was the Go
  debug port.
- **CAPTCHA stage** — JSON verification and self-hostable Cap provider.
- **GitLab SCIM compatibility mode**; SCIM group import.
- **WS-Federation** (Enterprise) — SAML 1.1 assertions for Microsoft 365 / Entra ID.
- **AKQL** open-sourced in 2026.5; JSON field queries match numeric and boolean
  values as of 2026.8.
- **Command palette** — `Ctrl/Cmd + K` (2026.5).
- **Application Dashboard** — "My applications" renamed; grid/list toggle
  remembered per browser.
- `AUTHENTIK_BOOTSTRAP_PASSWORD_HASH` (2026.5) — seed `akadmin` with a pre-hashed
  Django password instead of a plaintext one.

## Performance / behavior notes

- Rust worker cut ~200 MB RSS and one PostgreSQL connection per worker (2026.5).
- S3 storage clients are reused instead of constructed per operation.
- Task status now reflects log outcomes, so warnings and errors surface instead of
  showing green.
- Deleting an authenticator stage no longer deletes the enrolled devices.
- Task schedules gained a `waiting_for_dependencies` status.
- Lifecycle tooling now blocks unsupported version skips — upgrade through each
  release line rather than jumping.
