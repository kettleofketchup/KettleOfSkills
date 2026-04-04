---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/setup/navigation/
  - https://zensical.org/docs/setup/search/
---

# Navigation & Site Search

## Navigation Structure

Explicit nav in `zensical.toml`:

```toml
[project]
nav = [
  {"Home" = "index.md"},
  {"About" = [
    "about/index.md",
    "about/vision.md"
  ]},
  {"GitHub" = "https://github.com/org/repo"}
]
```

## Navigation Feature Flags

All set via `[project.theme] features`:

```toml
[project.theme]
features = [
  "navigation.instant",           # SPA-like XHR navigation (requires site_url)
  "navigation.instant.prefetch",  # prefetch on hover
  "navigation.instant.progress",  # loading progress bar
  "navigation.tracking",          # URL updates with active anchor
  "navigation.tabs",              # top-level sections as tabs (>1220px)
  "navigation.tabs.sticky",       # tabs stick on scroll
  "navigation.sections",          # top-level as sidebar groups
  "navigation.expand",            # auto-expand collapsible sections
  "navigation.path",              # breadcrumbs above title
  "navigation.prune",             # reduce HTML ~33% (incompatible with expand)
  "navigation.indexes",           # section index pages (incompatible with toc.integrate)
  "navigation.top",               # back-to-top button
  "navigation.footer",            # prev/next page links in footer
  "toc.follow",                   # sidebar scrolls to active anchor
  "toc.integrate",                # TOC in sidebar (incompatible with indexes)
]
```

**Important:** `site_url` must be set for instant navigation (relies on sitemap.xml).

## Per-Page Overrides (front matter)

```yaml
---
hide:
  - navigation
  - toc
  - path
  - footer
---
```

## Site Search

Built-in client-side search, enabled by default. No third-party service needed. Works offline.

### Search Highlighting

```toml
[project.theme]
features = ["search.highlight"]
```

Highlights all matching occurrences after clicking a search result.

### Exclude from Search

**Entire page:**
```yaml
---
search:
  exclude: true
---
```

**Specific section** (requires attr_list extension):
```markdown
## Section Title { data-search-exclude }
```

**Inline block:**
```markdown
Content to exclude
{ data-search-exclude }
```

### Limitations

- Search UI currently English-only (multilingual content works, UI not localized)
- Search engine planned as standalone open-source project in 2026
