# Light/dark and dark-only theming

## Why `@theme inline`

For runtime theme switching, the actual color values live in plain CSS variables
under `:root` (light) and `.dark` (dark). The `@theme inline` block maps theme
tokens to those variables so utilities emit `var(--primary)` and follow whichever
mode is active. A non-`inline` `@theme` would bake the value in at build time and
break switching.

## Class-based light/dark (manual toggle)

```css
@import "tailwindcss";

/* make the dark: variant follow a .dark class instead of prefers-color-scheme */
@custom-variant dark (&:where(.dark, .dark *));

:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary:    oklch(0.205 0 0);
  --border:     oklch(0.922 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary:    oklch(0.922 0 0);
  --border:     oklch(0.269 0 0);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary:    var(--primary);
  --color-border:     var(--border);
}
```

Toggle by adding/removing `class="dark"` on `<html>`. **Edit colors in `:root`
and/or `.dark`, never in the `@theme inline` mapping** — the mapping is plumbing,
not values.

### Which block to edit

| Change applies to | Edit |
|-------------------|------|
| Light mode only   | `:root` |
| Dark mode only    | `.dark` |
| Both modes        | both `:root` and `.dark` |

## System-preference light/dark (no toggle)

Skip `@custom-variant`; v4's `dark:` variant already follows
`prefers-color-scheme`. To switch the CSS variables automatically:

```css
:root { --background: oklch(1 0 0); --foreground: oklch(0.145 0 0); }

@media (prefers-color-scheme: dark) {
  :root { --background: oklch(0.145 0 0); --foreground: oklch(0.985 0 0); }
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
}
```

## Dark-only themes

When the product ships a single dark theme with no light mode, do **not** wire up
`.dark` or `prefers-color-scheme` — that indirection is dead weight. Define the
dark palette once and tell the browser the page is dark so form controls,
scrollbars, and `system` UI render correctly.

```css
@import "tailwindcss";

html { color-scheme: dark; }   /* native controls render dark */

@theme {
  --color-background: oklch(0.145 0 0);
  --color-foreground: oklch(0.985 0 0);
  --color-primary:    oklch(0.922 0 0);
  --color-border:     oklch(0.269 0 0);
}
```

This is just the **flat** pattern (`theme-colors.md`) with dark values — editing
a color means changing the literal in `@theme`. Use `@theme inline` + `:root`
here only if other code already reads the raw `--background`-style variables.

To leave room for a future light mode, instead put the dark values in `:root`,
add the `@theme inline` mapping, and add a `.dark`/light counterpart later
without touching markup.
