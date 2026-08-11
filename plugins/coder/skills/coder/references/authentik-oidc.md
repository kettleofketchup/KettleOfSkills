# Coder + Authentik SSO

Pairs with `oidc-auth.md` (Coder side) and the `authentik` skill (IdP side).

## Authentik Side

Create an **OAuth2/OpenID Provider**:

| Field | Value |
|-------|-------|
| Name | `coder` |
| Authorization flow | `default-provider-authorization-implicit-consent` (or explicit) |
| Client type | Confidential |
| Client ID / Secret | generated — copy both |
| Redirect URIs | `https://coder.example.com/api/v2/users/oidc/callback` |
| Signing key | your authentik signing certificate |
| Scopes | `openid`, `profile`, `email`, plus a custom `groups` mapping |

Then create an **Application** (slug `coder`) bound to that provider, and bind a policy/group so only intended
users can access it.

Issuer URL Coder must use: `https://auth.example.com/application/o/coder/` — note the **trailing slash**.
Verify with:

```bash
curl -s https://auth.example.com/application/o/coder/.well-known/openid-configuration | jq .issuer
```

## Groups Scope Mapping

Authentik does not emit group names by default. Create a **Scope Mapping**:

- Name: `coder-groups`
- Scope name: `groups`
- Expression:

```python
return {
    "groups": [group.name for group in request.user.ak_groups.all()],
}
```

Add `coder-groups` to the provider's selected scopes. Then on the Coder side request it:

```
CODER_OIDC_SCOPES=openid,profile,email,offline_access,groups
CODER_OIDC_GROUP_FIELD=groups
```

## Blueprint

Declarative equivalent — see the `authentik` skill's blueprint references for the full model list.

```yaml
version: 1
metadata:
  name: coder-oidc
entries:
  - model: authentik_providers_oauth2.scopemapping
    identifiers: { name: coder-groups }
    id: coder-groups
    attrs:
      scope_name: groups
      description: Coder group membership
      expression: |
        return {"groups": [g.name for g in request.user.ak_groups.all()]}

  - model: authentik_providers_oauth2.oauth2provider
    identifiers: { name: coder }
    id: coder-provider
    attrs:
      client_type: confidential
      client_id: !Env CODER_OIDC_CLIENT_ID
      client_secret: !Env CODER_OIDC_CLIENT_SECRET
      redirect_uris:
        - matching_mode: strict
          url: https://coder.example.com/api/v2/users/oidc/callback
      authorization_flow:
        !Find [authentik_flows.flow, [slug, default-provider-authorization-implicit-consent]]
      invalidation_flow:
        !Find [authentik_flows.flow, [slug, default-provider-invalidation-flow]]
      property_mappings:
        - !Find [authentik_providers_oauth2.scopemapping, [scope_name, openid]]
        - !Find [authentik_providers_oauth2.scopemapping, [scope_name, profile]]
        - !Find [authentik_providers_oauth2.scopemapping, [scope_name, email]]
        - !KeyOf coder-groups

  - model: authentik_core.application
    identifiers: { slug: coder }
    attrs:
      name: Coder
      provider: !KeyOf coder-provider
      meta_launch_url: https://coder.example.com
```

Confirm the `redirect_uris` schema against your authentik version — older releases took a newline-separated
string rather than the structured list shown here.

## Coder Side

```yaml
coder:
  env:
    - name: CODER_OIDC_ISSUER_URL
      value: "https://auth.example.com/application/o/coder/"
    - name: CODER_OIDC_CLIENT_ID
      valueFrom: { secretKeyRef: { name: coder-oidc, key: client-id } }
    - name: CODER_OIDC_CLIENT_SECRET
      valueFrom: { secretKeyRef: { name: coder-oidc, key: client-secret } }
    - name: CODER_OIDC_SCOPES
      value: "openid,profile,email,offline_access,groups"
    - name: CODER_OIDC_SIGN_IN_TEXT
      value: "Sign in with Authentik"
    - name: CODER_OIDC_ICON_URL
      value: "https://auth.example.com/static/dist/assets/icons/icon.png"
    - name: CODER_OIDC_GROUP_FIELD
      value: "groups"
    - name: CODER_OIDC_GROUP_AUTO_CREATE
      value: "true"
    - name: CODER_OIDC_ALLOWED_GROUPS
      value: "coder-users"
    - name: CODER_OIDC_EMAIL_DOMAIN
      value: "example.com"
```

```bash
kubectl create secret generic coder-oidc -n coder \
  --from-literal=client-id='...' --from-literal=client-secret='...'
```

## Mapping Authentik Groups to Coder Roles

Role sync is a Premium feature. With it:

```
CODER_OIDC_USER_ROLE_FIELD=groups
CODER_OIDC_USER_ROLE_MAPPING='{"coder-admins":["owner"],"platform-team":["template-admin"]}'
```

Without Premium, grant site roles manually (`coder users edit-roles`) and use group sync only to control
template visibility.

## Gotchas

- **Trailing slash** on the issuer URL — omitting it causes discovery failure.
- Authentik's implicit-consent flow skips the consent screen; explicit consent adds a click per login.
- Group changes apply at next login only. Force re-auth after changing membership.
- If authentik runs behind the same Traefik instance, ensure Coder resolves it over a route that presents the
  public certificate — a ClusterIP shortcut with a mismatched SAN breaks discovery.
