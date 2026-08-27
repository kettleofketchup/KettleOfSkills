# Branding Blueprints: Branded Login Flow

Blueprint to create a fully branded authentication flow with custom layout and stages.

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
      background: "/static/dist/custom-assets/login-bg.jpg"
      layout: content_left   # stacked | content_left | content_right | sidebar_left | sidebar_right

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

For basic brand setup, multi-domain, and CSS blueprints, see [blueprints-basic.md](blueprints-basic.md).
