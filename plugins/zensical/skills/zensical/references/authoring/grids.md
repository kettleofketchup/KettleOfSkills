---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_url: https://zensical.org/docs/authoring/grids/
---

# Grids

Arrange content in responsive grid layouts. Extensions: `attr_list`, `md_in_html`.

## Card Grids (list syntax)

Wrap an unordered list in a `grid cards` div:

```html
<div class="grid cards" markdown>

- :fontawesome-brands-html5: __HTML__ for content and structure
- :fontawesome-brands-js: __JavaScript__ for interactivity
- :fontawesome-brands-css3: __CSS__ for text running out of boxes
- :fontawesome-brands-python: __Python__ for backend logic

</div>
```

Each list item becomes a card with hover effects.

## Card Grids (block syntax)

Add `.card` class to individual blocks:

```html
<div class="grid" markdown>

:fontawesome-brands-html5: __HTML__ for content and structure
{ .card }

:fontawesome-brands-js: __JavaScript__ for interactivity
{ .card }

</div>
```

## Generic Grids

Arrange arbitrary block elements (admonitions, code blocks, tabs) in a grid:

```html
<div class="grid" markdown>

!!! note "Left column"
    First admonition.

!!! tip "Right column"
    Second admonition.

</div>
```

Works with code blocks, content tabs, and any other block elements.

## Responsive Behavior

- Items stretch to full viewport width on mobile
- 2-3+ columns on wider viewports
- Automatic column sizing based on container width
