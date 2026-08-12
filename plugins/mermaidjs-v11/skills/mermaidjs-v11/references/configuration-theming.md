# Mermaid.js Theming & Accessibility

Themes, theme variables, accessibility, icon packs, and math rendering.

## Theming

**Built-in Themes:**
- `default` - Standard colors
- `dark` - Dark background
- `forest` - Green tones
- `neutral` - Grayscale
- `base` - Fully customizable

**Theme Variables (base theme only):**
```javascript
mermaid.initialize({
  theme: 'base',
  themeVariables: {
    primaryColor: '#ff0000',
    primaryTextColor: '#fff',
    primaryBorderColor: '#7C0000',
    secondaryColor: '#006100',
    tertiaryColor: '#fff'
  }
});
```

**Customizable Variables:**
- Color families: primary, secondary, tertiary
- Node backgrounds and text colors
- Border and line colors
- Note background/text
- Diagram-specific (flowchart nodes, sequence actors, pie sections)

**Custom CSS:**
```javascript
mermaid.initialize({
  themeCSS: `
    .node rect { fill: #f9f; }
    .edgeLabel { background-color: white; }
  `
});
```

## Accessibility

**ARIA Support:**
```
accTitle: Diagram Title
accDescr: Brief description
accDescr {
  Multi-line detailed
  description
}
```

**Auto-generated:**
- `aria-roledescription` attributes
- `title` and `desc` SVG elements
- `aria-labelledby` and `aria-describedby`

**WCAG Compliance:**
Available for all diagram types (flowchart, sequence, class, Gantt, etc.)

## Icon Configuration

**Register Icon Packs:**
```javascript
import { registerIconPacks } from 'mermaid';
registerIconPacks([
  {
    name: 'logos',
    loader: () => import('https://esm.run/@iconify-json/logos')
  }
]);
```

**Usage:**
```
architecture-beta
  service api(logos:nodejs)[API]
```

**Loading Methods:**
1. CDN-based (lazy loading)
2. npm with dynamic import
3. Direct import

## Math Rendering

**KaTeX Support:**
```
graph LR
  A["$$f(x) = x^2$$"] --> B
```

**Configuration:**
- `legacyMathML`: Use old MathML rendering
- `forceLegacyMathML`: Force legacy even if browser supports native
