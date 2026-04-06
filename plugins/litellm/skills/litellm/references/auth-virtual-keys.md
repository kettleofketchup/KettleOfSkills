# Virtual Keys & Spend Tracking

Requires: PostgreSQL database + master key (`sk-` prefix).

## Key Management Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/key/generate` | POST | Create new API key |
| `/key/info` | GET | Key details + spend |
| `/key/update` | POST | Modify key settings |
| `/key/delete` | POST | Delete key |
| `/key/block` | POST | Disable key |
| `/key/unblock` | POST | Re-enable key |
| `/key/sk-xxx/regenerate` | POST | Rotate key (Enterprise) |

## Key Generation

```bash
curl -X POST 'http://proxy:4000/key/generate' \
  -H 'Authorization: Bearer sk-master-key' \
  -H 'Content-Type: application/json' \
  -d '{
    "models": ["gpt-4", "claude-3-opus"],
    "user_id": "user-123",
    "team_id": "team-456",
    "max_budget": 100,
    "duration": "30d",
    "tpm_limit": 1000,
    "rpm_limit": 100,
    "max_parallel_requests": 50,
    "aliases": {"gpt-3.5-turbo": "my-free-tier"},
    "metadata": {"user": "name@example.com"},
    "tags": ["prod"]
  }'
```

Duration formats: `30s`, `30m`, `30h`, `30d`

## Budget & Rate Limit Controls

```yaml
litellm_settings:
  # Upper bounds for any key created via API
  upperbound_key_generate_params:
    max_budget: 100
    duration: "30d"
    tpm_limit: 1000

  # Defaults when not specified in /key/generate
  default_key_generate_params:
    max_budget: 1.5
    models: ["azure-gpt-3.5"]

  # Who can create keys
  key_generation_settings:
    team_key_generation:
      allowed_team_member_roles: ["admin"]
    personal_key_generation:
      allowed_user_roles: ["proxy_admin"]
```

## Spend Tracking

Automatic USD cost tracking via `completion_cost()`. Tracked per key, user, and team.

Query endpoints:
- `/key/info` - key-level spend
- `/user/info` - user-level spend
- `/team/info` - team-level spend

Prometheus metric: `litellm_remaining_team_budget_metric`

## Custom Auth Header

Override default `Authorization: Bearer` header:

```yaml
general_settings:
  litellm_key_header_name: "X-Litellm-Key"
```

## Auto-Rotation (Enterprise)

```json
{
  "auto_rotate": true,
  "rotation_interval": "30d"
}
```
