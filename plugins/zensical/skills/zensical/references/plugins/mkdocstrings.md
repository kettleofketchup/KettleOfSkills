---
last_updated: 2026-03-25
version: "0.0.x (alpha)"
source_url: https://zensical.org/docs/setup/extensions/mkdocstrings/
---

# mkdocstrings — API Documentation

Generate API reference documentation from source code docstrings. Preliminary support since Zensical 0.0.11.

## Installation

```bash
# pip
pip install mkdocstrings-python

# uv
uv add mkdocstrings-python
```

## Configuration

```toml
[project.plugins.mkdocstrings.handlers.python]
inventories = ["https://docs.python.org/3/objects.inv"]
paths = ["src"]

[project.plugins.mkdocstrings.handlers.python.options]
docstring_style = "google"
inherited_members = true
show_source = false
```

```yaml
# mkdocs.yml equivalent
plugins:
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          inventories:
            - https://docs.python.org/3/objects.inv
          options:
            docstring_style: google
            inherited_members: true
            show_source: false
```

## Usage in Markdown

Reference Python objects with the autodoc syntax:

```markdown
::: my_module.MyClass
    options:
      show_source: true
      members:
        - method_a
        - method_b
```

## Key Options

| Option | Purpose |
|--------|---------|
| `paths` | Source directories to scan (default: `["src"]`) |
| `docstring_style` | Format: `google`, `numpy`, `sphinx` |
| `inherited_members` | Include parent class members |
| `show_source` | Display source code links |
| `inventories` | External intersphinx-style references |

## Limitations

- Backlinks not yet supported
- External source paths outside project folder not monitored during `zensical serve`
- Only Python handler currently documented; other languages may work via mkdocstrings community handlers
