# Authentik SAML SSO for Nextcloud

Authentik open-source (self-hosted) includes full SAML support with unlimited users at no cost.

**WARNING**: NEVER use SAML with Nextcloud server-side encryption. SAML does not provide cleartext passwords, causing irrevocable data loss with encryption enabled.

## Authentik Provider Setup

In Authentik admin (Applications > Providers > Create):

| Setting | Value |
|---------|-------|
| Type | SAML Provider |
| Name | `nextcloud` |
| ACS URL | `https://cloud.example.com/apps/user_saml/saml/acs` |
| Issuer | `https://authentik.example.com` |
| Audience | `https://cloud.example.com/apps/user_saml/saml/metadata` |
| SP Binding | Post |
| Signing Certificate | Select available certificate |

Then create an Application pointing to this provider. Note the **application slug**.

Download the signing certificate from provider details page.

## Nextcloud SAML Configuration

### Install the App

```bash
# Via occ in the pod
NEXTCLOUD_POD=$(kubectl get pod -n nextcloud -l app.kubernetes.io/name=nextcloud -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n nextcloud $NEXTCLOUD_POD -- su -s /bin/sh www-data -c "php occ app:install user_saml"
kubectl exec -n nextcloud $NEXTCLOUD_POD -- su -s /bin/sh www-data -c "php occ app:enable user_saml"
```

Or via Helm lifecycle hooks:

```yaml
nextcloud:
  hooks:
    post-installation: |-
      php occ app:install user_saml
      php occ app:enable user_saml
```

### Configure SAML Settings

In Nextcloud admin (Administration > SSO & SAML authentication):

| Setting | Value |
|---------|-------|
| UID attribute | `http://schemas.goauthentik.io/2021/02/saml/uid` |
| IdP Entity ID | `https://authentik.example.com` |
| SSO URL | `https://authentik.example.com/application/saml/<slug>/sso/binding/redirect/` |
| SLO URL | `https://authentik.example.com/application/saml/<slug>/slo/binding/redirect/` |
| X.509 Certificate | Paste downloaded signing certificate |
| Display name attr | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name` |
| Email attr | `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` |
| Groups attr | `http://schemas.xmlsoap.org/claims/Group` |

Replace `<slug>` with the Authentik application slug.

## Optional: Group Mapping and Quotas

Create custom SAML Property Mappings in Authentik:

**Admin group mapping** (expression):
```python
# Maps Authentik admin group to Nextcloud admin
groups = [group.name for group in request.user.ak_groups.all()]
if ak_is_group_member(request.user, name="Nextcloud Admins"):
    groups.append("admin")
return {
    "http://schemas.xmlsoap.org/claims/Group": groups,
}
```

**Quota mapping** (expression):
```python
# Set quota based on group membership
if ak_is_group_member(request.user, name="Premium"):
    return {"nextcloud_quota": "50 GB"}
return {"nextcloud_quota": "10 GB"}
```

In Nextcloud, set "Attribute to map the quota to" = `nextcloud_quota`.

## Gotchas

- Nextcloud must be served over HTTPS (or `overwriteprotocol => 'https'`)
- Some setups need `/index.php/` in ACS URL: `https://cloud.example.com/index.php/apps/user_saml/saml/acs`
- For migrating existing users to SAML: map to stable username attribute, not uid
- Use `env_mode` in SAML settings if deploying via environment variables
- To keep local admin login: enable "Allow the use of multiple user back-ends" in SAML settings
