---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/create-your-site/
  - https://zensical.org/docs/setup/basics/
  - https://zensical.org/docs/setup/extensions/
---

# Project Configuration

## Bootstrap

```bash
zensical new .
```

Generates:
```
.
├─ .github/
├─ docs/
│  ├─ index.md
│  └─ markdown.md
└─ zensical.toml
```

## zensical.toml

All settings live under `[project]`. TOML chosen over YAML to avoid indentation errors and type ambiguity.

```toml
[project]
site_name = "My site"           # required
site_url = "https://example.com" # recommended (needed for instant nav, sitemap)
site_description = "Project docs"
site_author = "Jane Doe"
copyright = "&copy; 2025 Jane Doe"
docs_dir = "docs"               # default
site_dir = "site"               # default
use_directory_urls = true       # default (usage.md -> /usage/)
dev_addr = "localhost:8000"     # default
```

## Theme Variants

```toml
[project.theme]
variant = "modern"  # default, new design
# variant = "classic"  # matches Material for MkDocs
```

## Extra Key-Value Pairs

```toml
[project.extra]
key = "value"
generator = false  # hide "Made with Zensical" footer
```

## Extensions

19 markdown extensions supported. Common extensions enabled by default if no extensions configured.

Default includes: abbr, admonition, attr_list, def_list, footnotes, md_in_html, toc, pymdownx.arithmatex (generic), pymdownx.emoji (twemoji), pymdownx.tabbed (alternate), pymdownx.tasklist (custom checkboxes), pymdownx.highlight, pymdownx.superfences, pymdownx.details, pymdownx.caret, pymdownx.mark, pymdownx.tilde, pymdownx.keys, pymdownx.snippets.

To reset to bare MkDocs defaults:

```toml
[project]
markdown_extensions = {}
```

To configure a specific extension:

```toml
[project.markdown_extensions.pymdownx.highlight]
anchor_linenums = true
line_spans = "__span"
pygments_lang_class = true
```

## Unsupported mkdocs.yml Settings

Not yet available: `remote_branch`, `remote_name`, `exclude_docs`, `draft_docs`, `not_in_nav`, `validation`, `strict`, `hooks`, `watch`.

`docs_dir` cannot be set to `.` (root) — use a subdirectory.
