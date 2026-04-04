# DiceBear Styles Reference

31 styles available. Full per-style options discoverable via schema endpoint:
`https://api.dicebear.com/9.x/<slug>/schema.json`

## Minimalist Styles

| Slug | Creator | License | Description |
|------|---------|---------|-------------|
| `glass` | DiceBear | CC0 1.0 | Overlapping letter shapes with colorful backgrounds |
| `icons` | Bootstrap Authors | MIT | 176 Bootstrap icons with colored backgrounds |
| `identicon` | DiceBear | CC0 1.0 | 5x5 grid geometric patterns (GitHub-style) |
| `initials` | DiceBear | CC0 1.0 | Text initials from seed with colored background |
| `rings` | DiceBear | CC0 1.0 | Concentric ring segments with rotation |
| `shapes` | DiceBear | CC0 1.0 | Layered geometric shapes (ellipses, polygons, lines) |
| `thumbs` | DiceBear | CC0 1.0 | Simple thumb-shaped faces with eyes/mouth |

## Character Styles

| Slug | Creator | License | Description |
|------|---------|---------|-------------|
| `adventurer` | Lisa Wischofsky | CC BY 4.0 | Illustrated characters with hair, earrings, glasses |
| `adventurer-neutral` | Lisa Wischofsky | CC BY 4.0 | Neutral version (no skin/hair color) |
| `avataaars` | Pablo Stanley | Free | Cartoon avatars with clothing, accessories, facial hair |
| `avataaars-neutral` | Pablo Stanley | Free | Neutral version (skin-tone backgrounds only) |
| `big-ears` | The Visual Team | CC BY 4.0 | Characters with prominent ears, diverse hairstyles |
| `big-ears-neutral` | The Visual Team | CC BY 4.0 | Neutral version |
| `big-smile` | Ashley Seo | CC BY 4.0 | Smiling characters with accessories |
| `bottts` | Pablo Stanley | Free | Robot/bot avatars with textures and parts |
| `bottts-neutral` | Pablo Stanley | Free | Neutral robot version |
| `croodles` | vijay verma | CC BY 4.0 | Hand-drawn doodle characters |
| `croodles-neutral` | vijay verma | CC BY 4.0 | Neutral doodle version |
| `dylan` | Natalia Spivak | CC BY 4.0 | Simple characters with mood expressions |
| `fun-emoji` | Davis Uche | CC BY 4.0 | Colorful emoji-style faces |
| `lorelei` | Lisa Wischofsky | CC0 1.0 | Line-art characters with detailed features |
| `lorelei-neutral` | Lisa Wischofsky | CC0 1.0 | Neutral line-art version |
| `micah` | Micah Lanier | CC BY 4.0 | Minimal flat characters with shirts |
| `miniavs` | Webpixels | CC BY 4.0 | Tiny avatar characters |
| `notionists` | Zoish | CC0 1.0 | Notion-style illustrated characters with gestures |
| `notionists-neutral` | Zoish | CC0 1.0 | Neutral Notion-style version |
| `open-peeps` | Pablo Stanley | CC0 1.0 | Hand-drawn people with masks and facial hair |
| `personas` | Draftbit | CC BY 4.0 | Stylized characters with varied body types |
| `pixel-art` | DiceBear | CC0 1.0 | 8-bit pixelated characters |
| `pixel-art-neutral` | DiceBear | CC0 1.0 | Neutral pixel version |
| `toon-head` | Johan Melin | CC BY 4.0 | Cartoon head/bust with clothing |

## Common Style Options

Most character styles support these option patterns (exact names vary per style):

**Appearance parts** (type: array) — comma-separated variant names:
- `hair`, `eyes`, `mouth`, `nose`, `eyebrows`, `beard`/`facialHair`
- `clothing`/`clothes`, `accessories`, `glasses`, `hat`/`top`

**Color options** (type: array) — hex colors without `#`:
- `hairColor`, `skinColor`, `clothingColor`/`clothesColor`
- `backgroundColor` (universal)

**Probability options** (type: integer, 0-100) — chance of including optional feature:
- `glassesProbability`, `accessoriesProbability`, `beardProbability`
- `facialHairProbability`, `hatProbability`, `earringsProbability`

## Gravatar Replacement Recommendations

| Use Case | Recommended Style | Why |
|----------|-------------------|-----|
| GitHub-like | `identicon` | Same pattern concept |
| Professional apps | `initials` | Clean, familiar |
| Fun/social apps | `avataaars` or `fun-emoji` | Expressive, recognizable |
| Tech/dev tools | `bottts` or `pixel-art` | Techy aesthetic |
| Minimal/clean | `lorelei-neutral` or `thumbs` | Simple, lightweight |
| Kids/education | `big-smile` or `adventurer` | Friendly, colorful |

## License Notes

- **CC0 1.0** — No restrictions, public domain equivalent
- **CC BY 4.0** — Attribution required (credit the creator)
- **Free / MIT** — Free for personal and commercial use
