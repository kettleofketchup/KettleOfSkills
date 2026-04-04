---
last_updated: 2026-03-24
version: "0.0.x (alpha)"
source_url: https://zensical.org/docs/authoring/admonitions/
---

# Admonitions

Call-out blocks for supplementary information. Require extensions: `admonition`, `pymdownx.details`, `pymdownx.superfences`.

## Basic Syntax

```markdown
!!! note
    Content indented four spaces.
```

## Custom Title

```markdown
!!! warning "Custom Title Here"
    Content with custom heading.
```

## No Title

```markdown
!!! note ""
    Content without icon or title.
```

## Collapsible (closed by default)

```markdown
??? note
    Hidden content revealed on click.
```

## Collapsible (open by default)

```markdown
???+ note
    Initially expanded content.
```

## Nested

```markdown
!!! note "Outer"
    Content here.

    !!! info "Inner"
        Nested content.
```

## Inline (sidebar)

```markdown
!!! info inline end "Right sidebar"
    Floats to right of content.

!!! info inline "Left sidebar"
    Floats to left of content.
```

## Supported Types

| Type | Aliases |
|------|---------|
| `note` | |
| `abstract` | summary, tldr |
| `info` | todo |
| `tip` | hint, important |
| `success` | check, done |
| `question` | help, faq |
| `warning` | caution, attention |
| `failure` | fail, missing |
| `danger` | error |
| `bug` | |
| `example` | |
| `quote` | cite |
