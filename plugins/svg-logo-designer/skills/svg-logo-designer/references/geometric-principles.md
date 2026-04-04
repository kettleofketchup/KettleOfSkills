# Geometric Principles for Logo Design

## The Golden Ratio (Phi)

**Value:** 1:1.618 (phi = 1.618033987...)

**Fibonacci sequence:** 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89...
Each number / predecessor approaches phi. Simplified working ratio: 2:3.

## Golden Rectangle in SVG

```xml
<!-- Golden rectangle: width = height * 1.618 -->
<!-- height=61.8, width=100 -->
<svg viewBox="0 0 100 61.8" xmlns="http://www.w3.org/2000/svg">
  <!-- Full golden rectangle -->
  <rect x="0" y="0" width="100" height="61.8" fill="none" stroke="#ccc"/>
  <!-- Internal square (61.8 x 61.8) -->
  <rect x="0" y="0" width="61.8" height="61.8" fill="none" stroke="#999"/>
  <!-- Remaining golden rectangle (38.2 x 61.8) -->
  <rect x="61.8" y="0" width="38.2" height="61.8" fill="none" stroke="#999"/>
  <!-- Circle inscribed in square -->
  <circle cx="30.9" cy="30.9" r="30.9" fill="none" stroke="#2563EB"/>
  <!-- Smaller circle in remaining area -->
  <circle cx="80.9" cy="30.9" r="19.1" fill="none" stroke="#2563EB"/>
</svg>
```

## Fibonacci Circle System

Apple and Twitter logos use circles sized from Fibonacci sequence:

```xml
<!-- Fibonacci circle set (radii scaled from sequence) -->
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="5"  fill="none" stroke="#ccc"/>
  <circle cx="100" cy="100" r="8"  fill="none" stroke="#ccc"/>
  <circle cx="100" cy="100" r="13" fill="none" stroke="#ccc"/>
  <circle cx="100" cy="100" r="21" fill="none" stroke="#ccc"/>
  <circle cx="100" cy="100" r="34" fill="none" stroke="#ccc"/>
  <circle cx="100" cy="100" r="55" fill="none" stroke="#ccc"/>
</svg>
```

Position and intersect circles to form organic curves. Overlapping edges define the logo outline.

## Layout Calculations

Given logo width `W`:
- Primary element: `W * 0.618`
- Secondary element: `W * 0.382`
- Ratio 0.618:0.382 is the golden split

### Typography Scale (phi-based)

| Level | Size |
|-------|------|
| Base | 16px |
| Level 2 | 26px (16 x 1.618) |
| Level 3 | 42px (26 x 1.618) |
| Level 4 | 68px (42 x 1.618) |

### Spacing Scale

| Gap | Size |
|-----|------|
| Small | 8px |
| Medium | 13px (8 x 1.618) |
| Large | 21px (13 x 1.618) |
| XL | 34px (21 x 1.618) |

## Grid-Based Logo Construction

1. **Define canvas** -- golden rectangle bounding box: `viewBox="0 0 162 100"`
2. **Establish grid** -- subdivide with golden ratio cuts horizontally and vertically
3. **Place primary element** -- align to larger subdivision (0.618)
4. **Place secondary element** -- fit within smaller subdivision (0.382)
5. **Use Fibonacci circles** for curved elements
6. **Test at multiple scales** -- verify at 16px, 32px, 64px, 128px, and larger

## Famous Examples

| Brand | Technique |
|-------|-----------|
| Apple | Outline from 7 overlapping Fibonacci circles |
| Twitter (old) | Constructed entirely from golden ratio circles |
| Toyota | Ovals sized using golden ratio grid |
| National Geographic | Yellow rectangle is golden ratio (1:1.618) |
| Pepsi | Circle proportions follow golden ratio |

## Practical Construction Template

```xml
<!-- Logo grid with golden subdivisions -->
<svg viewBox="0 0 162 100" xmlns="http://www.w3.org/2000/svg">
  <!-- Construction grid (remove in final) -->
  <rect width="162" height="100" fill="none" stroke="#eee"/>
  <line x1="100" y1="0" x2="100" y2="100" stroke="#eee"/><!-- golden split -->
  <line x1="0" y1="61.8" x2="162" y2="61.8" stroke="#eee"/><!-- golden split -->

  <!-- Primary element in 0-100 zone -->
  <g id="primary"><!-- main icon --></g>

  <!-- Secondary element in 100-162 zone -->
  <g id="secondary"><!-- accent/text --></g>
</svg>
```
