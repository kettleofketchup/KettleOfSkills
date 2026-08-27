# SAML Provider Configuration

## Create SAML Provider

In Admin UI → Applications → Providers → Create → SAML Provider:

| Setting | Description |
|---------|-------------|
| Name | Provider display name |
| Authorization flow | Flow used when user already authenticated |
| ACS URL | Service Provider's Assertion Consumer Service URL |
| Issuer | Authentik's entity ID (usually `https://auth.example.com`) |
| Service Provider Binding | `HTTP-POST` (most common) or `HTTP-Redirect` |
| Audience | SP entity ID / relying party identifier |
| Signing Certificate | Select self-signed or imported cert |
| Digest Algorithm | SHA-256 (recommended) |
| Signature Algorithm | RSA-SHA256, ECDSA-SHA256, or Ed25519/Ed448 (2026.2+) |
| Default NameID Policy | `default_name_id_policy` — policy used when the SP doesn't request one |
| Default Relay State | `default_relay_state` — RelayState for IdP-initiated flows |
| Logout Method | `logout_method` — front-channel or back-channel |

`issuer_override` is only needed when the SP demands a specific entity ID —
2026.5+ auto-generates the issuer URL from the instance base URL.

## NameID Policies

| Policy | Value | Use Case |
|--------|-------|----------|
| Persistent | Hashed user ID | Most applications |
| Email address | `user.email` | Apps requiring email as identifier |
| Windows | User UPN | Windows/AD environments |
| Transient | Session-based | Anonymous/ephemeral sessions |
| x509 Subject | Distinguished Name | Certificate-based |

## Endpoints

**2026.x unified endpoint** — one URL handles SSO *and* SLO for *both*
HTTP-POST and HTTP-Redirect bindings; the operation is detected from the
inbound SAML message:

```
https://auth.example.com/application/saml/<app-slug>/          # SSO + SLO, any binding
https://auth.example.com/application/saml/<app-slug>/init/     # IdP-initiated
https://auth.example.com/application/saml/<app-slug>/metadata/ # metadata XML
```

The binding-specific paths remain available for backward compatibility and are
still returned by the API (`url_sso_post`, `url_sso_redirect`, `url_sso_init`,
`url_slo_post`, `url_slo_redirect`), alongside the new `url_unified` and
`url_unified_init`:

```
/application/saml/<slug>/sso/binding/post/
/application/saml/<slug>/sso/binding/redirect/
/application/saml/<slug>/sso/binding/init/
/application/saml/<slug>/slo/binding/post/
/application/saml/<slug>/slo/binding/redirect/
```

Existing SP configurations pointing at `/sso/binding/post/` keep working — there
is no forced migration. On pre-2026 releases, or when pinning a legacy path, use
`/sso/binding/post/` rather than `/sso/binding/redirect/`: the redirect binding
trips CSRF protection for several SPs. The unified endpoint sidesteps that
choice entirely, since the binding no longer has to match the path.

Import SP metadata to auto-configure provider settings. Since 2026.2 the
metadata parser also imports Single Logout Service endpoints and encryption
certificates.

## Default SAML Property Mappings

7 built-in mappings (all use URN OID format):

| Mapping | SAML Attribute | Expression |
|---------|---------------|------------|
| Email | `urn:oid:0.9.2342.19200300.100.1.3` | `request.user.email` |
| Groups | `http://schemas.xmlsoap.org/claims/Group` | `user.groups.all()` |
| Name | `urn:oid:2.5.4.3` | `request.user.name` |
| UPN | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn` | `request.user.email` |
| User ID | `urn:oid:0.9.2342.19200300.100.1.1` | `request.user.pk` |
| Username | `http://schemas.goauthentik.io/2021/02/saml/username` | `request.user.username` |
| WindowsAccountName | `http://schemas.microsoft.com/ws/2008/06/identity/claims/windowsaccountname` | `request.user.username` |

**`user.ak_groups` is deprecated as of 2026.2 — use `user.groups`.** Legacy use
still works but logs a System Task configuration warning (throttled to once per
30 days). Update custom mappings and policy expressions.

## Custom Property Mapping

Create via Admin UI → Customization → Property Mappings → Create → SAML:

```python
# Expression variables available:
# request - HTTP request object
# request.user - authenticated user
# provider - SAML provider instance
# user - alias for request.user
# Expressions run on Python 3.14 as of 2026.2

# Example: custom group membership attribute
return list(request.user.groups.filter(
    name__startswith="app-"
).values_list("name", flat=True))
```

**SAML Attribute Name:** OID or friendly name the SP expects
**Friendly Name:** Optional human-readable name

## Application Binding

After creating provider, create Application:
1. Admin UI → Applications → Create
2. Set name, slug, provider (select SAML provider)
3. Optionally set launch URL, icon, policy bindings
4. App slug determines all SAML endpoint URLs

## Blueprint Example (SAML Provider)

```yaml
# See blueprints.md for full schema
- model: authentik_providers_saml.samlprovider
  state: present
  identifiers:
    name: my-app-saml
  id: provider-my-app
  attrs:
    authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
    acs_url: https://myapp.example.com/saml/acs
    issuer: https://auth.example.com
    sp_binding: post
    name_id_mapping: !Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/upn]]
    signing_kp: !Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]
    digest_algorithm: http://www.w3.org/2001/04/xmlenc#sha256
    signature_algorithm: http://www.w3.org/2001/04/xmldsig-more#rsa-sha256

- model: authentik_core.application
  state: present
  identifiers:
    slug: my-app
  attrs:
    name: My App
    provider: !KeyOf provider-my-app
    policy_engine_mode: any
```
