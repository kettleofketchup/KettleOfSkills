# Authentik OIDC — Role Mapping & Admin Config

## Role Mapping Expression

The `role_attribute_path` in `auth.generic_oauth` uses JMESPath:

```
contains(groups[*], 'Grafana Admins') && 'Admin' || contains(groups[*], 'Grafana Editors') && 'Editor' || 'Viewer'
```

Evaluation order: Admin first, then Editor, fallback Viewer.

To grant Grafana Server Admin to the Admins group:
```
contains(groups[*], 'Grafana Admins') && 'GrafanaAdmin' || contains(groups[*], 'Grafana Editors') && 'Editor' || 'Viewer'
```

Requires `allow_assign_grafana_admin: true` in `auth.generic_oauth`.

## Group Setup in Authentik

Create groups for role mapping:
- `Grafana Admins` — maps to Grafana Admin role
- `Grafana Editors` — maps to Grafana Editor role
- All other users fall back to Viewer

Assign users to groups in Authentik under **Directory > Groups**.

## Disable Default Admin

Once OIDC works, optionally disable built-in login:

```yaml
grafana:
  grafana.ini:
    auth:
      disable_login_form: true
    auth.generic_oauth:
      oauth_auto_login: true
```

## Troubleshooting Role Mapping

- **User always gets Viewer**: Check that Authentik sends `groups` claim — verify in provider's property mappings include the groups scope mapping.
- **JMESPath not evaluating**: Grafana requires `role_attribute_strict: false` to fall back to Viewer if expression fails.
- **Admin not persisting**: Set `allow_assign_grafana_admin: true` and use `GrafanaAdmin` (not `Admin`) in the path for server admin.

```yaml
auth.generic_oauth:
  role_attribute_path: "contains(groups[*], 'Grafana Admins') && 'GrafanaAdmin' || ..."
  role_attribute_strict: false
  allow_assign_grafana_admin: true
```
