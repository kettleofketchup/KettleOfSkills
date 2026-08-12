# API Reference — Admin and Models

Admin API endpoints for usage, cost, users, models, and skills.

## Admin API

### Usage Reports

```bash
GET /v1/admin/claude-code/usage
```

Query params: `start_date`, `end_date`, `user_id`, `workspace_id`

```bash
curl https://api.anthropic.com/v1/admin/claude-code/usage \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d start_date=2025-11-01 -d end_date=2025-11-06
```

### Cost Reports

```bash
GET /v1/admin/usage/cost
```

Query params: `start_date`, `end_date`, `group_by` (`user` | `project` | `model`)

### User Management

```bash
GET    /v1/admin/users
GET    /v1/admin/users/{user_id}
PATCH  /v1/admin/users/{user_id}
DELETE /v1/admin/users/{user_id}
```

## Models API

### List Models

```bash
GET /v1/models
```

Response:
```json
{
  "data": [
    { "id": "claude-sonnet-4-5-20250929", "type": "model",
      "display_name": "Claude Sonnet 4.5" }
  ]
}
```

### Get Model

```bash
GET /v1/models/{model_id}
```

## Skills API

### Create Skill

```bash
POST /v1/skills
```

```json
{
  "name": "my-skill",
  "description": "Skill description",
  "instructions": "Detailed instructions...",
  "version": "1.0.0"
}
```

### List / Update / Delete Skills

```bash
GET    /v1/skills
PATCH  /v1/skills/{skill_id}
DELETE /v1/skills/{skill_id}
```

## Authentication

Include API key in all requests:
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

For workspace keys, use `$WORKSPACE_API_KEY` instead.

## Rate Limits

Response headers:
```
anthropic-ratelimit-requests-limit: 1000
anthropic-ratelimit-requests-remaining: 999
anthropic-ratelimit-tokens-limit: 100000
anthropic-ratelimit-tokens-remaining: 99500
```

Best practices: monitor headers, exponential backoff, batch requests, use caching.

## See Also

- Messages/Files/SDK: `references/api-messages-files.md`
- API docs: https://docs.anthropic.com/api
