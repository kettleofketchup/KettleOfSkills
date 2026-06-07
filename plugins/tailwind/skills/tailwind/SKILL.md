---
name: tailwind
description: Tailwind CSS v4 (CSS-first) configuration and theming. Use when editing theme colors, light/dark or dark-only themes, @theme/@import/@plugin config, or syncing colors with a project brand skill.
---

# Tailwind CSS v4

Tailwind v4 is **CSS-first**: configuration and theme live in CSS, not a
`tailwind.config.js`. The entry stylesheet starts with `@import "tailwindcss";`
and customization happens in `@theme`, `@plugin`, `@source`, `@utility`, and
`@custom-variant` directives. This skill covers v4 only.

> **Related:** for building shadcn/ui + React components, forms (React Hook Form
> + Zod), accessibility, and responsive layouts, use the `ui-styling` skill. This
> skill focuses on the Tailwind layer itself — config, theme colors, and syncing
> with a project brand skill.

## Configuration essentials

The project's entry CSS is the file containing `@import "tailwindcss";` (often
`app.css`, `globals.css`, `styles.css`, or `index.css`). All config lives there.

- **Theme tokens:** `@theme { --color-*, --font-*, --spacing-*, --radius-*, --breakpoint-* }`. Each token generates utilities (e.g. `--color-brand-500` → `bg-brand-500`, `text-brand-500`).
- **Reference other vars:** use `@theme inline { ... }` when a token's value is `var(--something)`, so utilities resolve the variable at use-time (required for light/dark).
- **Content detection is automatic.** Add sources with `@source "../foo"`, exclude with `@source not "..."`, safelist with `@source inline("bg-red-500")`.
- **Plugins / legacy config:** `@plugin "@tailwindcss/typography";` and `@config "./tailwind.config.js";`.
- **Prefix / custom utilities / variants:** `@import "tailwindcss" prefix(tw);`, `@utility`, `@custom-variant`.

See `references/v4-configuration.md` for the full reference.

## Theming workflow

Use this flow whenever changing base theme colors.

### Step 0 — Detect a brand skill

Check the project for `.claude/skills/brand/` (also match `.claude/skills/*brand*/`).

- **Found** → the brand skill is the **source of truth**. Update its canonical
  color record first (Step 4), then propagate into the CSS.
- **Not found** → **Tailwind is primary**. Edit the CSS directly; skip Step 4.

```bash
ls -d .claude/skills/*brand*/ 2>/dev/null
```

### Step 1 — Locate the color definitions

Find the entry CSS, then locate within it:
- `@theme` / `@theme inline` blocks, and
- any `:root { --* }` and `.dark { --* }` (or `[data-theme]`) variable blocks.

```bash
grep -rl '@import "tailwindcss"' --include=*.css .
grep -n '@theme\|:root\|\.dark\|--color-' <entry.css>
```

### Step 2 — Identify the theming pattern

- **Flat** — colors are literal values inside `@theme { --color-primary: ... }`. No runtime switching.
- **Light/dark** — `@theme inline { --color-primary: var(--primary) }` with the real values in `:root` (light) and `.dark` (dark).
- **Dark-only** — a single dark palette, no `.dark` toggle.

Decision rule and full examples: `references/theme-colors.md` and
`references/light-dark-theming.md` (the dark-only section covers single-theme
projects).

### Step 3 — Apply the change

Edit the value in the place that matches the pattern:
- Flat → change the literal in `@theme`.
- Light/dark → change the raw value in `:root` **and/or** `.dark` (not the `@theme inline` mapping).
- Dark-only → change the single palette source.

Keep paired values consistent — if a token exists in both `:root` and `.dark`,
decide whether the change applies to one mode or both.

### Step 4 — Sync the brand skill (if present)

When a brand skill exists, record the change there so brand and CSS never drift.
Detection tiers and write-back rules are in `references/brand-sync.md`.

### Verify

Confirm the old value is gone and the new one is present in **both** the CSS and
(if applicable) the brand record:

```bash
grep -rn '<old-value>\|<new-value>' <entry.css> .claude/skills/*brand*/
```

## References

- `references/v4-configuration.md` — CSS-first configuration reference
- `references/theme-colors.md` — flat `@theme` colors, palette overrides, semantic tokens
- `references/light-dark-theming.md` — light/dark and dark-only patterns
- `references/brand-sync.md` — brand detection, source-of-truth rule, fallback
