# Gravatar REST API Reference

**Base URL:** `https://api.gravatar.com/v3`
**OpenAPI spec:** `https://api.gravatar.com/v3/openapi`

## Authentication

### API Key (Bearer Token) — Recommended

Create at [gravatar.com/developers](https://gravatar.com/developers/new-application).

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.gravatar.com/v3/profiles/HASH
```

Rate limit: 1000 req/hour (avatar URL requests don't count). Contact Gravatar for higher limits.

### OAuth2 (for user-scoped endpoints)

Uses WordPress.com OAuth. Authorization URL:
```
https://public-api.wordpress.com/oauth2/authorize?client_id=ID&redirect_uri=URI&response_type=code&scope[0]=auth&scope[1]=gravatar-profile:read&scope[2]=gravatar-profile:manage
```

Scopes: `auth`, `gravatar-profile:read`, `gravatar-profile:manage`

Token exchange (server-side): POST `https://public-api.wordpress.com/oauth2/token` with `client_id`, `client_secret`, `redirect_uri`, `grant_type=authorization_code`, `code`.

## Email Hash (Identifier)

SHA256 of trimmed, lowercased email. **Do NOT use MD5.**

```python
import hashlib
email_hash = hashlib.sha256("user@example.com".strip().lower().encode()).hexdigest()
```

## Endpoints

### GET /profiles/{hash}

Fetch profile by SHA256 hash or profile URL slug. Auth optional (unauthenticated returns limited data, max 4 verified_accounts).

**Response (authenticated):**
```json
{
  "hash": "84059b...",
  "display_name": "John Smith",
  "profile_url": "https://gravatar.com/example",
  "avatar_url": "https://0.gravatar.com/avatar/84059b...",
  "avatar_alt_text": "User's avatar",
  "pronouns": "He/Him",
  "location": "San Francisco, CA",
  "job_title": "Software Engineer",
  "company": "Tech Company",
  "description": "About me",
  "verified_accounts": [{"service_type": "github", "url": "..."}],
  "timezone": "America/Los_Angeles",
  "languages": [{"code": "en", "name": "English", "is_primary": true}],
  "first_name": "John", "last_name": "Smith",
  "links": [{"label": "Blog", "url": "..."}],
  "interests": [{"id": 1, "name": "photography"}],
  "registration_date": "2021-10-01T12:00:00Z"
}
```

### GET /profiles/search/by-verified-account (Experimental)

Search profiles by verified account username.

| Param | Required | Description |
|-------|----------|-------------|
| `username` | yes | Username on the service |
| `service` | no | Filter by service (e.g., `github`, `twitter`) |
| `page` | no | Page number (default: 1) |
| `per_page` | no | Results per page (1-50, default: 20) |

### GET /verified-accounts/services (Experimental)

List supported verified account services. No auth required.

### GET /qr-code/{hash}

Generate QR code for a profile. No auth required.

| Param | Description |
|-------|-------------|
| `size` | Size in px (default: 80) |
| `version` | Style: `1` (standard), `3` (modern dots) |
| `type` | Center icon: `user` (avatar), `gravatar` (logo), `none` |

### GET /me/profile (OAuth)

Get authenticated user's profile. Returns full Profile object.

### PATCH /me/profile (OAuth)

Update profile. Partial updates supported. Set field to empty string to unset.

Fields: `first_name`, `last_name`, `display_name`, `description`, `pronunciation`, `pronouns`, `location`, `job_title`, `company`, `cell_phone`, `contact_email`, `hidden_contact_info`

### GET /me/avatars (OAuth)

List user's avatars. Optional `selected_email_hash` param marks which is selected.

### POST /me/avatars (OAuth)

Upload avatar. Multipart form with `image` field. Images MUST be square.

| Param | Description |
|-------|-------------|
| `selected_email_hash` | Set as avatar for this email |
| `select_avatar` | `true`=always set, `false`=never, `null`=only if no existing |

### DELETE /me/avatars/{imageHash} (OAuth)

Delete an avatar by its hash.

### PATCH /me/avatars/{imageHash} (OAuth)

Update avatar metadata: `rating` (G/PG/R/X), `alt_text`.

### POST /me/avatars/{imageId}/email (OAuth)

Set avatar for email. Body: `{"email_hash": "SHA256_HASH"}`.

### GET /me/associated-email (OAuth)

Check if email is associated with authenticated user. Param: `email_hash`.

## Rate Limit Headers

- `X-RateLimit-Limit` — Total allowed per period
- `X-RateLimit-Remaining` — Remaining in period
- `X-RateLimit-Reset` — Unix timestamp of reset

## Error Codes

| HTTP | Code | Description |
|------|------|-------------|
| 400 | `uncropped_image` | Image not square |
| 400 | `unsupported_image` | Bad format (use JPG/PNG/GIF) |
| 401 | — | Auth failed |
| 403 | `insufficient_scope` | Missing OAuth scope |
| 404 | `disabled` | Profile disabled |
| 429 | `rate_limit_exceeded` | Too many requests |
