---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/authoring/images/
  - https://zensical.org/docs/authoring/icons-emojis/
  - https://zensical.org/docs/authoring/diagrams/
  - https://zensical.org/docs/authoring/math/
---

# Images

Extensions: `attr_list`, `md_in_html`, `pymdownx.blocks.caption`.

## Alignment

```markdown
![Image](url){ align=left }
![Image](url){ align=right }
```

No centered alignment via `align` attribute. On mobile, images stretch to full width.

## Captions

HTML approach:
```html
<figure markdown>
  ![Image](url)
  <figcaption>Caption text</figcaption>
</figure>
```

Caption extension:
```markdown
![Image](url)
/// caption
Caption text
///
```

## Lazy Loading

```markdown
![Image](url){ loading=lazy }
```

## Light/Dark Mode

```markdown
![Light only](url#only-light)
![Dark only](url#only-dark)
```

---

# Icons & Emojis

Extensions: `attr_list`, `pymdownx.emoji` (with Twemoji settings).

10,000+ icons from 5 bundled sets: **Lucide** (lucide.dev), **Material Design** (Pictogrammers), **FontAwesome** (free), **Octicons** (GitHub), **Simple Icons** (brands).

## Emojis

```markdown
:smile:  :rocket:  :thumbsup:
```

## Icons

```markdown
:fontawesome-regular-face-laugh-wink:
:lucide-braces:
:material-account-circle:
:octicons-heart-fill-24:
:simple-python:
```

## Styled Icons

```markdown
:fontawesome-brands-youtube:{ .youtube }
```

CSS: `.youtube { color: #EE0F0F; }` (add via `extra_css`).

## Custom Icons

Place SVGs in `overrides/.icons/`, reference as `:custom-icon-name:`.

---

# Diagrams (Mermaid)

Extension: `pymdownx.superfences` with mermaid custom fence.

Officially supported types: flowcharts, sequence diagrams, state diagrams, class diagrams, entity-relationship diagrams. Other types (pie, gantt, user journey, git graph) work but aren't mobile-optimized.

````markdown
```mermaid
graph LR
  A[Start] --> B{Decision}
  B -->|Yes| C[Result]
  B -->|No| D[Other]
```
````

Mermaid auto-uses configured fonts/colors, works with instant navigation, supports light/dark schemes. Extend via `extra_javascript` (e.g., ELK layouts).

---

# Math

Extension: `pymdownx.arithmatex` with `generic: true`.

Choose MathJax or KaTeX (add via `extra_javascript`).

**Block:** `$$ \cos x = \sum_{k=0}^{\infty} ... $$`

**Inline:** `The function $f(x) = x^2$`

| | KaTeX | MathJax |
|---|---|---|
| Speed | Faster | Slower |
| Syntax | LaTeX subset | LaTeX + AsciiMath + MathML |
| Accessibility | Limited | Better (MathML) |
