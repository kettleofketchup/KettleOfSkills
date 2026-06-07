# Theme colors (flat `@theme`)

Use the flat pattern when the project has a single, static palette with no
runtime theme switching.

## Defining and overriding colors

```css
@import "tailwindcss";

@theme {
  /* semantic tokens */
  --color-primary: oklch(0.62 0.19 255);
  --color-accent: oklch(0.74 0.16 75);
  --color-surface: oklch(0.98 0 0);

  /* override a built-in scale step */
  --color-blue-500: #2563eb;

  /* add a full custom scale */
  --color-brand-50:  oklch(0.97 0.02 255);
  --color-brand-500: oklch(0.62 0.19 255);
  --color-brand-900: oklch(0.28 0.09 255);
}
```

Every `--color-<name>` token generates the full utility set:
`bg-<name>`, `text-<name>`, `border-<name>`, `fill-<name>`, `ring-<name>`,
`from-<name>`, `divide-<name>`, etc. It also becomes a live CSS variable:
`var(--color-primary)`.

## Two kinds of color edits

1. **Semantic tokens** (`--color-primary`, `--color-surface`) — preferred. Markup
   references intent (`bg-primary`), so a single token edit restyles everything.
2. **Palette overrides** (`--color-blue-500`) — change Tailwind's defaults
   globally. Use sparingly; markup that says `bg-blue-500` now silently means
   your brand blue.

When changing "base theme colors," prefer editing semantic tokens unless the
project deliberately reuses default scale names as its brand palette.

## Removing defaults

```css
@theme {
  --color-*: initial;        /* drop ALL default colors */
  --color-white: #fff;       /* then re-add only what you need */
  --color-brand-500: oklch(0.62 0.19 255);
}
```

## Color format

v4 ships its default palette in **oklch**. Prefer oklch for new tokens — it
keeps lightness/chroma perceptually even across a scale and is what the brand
skill values usually carry. Hex and rgb are still valid.

## Gotchas

- `@theme` cannot be nested inside a selector — keep it top-level.
- Opacity modifiers (`bg-primary/50`) work automatically for any `--color-*`
  token; no extra setup.
- If a new token's utilities don't appear, rebuild — theme changes are not
  always picked up by HMR alone.
- Do **not** put `var(--x)`-valued colors in a plain `@theme`; use `@theme
  inline` (see `light-dark-theming.md`).
