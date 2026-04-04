---
name: dicebear
description: DiceBear avatar generation and Gravatar API integration. Use when generating procedural avatars from seeds/emails, self-hosting DiceBear HTTP API on Docker/Kubernetes, replacing Gravatar with DiceBear, fetching Gravatar profiles by email hash (SHA256), uploading avatars via Gravatar OAuth2, configuring DiceBear styles (avataaars, pixel-art, identicon, initials, bottts, lorelei, etc.), or building avatar URL patterns with fallback defaults.
---

# DiceBear & Gravatar Avatars

Procedural avatar generation with DiceBear and Gravatar profile/avatar API integration. Primary use case: self-hosted DiceBear as a Gravatar replacement.

## DiceBear HTTP API

**Public API:** `https://api.dicebear.com/9.x/<style>/<format>`
**Self-hosted:** See [dicebear-self-hosting.md](references/dicebear-self-hosting.md)

### Quick Reference

```
# SVG avatar with seed
https://api.dicebear.com/9.x/identicon/svg?seed=user@example.com

# PNG at specific size
https://api.dicebear.com/9.x/avataaars/png?seed=John&size=128

# With style options
https://api.dicebear.com/9.x/pixel-art/svg?seed=Felix&hair=short01,short02&backgroundColor=b6e3f4

# Get style schema (all available options)
https://api.dicebear.com/9.x/pixel-art/schema.json
```

Formats: `svg` (recommended, 50 req/s), `png`, `jpg`, `webp`, `avif` (10 req/s, max 256px), `json` (metadata)

See [dicebear-http-api.md](references/dicebear-http-api.md) for core options and parameters.
See [dicebear-styles.md](references/dicebear-styles.md) for all 31 available styles.

## Gravatar API

**REST API:** `https://api.gravatar.com/v3`
**Avatar URLs:** `https://gravatar.com/avatar/<SHA256_HASH>`

### Quick Reference

```python
# Generate Gravatar hash
import hashlib
email_hash = hashlib.sha256(email.strip().lower().encode()).hexdigest()

# Avatar URL with fallback
avatar_url = f"https://gravatar.com/avatar/{email_hash}?d=identicon&s=200"

# Profile lookup (requires API key)
GET https://api.gravatar.com/v3/profiles/{email_hash}
Authorization: Bearer YOUR_API_KEY
```

Built-in defaults: `identicon`, `mp` (mystery person), `monsterid`, `wavatar`, `retro`, `robohash`, `blank`, `404`, `initials`, `color`

See [gravatar-rest-api.md](references/gravatar-rest-api.md) for REST endpoints and auth.
See [gravatar-avatar-urls.md](references/gravatar-avatar-urls.md) for URL-based avatar params.

## Gravatar Replacement with DiceBear

To replace Gravatar with self-hosted DiceBear:

1. **Deploy DiceBear API** — Docker container on port 3000
2. **Use email as seed** — `https://dicebear.local/9.x/identicon/svg?seed=user@example.com`
3. **Choose a style** — `identicon`, `initials`, `pixel-art`, `avataaars` are common replacements
4. **Map Gravatar defaults** to DiceBear styles:

| Gravatar `d=` | DiceBear Style |
|----------------|----------------|
| `identicon` | `identicon` |
| `initials` | `initials` |
| `retro` | `pixel-art` |
| `monsterid` | `bottts` or `fun-emoji` |
| `robohash` | `bottts` |
| `mp` | `avataaars-neutral` or `lorelei-neutral` |

## Deterministic Avatars

Both systems generate consistent avatars from identifiers:
- **DiceBear:** `?seed=<any_string>` — same seed always produces same avatar
- **Gravatar:** SHA256 hash of lowercase trimmed email — same email always produces same avatar

For DiceBear, use the email address (or email hash) as the seed for Gravatar-compatible behavior.
