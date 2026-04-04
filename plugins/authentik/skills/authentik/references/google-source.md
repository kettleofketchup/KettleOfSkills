# Google Workspace SAML Federation Source

## Overview

Configure "Login with Google" on the Authentik login page using SAML federation.
Google Workspace acts as IdP, Authentik acts as SP.

## Google Admin Console Setup

1. Sign in as super-admin at `admin.google.com`
2. Navigate to **Apps → Web and mobile apps**
3. Click **Add app → Add custom SAML app**
4. Name: `authentik`, Description: `Single Sign-On for authentik`
5. **Download the signing certificate** (save for later)
6. Copy the **SSO URL** provided by Google

### Service Provider Details

| Field | Value |
|-------|-------|
| ACS URL | `https://auth.example.com/source/saml/<slug>/acs/` |
| Entity ID | `https://auth.example.com/source/saml/<slug>/metadata/` |
| Start URL | `https://auth.example.com` |
| Name ID format | EMAIL |
| Name ID | Basic Information > Primary Email |

### Attribute Mapping

| Google Directory Attribute | App Attribute |
|---------------------------|---------------|
| Primary Email | `email` |
| First Name | `first_name` (optional) |
| Last Name | `last_name` (optional) |

### Enable

Turn on the application under **User access** for your organization.

## Authentik Configuration

### 1. Import Google Certificate

Admin UI → System → Certificates → Import:
- Upload the certificate downloaded from Google
- No private key needed (verification only)

### 2. Create SAML Source

Admin UI → Directory → Federation and Social login → Create → SAML Source:

| Setting | Value |
|---------|-------|
| Name | `Google Workspace` |
| Slug | `google` (must match ACS URL slug) |
| SSO URL | Google's SSO URL from step 6 above |
| Issuer | `https://auth.example.com/source/saml/google/metadata/` |
| Verification Certificate | The imported Google certificate |
| **Verify Assertion Signature** | **DISABLED** (CRITICAL - must be off) |
| **Verify Response Signature** | **ENABLED** |
| Allow IdP-initiated Login | ENABLED |
| NameID Policy | Email address |

**CRITICAL:** Assertion signature verification MUST be disabled or the integration will not work with Google Workspace.

### 3. Bind to Authentication Flow

The SAML source automatically appears on the login page when bound to the default authentication flow's identification stage.

Admin UI → Flows → `default-authentication-flow` → Stage Bindings → Identification Stage → Edit:
- Under "Sources", add the Google Workspace SAML source

## Blueprint Example

```yaml
version: 1
metadata:
  name: google-workspace-source
  labels:
    blueprints.goauthentik.io/description: "Google Workspace SAML login"

entries:
  # Import certificate (must be done manually or via API)
  # Blueprints cannot import certificate files directly

  - model: authentik_sources_saml.samlsource
    state: present
    identifiers:
      slug: google
    attrs:
      name: Google Workspace
      sso_url: !Env [GOOGLE_SSO_URL]
      issuer: !Format ["https://%s/source/saml/google/metadata/", !Env [AUTHENTIK_HOST]]
      signing_kp: !Find [authentik_crypto.certificatekeypair, [name, Google Workspace]]
      digest_algorithm: http://www.w3.org/2001/04/xmlenc#sha256
      signature_algorithm: http://www.w3.org/2001/04/xmldsig-more#rsa-sha256
      name_id_policy: urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress
      allow_idp_initiated: true
      authentication_flow: !Find [authentik_flows.flow, [slug, default-authentication-flow]]
      enrollment_flow: !Find [authentik_flows.flow, [slug, default-source-enrollment]]

  # Bind source to identification stage
  - model: authentik_stages_identification.identificationstage
    state: present
    identifiers:
      name: default-authentication-identification
    attrs:
      sources:
        - !Find [authentik_sources_saml.samlsource, [slug, google]]
```

## Troubleshooting

| Error | Fix |
|-------|-----|
| `403 app_not_configured_for_user` | Entity IDs must match exactly between Google and Authentik |
| SAML response invalid | Disable assertion signature verification, enable response signature only |
| User not created on first login | Ensure enrollment flow is configured on the SAML source |
| Google login button not showing | Add source to identification stage's sources list |
