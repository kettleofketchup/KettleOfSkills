# Tailwind CSS: Advanced Customization

Custom utilities, variants, layers, plugins, full config, and dark mode.

## Custom Utilities

```css
@utility content-auto {
  content-visibility: auto;
}

@utility tab-* {
  tab-size: var(--tab-size-*);
}

@utility glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

```html
<div class="content-auto">Optimized rendering</div>
<pre class="tab-4">Code with 4-space tabs</pre>
<div class="glass">Glassmorphism effect</div>
```

## Custom Variants

```css
@custom-variant theme-midnight (&:where([data-theme="midnight"] *));
@custom-variant aria-checked (&[aria-checked="true"]);
@custom-variant required (&:required);
```

```html
<div data-theme="midnight">
  <div class="theme-midnight:bg-navy-900">Applies in midnight theme</div>
</div>
<input class="required:border-red-500" required />
```

## Layer Organization

```css
@layer base {
  h1 { @apply text-4xl font-bold tracking-tight; }
  h2 { @apply text-3xl font-semibold; }
  a { @apply text-blue-600 hover:text-blue-700 underline-offset-4 hover:underline; }
  body { @apply bg-background text-foreground antialiased; }
}

@layer components {
  .btn { @apply px-4 py-2 rounded-lg font-medium transition-colors; }
  .btn-primary { @apply bg-blue-600 text-white hover:bg-blue-700; }
  .card { @apply bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow; }
  .input { @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500; }
}

@layer utilities {
  .text-balance { text-wrap: balance; }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
    &::-webkit-scrollbar { display: none; }
  }
}
```

## @apply Directive

```css
.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3
         rounded-lg shadow-md transition-all focus:ring-4 focus:ring-blue-300;
}
.section-container { @apply container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl; }
```

## Plugins

```bash
npm install -D @tailwindcss/typography @tailwindcss/forms @tailwindcss/container-queries
```

```javascript
export default { plugins: [require('@tailwindcss/typography'), require('@tailwindcss/forms')] }
```

```html
<article class="prose lg:prose-xl"><h1>Styled article</h1></article>
```

### Custom Plugin

```javascript
const plugin = require('tailwindcss/plugin')
export default {
  plugins: [
    plugin(function({ addUtilities, addComponents, theme }) {
      addUtilities({
        '.text-shadow': { textShadow: '2px 2px 4px rgba(0, 0, 0, 0.1)' },
        '.text-shadow-lg': { textShadow: '4px 4px 8px rgba(0, 0, 0, 0.2)' },
      })
      addComponents({
        '.card-custom': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.lg'),
          padding: theme('spacing.6'),
        },
      })
    }),
  ],
}
```

## Complete Config + Dark Mode

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'
const config: Config = {
  darkMode: ["class"],  // or "media"
  content: ['./pages/**/*.{ts,tsx}', './components/**/*.{ts,tsx}', './app/**/*.{ts,tsx}'],
  safelist: ['bg-red-500', { pattern: /bg-(red|green|blue)-(100|500|900)/ }],
  theme: {
    container: { center: true, padding: "2rem", screens: { "2xl": "1400px" } },
    extend: {
      colors: {
        border: "hsl(var(--border))", background: "hsl(var(--background))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
      },
      borderRadius: { lg: "var(--radius)", md: "calc(var(--radius) - 2px)" },
      animation: { "slide-in": "slide-in 0.5s ease-out" },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
export default config
// Usage: <html class="dark"> → <div class="bg-white dark:bg-gray-900">
```
