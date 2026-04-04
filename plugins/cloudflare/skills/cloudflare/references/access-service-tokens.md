# Cloudflare Access Service Tokens Reference

*Last updated: 2026-03-23*

## Creating Service Tokens

```bash
# Create token (duration in Go format: 8760h = 1 year)
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/access/service_tokens" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "dota-production", "duration": "8760h"}'
```

Response contains `client_id` and `client_secret` — **shown only once**.

## Authentication Headers

Client sends two headers:

| Header | Value |
|--------|-------|
| `CF-Access-Client-Id` | Client ID from token creation |
| `CF-Access-Client-Secret` | Client Secret from token creation |

## Creating Access Applications

```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grafana",
    "domain": "grafana.home.kettle.sh",
    "type": "self_hosted",
    "session_duration": "24h"
  }'
```

## Creating Service Token Policies

**CRITICAL: Use `decision: non_identity`** for service tokens. `allow` redirects to IdP login.

### Allow specific token:

```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account_id}/access/apps/{app_id}/policies" \
  -H "Authorization: Bearer $CF_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Allow dota-production",
    "decision": "non_identity",
    "include": [{"service_token": {"token_id": "<service_token_id>"}}]
  }'
```

### Allow any valid token:

```bash
-d '{"name": "Allow any token", "decision": "non_identity", "include": [{"any_valid_service_token": {}}]}'
```

## Headers Set by Cloudflare After Validation

| Header | Description |
|--------|-------------|
| `Cf-Access-Jwt-Assertion` | Signed JWT — **validate this** |
| `Cf-Access-Authenticated-User-Email` | User email (placeholder for service tokens) |
| `CF_Authorization` | Same JWT as cookie (not guaranteed for non-browser) |

## Token Lifecycle

```bash
# Rotate (new secret, same ID)
POST /accounts/{id}/access/service_tokens/{token_id}/rotate

# Refresh (extend expiration)
POST /accounts/{id}/access/service_tokens/{token_id}/refresh

# Delete (revoke immediately)
DELETE /accounts/{id}/access/service_tokens/{token_id}
```

## Testing with curl

```bash
curl -v \
  -H "CF-Access-Client-Id: $CLIENT_ID" \
  -H "CF-Access-Client-Secret: $CLIENT_SECRET" \
  https://grafana.home.kettle.sh/api/health
```

| Response | Meaning |
|----------|---------|
| 200 + `Set-Cookie: CF_Authorization` | Service token accepted |
| 403 Forbidden | Token invalid, expired, or no matching policy |
| 302 to IdP | No Service Auth policy matched (wrong `decision` type) |

## API Endpoints Quick Reference

| Operation | Method | Path |
|-----------|--------|------|
| Create token | POST | `/accounts/{id}/access/service_tokens` |
| List tokens | GET | `/accounts/{id}/access/service_tokens` |
| Rotate token | POST | `/accounts/{id}/access/service_tokens/{tid}/rotate` |
| Delete token | DELETE | `/accounts/{id}/access/service_tokens/{tid}` |
| Create app | POST | `/accounts/{id}/access/apps` |
| Create policy | POST | `/accounts/{id}/access/apps/{aid}/policies` |

Base URL: `https://api.cloudflare.com/client/v4`
