# Blueprint Examples: Proxy Provider, ConfigMap, Dependencies

## Proxy Provider (Traefik Forward Auth)

```yaml
version: 1
metadata:
  name: proxy-dashboard
  labels:
    blueprints.goauthentik.io/description: "Forward auth for dashboard"
entries:
  - model: authentik_providers_proxy.proxyprovider
    identifiers:
      name: forward-auth-dashboard
    id: proxy-provider
    attrs:
      authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
      mode: forward_single
      external_host: !Format ["https://dashboard.%s", !Env [DOMAIN]]

  - model: authentik_core.application
    identifiers:
      slug: dashboard
    attrs:
      name: Dashboard
      provider: !KeyOf proxy-provider

  - model: authentik_outposts.outpost
    identifiers:
      name: authentik Embedded Outpost
    attrs:
      type: proxy
      providers:
        - !KeyOf proxy-provider
```

## Kubernetes ConfigMap with Multiple Blueprints

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: authentik-blueprints-apps
  namespace: authentik
data:
  saml-apps.yaml: |
    version: 1
    metadata:
      name: saml-apps
    entries:
      - model: authentik_providers_saml.samlprovider
        identifiers:
          name: grafana-saml
        id: grafana-provider
        attrs:
          authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
          acs_url: https://grafana.example.com/saml/acs
          issuer: https://auth.example.com
          sp_binding: post
          signing_kp: !Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]
      - model: authentik_core.application
        identifiers:
          slug: grafana
        attrs:
          name: Grafana
          provider: !KeyOf grafana-provider
  groups.yaml: |
    version: 1
    metadata:
      name: default-groups
    entries:
      - model: authentik_core.group
        identifiers:
          name: admins
        state: created
        attrs:
          is_superuser: false
      - model: authentik_core.group
        identifiers:
          name: viewers
        state: created
```

## Blueprint with Dependencies (metaapplyblueprint)

```yaml
version: 1
metadata:
  name: my-app-with-deps
entries:
  # Ensure authentication flow exists first
  - model: authentik_blueprints.metaapplyblueprint
    identifiers:
      name: Default - Authentication flow
    attrs:
      required: true

  # Then create our provider and app
  - model: authentik_providers_saml.samlprovider
    identifiers:
      name: my-app-saml
    id: provider
    attrs:
      authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
      acs_url: https://app.example.com/saml/acs
      issuer: https://auth.example.com
      sp_binding: post
      signing_kp: !Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]

  - model: authentik_core.application
    identifiers:
      slug: my-app
    attrs:
      name: My App
      provider: !KeyOf provider
```
