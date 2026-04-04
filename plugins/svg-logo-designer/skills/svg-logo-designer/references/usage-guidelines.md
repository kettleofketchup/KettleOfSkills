# Logo Usage Guidelines Template

Provide this documentation with every logo delivery. Customize per project.

## File Formats

### SVG (Primary)
- Use for: websites, digital apps, large prints
- Benefits: infinitely scalable, small file size, editable
- Embed directly in HTML or open in design tools (Figma, Illustrator, Inkscape)

### Exporting to PNG

```bash
# Inkscape (free, cross-platform)
inkscape logo.svg --export-png=logo.png --export-width=1000

# ImageMagick
convert -background none logo.svg logo.png

# Specific sizes
inkscape logo.svg --export-png=logo-64.png --export-width=64    # favicon
inkscape logo.svg --export-png=logo-512.png --export-width=512  # social
inkscape logo.svg --export-png=logo-1024.png --export-width=1024 # print
```

## Clear Space

Minimum padding around logo = height of logo symbol.
No text, graphics, or visual clutter in clear space zone.

## Minimum Sizes

| Context | Minimum |
|---------|---------|
| Digital | 100px width |
| Print | 1 inch width |
| Favicon | 16x16 or 32x32 |

## Color Usage by Context

### Website Headers
- Full color preferred
- Ensure 4.5:1 contrast with background (WCAG AA)

### Social Media
- Use square/icon layout
- Provide solid background color if needed

### Print
- Full color for color printing
- Monochrome dark for B&W
- Consider spot color for cost-effective printing

### Dark Backgrounds
- Use monochrome light (white) version
- Or reversed full-color version with light fills

## Web Implementation

```html
<!-- Inline SVG (recommended for control + performance) -->
<div class="logo">
  <svg><!-- paste SVG code --></svg>
</div>

<!-- Image tag (simpler) -->
<img src="logo.svg" alt="Company Name Logo" width="200" height="60"/>

<!-- CSS background -->
<style>
.logo {
  background-image: url('logo.svg');
  background-size: contain;
  background-repeat: no-repeat;
  width: 200px;
  height: 60px;
}
</style>
```

### Responsive

```css
.logo {
  width: 100%;
  max-width: 200px;
  height: auto;
}
@media (max-width: 768px) {
  .logo { max-width: 120px; }
}
```

## File Organization

```
logos/
  {brand}-concept1-horizontal.svg
  {brand}-concept1-vertical.svg
  {brand}-concept1-icon.svg
  {brand}-concept1-monochrome-dark.svg
  {brand}-concept1-monochrome-light.svg
  {brand}-concept2-horizontal.svg
  {brand}-concept2-vertical.svg
  {brand}-concept2-icon.svg
  ...
```

## Incorrect Usage

Do NOT:
- Stretch or distort (always preserve aspect ratio)
- Change colors outside approved palette
- Add shadows, glows, or effects
- Rotate or skew
- Place on busy backgrounds without clear space
- Modify or recreate logo elements
- Use low-resolution raster versions when SVG is available
