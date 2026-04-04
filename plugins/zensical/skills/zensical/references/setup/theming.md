---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_urls:
  - https://zensical.org/docs/setup/colors/
  - https://zensical.org/docs/setup/fonts/
  - https://zensical.org/docs/setup/logo-and-icons/
  - https://zensical.org/docs/setup/header/
  - https://zensical.org/docs/setup/footer/
  - https://zensical.org/docs/setup/repository/
  - https://zensical.org/docs/setup/analytics/
  - https://zensical.org/docs/setup/data-privacy/
  - https://zensical.org/docs/customization/
---

# Theming & Customization

## Color Schemes

Built-in: `default` (light) and `slate` (dark).

```toml
[project.theme.palette]
scheme = "default"
primary = "indigo"
accent = "indigo"
```

Available colors: red, pink, purple, deep-purple, indigo, blue, light-blue, cyan, teal, green, light-green, lime, yellow, amber, orange, deep-orange, brown, grey, blue-grey, black, white.

### Light/Dark Toggle

```toml
[[project.theme.palette]]
scheme = "default"
toggle.icon = "lucide/sun"
toggle.name = "Switch to dark mode"

[[project.theme.palette]]
scheme = "slate"
toggle.icon = "lucide/moon"
toggle.name = "Switch to light mode"
```

### System Preference

```toml
[[project.theme.palette]]
media = "(prefers-color-scheme: light)"
scheme = "default"
```

### Custom Colors

Set `primary = "custom"` or `accent = "custom"`, then override in CSS:

```css
:root > * {
  --md-primary-fg-color: #EE0F0F;
  --md-primary-fg-color--light: #ECB7B7;
  --md-primary-fg-color--dark: #90030C;
}
```

Custom named scheme: `[data-md-color-scheme="youtube"] { --md-primary-fg-color: #EE0F0F; }`

## Fonts

```toml
[project.theme]
font.text = "Inter"         # body text (Google Fonts)
font.code = "JetBrains Mono" # code blocks
font = false                 # disable Google Fonts (system fallback)
```

Self-hosted fonts: add `@font-face` in `extra_css`, set `--md-text-font` and `--md-code-font` CSS vars.

## Logo & Icons

```toml
[project.theme]
logo = "images/logo.png"     # image file
favicon = "images/favicon.png"

[project.theme.icon]
logo = "lucide/smile"        # bundled icon alternative
repo = "fontawesome/brands/github"
edit = "material/pencil"
view = "material/eye"
```

Customizable icons: logo, menu, alternate, search, share, close, top, edit, view, repo, admonition, tag, previous, next.

## Header

```toml
[project.theme]
features = ["header.autohide", "announce.dismiss"]
```

Announcement bar: extend theme, override `announce` block in `overrides/main.html`.

## Footer

```toml
[project.theme]
features = ["navigation.footer"]  # prev/next links

[[project.extra.social]]
icon = "fontawesome/brands/github"
link = "https://github.com/org/repo"

[project]
copyright = "Copyright &copy; 2025 Jane Doe"

[project.extra]
generator = false  # hide "Made with Zensical"
```

## Repository

```toml
[project]
repo_url = "https://github.com/org/repo"
repo_name = "org/repo"
edit_uri = "edit/main/docs/"

[project.theme]
features = ["content.action.edit", "content.action.view"]
```

## Custom CSS/JS

```toml
[project]
extra_css = ["stylesheets/extra.css"]
extra_javascript = ["javascripts/extra.js"]
```

For instant navigation, use `document$.subscribe()` to reinitialize JS on page load.

## Theme Overrides

```toml
[project.theme]
custom_dir = "overrides"
```

Override blocks in `overrides/main.html`:
```html
{% extends "base.html" %}
{% block htmltitle %}<title>Custom</title>{% endblock %}
```

Available blocks: analytics, announce, config, container, content, extrahead, fonts, footer, header, hero, htmltitle, libs, outdated, scripts, site_meta, site_nav, styles, tabs.

Partial overrides: create matching files in `overrides/partials/`. Custom 404: `overrides/404.html`.

## Analytics & Privacy

```toml
[project.extra.analytics]
provider = "google"
property = "G-XXXXXXXXXX"

[project.extra.consent]
title = "Cookie consent"
description = "We use cookies..."
```

Feedback widget, custom analytics provider, and cookie consent configurable. See source URLs for full details.
