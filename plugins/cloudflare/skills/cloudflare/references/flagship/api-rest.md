# Flagship REST API

Split out of `api.md`; see it for the preceding sections.

## REST API (Flag Management)

Source of truth: [Cloudflare Flagship API reference](https://developers.cloudflare.com/api/resources/flagship/). Use it to verify REST paths, envelopes, response fields, and permission wording before relying on examples here.

### FIRST: Check Prerequisites

Before making any REST API calls (create, read, update, delete, toggle flags), verify these environment variables are set:

| Variable | Purpose | How to get |
|----------|---------|------------|
| `CLOUDFLARE_ACCOUNT_ID` | Account identifier | Dashboard URL or `wrangler whoami` |
| `CLOUDFLARE_API_TOKEN` | Bearer token for API auth | [Create API token](https://dash.cloudflare.com/profile/api-tokens) with Flagship permissions |
| `FLAGSHIP_APP_ID` | Target app UUID | Dashboard under **Compute > Flagship**, or `GET /apps` endpoint |

Check with:

```bash
echo "CLOUDFLARE_ACCOUNT_ID=${CLOUDFLARE_ACCOUNT_ID:-(not set)}"
echo "CLOUDFLARE_API_TOKEN=${CLOUDFLARE_API_TOKEN:-(not set)}"
echo "FLAGSHIP_APP_ID=${FLAGSHIP_APP_ID:-(not set)}"
```

**If any are missing, ask the user to provide them before proceeding.**

### Base URL and Auth

Base URL: `https://api.cloudflare.com/client/v4/accounts/{account_id}/flagship`

Authentication: `Authorization: Bearer <API_TOKEN>`

Management endpoints use the Cloudflare v4 envelope. On success, the payload is under `result`; errors are an array under `errors`.

```jsonc
// Success
{ "success": true, "result": <T>, "errors": [], "messages": [] }

// Paginated success
{
  "success": true,
  "result": [<T>],
  "result_info": { "count": 50, "cursor": "next-cursor-or-null" },
  "errors": [],
  "messages": []
}

// Error
{ "success": false, "result": null, "errors": [{ "message": "message" }], "messages": [] }
```

### App Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/apps` | List all apps |
| `GET` | `/apps/{app_id}` | Get app |
| `POST` | `/apps` | Create app (`{ "name": "my-app" }`) |
| `PUT` | `/apps/{app_id}` | Update app (`{ "name": "new-name" }`) |
| `DELETE` | `/apps/{app_id}` | Delete app |

App name constraints: alphanumeric + hyphens + underscores, 1-64 chars.

### Flag Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/apps/{app_id}/flags?limit=50&cursor=<cursor>` | List flags (paginated) |
| `GET` | `/apps/{app_id}/flags/{flag_key}` | Get flag |
| `POST` | `/apps/{app_id}/flags` | Create flag |
| `PUT` | `/apps/{app_id}/flags/{flag_key}` | Update flag (full replace) |
| `DELETE` | `/apps/{app_id}/flags/{flag_key}` | Delete flag |
| `GET` | `/apps/{app_id}/flags/{flag_key}/changelog?limit=20&cursor=<cursor>` | Flag changelog |

### Evaluate Endpoint

```
GET /apps/{app_id}/evaluate?flagKey=<key>&<context-attrs>
```

Requires an API token with the `com.cloudflare.account.flagship.evaluate` permission. Context attributes passed as query params. This endpoint is not wrapped in the management envelope; the SDK contract returns OpenFeature-style camelCase:

```json
{
  "flagKey": "my-flag",
  "value": true,
  "variant": "on",
  "reason": "SPLIT"
}
```

Reasons: `TARGETING_MATCH`, `SPLIT`, `DEFAULT`, `DISABLED`.

### Management Response Payloads

Management endpoints are wrapped in the Cloudflare v4 envelope shown above. Common `.result` payloads:

**App result**

```json
{
  "id": "app-uuid",
  "name": "my-app",
  "created_at": "2026-06-09T12:00:00.000Z",
  "updated_at": "2026-06-09T12:00:00.000Z",
  "updated_by": "user@example.com"
}
```

**Flag result**

```json
{
  "key": "my-flag",
  "type": "boolean",
  "default_variation": "off",
  "variations": { "on": true, "off": false },
  "rules": [],
  "description": "Enables the new feature",
  "enabled": true,
  "updated_at": "2026-06-09T12:00:00.000Z",
  "updated_by": "user@example.com"
}
```

**Changelog entry**

```json
{
  "flag_key": "my-flag",
  "event": "update",
  "after": { "key": "my-flag", "default_variation": "off", "variations": { "on": true, "off": false }, "rules": [], "enabled": true },
  "diff": { "enabled": { "from": false, "to": true } }
}
```

Changelog entries include the full flag state after the change. `update` entries also include `diff`.

---

Continued in `api-schema.md`.
