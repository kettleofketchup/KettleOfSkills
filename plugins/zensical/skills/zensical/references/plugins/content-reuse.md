---
last_updated: 2026-03-25
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/authoring/tooltips/
  - https://zensical.org/docs/setup/extensions/
migrates_from:
  - mkdocs-include-markdown-plugin
  - mkdocs-macros-plugin
---

# Content Reuse

## Snippets (pymdownx.snippets) — Include-Markdown Substitute

The `pymdownx.snippets` extension is Zensical's built-in mechanism for content reuse across pages. It replaces the `mkdocs-include-markdown` plugin from mkdocs-material projects.

### Include External Files

Embed content from another file inline using the scissors syntax:

```markdown
--8<-- "path/to/file.md"
```

Partial file inclusion (specific lines):

```markdown
--8<-- "path/to/file.md:3:10"
```

### Auto-Append (Site-Wide Includes)

Automatically append a file to every page — useful for shared glossaries, abbreviations, or footer content:

```toml
[project.markdown_extensions.pymdownx.snippets]
auto_append = ["includes/abbreviations.md"]
```

```yaml
# mkdocs.yml equivalent
markdown_extensions:
  - pymdownx.snippets:
      auto_append:
        - includes/abbreviations.md
```

### Practical Pattern: Site-Wide Glossary

1. Create `includes/abbreviations.md` (outside `docs/` to avoid build warnings):

```markdown
*[HTML]: Hyper Text Markup Language
*[CSS]: Cascading Style Sheets
*[API]: Application Programming Interface
```

2. Configure auto-append in `zensical.toml`:

```toml
[project.markdown_extensions.abbr]
[project.markdown_extensions.pymdownx.snippets]
auto_append = ["includes/abbreviations.md"]
```

3. All abbreviations become tooltips site-wide automatically.

### Migration from mkdocs-include-markdown

| mkdocs-include-markdown | Zensical (Snippets) |
|------------------------|---------------------|
| `{% include "file.md" %}` | `--8<-- "file.md"` |
| `{% include-markdown "file.md" %}` | `--8<-- "file.md"` |
| `start` / `end` markers | Line range: `"file.md:3:10"` |
| Plugin in `plugins:` | Extension in `markdown_extensions:` |

## Macros Plugin — No Direct Substitute

`mkdocs-macros-plugin` (Jinja2 template variables and macros in Markdown) has **no direct Zensical equivalent**. Zensical is developing a "comprehensive module system" but it is not yet available.

### Workarounds

- **Static values:** Use Snippets to include shared content fragments
- **Dynamic values:** Use `[project.extra]` key-value pairs, accessible in Jinja theme templates (but not in Markdown content directly)
- **Conditional content:** Use theme overrides with Jinja2 logic in `overrides/` templates
- **Build-time generation:** Pre-process Markdown files with a script before `zensical build`

### Extra Variables in Templates

```toml
[project.extra]
version = "2.0.0"
api_base = "https://api.example.com"
```

Accessible in theme templates as `{{ config.extra.version }}` but **not** in Markdown content.
