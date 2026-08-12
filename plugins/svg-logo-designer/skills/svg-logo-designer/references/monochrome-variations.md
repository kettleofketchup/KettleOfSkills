# Monochrome Variations

For any logo, create monochrome versions by replacing all fills with CSS overrides.

## CSS Override Patterns

```xml
<!-- Monochrome Dark (for light backgrounds) -->
<style>.primary, .secondary, .accent { fill: #1F2937; }</style>

<!-- Monochrome Light (for dark backgrounds) -->
<style>.primary, .secondary, .accent { fill: #FFFFFF; }</style>
```

## File Naming Convention

Save monochrome versions alongside full-color variants:

```
logos/
  {brand}-concept1-horizontal.svg
  {brand}-concept1-monochrome-dark.svg
  {brand}-concept1-monochrome-light.svg
```

## When to Use Each Variant

| Variant | Background | Use Case |
|---------|-----------|----------|
| Full color | Any | Primary logo presentation |
| Monochrome dark | White/light | Legal documents, fax, single-color print |
| Monochrome light | Dark/black | Dark mode UI, night banners, reversed print |

## Preparation Tips

- Use CSS classes (`.primary`, `.secondary`, `.accent`) on all fill elements, not inline `fill=` attributes
- Group related elements: icon fills, text fills, background fills
- Test at 16x16px (favicon scale) — monochrome must remain legible
- Avoid using opacity for color differentiation; use distinct class names instead
