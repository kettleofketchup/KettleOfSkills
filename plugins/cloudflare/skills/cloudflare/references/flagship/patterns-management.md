# Flagship Flag Management Patterns

Split out of `patterns.md`; see it for the preceding sections.

## Managing Flags via REST API

All examples use `api.cloudflare.com`. Set `CLOUDFLARE_ACCOUNT_ID`, `FLAGSHIP_APP_ID`, and `CLOUDFLARE_API_TOKEN` first.

### Create a Boolean Flag

```bash
curl -s -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "new-feature",
    "default_variation": "off",
    "variations": { "on": true, "off": false },
    "rules": [],
    "description": "Enable the new feature",
    "enabled": false
  }' \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags" | jq .
```

### Create a Flag with Internal-Only Targeting

```bash
curl -s -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "beta-feature",
    "default_variation": "off",
    "variations": { "on": true, "off": false },
    "rules": [
      {
        "priority": 1,
        "conditions": [
          { "attribute": "email", "operator": "ends_with", "value": "@cloudflare.com" }
        ],
        "serve_variation": "on"
      }
    ],
    "description": "Beta feature for internal users",
    "enabled": true
  }' \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags" | jq .
```

### Create a JSON Config Flag

```bash
curl -s -X POST \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "rate-limits",
    "default_variation": "standard",
    "variations": {
      "standard": { "rpm": 100, "burst": 20 },
      "premium": { "rpm": 1000, "burst": 200 }
    },
    "rules": [
      {
        "priority": 1,
        "conditions": [
          { "attribute": "plan", "operator": "in", "value": ["enterprise", "business"] }
        ],
        "serve_variation": "premium"
      }
    ],
    "description": "Rate limit configuration by plan",
    "enabled": true
  }' \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags" | jq .
```

### Read a Flag

```bash
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags/new-feature" | jq .
```

### List All Flags (with pagination)

```bash
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags?limit=50" | jq .
```

If `result_info.cursor` is non-null, fetch the next page:

```bash
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags?limit=50&cursor=<cursor>" | jq .
```

### Update a Flag (Full Replace)

Updates use PUT with the full `FlagDefinition`. Always GET first, modify, then PUT back.

```bash
# 1. Read current flag
FLAG=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags/new-feature" | jq '.result')

# 2. Modify (e.g., enable the flag)
UPDATED=$(echo "$FLAG" | jq '.enabled = true')

# 3. PUT back
echo "$UPDATED" | curl -s -X PUT \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags/new-feature" | jq .
```

### Toggle a Flag On

Read-modify-write to set `enabled: true`:

```bash
BASE="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags"

FLAG=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$BASE/new-feature" | jq '.result')
UPDATED=$(echo "$FLAG" | jq '.enabled = true')
echo "$UPDATED" | curl -s -X PUT \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- "$BASE/new-feature" | jq .
```

### Toggle a Flag Off (Disable)

Same pattern, set `enabled: false`. The flag immediately returns its default variation for all evaluations.

```bash
BASE="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags"

FLAG=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$BASE/new-feature" | jq '.result')
UPDATED=$(echo "$FLAG" | jq '.enabled = false')
echo "$UPDATED" | curl -s -X PUT \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- "$BASE/new-feature" | jq .
```

### Add a Targeting Rule to an Existing Flag

Append a rule to the existing rules array. Pick a priority that doesn't collide with existing rules.

```bash
BASE="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags"

FLAG=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$BASE/new-feature" | jq '.result')
UPDATED=$(echo "$FLAG" | jq '.rules += [{
  "priority": 2,
  "conditions": [{ "attribute": "plan", "operator": "equals", "value": "enterprise" }],
  "serve_variation": "on"
}]')
echo "$UPDATED" | curl -s -X PUT \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- "$BASE/new-feature" | jq .
```

### Change Rollout Percentage

Update the rollout percentage on an existing rule (e.g., rule at index 0):

```bash
BASE="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags"

FLAG=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$BASE/gradual-rollout" | jq '.result')
UPDATED=$(echo "$FLAG" | jq '.rules[0].rollout.percentage = 50')
echo "$UPDATED" | curl -s -X PUT \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- "$BASE/gradual-rollout" | jq .
```

### Change Default Variation

```bash
BASE="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags"

FLAG=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$BASE/new-feature" | jq '.result')
UPDATED=$(echo "$FLAG" | jq '.default_variation = "on"')
echo "$UPDATED" | curl -s -X PUT \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- "$BASE/new-feature" | jq .
```

### Add a New Variation

```bash
BASE="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags"

FLAG=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$BASE/checkout-flow" | jq '.result')
UPDATED=$(echo "$FLAG" | jq '.variations["treatment-c"] = "minimal"')
echo "$UPDATED" | curl -s -X PUT \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- "$BASE/checkout-flow" | jq .
```

### Remove a Rule

Remove a rule by filtering on priority:

```bash
BASE="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags"

FLAG=$(curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "$BASE/new-feature" | jq '.result')
UPDATED=$(echo "$FLAG" | jq '.rules = [.rules[] | select(.priority != 2)]')
echo "$UPDATED" | curl -s -X PUT \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- "$BASE/new-feature" | jq .
```

### Delete a Flag

```bash
curl -s -X DELETE \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/flagship/apps/$FLAGSHIP_APP_ID/flags/old-feature" | jq .
```

---

Continued in `patterns-targeting.md`.
