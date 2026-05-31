---
name: authentik
description: Authentik self-hosted IdP on Kubernetes. This skill should be used when deploying via Helm, configuring SAML/OAuth2 providers, blueprints, Google Workspace SSO, forward-auth, branding, or app SSO.
---

# Authentik

Self-hosted identity provider supporting SAML, OAuth2/OIDC, LDAP, and proxy authentication. Designed for Kubernetes deployment via Helm with declarative configuration through blueprints.

## Quick Start

### Helm Deployment

```bash
helm repo add authentik https://charts.goauthentik.io
helm repo update
helm upgrade --install authentik authentik/authentik -f values.yaml -n authentik --create-namespace
```

Initial setup: `https://<host>/if/flow/initial-setup/`

For Helm values reference and ArgoCD app-of-apps integration, see [deployment.md](references/deployment.md).

## Task Reference

### SAML Provider Setup
Configure SAML providers for SSO with applications (ArgoCD, Grafana, etc.).
- Provider settings, NameID policies, signing certificates
- Metadata URL: `/application/saml/<slug>/metadata/`
- ACS URL: `/application/saml/<slug>/sso/binding/post/`
- See [saml.md](references/saml.md)

### Blueprints (Declarative Config)
YAML-based declarative configuration for flows, stages, providers, applications.
- v1 schema: `version`, `metadata`, `context`, `entries`
- Tags: `!KeyOf` (intra-blueprint only), `!Find`, `!FindObject` (2025.8+), `!Env`, `!Context`, `!Format`, `!If`, `!Condition`, `!Enumerate`. **`!Slice` does not exist** — common mis-citation.
- `state:` values: `present` (reconcile drift), `created` (create-once-ignore-after), `must_created` (fail if exists), `absent` (delete)
- Mount via ConfigMap at `/blueprints/custom/` in server + worker pods, atomic per-file transactions, 60min reapply cadence
- See [blueprints.md](references/blueprints.md) for the structural overview
- **State semantics, !KeyOf scoping, first-boot chicken-and-egg**: [blueprints/sync_states.md](references/blueprints/sync_states.md)
- **LDAP sources** (`user_matching_mode`, password sync, delete_not_found): [blueprints/ldap_sources.md](references/blueprints/ldap_sources.md)

### Traefik Forward Auth Middleware
Protect apps behind Traefik using Authentik proxy provider outpost.
- Proxy provider → embedded or standalone outpost
- Traefik `forwardAuth` middleware pointing to outpost
- Headers: `X-authentik-username`, `X-authentik-groups`, `X-authentik-email`
- See [middleware.md](references/middleware.md)

### Hiding Applications from the User Library
Use `meta_launch_url: "blank://blank"` to hide a proxy-provider Application's tile from My Applications without changing its policies. The literal is `blank://blank` — `blank://` alone fails Authentik's URL validator with `Enter a valid URL`. Hide forward-auth proxies that **duplicate** an existing OIDC/SAML user-facing app; keep visible (with a real launch URL) for proxies that ARE the only user-facing entry.
- See [hide-from-library.md](references/hide-from-library.md)

### Google Workspace SAML Login
"Login with Google" via SAML federation source.
- Google Admin Console: custom SAML app → ACS URL + Entity ID
- Authentik: SAML source with Google SSO URL + signing certificate
- See [google-source.md](references/google-source.md)

### Application Integrations
SAML/OIDC setup for common self-hosted apps.
- ArgoCD SAML via Dex (recommended) → [integrations/argocd.md](references/integrations/argocd.md)
- Grafana, Gitea, MinIO, generic SAML → [integrations.md](references/integrations.md)
- **Critical**: SAML SSO URLs must use `/sso/binding/post/` not `/sso/binding/redirect/` (CSRF)

### Configuration & Environment Variables
All settings via `AUTHENTIK_*` env vars. Double underscore (`__`) separates nested keys.
- Core: `SECRET_KEY`, `LOG_LEVEL`, `COOKIE_DOMAIN`
- PostgreSQL: connection, SSL/TLS, PgBouncer (`DISABLE_SERVER_SIDE_CURSORS`), read replicas
- Storage: file or S3 backend, per-category overrides (media, reports)
- Web/Worker tuning: Gunicorn workers/threads, Dramatiq task settings
- Listen addresses, cache timeouts, email/SMTP, outpost image base
- Values support `env://` and `file://` URI syntax for indirection
- See [configuration.md](references/configuration.md)

### Airgapped / Offline Deployment
Disable all outbound connections for air-gapped environments:
- `AUTHENTIK_DISABLE_UPDATE_CHECK=true` — disable version checker
- `AUTHENTIK_DISABLE_STARTUP_ANALYTICS=true` — disable startup analytics
- `AUTHENTIK_ERROR_REPORTING__ENABLED=false` — disable Sentry
- Avatars: set to `initials` in System > Settings (default uses Gravatar)
- GeoIP: auto-skipped if DB files missing at `/geoip/`
- Mirror container images and Helm chart to internal registries
- Set `AUTHENTIK_OUTPOSTS__CONTAINER_IMAGE_BASE` to internal registry
- See [configuration.md](references/configuration.md) (Airgapped Deployment Settings section)

### Branding & Theming
Custom logos, colors, CSS, and per-domain visual identity via the `authentik_brands.brand` model.
- Brand fields: title, logo, favicon, custom CSS, default flow background
- Logo theme variants with `%(theme)s` placeholder (light/dark)
- Patternfly CSS variables (`--pf-global--primary-color--*`) for color schemes
- Flow-level overrides: per-flow backgrounds and layout (stacked, content_left/right, sidebar)
- Multi-domain brands: different branding per domain with wildcard support
- Custom font loading, UI element hiding, Shadow DOM `::part()` targeting
- See [branding/brand-model.md](references/branding/brand-model.md) — brand fields, attributes, asset serving, API
- See [branding/custom-css.md](references/branding/custom-css.md) — CSS variables, color schemes, component styling
- See [branding/blueprints.md](references/branding/blueprints.md) — declarative brand config, multi-domain, Kustomize

### Property Mappings & Policies
Custom attribute statements and access control.
- SAML mappings: Python expressions with `request`, `user`, `provider` variables
- 7 default SAML mappings (Email, Groups, Name, UPN, User ID, Username, WindowsAccountName)
- Expression policies for conditional access
- See [saml.md](references/saml.md)

## Key URLs

| Endpoint | URL Pattern |
|----------|-------------|
| Admin UI | `/if/admin/` |
| User UI | `/if/user/` |
| SAML Metadata | `/application/saml/<slug>/metadata/` |
| SAML SSO (POST) | `/application/saml/<slug>/sso/binding/post/` |
| SAML SSO (Redirect) | `/application/saml/<slug>/sso/binding/redirect/` |
| SAML SLO | `/application/saml/<slug>/slo/binding/[post\|redirect]/` |
| IdP-initiated SSO | `/application/saml/<slug>/sso/binding/init/` |
| OAuth2 Authorize | `/application/o/authorize/` |
| OIDC Discovery | `/application/o/<slug>/.well-known/openid-configuration` |
| Outpost health | `outpost:9300/metrics` |
