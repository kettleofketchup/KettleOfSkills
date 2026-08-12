# Traefik Forward Auth: Blueprint Example

Blueprint to declaratively create a proxy provider, application, and outpost binding.

```yaml
- model: authentik_providers_proxy.proxyprovider
  state: present
  identifiers:
    name: forward-auth-myapp
  id: proxy-myapp
  attrs:
    authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
    mode: forward_single
    external_host: https://app.example.com

- model: authentik_core.application
  state: present
  identifiers:
    slug: myapp
  attrs:
    name: My Protected App
    provider: !KeyOf proxy-myapp

- model: authentik_outposts.outpost
  state: present
  identifiers:
    name: authentik Embedded Outpost
  attrs:
    providers:
      - !KeyOf proxy-myapp
    type: proxy
    config:
      authentik_host: https://auth.example.com
```

For setup steps, Traefik Middleware CRDs, and header reference, see [middleware-setup.md](middleware-setup.md).
