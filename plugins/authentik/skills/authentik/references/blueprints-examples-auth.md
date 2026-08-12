# Blueprint Examples: Auth Flow, SAML, OIDC

## Authentication Flow (from default blueprints)

```yaml
version: 1
metadata:
  name: Default - Authentication flow
entries:
  - model: authentik_flows.flow
    identifiers:
      slug: default-authentication-flow
    id: flow
    attrs:
      designation: authentication
      name: Welcome to authentik!
      title: Welcome to authentik!

  - model: authentik_stages_identification.identificationstage
    identifiers:
      name: default-authentication-identification
    id: identification

  - model: authentik_stages_password.passwordstage
    identifiers:
      name: default-authentication-password
    id: password
    attrs:
      configure_flow: !Find [authentik_flows.flow, [slug, default-password-change]]

  - model: authentik_stages_authenticator_validate.authenticatorvalidatestage
    identifiers:
      name: default-authentication-mfa-validation
    id: mfa

  - model: authentik_stages_user_login.userloginstage
    identifiers:
      name: default-authentication-login
    id: login
    attrs:
      session_duration: seconds=0

  # Bind stages to flow in order
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
      order: 30
      stage: !KeyOf mfa
      target: !KeyOf flow
  - model: authentik_flows.flowstagebinding
    identifiers:
      order: 100
      stage: !KeyOf login
      target: !KeyOf flow
```

## SAML Provider + Application + Group Policy

```yaml
version: 1
metadata:
  name: saml-myapp
  labels:
    blueprints.goauthentik.io/description: "SAML SSO for My App"
entries:
  - model: authentik_providers_saml.samlprovider
    identifiers:
      name: myapp-saml
    id: saml-provider
    attrs:
      authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
      acs_url: !Format ["https://myapp.%s/saml/acs", !Env [DOMAIN]]
      issuer: !Format ["https://auth.%s", !Env [DOMAIN]]
      sp_binding: post
      signing_kp: !Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]
      digest_algorithm: http://www.w3.org/2001/04/xmlenc#sha256
      signature_algorithm: http://www.w3.org/2001/04/xmldsig-more#rsa-sha256
  - model: authentik_core.application
    identifiers:
      slug: myapp
    attrs:
      name: My App
      provider: !KeyOf saml-provider
      policy_engine_mode: any
  - model: authentik_core.group
    identifiers:
      name: myapp-users
    id: group-users
  - model: authentik_policies.policybinding
    identifiers:
      order: 0
      target: !KeyOf saml-provider
    attrs:
      group: !KeyOf group-users
```

## OAuth2/OIDC Provider (ArgoCD via Dex)

```yaml
version: 1
metadata:
  name: oidc-argocd
  labels:
    blueprints.goauthentik.io/description: "OIDC for ArgoCD"
entries:
  - model: authentik_providers_oauth2.oauth2provider
    identifiers:
      name: argocd-oidc
    id: oidc-provider
    attrs:
      authorization_flow: !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
      client_type: confidential
      client_id: argocd
      client_secret: !Env [ARGOCD_OIDC_SECRET]
      redirect_uris: |
        https://argocd.example.com/api/dex/callback
        https://localhost:8085/auth/callback
      signing_key: !Find [authentik_crypto.certificatekeypair, [name, authentik Self-signed Certificate]]
      property_mappings:
        - !Find [authentik_providers_oauth2.scopemapping, [managed, goauthentik.io/providers/oauth2/scope-openid]]
        - !Find [authentik_providers_oauth2.scopemapping, [managed, goauthentik.io/providers/oauth2/scope-email]]
        - !Find [authentik_providers_oauth2.scopemapping, [managed, goauthentik.io/providers/oauth2/scope-profile]]

  - model: authentik_core.application
    identifiers:
      slug: argocd
    attrs:
      name: ArgoCD
      provider: !KeyOf oidc-provider
  - model: authentik_core.group
    identifiers:
      name: ArgoCD Admins
    state: created
  - model: authentik_core.group
    identifiers:
      name: ArgoCD Viewers
    state: created
```
