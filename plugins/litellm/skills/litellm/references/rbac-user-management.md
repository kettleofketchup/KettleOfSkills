# RBAC & User Management

## Hierarchy

Organizations > Teams > Users > Keys

## Global Roles

| Role | Permissions |
|------|------------|
| `proxy_admin` | Full platform control |
| `proxy_admin_viewer` | Read-only platform-wide |
| `internal_user` | Create/delete own keys, view own spend |
| `internal_user_view_only` | Read-only personal (deprecated) |

## Organization/Team Roles (Premium)

| Role | Permissions |
|------|------------|
| `org_admin` | Manage org teams, add users, view org spend |
| `team_admin` | Manage single team, create keys for members |

## Team Management

```bash
# Create team with budget
curl -X POST 'http://proxy:4000/team/new' \
  -H 'Authorization: Bearer sk-master-key' \
  -d '{
    "team_alias": "my-team",
    "max_budget": 100,
    "budget_duration": "30d",
    "models": ["gpt-4", "claude-3-opus"],
    "members_with_roles": [
      {"role": "admin", "user_id": "user-1"},
      {"role": "user", "user_id": "user-2"}
    ]
  }'
```

Budget durations: `1s`, `1m`, `1h`, `1d`, `30d`

## User Management

```bash
# Create user
curl -X POST 'http://proxy:4000/user/new' \
  -H 'Authorization: Bearer sk-master-key' \
  -d '{
    "user_id": "user-123",
    "user_role": "internal_user",
    "max_budget": 50,
    "user_email": "user@company.com"
  }'
```

## Spend Tracking Endpoints

| Endpoint | Scope |
|----------|-------|
| `/key/info` | Per-key spend |
| `/user/info` | Per-user spend |
| `/team/info` | Per-team spend |
| `/organization/info` | Per-org spend |

## Budget Alerts

Budget alerts configured via callbacks. Prometheus metric `litellm_remaining_team_budget_metric` for monitoring.
