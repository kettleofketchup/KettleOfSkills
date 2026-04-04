---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/authoring/frontmatter/
  - https://zensical.org/docs/setup/tags/
  - https://zensical.org/docs/authoring/data-tables/
  - https://zensical.org/docs/authoring/lists/
  - https://zensical.org/docs/authoring/footnotes/
  - https://zensical.org/docs/authoring/tooltips/
---

# Front Matter

YAML metadata at top of Markdown files:

```yaml
---
title: Page Title
description: Meta description for SEO
icon: lucide/braces
status: new            # or: deprecated (custom statuses via config)
template: custom.html  # custom Jinja template
hide:
  - navigation
  - toc
  - path
  - footer
  - tags
search:
  exclude: true        # exclude from search index
tags:
  - HTML5
  - JavaScript
---
```

Page title priority: nav config > front matter `title` > first `# heading` > filename.

Custom metadata accessible in templates via `page.meta`.

---

# Tags

Built-in tagging via front matter. Tag identifiers map to icons:

```toml
[project.extra.tags]
Compatibility = "compat"

[project.theme.icon.tag]
default = "lucide/hash"
html = "fontawesome/brands/html5"
```

Tag listing pages not yet supported (in development).

---

# Data Tables

Extension: `tables`

```markdown
| Left | Center | Right |
| :--- | :----: | ----: |
| L    |   C    |     R |
```

Sortable tables via tablesort JS library:

```toml
[project]
extra_javascript = [
  "https://unpkg.com/tablesort@5.3.0/dist/tablesort.min.js",
  "javascripts/tablesort.js",
]
```

```javascript
// docs/javascripts/tablesort.js
document$.subscribe(function() {
  var tables = document.querySelectorAll("article table:not([class])")
  tables.forEach(function(table) { new Tablesort(table) })
})
```

---

# Lists

Extensions: `def_list`, `pymdownx.tasklist` (with `custom_checkbox: true`).

**Definition list:**
```markdown
`Term`
:   Definition text with full Markdown support.
```

**Task list:**
```markdown
- [x] Completed
- [ ] Incomplete
    * [x] Nested completed
```

---

# Footnotes

Extension: `footnotes`. Feature: `content.footnote.tooltips` (hover preview).

```markdown
Text with footnote[^1] reference.

[^1]: Footnote content here.

[^2]:
    Multi-paragraph footnote
    indented by four spaces.
```

---

# Tooltips

Extensions: `abbr`, `attr_list`, `pymdownx.snippets`. Feature: `content.tooltips`.

**Link tooltip:** `[text](url "tooltip text")`

**Icon tooltip:** `:icon:{ title="tooltip text" }`

**Abbreviation:** `*[ACRONYM]: Full Definition`

**Site-wide glossary:** store abbreviations in `includes/abbreviations.md`, auto-append via snippets config.
