# Tailwind v4 CSS-first configuration

In v4 there is no required `tailwind.config.js`. Everything is driven from the
entry CSS file that imports Tailwind.

## Entry file

```css
@import "tailwindcss";
```

This single import replaces the v3 `@tailwind base; @tailwind components;
@tailwind utilities;` trio. Everything below lives in the same file (or files it
`@import`s).

## `@theme` — design tokens

`@theme` defines CSS variables in known namespaces; each generates utilities.

```css
@theme {
  --color-brand-500: oklch(0.62 0.19 255);   /* bg-brand-500, text-brand-500, ... */
  --font-display: "Satoshi", sans-serif;       /* font-display */
  --spacing: 0.25rem;                           /* base spacing scale */
  --radius-card: 1rem;                          /* rounded-card */
  --breakpoint-3xl: 120rem;                     /* 3xl: variant */
}
```

Namespaces include `--color-*`, `--font-*`, `--text-*`, `--spacing-*`,
`--radius-*`, `--shadow-*`, `--breakpoint-*`, `--container-*`, `--ease-*`,
`--animate-*`.

Rules:
- `@theme` must be **top-level** (not nested in a selector).
- Theme variables are also emitted as real CSS variables under `:root`, so they
  are usable at runtime (`var(--color-brand-500)`).
- Override a default: redefine it (`--color-blue-500: #2563eb;`).
- Remove a default group: `--color-*: initial;` (then define your own).
- Reset the entire default theme: `--*: initial;`.

## `@theme inline` — values that reference variables

Use `inline` when a token's value is itself a `var()`. Without `inline`,
Tailwind copies the value into `:root` and the indirection breaks; with `inline`
the utility emits `var(--primary)` directly so it tracks whatever `:root`/`.dark`
currently defines. This is the backbone of light/dark theming.

```css
@theme inline {
  --color-primary: var(--primary);
}
```

## Content detection and `@source`

v4 auto-detects template files (respecting `.gitignore`, skipping binaries).
Adjust when needed:

```css
@source "../node_modules/@my/ui";        /* include an extra source */
@source not "../legacy";                  /* exclude a path */
@source inline("bg-red-500 hover:bg-red-700"); /* safelist dynamic classes */
```

## Plugins and legacy JS config

```css
@plugin "@tailwindcss/typography";   /* load a JS plugin */
@config "./tailwind.config.js";      /* opt back into a JS config file */
```

## Prefix, custom utilities, variants

```css
@import "tailwindcss" prefix(tw);    /* tw:flex, tw:bg-brand-500 */

@utility content-auto {              /* custom utility */
  content-visibility: auto;
}

@custom-variant dark (&:where(.dark, .dark *));  /* class-based dark mode */
```

By default the `dark:` variant in v4 follows `prefers-color-scheme`. The
`@custom-variant dark` line above switches it to a `.dark` class toggle — needed
for manual theme switchers.

## Quick checklist when editing config

1. Find the file with `@import "tailwindcss";` — that is the config.
2. Token changes go in `@theme`; runtime-variable mappings go in `@theme inline`.
3. After adding classes used only dynamically, add `@source inline(...)`.
4. Restart/rebuild the dev server if tokens don't appear (theme changes require
   a rebuild, not just HMR, in some setups).
