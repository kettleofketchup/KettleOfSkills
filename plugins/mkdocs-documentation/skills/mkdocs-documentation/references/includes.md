# Include-Markdown Plugin

Reuse content across pages using `mkdocs-include-markdown-plugin`.

## Setup

```yaml
# mkdocs.yml
plugins:
  - include-markdown
```

```toml
# pyproject.toml
dependencies = ["mkdocs-include-markdown-plugin"]
```

## Syntax

```markdown
{%
   include-markdown "path/to/file.md"
%}
```

**Paths are relative to `docs/` root**, not the including file's directory.

## `_includes` Pattern for Diagrams

Store reusable Mermaid diagrams in `docs/architecture/_includes/`:

```
docs/
  architecture/
    _includes/
      .pages            # hide: true (exclude from nav)
      ai-overview.md    # top-level overview diagram
      vllm-detail.md    # per-component deep-dive
      secret-flow.md    # cross-cutting concern
    ai-stack.md         # references _includes via include-markdown
```

### Hide from Navigation

```yaml
# docs/architecture/_includes/.pages
hide: true
```

### Reference from Pages

```markdown
## Architecture Overview

{%
   include-markdown "architecture/_includes/ai-overview.md"
%}

## Components

### vLLM

{%
   include-markdown "architecture/_includes/vllm-detail.md"
%}
```

### Each Include File Contains One Diagram

```markdown
<!-- architecture/_includes/vllm-detail.md -->
` ` `mermaid
flowchart LR
    subgraph vllm_ns["vllm namespace"]
        pod["vLLM :8000"]
        pvc["Model Cache 100Gi"]
    end
    gpu["NVIDIA GPU"]
    pod --> gpu
    pod --> pvc
` ` `
```

## When to Split into Includes

| Condition | Action |
|-----------|--------|
| Diagram > 15 lines | Split into `_includes/` |
| Diagram reused on 2+ pages | Must be in `_includes/` |
| Single-use, < 15 lines | Keep inline |
| Cross-cutting concern (secret flow, boot sequence) | Always `_includes/` |

## Diagram Splitting Rules

**REQUIRED:** Use `mermaidjs-v11` skill for diagram creation.

1. **Overview diagram** — max 5-7 top-level blocks, no internal details, use color `style` directives
2. **Deep-dive diagrams** — one per component, show internal structure (pods, PVCs, secrets, connections)
3. **Cross-cutting diagrams** — for flows spanning multiple namespaces (Reflector, init jobs)

## Other Include Uses

Include any reusable markdown — not just diagrams:

```markdown
<!-- Reuse a warning across pages -->
{%
   include-markdown "architecture/_includes/airgap-warning.md"
%}

<!-- Include with heading offset -->
{%
   include-markdown "shared/table.md"
   heading_offset=1
%}

<!-- Include specific lines -->
{%
   include-markdown "reference.md"
   start="## Section Start"
   end="## Section End"
%}
```
