# Custom CSS: Component Styling and UI Elements

For color variable reference, see [custom-css-colors.md](custom-css-colors.md).

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

## Color Scheme Template

Combine the primary/dark/light overrides from [custom-css-colors.md](custom-css-colors.md) into one `branding_custom_css` block. Replace `#REPLACE` placeholders with brand colors. Use the variable tables and dark/light mode examples as reference for available properties.
