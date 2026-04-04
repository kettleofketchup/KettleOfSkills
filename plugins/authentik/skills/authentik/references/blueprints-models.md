# Blueprint Model Reference

All models use `app_label.modelname` notation in blueprint `model` field.

## Brands

| Model | Key Fields |
|-------|------------|
| `authentik_brands.brand` | domain, default, branding_title, branding_logo, branding_favicon, branding_custom_css, branding_default_flow_background, flow_authentication, flow_invalidation, flow_recovery, flow_unenrollment, flow_user_settings, flow_device_code, default_application, web_certificate, client_certificates, attributes |

Default brand: `!Find [authentik_brands.brand, [domain, .]]`

## Core

| Model | Key Fields |
|-------|------------|
| `authentik_core.application` | slug, name, provider, icon (URL), policy_engine_mode |
| `authentik_core.group` | name, is_superuser, parent, attributes |
| `authentik_core.user` | username, name, email, password, path, attributes |
| `authentik_core.token` | identifier, key, user, intent, expiring |

## Flows

| Model | Key Fields |
|-------|------------|
| `authentik_flows.flow` | slug, name, title, designation, denied_action, background (URL) |
| `authentik_flows.flowstagebinding` | target (flow), stage, order, evaluate_on_plan, re_evaluate_policies |

Flow designations: `authentication`, `authorization`, `enrollment`, `invalidation`, `recovery`, `stage_configuration`, `unenrollment`

## Stages

| Model | Key Fields |
|-------|------------|
| `authentik_stages_identification.identificationstage` | name, user_fields, sources, show_matched_user |
| `authentik_stages_password.passwordstage` | name, backends, configure_flow |
| `authentik_stages_authenticator_validate.authenticatorvalidatestage` | name, device_classes |
| `authentik_stages_user_login.userloginstage` | name, session_duration, remember_me_offset |
| `authentik_stages_consent.consentstage` | name, mode (always/once/until_expiry) |
| `authentik_stages_deny.denystage` | name |
| `authentik_stages_user_write.userwritestage` | name, create_users_as_inactive |
| `authentik_stages_user_logout.userlogoutstage` | name |
| `authentik_stages_email.emailstage` | name, host, port, subject, template |
| `authentik_stages_invitation.invitationstage` | name, continue_flow_without_invitation |
| `authentik_stages_prompt.promptstage` | name, fields, validation_policies |
| `authentik_stages_captcha.captchastage` | name, public_key, private_key |

## Providers

| Model | Key Fields |
|-------|------------|
| `authentik_providers_saml.samlprovider` | name, authorization_flow, acs_url, issuer, sp_binding, audience, signing_kp, name_id_mapping, digest_algorithm, signature_algorithm, property_mappings |
| `authentik_providers_saml.samlpropertymapping` | name, saml_name, friendly_name, expression, managed |
| `authentik_providers_oauth2.oauth2provider` | name, authorization_flow, client_type, client_id, client_secret, redirect_uris, signing_key, property_mappings |
| `authentik_providers_oauth2.scopemapping` | name, scope_name, expression, managed |
| `authentik_providers_proxy.proxyprovider` | name, authorization_flow, mode (proxy/forward_single/forward_domain), external_host, internal_host |
| `authentik_providers_ldap.ldapprovider` | name, authorization_flow, base_dn, search_group |
| `authentik_providers_radius.radiusprovider` | name, authorization_flow, shared_secret |

Proxy modes: `proxy`, `forward_single`, `forward_domain`

## Sources (Federation)

| Model | Key Fields |
|-------|------------|
| `authentik_sources_oauth.oauthsource` | name, slug, provider_type, consumer_key, consumer_secret, authorization_url, access_token_url, profile_url, authentication_flow, enrollment_flow |
| `authentik_sources_saml.samlsource` | name, slug, sso_url, issuer, signing_kp, name_id_policy, allow_idp_initiated, authentication_flow, enrollment_flow |
| `authentik_sources_plex.plexsource` | name, slug, client_id, allowed_servers |

## Policies

| Model | Key Fields |
|-------|------------|
| `authentik_policies.policybinding` | target, policy/group/user (exactly one), order, enabled, negate, timeout |
| `authentik_policies_expression.expressionpolicy` | name, expression, execution_logging |
| `authentik_policies_event_matcher.eventmatcherpolicy` | name, action, client_ip, app |
| `authentik_policies_password.passwordpolicy` | name, length_min, amount_digits, amount_uppercase, amount_lowercase, amount_symbols |
| `authentik_policies_reputation.reputationpolicy` | name, check_ip, check_username, threshold |

## Crypto & Certificates

| Model | Key Fields |
|-------|------------|
| `authentik_crypto.certificatekeypair` | name, certificate_data, key_data, managed |

Default cert: `!Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]`

## Outposts

| Model | Key Fields |
|-------|------------|
| `authentik_outposts.outpost` | name, type (proxy/ldap/radius/rac), providers, config, service_connection |

Embedded outpost: `!Find [authentik_outposts.outpost, [name, authentik Embedded Outpost]]`

## RBAC

| Model | Key Fields |
|-------|------------|
| `authentik_rbac.role` | name, permissions |

## Meta Models

| Model | Key Fields |
|-------|------------|
| `authentik_blueprints.metaapplyblueprint` | identifiers.name, attrs.required (default true) |

## Common !Find Patterns

```yaml
# Default flows
!Find [authentik_flows.flow, [slug, default-authentication-flow]]
!Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
!Find [authentik_flows.flow, [slug, default-provider-authorization-explicit-consent]]
!Find [authentik_flows.flow, [slug, default-source-enrollment]]
!Find [authentik_flows.flow, [slug, default-password-change]]
!Find [authentik_flows.flow, [slug, default-invalidation-flow]]

# Default cert
!Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]

# Default SAML property mappings (managed names)
!Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/upn]]
!Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/name]]
!Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/email]]
!Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/username]]
!Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/uid]]
!Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/groups]]
!Find [authentik_providers_saml.samlpropertymapping, [managed, goauthentik.io/providers/saml/ms-windowsaccountname]]

# Default OAuth2 scope mappings
!Find [authentik_providers_oauth2.scopemapping, [managed, goauthentik.io/providers/oauth2/scope-openid]]
!Find [authentik_providers_oauth2.scopemapping, [managed, goauthentik.io/providers/oauth2/scope-email]]
!Find [authentik_providers_oauth2.scopemapping, [managed, goauthentik.io/providers/oauth2/scope-profile]]

# Embedded outpost
!Find [authentik_outposts.outpost, [name, authentik Embedded Outpost]]
```
