# Branding Blueprints

Declarative brand configuration via Authentik blueprints. Model: `authentik_brands.brand`.

## Basic Brand Blueprint

```yaml
version: 1
metadata:
  name: Custom Brand
  labels:
    blueprints.goauthentik.io/description: "Custom branding configuration"
entries:
  - model: authentik_brands.brand
    identifiers:
      domain: "."
      default: true
    attrs:
      branding_title: "My Organization"
      branding_logo: "/static/custom-assets/logo.svg"
      branding_favicon: "/static/custom-assets/favicon.png"
      flow_authentication: !Find [authentik_flows.flow, [slug, default-authentication-flow]]
      flow_invalidation: !Find [authentik_flows.flow, [slug, default-invalidation-flow]]
      flow_recovery: !Find [authentik_flows.flow, [slug, default-recovery-flow]]
      flow_user_settings: !Find [authentik_flows.flow, [slug, default-user-settings-flow]]
```

## Brand with Custom CSS

```yaml
version: 1
metadata:
  name: Branded Theme
entries:
  - model: authentik_brands.brand
    identifiers:
      domain: "."
      default: true
    attrs:
      branding_title: "My Org"
      branding_logo: "/static/custom-assets/logo.svg"
      branding_favicon: "/static/custom-assets/favicon.png"
      branding_default_flow_background: "background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%)"
      branding_custom_css: |
        :root {
          --pf-global--primary-color--100: #6366f1;
          --pf-global--primary-color--200: #4f46e5;
        }
        :host([theme="dark"]), [data-theme="dark"] {
          --pf-global--BackgroundColor--100: #0f172a;
          --pf-global--BackgroundColor--200: #1e293b;
          --pf-global--Color--100: #f1f5f9;
        }
        .pf-c-login__main {
          border-radius: 12px;
          backdrop-filter: blur(12px);
        }
      flow_authentication: !Find [authentik_flows.flow, [slug, default-authentication-flow]]
      flow_invalidation: !Find [authentik_flows.flow, [slug, default-invalidation-flow]]
      flow_user_settings: !Find [authentik_flows.flow, [slug, default-user-settings-flow]]
      attributes:
        settings:
          theme:
            base: automatic
          locale: en
```

## Brand with Theme Variants (Logo)

```yaml
entries:
  - model: authentik_brands.brand
    identifiers:
      domain: "."
      default: true
    attrs:
      # %(theme)s resolves to "light" or "dark"
      branding_logo: "/static/custom-assets/logo_%(theme)s.svg"
      branding_favicon: "/static/custom-assets/favicon.png"
      branding_title: "My Org"
      flow_authentication: !Find [authentik_flows.flow, [slug, default-authentication-flow]]
      flow_invalidation: !Find [authentik_flows.flow, [slug, default-invalidation-flow]]
      flow_user_settings: !Find [authentik_flows.flow, [slug, default-user-settings-flow]]
```

Requires two logo files: `logo_light.svg` and `logo_dark.svg`.

## Multi-Domain Brands

```yaml
version: 1
metadata:
  name: Multi-Domain Brands
entries:
  # Internal staff brand (default fallback)
  - model: authentik_brands.brand
    identifiers:
      domain: "."
      default: true
    attrs:
      branding_title: "Staff Portal"
      branding_logo: "/static/custom-assets/internal-logo.svg"
      branding_favicon: "/static/custom-assets/internal-favicon.png"
      branding_custom_css: |
        :root { --pf-global--primary-color--100: #2563eb; }
      flow_authentication: !Find [authentik_flows.flow, [slug, default-authentication-flow]]
      flow_invalidation: !Find [authentik_flows.flow, [slug, default-invalidation-flow]]
      flow_user_settings: !Find [authentik_flows.flow, [slug, default-user-settings-flow]]

  # Customer-facing brand
  - model: authentik_brands.brand
    identifiers:
      domain: "login.product.com"
    attrs:
      branding_title: "Product Login"
      branding_logo: "/static/custom-assets/product-logo.svg"
      branding_favicon: "/static/custom-assets/product-favicon.png"
      branding_default_flow_background: "/static/custom-assets/product-bg.jpg"
      branding_custom_css: |
        :root { --pf-global--primary-color--100: #059669; }
        .pf-c-login__footer-band { display: none; }
      flow_authentication: !Find [authentik_flows.flow, [slug, customer-authentication-flow]]
      flow_invalidation: !Find [authentik_flows.flow, [slug, default-invalidation-flow]]
```

## Branded Flow with Custom Layout

```yaml
version: 1
metadata:
  name: Branded Login Flow
entries:
  - model: authentik_flows.flow
    identifiers:
      slug: branded-authentication
    id: flow
    attrs:
      name: "Welcome"
      title: "Sign in to My Org"
      designation: authentication
      background: "/static/custom-assets/login-bg.jpg"
      layout: content_left   # stacked | content_left | content_right | sidebar_left | sidebar_right

  # Bind stages...
  - model: authentik_stages_identification.identificationstage
    identifiers:
      name: branded-identification
    id: identification
    attrs:
      user_fields:
        - email
      show_matched_user: true

  - model: authentik_stages_password.passwordstage
    identifiers:
      name: branded-password
    id: password

  - model: authentik_stages_user_login.userloginstage
    identifiers:
      name: branded-login
    id: login

  - model: authentik_flows.flowstagebinding
    identifiers:
      order: 10
      stage: !KeyOf identification
      target: !KeyOf flow
  - model: authentik_flows.flowstagebinding
    identifiers:
      order: 20
      stage: !KeyOf password
      target: !KeyOf flow
  - model: authentik_flows.flowstagebinding
    identifiers:
      order: 100
      stage: !KeyOf login
      target: !KeyOf flow
```

## Kubernetes Asset Delivery

Serve brand assets via ConfigMap mounted into the server pod. See [brand-model.md](brand-model.md) "Serving Custom Assets" section for volume mount configuration.

For Kustomize integration, use `configMapGenerator` to bundle blueprint YAML and reference in Helm `blueprints.configMaps`. See [blueprints.md](../blueprints.md) "Helm Chart: Native Blueprint ConfigMaps" section.
