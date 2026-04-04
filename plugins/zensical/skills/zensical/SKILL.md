---
name: zensical
last_updated: 2026-03-25
version: "0.0.x (alpha)"
description: "Zensical modern static site generator for project documentation (successor to Material for MkDocs). This skill should be used when creating or editing Zensical documentation sites, writing zensical.toml configuration, authoring Markdown with Zensical extensions (admonitions, code blocks, content tabs, grids, diagrams, math), migrating from mkdocs-material to Zensical, setting up Docker or uv development workflows, configuring live preview with zensical serve, building production Docker images, publishing to GitHub Pages or GitLab Pages, configuring site search, navigation features, theming (colors/fonts/logo), customizing Zensical sites with CSS/JS overrides, using Snippets for content reuse (include-markdown substitute), or generating API docs with mkdocstrings."
---

# Zensical Documentation

Modern static site generator by the makers of Material for MkDocs. Written in Rust and Python, published as a Python package. Uses `zensical.toml` (TOML) for configuration instead of `mkdocs.yml` (YAML), though legacy YAML is supported for migration.

## Setup

| Topic | Reference |
|-------|-----------|
| Installation (pip, uv, Docker) | [installation.md](references/setup/installation.md) |
| Project config (`zensical.toml`, extensions) | [project-config.md](references/setup/project-config.md) |
| Dev workflow (serve, build, CLI) | [dev-workflow.md](references/setup/dev-workflow.md) |
| Publishing (GitHub/GitLab Pages) | [publishing.md](references/setup/publishing.md) |
| Navigation & site search | [navigation-search.md](references/setup/navigation-search.md) |
| Theming & customization | [theming.md](references/setup/theming.md) |

For CI/CD pipeline details, reference the `/github` or `/gitlab-ci` skills.

## Authoring

| Topic | Reference |
|-------|-----------|
| Admonitions (callouts) | [admonitions.md](references/authoring/admonitions.md) |
| Code blocks & content tabs | [code-blocks-tabs.md](references/authoring/code-blocks-tabs.md) |
| Grids (card & generic) | [grids.md](references/authoring/grids.md) |
| Text formatting & buttons | [formatting-text.md](references/authoring/formatting-text.md) |
| Images, icons, diagrams, math | [media-diagrams.md](references/authoring/media-diagrams.md) |
| Front matter, tags, tables, lists, footnotes, tooltips | [metadata-elements.md](references/authoring/metadata-elements.md) |

## Plugins

| Topic | Reference |
|-------|-----------|
| Content reuse (Snippets, include-markdown substitute) | [content-reuse.md](references/plugins/content-reuse.md) |
| API documentation (mkdocstrings) | [mkdocstrings.md](references/plugins/mkdocstrings.md) |

## Migration from mkdocs-material

Config conversion from `mkdocs.yml` to `zensical.toml`, feature parity status, extension compatibility, theme overrides, analytics, and plugin substitutes.
- See [migration.md](references/migration.md)

## Key Differences from mkdocs-material

- Config format: TOML (`zensical.toml`) instead of YAML (`mkdocs.yml`)
- All settings scoped under `[project]`
- Theme variants: `modern` (new) or `classic` (Material-compatible)
- Icon prefix uses `lucide/` by default (also supports fontawesome, material, octicons, simple-icons)
- Extensions configured via `[project.markdown_extensions.<name>]` TOML tables
- Sensible defaults: common extensions enabled automatically without explicit config
- Plugins configured via `[project.plugins.<name>]` TOML tables
- CLI commands: `zensical new`, `zensical serve`, `zensical build`
- Default dev server port: `localhost:8000`
- `pymdownx.snippets` replaces `mkdocs-include-markdown` for content reuse
- `mkdocs-macros` has no direct substitute; Zensical is developing a module system
