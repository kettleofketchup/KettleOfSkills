# SVG Best Practices for Logos

## Clean Structure Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"
     role="img" aria-labelledby="logo-title logo-desc">
  <title id="logo-title">Brand Name Logo</title>
  <desc id="logo-desc">Visual description</desc>
  <defs>
    <style>.primary { fill: #2563EB; } .bg { fill: #F8FAFC; }</style>
  </defs>
  <g id="icon"><!-- elements --></g>
  <g id="wordmark"><!-- text --></g>
</svg>
```

## Optimization Rules

1. **Basic shapes over `<path>`** -- `<circle>`, `<rect>`, `<ellipse>`, `<polygon>` are smaller and clearer
2. **Strip editor metadata** -- remove `<metadata>`, Illustrator/Sketch comments, empty `<defs>`/`<g>`
3. **viewBox origin 0,0** with round numbers: `viewBox="0 0 100 100"`
4. **2 decimal places** for coordinates; 4 only for complex curves
5. **CSS classes not inline styles** for repeated colors
6. **`<defs>` + `<use>`** for repeated elements:
   ```xml
   <defs><circle id="dot" r="5"/></defs>
   <use href="#dot" x="20" y="50" fill="#2563EB"/>
   <use href="#dot" x="50" y="50" fill="#2563EB"/>
   ```
7. **Omit `px` units** -- SVG coords are unitless by default
8. **Target 5-30KB** file size for optimized logos
9. **Never omit `viewBox`** -- without it SVG cannot scale responsively
10. **Keep `preserveAspectRatio="xMidYMid meet"`** (the default) to prevent distortion

## Typography in SVG

### `<text>` vs Paths

| Use `<text>` | Convert to paths |
|--------------|-----------------|
| Font available via web fonts | Logo must look identical everywhere |
| SEO/accessibility matters | Font not used elsewhere on page |
| Small file size needed | Zero font dependencies required |

### `<text>` Best Practices

```xml
<text font-family="'Inter', 'Helvetica Neue', Arial, sans-serif"
      font-weight="700" font-size="32" fill="#1A1A2E"
      text-anchor="middle" x="100" y="40"
      letter-spacing="0.05em">BRAND</text>
```

- Use `em` for `letter-spacing` so it scales with font-size
- `text-anchor`: `start` (left), `middle` (center), `end` (right)
- `textLength` + `lengthAdjust` to force text to fit a specific width
- Monospace stack: `'JetBrains Mono', 'SF Mono', 'Fira Code', 'Consolas', monospace`

### Accessibility for Path-Converted Text

```xml
<svg role="img" aria-labelledby="logo-title">
  <title id="logo-title">Company Name</title>
  <path d="M..."/><!-- outlined text -->
</svg>
```

## Anti-Patterns to Avoid

### Rendering
- **Sub-pixel blur**: fractional coords cause anti-aliasing blur. Round to integers for even strokes
- **CSS transforms on SVG**: `transform: scale()` causes rasterization. Change width/height instead
- **Missing namespace**: programmatic SVG needs `http://www.w3.org/2000/svg`

### Design
- **Overly complex shapes**: must read at 16x16px through billboard scale
- **Gradient dependency**: fails in monochrome. Always design single-color fallback
- **Too many colors**: >3 reduces memorability. Stick to 2-3 max
- **No clear space**: define minimum padding as proportion of logo height

### Code
- **Editor bloat**: empty `<defs>`, redundant `<g>`, default attribute values
- **Inline styles**: use `<style>` block with CSS classes instead
- **`<path>` for everything**: use `<circle>`, `<rect>`, `<polygon>` for basic shapes
- **All text to outlines**: 4KB SVG can balloon to 260KB. Only convert when needed
- **Deprecated `<font>`/`<glyph>`**: not supported in modern browsers

### Browser
- **Safari subpixel**: SVGs at non-integer pixel values blur. Test at common sizes
- **Inconsistent anti-aliasing**: test Chrome, Firefox, Safari. Use `shape-rendering: crispEdges` for pixel-precise elements (makes diagonals jagged)

## Color Management

```xml
<!-- Define once, reuse throughout -->
<defs>
  <style>
    .primary { fill: #4F46E5; }
    .secondary { fill: #10B981; }
    .text-color { fill: #1F2937; }
    .light { fill: #FFFFFF; }
  </style>
</defs>
```

For monochrome variations, create separate SVGs with single-color classes.
