# Gravatar Avatar URL API

URL-based avatar requests. These do NOT count towards REST API rate limits.

## URL Pattern

```
https://gravatar.com/avatar/SHA256_HASH
https://gravatar.com/avatar/SHA256_HASH.jpg
```

Hash = SHA256 of trimmed, lowercased email address.

## Parameters

### Size (`s=` or `size=`)

Output size in pixels (images are always square).

- Default: 80px
- Range: 1–2048px

```
https://gravatar.com/avatar/HASH?s=200
```

### Default Image (`d=` or `default=`)

Fallback when no Gravatar exists for the hash.

**Built-in defaults:**

| Value | Description |
|-------|-------------|
| `identicon` | Geometric pattern from hash |
| `mp` | Mystery-person silhouette (same for all) |
| `monsterid` | Generated monster face |
| `wavatar` | Generated face with features |
| `retro` | 8-bit arcade pixelated face |
| `robohash` | Generated robot |
| `blank` | Transparent PNG |
| `404` | Return HTTP 404, no image |
| `initials` | Initials from profile name with generated colors (beta) |
| `color` | Generated solid color (beta) |

**Custom URL** — must be URL-encoded, publicly accessible, have image extension, no querystring:
```
https://gravatar.com/avatar/HASH?d=https%3A%2F%2Fexample.com%2Favatar.jpg
```

### Force Default (`f=` or `forcedefault=`)

Always load the default image, ignoring any existing Gravatar.

```
https://gravatar.com/avatar/HASH?f=y
```

### Rating (`r=` or `rating=`)

Maximum content rating. Default: `g`.

| Rating | Content Level |
|--------|---------------|
| `g` | Suitable for all |
| `pg` | Mild content |
| `r` | Mature content |
| `x` | Explicit content |

### Initials Params

- `initials` — specify exact initials to show
- `name` — pass a name, initials are extracted

## Combined Examples

```bash
# 200px with identicon fallback, PG rating
https://gravatar.com/avatar/HASH?s=200&d=identicon&r=pg

# Force mystery person default
https://gravatar.com/avatar/HASH?s=128&d=mp&f=y

# 404 if no avatar (useful for checking existence)
https://gravatar.com/avatar/HASH?d=404

# Custom fallback URL
https://gravatar.com/avatar/HASH?d=https%3A%2F%2Fcdn.example.com%2Fdefault-avatar.png&s=256
```

## DiceBear as Custom Default

Use self-hosted DiceBear as Gravatar's custom default:

```
https://gravatar.com/avatar/HASH?d=https%3A%2F%2Fdicebear.local%2F9.x%2Fidenticon%2Fsvg%3Fseed%3DHASH
```

Or skip Gravatar entirely and use DiceBear directly with email as seed:

```
https://dicebear.local/9.x/identicon/svg?seed=user@example.com
```
