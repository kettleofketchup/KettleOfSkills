# Tailwind CSS: Theme Customization

`@theme` directive, colors, typography, and spacing extensions.

> **For deeper Tailwind v4 theming, use the `tailwind` skill.** It covers
> light/dark and dark-only patterns, `@theme inline` mechanics, and a workflow
> for syncing base theme colors with a project's `/brand` skill. Use this
> reference for shadcn/React-oriented customization; reach for `tailwind` when
> theming is the main task or the project isn't shadcn/React.

## @theme Directive

Modern CSS-based approach to customization:

```css
@import "tailwindcss";

@theme {
  /* Custom colors */
  --color-brand-50: oklch(0.97 0.02 264);
  --color-brand-500: oklch(0.55 0.22 264);
  --color-brand-900: oklch(0.25 0.15 264);

  /* Custom fonts */
  --font-display: "Satoshi", "Inter", sans-serif;
  --font-body: "Inter", system-ui, sans-serif;

  /* Custom spacing */
  --spacing-18: calc(var(--spacing) * 18);
  --spacing-navbar: 4.5rem;

  /* Custom breakpoints */
  --breakpoint-3xl: 120rem;
  --breakpoint-tablet: 48rem;

  /* Custom shadows */
  --shadow-glow: 0 0 20px rgba(139, 92, 246, 0.3);

  /* Custom radius */
  --radius-large: 1.5rem;
}
```

```html
<div class="bg-brand-500 font-display shadow-glow rounded-large">Custom</div>
<div class="tablet:grid-cols-2 3xl:grid-cols-6">Custom breakpoints</div>
```

## Color Customization

### Full Color Scale

```css
@theme {
  --color-primary-50: oklch(0.98 0.02 250);
  --color-primary-100: oklch(0.95 0.05 250);
  --color-primary-200: oklch(0.90 0.10 250);
  --color-primary-300: oklch(0.85 0.15 250);
  --color-primary-400: oklch(0.75 0.18 250);
  --color-primary-500: oklch(0.65 0.22 250);
  --color-primary-600: oklch(0.55 0.22 250);
  --color-primary-700: oklch(0.45 0.20 250);
  --color-primary-800: oklch(0.35 0.18 250);
  --color-primary-900: oklch(0.25 0.15 250);
  --color-primary-950: oklch(0.15 0.10 250);
}
```

### Semantic Colors

```css
@theme {
  --color-success: oklch(0.65 0.18 145);
  --color-warning: oklch(0.75 0.15 85);
  --color-error: oklch(0.60 0.22 25);
  --color-info: oklch(0.65 0.18 240);
}
```

```html
<div class="bg-success text-white">Success</div>
<div class="border-error">Error state</div>
```

## Typography

### Custom Fonts

```css
@theme {
  --font-sans: "Inter", system-ui, sans-serif;
  --font-serif: "Merriweather", Georgia, serif;
  --font-mono: "JetBrains Mono", Consolas, monospace;
  --font-display: "Playfair Display", serif;
}
```

### Custom Font Sizes

```css
@theme {
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  --font-size-5xl: 3rem;
  --font-size-jumbo: 4rem;
}
```

## Spacing

```css
@theme {
  --spacing-13: calc(var(--spacing) * 13);
  --spacing-15: calc(var(--spacing) * 15);
  --spacing-18: calc(var(--spacing) * 18);

  /* Named spacing */
  --spacing-header: 4rem;
  --spacing-footer: 3rem;
  --spacing-section: 6rem;
}
```

```html
<div class="p-18">Custom padding</div>
<section class="py-section">Section spacing</section>
```

## Best Practices

1. **Use @theme for simple customizations**: Prefer CSS-based customization
2. **Leverage design tokens**: Define custom tokens in @theme
3. **Semantic naming**: Use descriptive names (`primary` not `blue`)
4. **Document custom utilities**: Add comments explaining custom classes
