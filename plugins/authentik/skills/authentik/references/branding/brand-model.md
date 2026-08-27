# Brand Model Reference

Per-domain visual identity and flow routing. Model: `authentik_brands.brand` (renamed from `authentik_tenants.tenant` in 2024.2+).

## Brand Fields

| Field | Type | Description |
|-------|------|-------------|
| `domain` | text | Domain match: exact (`app.example.com`), wildcard (`*.example.com`), or default (`.`) |
| `default` | bool | Fallback brand when no domain matches |
| `branding_title` | text | Browser tab title, displayed throughout UI |
| `branding_logo` | file/URL | Upper-left logo. Supports `%(theme)s` placeholder for theme variants |
| `branding_favicon` | file/URL | Browser tab icon |
| `branding_custom_css` | text | Custom CSS injected into all pages (including ShadowDOM since 2025.4) |
| `branding_default_flow_background` | file/URL | Flow executor background. **URL/path only — a CSS value is silently ignored** |
| `branding_map_tiles` | text | Events-map vector tiles (2026.8+): XYZ template with `{z}`/`{x}`/`{y}`, or `pmtiles://` URL. Empty = bundled offline basemap. **Served to unauthenticated clients — no API keys** |
| `flow_authentication` `flow_invalidation` `flow_recovery` `flow_unenrollment` `flow_user_settings` `flow_device_code` | FK→flow | Login, logout, recovery, account removal, user settings, device code (smart TV) |
| `flow_user_switch` `flow_request` | FK→flow | Account switching and access requests / PAM (2026.8+) |
| `flow_lockdown` | FK→flow | Account lockdown (2026.5+) |
| `default_application` | FK→app | Redirect target for external users |
| `web_certificate` | FK→cert | HTTPS certificate |
| `client_certificates` | M2M→cert | Trusted CAs for mutual TLS |
| `attributes` | JSON | Custom attributes (locale, theme, user display settings) |

## Brand Attributes (JSON)

```yaml
attributes:
  settings:
    theme:
      base: automatic    # automatic | dark | light
    locale: en           # Language code
    default_user_display: username  # username | name | email
    layout:
      type: row          # row | 2-column | 3-column (Application Dashboard)
    search: true         # Show search bar
    sidebar:
      api_drawer: true   # API Drawer toggle
      notification_drawer: true
      user_settings: true
      application_edit: true
```

## Logo & Favicon Guidelines

- **Format**: SVG preferred; ~7:1 for wordmarks, 1:1 for icon-only
- **Favicon**: square, 32x32 or 48x48
- Remove fixed `width`/`height` from SVGs and trim excess `viewBox` whitespace
- **Theme variants**: `%(theme)s` in the path resolves to `light`/`dark` — e.g.
  `/static/dist/assets/icons/icon_%(theme)s.svg`; provide both files

## Serving Custom Assets

### Via Media Storage
Upload through Admin UI (System > Brands > edit). On the default `file` backend the media
dir is per-pod and ephemeral, so a multi-replica deploy needs an RWX volume or S3 first —
otherwise the upload hits one pod and is lost on restart. Imperative state, too: no
blueprint reproduces it.

### Via Static Files (Kubernetes)
Mount custom assets into the server pod:
```yaml
# values.yaml
server:
  volumes:
    - name: brand-assets
      configMap:
        name: authentik-brand-assets
  volumeMounts:
    - name: brand-assets
      mountPath: /web/dist/custom-assets/
      readOnly: true
```

Reference in brand: `/static/dist/custom-assets/logo.svg`

**The `dist` segment is required** — `/static/custom-assets/...` 404s (verified 2026.5.5),
failing silently as a broken image. `/static/dist/` maps to `/web/dist/`, a plain directory
server (no staticfiles manifest, no collectstatic step). Mount a NEW subdir: a ConfigMap
volume replaces the directory it lands on, so `/web/dist/assets/images` would hide
authentik's stock images.

### Via External URL
Point `branding_logo`/`branding_favicon` at a CDN or S3 URL — but this makes the login page
depend on an external host at render time.

## Flow Background Customization

Set at brand level; overridable per flow via `authentik_flows.flow` `background`.

### The field is a URL only — not a CSS value

```yaml
branding_default_flow_background: "/static/dist/custom-assets/bg.jpg"
```

**A CSS value like `background: linear-gradient(...)` does not work.** The
frontend wraps the value in `url("…")`, so a CSS declaration becomes a nonsense
image URL. This has never worked — verified in `FlowExecutor.ts` (2025.8.0) and
`applyBackgroundImageProperty` in `web/src/common/theme.ts` (2026.8.0); it is
not a 2026.x regression. Since 2026.5 the value is also gated by
`URL.canParse()` and a failing value is **silently ignored**, which is why a bad
value reads as "the setting does nothing". For a gradient use
`branding_custom_css`.

### Per-Flow Override
```yaml
- model: authentik_flows.flow
  identifiers:
    slug: my-login-flow
  attrs:
    background: "/static/dist/custom-assets/login-bg.jpg"
```

## Flow Layout Options

Set on individual flows, not brands:

| Layout | Description |
|--------|-------------|
| `stacked` | Single centered column (default) |
| `content_left` | Content on left, background on right |
| `content_right` | Content on right, background on left |
| `sidebar_left` | Sidebar navigation on left |
| `sidebar_right` | Sidebar navigation on right |

## API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| List brands | GET | `/api/v3/brands/` |
| Create brand | POST | `/api/v3/brands/` |
| Get brand | GET | `/api/v3/brands/{brand_uuid}/` |
| Update brand | PUT | `/api/v3/brands/{brand_uuid}/` |
| Partial update | PATCH | `/api/v3/brands/{brand_uuid}/` |
| Delete brand | DELETE | `/api/v3/brands/{brand_uuid}/` |
| Current brand | GET | `/api/v3/brands/current/` |

## Multi-Brand Strategy

Use multiple brands for different audiences on separate domains:

| Brand | Domain | Use Case |
|-------|--------|----------|
| Default | `.` (fallback) | Internal staff portal |
| Customer | `login.product.com` | Customer-facing, different logo/colors |
| Partner | `partner.example.com` | Partner portal, co-branded |

Each brand can assign different authentication flows, recovery flows, and visual themes.
