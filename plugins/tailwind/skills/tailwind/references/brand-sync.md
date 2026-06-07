# Brand skill synchronization

Many projects keep canonical brand colors in a per-project skill at
`.claude/skills/brand/` (or a directory matching `*brand*`). When one exists it
is the **source of truth**: change colors there first, then propagate to the
Tailwind `@theme`. When none exists, **Tailwind is primary** — edit the CSS
directly and skip everything here.

## Detect

```bash
ls -d .claude/skills/*brand*/ 2>/dev/null
```

If nothing is returned, stop — Tailwind-primary, no sync needed.

## Read tiers

Brand skills are unstructured, so look for color definitions in this order and
use the first that exists:

1. **Machine-readable token file** — `references/colors.json`, `tokens.json`,
   `colors.yaml`, `*.tokens.json`, or a CSS file with `--color-*` / `--*`
   declarations. Parse key→value pairs.
   ```bash
   ls .claude/skills/*brand*/references/ 2>/dev/null
   grep -rEn '"#|oklch|rgb|hsl|--[a-z-]+:' .claude/skills/*brand*/ 2>/dev/null
   ```
2. **Markdown color table** — a table in the brand `SKILL.md` or a reference
   (columns like `Token | Value` / `Name | Hex`). Read name + value cells.
3. **Inline declarations** — loose `--color-name: value;` lines anywhere in the
   brand skill.

If none is parseable, treat the brand `SKILL.md` color section as prose and
update it in place, noting the assumed token→value mapping in your summary.

## Source-of-truth rule

```
brand skill present ──> 1. update canonical value in the brand skill (same tier/format you read)
                        2. propagate the value into the project @theme / :root / .dark
                        3. verify both match

brand skill absent  ──> edit @theme / :root / .dark directly
```

Always write back to the brand skill in the **same form** it was read (JSON stays
JSON, the markdown table row gets edited, an inline `--color-*` line is
replaced). Never silently introduce a second, divergent format.

## Map brand names to Tailwind tokens

Brand names rarely match `--color-*` token names one-to-one. Build an explicit
mapping and reuse it both directions:

| Brand token (source of truth) | Tailwind token (`@theme`) |
|-------------------------------|---------------------------|
| `brand.primary`               | `--color-primary`         |
| `brand.surface`               | `--color-background`      |
| `brand.ink`                   | `--color-foreground`      |

When the names already align (e.g. brand defines `--color-primary` directly),
copy verbatim.

## Verify

```bash
# the new value should appear in BOTH the CSS and the brand record
grep -rn '<new-value>' <entry.css> .claude/skills/*brand*/
# the old value should appear in NEITHER
grep -rn '<old-value>' <entry.css> .claude/skills/*brand*/
```

Report which file is the source of truth, what changed, and the brand↔Tailwind
token mapping you used.
