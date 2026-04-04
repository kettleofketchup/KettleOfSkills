# DiceBear HTTP API Reference

## Endpoint Pattern

```
https://api.dicebear.com/9.x/<styleName>/<format>
```

Current version: `9.x`. Deprecated: 5.x-8.x (EOL April 30, 2028).

## Output Formats

| Format | Suffix | Max Size | Rate Limit |
|--------|--------|----------|------------|
| SVG | `/svg` | Unlimited | 50 req/s |
| PNG | `/png` | 256px | 10 req/s |
| JPG | `/jpg` | 256px | 10 req/s |
| WebP | `/webp` | 256px | 10 req/s |
| AVIF | `/avif` | 256px | 10 req/s |
| JSON | `/json` | N/A | N/A |

Schema: `https://api.dicebear.com/9.x/<style>/schema.json`

Rate limit exceeded returns HTTP 429.

## Core Options (All Styles)

| Option | Type | Default | Range | Description |
|--------|------|---------|-------|-------------|
| `seed` | string | random | any | PRNG seed for reproducible avatars |
| `flip` | bool | false | | Horizontal mirror |
| `rotate` | int | 0 | 0-360 | Rotation degrees |
| `scale` | int | 100 | 0-200 | Scale percentage |
| `radius` | int | 0 | 0-50 | Border radius (rounded corners) |
| `size` | int | -- | 1+ | Output size in pixels |
| `backgroundColor` | array | varies | hex/`transparent` | Background color(s) |
| `backgroundType` | array | `solid` | `solid`, `gradientLinear` | Fill type |
| `backgroundRotation` | array | [0,360] | 0-360 | Gradient angle range |
| `translateX` | int | 0 | -100 to 100 | Horizontal offset |
| `translateY` | int | 0 | -100 to 100 | Vertical offset |
| `clip` | bool | true | | Clip to canvas bounds |
| `randomizeIds` | bool | false | | Randomize SVG element IDs (use when embedding multiple) |

## Query Parameter Syntax

Arrays as comma-separated values:
```
?hair=short01,short02,short03
```

Booleans as strings:
```
?flip=true&randomizeIds=false
```

Range arrays as min,max:
```
?backgroundRotation=0,180
```

## Usage Examples

```bash
# Basic SVG
https://api.dicebear.com/9.x/avataaars/svg

# Seeded (deterministic)
https://api.dicebear.com/9.x/avataaars/svg?seed=john@example.com

# PNG with size
https://api.dicebear.com/9.x/pixel-art/png?seed=Felix&size=128

# Gradient background
https://api.dicebear.com/9.x/shapes/svg?backgroundType=gradientLinear&backgroundColor=ff0000,0000ff

# Rounded avatar
https://api.dicebear.com/9.x/identicon/svg?seed=test&radius=50

# Multiple style options
https://api.dicebear.com/9.x/adventurer/svg?seed=Jane&flip=true&hair=long01,long05&glassesProbability=50
```

## Self-Hosting Notes

Public API has no availability guarantees. Self-host for production.
See [dicebear-self-hosting.md](dicebear-self-hosting.md) for Docker deployment and env var config.
Self-hosted supports higher size limits (configurable via env vars) and no rate limits.
