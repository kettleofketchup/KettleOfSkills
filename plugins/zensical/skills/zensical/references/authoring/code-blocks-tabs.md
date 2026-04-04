---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/authoring/code-blocks/
  - https://zensical.org/docs/authoring/content-tabs/
---

# Code Blocks

Extensions: `pymdownx.highlight`, `pymdownx.inlinehilite`, `pymdownx.snippets`, `pymdownx.superfences`.

## Configuration

```toml
[project.markdown_extensions.pymdownx.highlight]
anchor_linenums = true
line_spans = "__span"
pygments_lang_class = true
```

## Theme Features

```toml
[project.theme]
features = [
  "content.code.copy",      # copy-to-clipboard button
  "content.code.select",    # line selection button
  "content.code.annotate",  # numeric annotation markers
]
```

## Syntax

**Basic:** ` ```py `

**Title:** ` ```py title="filename.py" `

**Line numbers:** ` ```py linenums="1" `

**Highlight lines:** ` ```py hl_lines="2 3" ` or ` ```py hl_lines="3-5" `

**Inline highlighting:** `` `#!python range()` ``

**External file embed:** ` --8<-- "path/to/file" ` (via Snippets extension)

## Annotations

Place `# (1)!` markers in code comments, define content below:

````markdown
```py
def hello(): # (1)!
    pass
```

1. This annotation explains the function.
````

Per-block copy/no-copy: add `{ .copy }` or `{ .no-copy }` attribute.

## Custom Syntax Colors

Override via CSS: `--md-code-hl-string-color`, `--md-code-hl-keyword-color`, `--md-code-hl-comment-color`, `--md-code-hl-function-color`, `--md-code-hl-operator-color`, etc.

---

# Content Tabs

Extensions: `pymdownx.superfences`, `pymdownx.tabbed` with `alternate_style: true`.

## Configuration

```toml
[project.markdown_extensions.pymdownx.tabbed]
alternate_style = true

[project.theme]
features = ["content.tabs.link"]  # sync matching tab labels site-wide
```

## Syntax

```markdown
=== "Python"
    ```python
    print("hello")
    ```

=== "JavaScript"
    ```javascript
    console.log("hello")
    ```
```

## Features

- Each tab gets an anchor link for sharing
- `content.tabs.link` syncs same-label tabs across pages (persists across loads)
- Tabs support nested content: admonitions, blockquotes, other tabs (via SuperFences)
- Multiple code blocks in one tab trigger horizontal spacing; single code block renders flush
