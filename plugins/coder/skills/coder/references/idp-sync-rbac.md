# Coder IdP Sync, Roles & Groups

Sync evaluates **on every login**. Nothing changes until the user re-authenticates.

## Group Sync

Env-var form (deployment-wide, OSS-compatible):

```
CODER_OIDC_GROUP_FIELD=groups
CODER_OIDC_GROUP_MAPPING='{"idp-group-name":"coder-group-name"}'
CODER_OIDC_GROUP_AUTO_CREATE=true
CODER_OIDC_GROUP_REGEX_FILTER=^coder-.*$
CODER_OIDC_ALLOWED_GROUPS=coder-users,contractors
```

Runtime/CLI form (per-organization, survives restarts, no redeploy):

```bash
coder organizations settings show group-sync --org default > group-sync.json
# edit
coder organizations settings set group-sync --org default < group-sync.json
```

```json
{
  "field": "groups",
  "mapping": {
    "idp-group-name": ["coder-group-uuid-1", "coder-group-uuid-2"]
  },
  "regex_filter": "^coder-.*$",
  "auto_create_missing_groups": true
}
```

The mapping targets **group UUIDs, not names**. Get them with `coder groups list -O <org>` or the API.
`regex_filter` is applied *after* mapping.

## Role Sync (Premium)

```
CODER_OIDC_USER_ROLE_FIELD=roles
CODER_OIDC_USER_ROLE_MAPPING='{"TemplateAuthor":["template-admin","user-admin"]}'
CODER_OIDC_SCOPES=openid,profile,email,offline_access,roles
```

```bash
coder organizations settings show role-sync --org default > role-sync.json
coder organizations settings set role-sync --org default < role-sync.json
coder organization roles show --org default     # list assignable role names
```

```json
{
  "field": "roles",
  "mapping": {
    "coder-admins": ["organization-admin"],
    "infra-admins": ["provisioner-admin"]
  }
}
```

Use the role **name**, not the display name. One IdP claim value may map to several Coder roles.

Role sync overwrites manually assigned roles at login. Once enabled, the IdP is the single source of truth —
don't mix it with `coder users edit-roles`.

## Organization Sync (Premium)

CLI/dashboard only — no env vars.

```bash
coder organization settings show org-sync > org-sync.json
coder organization settings set org-sync < org-sync.json
```

```json
{
  "field": "organizations",
  "mapping": {
    "product": ["868e9b76-dc6e-46ab-be74-a891e9bd784b"],
    "sales":   ["d79144d9-b30a-455a-9af8-7dac83b2f4ec"]
  },
  "organization_assign_default": true
}
```

Set `organization_assign_default: false` only once every user is guaranteed a mapping — otherwise unmapped
users land in no organization and cannot create workspaces.

## Built-in Site Roles

| Role | Capability |
|------|-----------|
| **Owner** | Everything: users, roles, all templates, all workspaces, provisioners, audit log |
| **User Admin** | Create/remove users, manage groups; no template or workspace control |
| **Template Admin** | Manage/view all templates, view all workspaces, run external provisioners; cannot change roles |
| **Auditor** | Read audit logs and template definitions only |
| **Member** | Implicit for every user — own workspaces only |

## Organization Roles (Premium)

Org-scoped equivalents (`organization-admin`, `organization-user-admin`, `organization-template-admin`,
`organization-auditor`) confine the same powers to one organization. Custom org roles are available from
v2.16.0+ via `coder organization roles`.

## Groups

Groups gate **template access**. Give a template's ACL to `devops` and only its members can create workspaces
from it.

```bash
coder groups create devops -O default
coder groups edit devops --add-users alice,bob
coder templates edit k8s-dev --group-acl devops:use
```

Every user is implicitly in the **Everyone** group scoped to their organization; a template granted to
Everyone is available org-wide. Groups also drive quota allocation — a user's budget is the **sum** of the
allowances of every group they belong to (→ `scheduling-quotas.md`).

## Auditing the Result

```bash
coder users list                       # roles column
coder groups list -O default
coder users show <username>            # effective groups + roles
```

When sync appears not to apply, confirm the claim actually arrived before touching the mapping:

```bash
kubectl logs -n coder deploy/coder | grep -i "oidc claims"
```
