---
last_updated: 2026-03-25
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/setup/basics/
  - https://zensical.org/docs/upgrade/
  - https://zensical.org/docs/get-started/
  - https://zensical.org/docs/setup/extensions/
  - https://zensical.org/docs/customization/
---

# Migration from mkdocs-material

Zensical is the successor to Material for MkDocs, created by the same team. It supports both `zensical.toml` (TOML, recommended) and legacy `mkdocs.yml` (YAML) configuration.

## Config Conversion: mkdocs.yml to zensical.toml

### Basic Structure

All settings move under `[project]`:

**mkdocs.yml:**
```yaml
site_name: My Site
site_url: https://example.com
site_description: Project docs
edit_uri: edit/main/docs/
theme:
  name: material
  features:
    - navigation.instant
    - navigation.tabs
  palette:
    scheme: default
    primary: indigo
```

**zensical.toml:**
```toml
[project]
site_name = "My Site"
site_url = "https://example.com"
site_description = "Project docs"
edit_uri = "edit/main/docs/"

[project.theme]
features = ["navigation.instant", "navigation.tabs"]

[project.theme.palette]
scheme = "default"
primary = "indigo"
```

### Extensions

**mkdocs.yml:**
```yaml
markdown_extensions:
  - admonition
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
```

**zensical.toml:**
```toml
[project.markdown_extensions.admonition]
[project.markdown_extensions.pymdownx.highlight]
anchor_linenums = true
[project.markdown_extensions.pymdownx.superfences]
```

If no extensions defined, Zensical auto-enables common defaults.

### Nav, Extra/Social, Custom CSS/JS

**mkdocs.yml:**
```yaml
nav:
  - Home: index.md
  - About:
    - about/index.md
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/org
extra_css:
  - stylesheets/extra.css
extra_javascript:
  - javascripts/extra.js
```

**zensical.toml:**
```toml
[project]
nav = [
  {"Home" = "index.md"},
  {"About" = ["about/index.md"]}
]
extra_css = ["stylesheets/extra.css"]
extra_javascript = ["javascripts/extra.js"]

[[project.extra.social]]
icon = "fontawesome/brands/github"
link = "https://github.com/org"
```

### Theme Overrides

**mkdocs.yml:**
```yaml
theme:
  name: material
  custom_dir: overrides
```

**zensical.toml:**
```toml
[project.theme]
custom_dir = "overrides"
```

Override blocks and partials work the same way. `overrides/main.html` extends `base.html`.

### Analytics & Consent

**mkdocs.yml:**
```yaml
extra:
  analytics:
    provider: google
    property: G-XXXXXXXXXX
  consent:
    title: Cookie consent
    description: We use cookies...
```

**zensical.toml:**
```toml
[project.extra.analytics]
provider = "google"
property = "G-XXXXXXXXXX"

[project.extra.consent]
title = "Cookie consent"
description = "We use cookies..."
```

### Plugin Migration

| mkdocs-material plugin | Zensical equivalent |
|------------------------|---------------------|
| `search` | Built-in (no config needed) |
| `tags` | `[project.extra.tags]` config |
| `mkdocs-include-markdown` | `pymdownx.snippets` extension (`--8<-- "file.md"`) |
| `mkdocs-macros` | No direct substitute (module system in development) |
| `mkdocstrings` | `[project.plugins.mkdocstrings]` (preliminary support) |
| `social` (social cards) | Under development |
| `blog` | Not yet available |

See [plugins/content-reuse.md](plugins/content-reuse.md) for Snippets details.

## Key Differences

| mkdocs-material | Zensical |
|-----------------|----------|
| `mkdocs.yml` (YAML) | `zensical.toml` (TOML) or legacy YAML |
| `theme: name: material` | Theme built-in, no `name` needed |
| `mkdocs serve` / `build` / `new` | `zensical serve` / `build` / `new` |
| `mkdocs gh-deploy` | GitHub Actions workflow (no built-in deploy command) |
| Explicit extension config required | Common extensions auto-enabled |
| `material/` icon prefix default | `lucide/` default (all sets available) |
| pip/pipx install | pip, uv, or Docker |

## Theme Variants

Use `variant = "classic"` to match Material for MkDocs appearance during migration. Switch to `variant = "modern"` (default) when ready.

## Feature Parity Status

Most features supported. Not yet available:
- Social cards (under development)
- Tag listing pages (under development)
- Blog plugin
- `strict` mode, `hooks`, `watch`, `validation` settings
- `mkdocs gh-deploy` command (use CI/CD workflows instead)

## Publishing Changes

Replace in CI workflows:
- `pip install mkdocs-material` → `pip install zensical`
- `mkdocs build` → `zensical build --clean`
- `mkdocs gh-deploy` → Use GitHub Actions deploy workflow (see [setup/publishing.md](setup/publishing.md))
