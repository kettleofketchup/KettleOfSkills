---
name: svg-logo-designer
description: "Create professional SVG logos from descriptions and design specifications. Generates multiple logo variations with different layouts, styles, and concepts. Produces scalable vector graphics that can be used directly or exported to PNG. This skill should be used when users ask to create logos, brand identities, icons, visual marks, wordmarks, lettermarks, abstract marks, combination marks, or emblems for their designs."
---

# SVG Logo Designer

Create professional, scalable SVG logos from design specifications with multiple variations and layout options.

## When to Use

Activate when the user requests:
- Logo creation from a description or spec
- Brand identity or visual mark design
- Logo variations and concepts (wordmark, lettermark, pictorial, abstract, combination, emblem)
- Icons, symbols, or scalable graphics for branding
- Logo export in different layouts and styles

## Workflow

### Phase 1: Requirements Gathering

Collect before designing (ask 2-3 focused questions, not all at once):

1. **Brand info** -- name, industry, target audience, personality (modern/classic/playful/serious)
2. **Logo type** -- wordmark, lettermark, pictorial, abstract, combination mark, or emblem
3. **Style** -- minimalist, geometric, organic, bold, elegant, tech/modern, vintage/retro
4. **Colors** -- specific palette or let designer choose (see `references/color-palettes.md`)
5. **Usage context** -- website, print, merchandise, favicon, app icon
6. **Variations** -- recommend 3 concepts with horizontal, vertical, and icon-only layouts each

### Phase 2: Design Concepts

For each concept, apply these principles:
- Use golden ratio and geometric grids (see `references/geometric-principles.md`)
- Choose visual metaphors related to brand
- Exploit negative space opportunities
- Balance simplicity with distinctiveness
- Limit to 2-3 colors maximum

Reference `references/design-patterns.md` for SVG templates of each logo type.

### Phase 3: SVG Generation

Follow `references/svg-best-practices.md` for:
- Clean, semantic SVG structure with `viewBox` (never omit)
- CSS classes in `<style>` for color management (not inline styles)
- `<defs>` with `<use>` for repeated elements
- Accessibility: `role="img"`, `<title>`, `<desc>`, `aria-labelledby`
- Path precision: 2 decimal places (4 for complex curves)
- Basic shapes (`<circle>`, `<rect>`, `<polygon>`) over `<path>` when possible

Reference `references/svg-path-techniques.md` for advanced path construction.

#### SVG Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60"
     role="img" aria-labelledby="logo-title logo-desc">
  <title id="logo-title">Brand Name Logo</title>
  <desc id="logo-desc">Description of logo appearance</desc>
  <defs>
    <style>
      .primary { fill: #4F46E5; }
      .secondary { fill: #10B981; }
      .text { fill: #1F2937; }
    </style>
  </defs>
  <g id="icon"><!-- Symbol elements --></g>
  <g id="wordmark"><!-- Text elements --></g>
</svg>
```

### Phase 4: Layout Variations

Generate per concept:

| Layout | Aspect | Best For |
|--------|--------|----------|
| Horizontal | Wide | Website headers, business cards |
| Vertical | Tall | Social media profiles, app icons |
| Icon only | 1:1 | Favicon, small spaces, watermarks |

Color variations per layout: full color, monochrome dark, monochrome light (reversed).

### Phase 5: File Output

Save SVGs using the Write tool with naming convention:
```
logos/
  {brand}-concept1-horizontal.svg
  {brand}-concept1-vertical.svg
  {brand}-concept1-icon.svg
  {brand}-concept1-monochrome-dark.svg
  {brand}-concept1-monochrome-light.svg
  {brand}-concept2-horizontal.svg
  ...
```

### Phase 6: Usage Guidelines

After delivering logos, provide usage guidelines based on `references/usage-guidelines.md`:
- Clear space rules, minimum sizes
- Color usage by context (web, print, social)
- Export instructions (SVG to PNG via Inkscape/ImageMagick)
- Web implementation examples (inline SVG, `<img>`, CSS background)
- Dos and don'ts

### Phase 7: Iteration

Present concepts, then:
1. Gather feedback -- which concept resonates, what to keep/change
2. Refine selected concept -- adjust colors, proportions, details
3. Finalize all variations and deliver complete package

## Key Design Principles

- **Simple** -- works at 16x16px (favicon) through billboard scale
- **Memorable** -- unique, recognizable at a glance
- **Timeless** -- avoid trends that date quickly
- **Versatile** -- works in color, monochrome, on any background
- **Appropriate** -- matches brand personality and industry

## References

| File | Content |
|------|---------|
| `references/color-palettes.md` | Color psychology, industry palettes, WCAG accessibility, brand colors |
| `references/svg-path-techniques.md` | Path commands, bezier curves, arc commands, shape patterns |
| `references/svg-best-practices.md` | Optimization, anti-patterns, typography in SVG |
| `references/geometric-principles.md` | Golden ratio, Fibonacci circles, grid-based construction |
| `references/design-patterns.md` | SVG code templates for each logo type |
| `references/usage-guidelines.md` | Logo usage documentation template, export and web implementation |
