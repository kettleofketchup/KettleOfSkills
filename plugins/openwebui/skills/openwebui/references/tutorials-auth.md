# Authentication & SSO Tutorials

**Connect Open WebUI to your identity provider for single sign-on, LDAP, and group synchronization.**

These community-contributed guides walk through real-world authentication setups step by step.

| Tutorial | What you'll achieve | Audience |
|----------|-------------------|----------|
| Okta SSO (OIDC) | Single sign-on with Okta, optional group sync and MFA | Admin, 30 min |
| Azure AD LDAP | Secure LDAP authentication against Azure AD Domain Services | Admin, 45 min |
| Dual OAuth Setup | Microsoft and Google OAuth running simultaneously | Admin, 15 min |
| Entra ID Group Name Sync | Human-readable group names instead of GUIDs from Microsoft Entra | Admin, 30 min |
| Tailscale | HTTPS and SSO via Tailscale Serve, plus secure tunnels with Funnel | Admin, 20 min |

---

## Dual OAuth Configuration (Microsoft & Google)

**Note:** This configuration is a community-contributed workaround and is **not officially supported** by the Open WebUI team. Behavior may change in future updates.

### Overview

While Open WebUI officially supports only one **OpenID Connect (OIDC)** provider at a time via the `OPENID_PROVIDER_URL` variable, it is possible to support both **Microsoft** and **Google** simultaneously.

The trick is to configure one provider (e.g., Microsoft) as the primary OIDC provider and the other (e.g., Google) as a standard OAuth provider by utilizing Open WebUI's built-in support for specific providers.

### Prerequisites

- Access to your Open WebUI environment variables (Docker or local).
- Client IDs and Secrets from both Google Cloud Console and Microsoft Azure/Entra ID.
- `OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true` must be enabled to ensure users are mapped to the same account regardless of the provider used.

### Environment Variables

```bash
# Enable signup and account merging (CRITICAL)
ENABLE_OAUTH_SIGNUP=true
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true

# 1. Microsoft as the primary OIDC provider
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_CLIENT_TENANT_ID=your_tenant_id
MICROSOFT_REDIRECT_URI=https://your-webui.com/oauth/microsoft/callback
OPENID_PROVIDER_URL=https://login.microsoftonline.com/your_tenant_id/v2.0/.well-known/openid-configuration

# Optional: Custom scope for Microsoft OAuth
# MICROSOFT_OAUTH_SCOPE=openid email profile offline_access api://<Application ID URI>/<custom_scope>

# Optional: Include scope in refresh token requests
# OAUTH_REFRESH_TOKEN_INCLUDE_SCOPE=true

# 2. Google as a secondary OAuth provider
# Do NOT provide an OPENID_PROVIDER_URL for Google.
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Why This Works

1. **Microsoft** is handled via the generic OIDC flow because `OPENID_PROVIDER_URL` is set to the Microsoft endpoint.
2. **Google** is handled via the dedicated internal Google OAuth module because the system detects `GOOGLE_CLIENT_ID` but sees that the global `OPENID_PROVIDER_URL` is already claimed by Microsoft.
3. **Account Merging**: Since both providers return the user's email, `OAUTH_MERGE_ACCOUNTS_BY_EMAIL=true` ensures the user logs into the same profile regardless of provider.

### Troubleshooting

- **Redirect Mismatch**: Ensure your Redirect URIs in both consoles match your `WEBUI_URL`.
- **Merge Failures**: Double-check that `OAUTH_MERGE_ACCOUNTS_BY_EMAIL` is set to `true`.
- **Microsoft Logout**: Microsoft often requires the `OPENID_PROVIDER_URL` to handle the logout redirect correctly.
- **Azure AD Refresh Token Failures (`AADSTS90009`)**: Set `OAUTH_REFRESH_TOKEN_INCLUDE_SCOPE=true`. You may also need to set `MICROSOFT_OAUTH_SCOPE` to include `offline_access` and any custom API scopes.

---

## Tailscale Integration

**Private, encrypted access to Open WebUI from any device. No ports to open, no certificates to manage.**

Tailscale creates a WireGuard-based mesh VPN (a "tailnet") between your devices. Every device gets a stable hostname like `my-server.tail1234.ts.net`, and Tailscale can provision trusted HTTPS certificates automatically. Your Open WebUI instance stays completely private, accessible only to devices on your tailnet.

Tailscale is ideal when you want **private, authenticated access** across devices without exposing Open WebUI to the public internet.

### Prerequisites

| Requirement | Details |
| :--- | :--- |
| **Open WebUI** | Running locally on port `8080` (default) |
| **Tailscale account** | Free for personal use at tailscale.com |
| **Tailscale installed** | On both the server running Open WebUI and any client devices |

### Quick Start

**1. Install Tailscale**

macOS:
```bash
brew install tailscale
```

Linux:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Windows: Download from tailscale.com/download/windows.

**2. Connect the server**

```bash
sudo tailscale up
```

Find your tailnet hostname with:
```bash
tailscale status
```

**3. Access Open WebUI**

From any device on the same tailnet:
```
http://my-server.tail1234.ts.net:8080
```

This connection is already encrypted end-to-end by WireGuard.

### HTTPS with Tailscale

```bash
# Proxy HTTPS traffic directly to Open WebUI
sudo tailscale serve https / http://localhost:8080
```

Your instance is now available at `https://my-server.tail1234.ts.net` with a valid TLS certificate.
