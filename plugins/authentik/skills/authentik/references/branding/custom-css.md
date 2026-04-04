# Custom CSS Reference

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

## Flow Executor Styling

### Login Page Background

```css
/* Gradient background on flow executor */
.pf-c-login {
  --pf-c-login--BackgroundImage: none;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4c1d95 100%);
}
```

### Login Card Styling

```css
/* Customize the login card */
.pf-c-login__main {
  --pf-c-login__main--BackgroundColor: rgba(15, 23, 42, 0.85);
  border-radius: 12px;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Flow Title Styling

```css
.pf-c-login__main-header-desc,
.pf-c-title {
  color: #e2e8f0;
}
```

## User Interface Styling

### Application Cards

```css
/* My Applications page cards */
.pf-c-card {
  --pf-c-card--BackgroundColor: #1e293b;
  border-radius: 8px;
  border: 1px solid #334155;
}

.pf-c-card:hover {
  border-color: var(--pf-global--primary-color--100);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}
```

### Navigation Sidebar (Admin)

```css
.pf-c-nav {
  --pf-c-nav--BackgroundColor: #0f172a;
}

.pf-c-nav__link {
  --pf-c-nav__link--Color: #94a3b8;
  --pf-c-nav__link--hover--Color: #f1f5f9;
}

.pf-c-nav__link.pf-m-current {
  --pf-c-nav__link--m-current--Color: var(--pf-global--primary-color--100);
}
```

## Shadow DOM Targeting with ::part

Target internal component elements exposed via `part` attributes:

```css
/* Example: style a button part inside a web component */
ak-flow-executor::part(submit-button) {
  background-color: #6366f1;
  border-radius: 8px;
}
```

Inspect components in DevTools to discover available parts.

## Hiding UI Elements

```css
/* Hide locale selector on login page */
.pf-c-login__footer .ak-locale-selector {
  display: none;
}

/* Hide "Powered by authentik" footer */
.pf-c-login__footer-band {
  display: none;
}

/* Hide specific admin sidebar items */
.pf-c-nav__item[data-nav-id="admin-system-brands"] {
  display: none;
}
```

## Custom Font Loading

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --pf-global--FontFamily--sans-serif: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --pf-global--FontFamily--heading--sans-serif: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

For airgapped environments, serve fonts from static files and use `@font-face` instead.

## Color Scheme Template

Combine the primary/dark/light overrides from above into one `branding_custom_css` block. Replace `#REPLACE` placeholders with brand colors. Use the variable tables and dark/light mode examples in previous sections as reference for available properties.
