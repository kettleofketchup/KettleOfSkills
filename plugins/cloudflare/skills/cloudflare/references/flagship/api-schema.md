# Flagship Schema, Rate Limits & Error Codes

Split out of `api.md`; see it for the preceding sections.

## FlagDefinition Schema

```json
{
  "key": "my-flag",
  "type": "boolean",
  "default_variation": "off",
  "variations": {
    "on": true,
    "off": false
  },
  "rules": [
    {
      "priority": 1,
      "conditions": [
        {
          "attribute": "email",
          "operator": "ends_with",
          "value": "@cloudflare.com"
        }
      ],
      "serve_variation": "on",
      "rollout": { "percentage": 100 }
    }
  ],
  "description": "Enables the new feature",
  "enabled": true
}
```

### Field Constraints

| Field | Type | Constraints |
|-------|------|-------------|
| `key` | string | 1-64 chars, `/^[a-zA-Z0-9_-]+$/` |
| `type` | enum | Optional. `boolean`, `string`, `number`, `json` (auto-inferred from variations) |
| `default_variation` | string | Must be a key in `variations` |
| `variations` | `Record<string, T>` | At least one. All values same type. Keys: alphanumeric/hyphens/underscores, max 64 chars. Values max 10KB. |
| `rules` | `Rule[]` | Can be empty. No duplicate priorities. |
| `description` | string? | Max 512 chars, nullable |
| `enabled` | boolean | Required. `false` = always returns default variation. |

### Rule Schema

```json
{
  "priority": 1,
  "conditions": [ /* Condition[] */ ],
  "serve_variation": "on",
  "rollout": { "percentage": 50, "attribute": "targetingKey" }
}
```

- `priority`: integer >= 1, unique across rules in the flag (lower = evaluated first)
- `conditions`: array of base or logical conditions
- `serve_variation`: must be a key in `variations`
- `rollout`: optional. `percentage` 0-100. `attribute` defaults to `targetingKey`.

### Condition Schema

**Base condition:**

```json
{ "attribute": "email", "operator": "ends_with", "value": "@cloudflare.com" }
```

**Logical condition (AND/OR):**

```json
{
  "logical_operator": "AND",
  "clauses": [
    { "attribute": "country", "operator": "equals", "value": "US" },
    { "attribute": "plan", "operator": "in", "value": ["enterprise", "business"] }
  ]
}
```

Nesting supported up to 6 levels deep.

### Operators

| Operator | Description | Value Type |
|----------|-------------|------------|
| `equals` | Exact match (case-sensitive) | String |
| `not_equals` | Not exact match | String |
| `greater_than` | Numeric / datetime > | Number, ISO 8601 |
| `less_than` | Numeric / datetime < | Number, ISO 8601 |
| `greater_than_or_equals` | >= | Number, ISO 8601 |
| `less_than_or_equals` | <= | Number, ISO 8601 |
| `contains` | Substring match (case-sensitive) | String |
| `starts_with` | Prefix match | String |
| `ends_with` | Suffix match | String |
| `in` | Value in array | Array |
| `not_in` | Value not in array | Array |

---

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Mutations (POST/PUT/DELETE) | 60 per 60s per account:app |
| Reads (GET) | 600 per 60s per account:app |

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| 200 | Success (read/update/delete) |
| 201 | Created (create) |
| 400 | Validation error (check `errors[].message`) |
| 401 | Invalid or missing token |
| 404 | Flag or app not found |
| 409 | Flag key already exists (create) |
| 429 | Rate limited |
