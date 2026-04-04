---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/authoring/formatting/
  - https://zensical.org/docs/authoring/buttons/
---

# Text Formatting

Extensions: `pymdownx.caret`, `pymdownx.keys`, `pymdownx.mark`, `pymdownx.tilde`.

## Highlighting

| Syntax | Result | Extension |
|--------|--------|-----------|
| `==marked text==` | Highlighted/marked | pymdownx.mark |
| `^^inserted text^^` | Underlined/inserted | pymdownx.caret |
| `~~deleted text~~` | Strikethrough | pymdownx.tilde |

## Sub/Superscript

```markdown
H~2~O          → H₂O (subscript)
A^T^A          → AᵀA (superscript)
```

## Keyboard Keys

Extension: `pymdownx.keys`

```markdown
++ctrl+alt+del++    → Ctrl+Alt+Del
++cmd+shift+p++     → Cmd+Shift+P
```

See Python Markdown Extensions docs for full key shortcode list.

---

# Buttons

Extension: `attr_list`

## Standard Button (outlined)

```markdown
[Subscribe to newsletter](#){ .md-button }
```

## Primary Button (filled)

```markdown
[Get started](#){ .md-button .md-button--primary }
```

## Button with Icon

```markdown
[Send :fontawesome-solid-paper-plane:](#){ .md-button }
```

Buttons work on any link, label, or button element.

---

# Linting

Zensical does not ship a built-in linter. Recommended approach:

- Use [markdownlint](https://github.com/DavidAnson/markdownlint) for Markdown style/syntax checks
- Configure `.markdownlint.yml` to allow Zensical-specific syntax (admonitions, tabs, attrs)
- Run `zensical build --clean` as a validation step — build failures catch broken references and config errors
- Add linting to CI pipeline before the build step

```yaml
# .markdownlint.yml example for Zensical projects
MD033: false   # allow inline HTML (grids, md_in_html)
MD046: false   # allow different code block styles (fenced + indented)
```
