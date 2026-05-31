# Hiding Applications from the User Library

## TL;DR

To hide an application's tile from the user's My Applications library
**without** changing its policies or removing it, set
`meta_launch_url: "blank://blank"` on the application.

**Critical:** the literal value is `blank://blank` — **NOT** `blank://`.
Authentik's URL validator rejects schemes without an authority part, so
`blank://` alone fails the serializer and the blueprint apply errors with:

```
Serializer errors {'meta_launch_url': ['Enter a valid URL.']}
```

This is the official, documented mechanism — see
https://docs.goauthentik.io/docs/applications/manage_apps#hide-applications

> "set the Launch URL to `blank://blank`, which will hide the application
> from users."

## When to use

The most common case is **forward-auth proxy providers that duplicate an
existing user-facing application**.

For example: Grafana has both a SAML provider (the real "Sign in with
Authentik" entry) and a forward-auth proxy provider (middleware that
gates the ingress). Both need an `authentik_core.application` row, but
the user only ever clicks the SAML one. The proxy-provider Application
exists purely to wire the provider into the embedded outpost — its tile
in the library is noise.

| App pattern | Hide? | Why |
|---|---|---|
| User-facing OIDC/SAML app | **No** — `meta_launch_url: https://app.<base>` | This IS the entry the user clicks |
| Forward-auth proxy that duplicates an OIDC/SAML app | **Yes** — `meta_launch_url: "blank://blank"` | Middleware-only; the OIDC/SAML entry is the user's click target |
| Forward-auth proxy that IS the user-facing app (no separate OIDC/SAML) | **No** — `meta_launch_url: https://app.<base>` | The proxy entry is the only entry; users find the app here |

A useful naming convention: hidden duplicates get the suffix
`<DisplayName> Access` (e.g. "Grafana Access"), visible user-facing
proxies get a clean human name (e.g. "Files", "Models").

## Blueprint pattern

```yaml
- model: authentik_core.application
  identifiers:
    slug: grafana-access
  attrs:
    name: "Grafana Access"
    provider: !KeyOf grafana-proxy
    policy_engine_mode: any
    # Hidden — duplicates the Grafana SAML entry that users actually click
    meta_launch_url: "blank://blank"
```

vs.

```yaml
- model: authentik_core.application
  identifiers:
    slug: copyparty-access
  attrs:
    name: "Files"
    provider: !KeyOf copyparty-proxy
    policy_engine_mode: any
    # Visible — CopyParty has no separate OIDC/SAML, this IS the entry
    meta_launch_url: "https://files.example.com"
```

## Helm chart pattern

For umbrella charts that template proxy providers from a values list,
add a `hide` flag per provider (default `true`, since most forward-auth
providers are duplicates):

```yaml
# values.yaml
providers:
  - name: grafana
    displayName: Grafana
    subdomain: grafana
    hide: true   # duplicates Grafana SAML
  - name: copyparty
    displayName: Files
    subdomain: files
    hide: false  # CopyParty has no separate OIDC/SAML — this IS the app
```

In the helper template, default `hide` to `true` if the key is omitted.
Use `ternary` (not `=` inside an `if` block — that creates a
block-scoped variable in Go templates):

```gotemplate
{{- $hide := ternary .hide true (hasKey . "hide") -}}

- model: authentik_core.application
  identifiers:
    slug: {{ .name }}-access
  attrs:
    {{- if $hide }}
    name: "{{ .displayName }} Access"
    meta_launch_url: "blank://blank"
    {{- else }}
    name: "{{ .displayName }}"
    meta_launch_url: "https://{{ .subdomain }}.{{ .baseDomain }}"
    {{- end }}
    provider: !KeyOf {{ .name }}-proxy
    policy_engine_mode: any
```

**Gotcha:** when including this helper from a parent template, the dict
constructor must explicitly pass `hide` through, otherwise `hasKey`
inside the helper is always false and everything ends up hidden:

```gotemplate
{{- range .Values.providers }}
{{ include "proxy-providers.entry" (dict
    "name" .name
    "displayName" .displayName
    "subdomain" .subdomain
    "baseDomain" $.Values.global.baseDomain
    "groups" .groups
    "hide" .hide) | indent 6 }}
{{- end }}
```

## Verifying

After the blueprint applies, check in the Admin UI:

- **Applications → Applications**: the entry exists with the right name
- **My Applications** (logged in as a normal user): the hidden entry is
  absent; the visible one is present and clicks through to the launch URL

If the blueprint reports `Enter a valid URL` on `meta_launch_url`, the
template is emitting `blank://` instead of `blank://blank` — fix the
literal.
