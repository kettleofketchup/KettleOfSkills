---
name: mkdocs-documentation
description: MkDocs Material documentation management. This skill should be used when writing, formatting, or validating documentation in docs/. Covers admonitions, Mermaid diagrams, code blocks with annotations, content tabs, navigation setup, include-markdown for reusable content, _includes pattern for shared diagrams, and mkdocs testing. Always check project-specific docs at docs/dev/ai/skills/ and docs/dev/ai/agents/ for project-specific Claude skill and Claude agent documentation when available.
---

# MkDocs Material Documentation

Write and maintain documentation using MkDocs Material in the `docs/` directory.

## Project-Specific Claude Documentation

**Always check first for project-specific Claude configurations:**
- `docs/dev/ai/skills/SKILL-NAME.md` - Project-specific Claude skill docs
- `docs/dev/ai/agents/AGENT-NAME.md` - Project-specific Claude agent docs

These take precedence over general patterns.

## Quick Reference

| Task | Reference |
|------|-----------|
| Callout boxes | [admonitions.md](references/admonitions.md) |
| Flowcharts, diagrams | [diagrams.md](references/diagrams.md) |
| Syntax highlighting | [code-blocks.md](references/code-blocks.md) |
| Multi-option examples | [content-tabs.md](references/content-tabs.md) |
| Links, nav structure | [navigation.md](references/navigation.md) |
| Reusable content includes | [includes.md](references/includes.md) |
| Build, validate | [testing.md](references/testing.md) |

## Diagram Rules

**REQUIRED SUB-SKILL:** Use `mermaidjs-v11` for all Mermaid diagram creation.

Diagrams with more than **15 nodes or lines** must be split:

1. Create a **top-level overview** showing high-level blocks only
2. Create **per-component deep-dives** with internal details
3. Store each diagram in `docs/architecture/_includes/` as a separate `.md` file
4. Reference from pages using `{% include-markdown %}` directives
5. Add `hide: true` to `_includes/.pages` to exclude from navigation

See [includes.md](references/includes.md) for the full pattern.

## Common Patterns

### Admonition with Code

```markdown
!!! example "Usage"

    ```python
    from module import func
    func()
    ```
```

### Tabbed Content

````markdown
=== "pip"

    ```bash
    pip install package
    ```

=== "uv"

    ```bash
    uv add package
    ```
````

## Workflow

1. **Write content** — use references for formatting syntax
2. **Diagrams** — invoke `mermaidjs-v11` skill, split large diagrams into `_includes/`
3. **Preview** — `uv run mkdocs serve` for live reload
4. **Validate** — `uv run mkdocs build --strict` catches issues

## Validation Commands

```bash
# Dev server with live reload
uv run mkdocs serve

# Strict build (CI validation)
uv run mkdocs build --strict

# Quick dirty reload during editing
uv run mkdocs serve --dirty
```

## Dependencies

Managed via `pyproject.toml` + `uv sync`:

```toml
[project]
dependencies = [
    "mkdocs-material",
    "mkdocs-awesome-nav",
    "mkdocs-glightbox",
    "mkdocs-macros-plugin",
    "mkdocs-include-markdown-plugin",
]
```

Dockerfile uses `uv` from `ghcr.io/astral-sh/uv:0.11.0`.
