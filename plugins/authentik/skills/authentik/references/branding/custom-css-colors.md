# Custom CSS: Color Schemes and Variables

Custom CSS is injected via the brand's `branding_custom_css` field. Since 2025.4.0, CSS loads inside ShadowDOMs for full component-level control.

## Architecture

Authentik uses Lit web components with Patternfly as the design system.
- `--ak-*` prefix: Authentik-specific CSS variables
- `--pf-*` prefix: Patternfly design system variables
- `::part()` selector: targets shadow DOM elements by their `part` attribute

**Discovery**: No comprehensive variable list exists. Use browser DevTools to inspect rendered HTML, look for `part="..."` attributes and active CSS variables.

## Color Scheme Customization

### Primary / Accent Colors

```css
/* Override Patternfly primary color (buttons, links, focus rings) */
:root {
  --pf-global--primary-color--100: #6366f1;     /* indigo-500 */
  --pf-global--primary-color--200: #4f46e5;     /* indigo-600 (hover) */
  --pf-global--primary-color--light-100: #e0e7ff; /* indigo-100 (light bg) */
  --pf-global--primary-color--dark-100: #4338ca;  /* indigo-700 (dark mode) */
}
```

### Dark Mode Overrides

```css
/* Target dark theme specifically */
:host([theme="dark"]),
[data-theme="dark"] {
  --pf-global--BackgroundColor--100: #0f172a;
  --pf-global--BackgroundColor--200: #1e293b;
  --pf-global--Color--100: #f1f5f9;
  --pf-global--primary-color--100: #818cf8;
}
```

### Light Mode Overrides

```css
:host([theme="light"]),
[data-theme="light"] {
  --pf-global--BackgroundColor--100: #ffffff;
  --pf-global--BackgroundColor--200: #f8fafc;
  --pf-global--Color--100: #1e293b;
  --pf-global--primary-color--100: #4f46e5;
}
```

## Common Patternfly Variables

### Colors
| Variable | Purpose |
|----------|---------|
| `--pf-global--primary-color--100` | Primary action color |
| `--pf-global--primary-color--200` | Primary hover state |
| `--pf-global--danger-color--100` | Error/destructive actions |
| `--pf-global--success-color--100` | Success indicators |
| `--pf-global--warning-color--100` | Warning indicators |
| `--pf-global--info-color--100` | Informational indicators |
| `--pf-global--Color--100` | Default text color |
| `--pf-global--Color--200` | Secondary text color |
| `--pf-global--BackgroundColor--100` | Page background |
| `--pf-global--BackgroundColor--200` | Card/surface background |
| `--pf-global--BackgroundColor--dark-100` | Dark surface |
| `--pf-global--BorderColor--100` | Default border color |
| `--pf-global--active-color--100` | Active/selected state |
| `--pf-global--link--Color` | Link text color |
| `--pf-global--link--Color--hover` | Link hover color |

### Typography & Spacing
Also available: `--pf-global--FontFamily--sans-serif`, `--pf-global--FontFamily--heading--sans-serif`, `--pf-global--FontSize--{sm,md,lg,xl}`, `--pf-global--spacer--{sm,md,lg}`, `--pf-global--BorderRadius--sm`.

## Custom Font Loading

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --pf-global--FontFamily--sans-serif: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --pf-global--FontFamily--heading--sans-serif: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

For airgapped environments, serve fonts from static files and use `@font-face` instead.
