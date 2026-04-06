# Plugin Directory Structure

## Required Layout

```
plugins/<skill-name>/
└── skills/
    └── <skill-name>/
        ├── SKILL.md            # Required: skill content with YAML frontmatter
        ├── config.yaml         # Required: category assignments
        └── references/         # Optional: detailed reference docs
            ├── topic-a.md
            └── topic-b.md
```

The `<skill-name>` must be identical at both directory levels and match the `name:` in SKILL.md frontmatter.

## SKILL.md Requirements

**Frontmatter (required):**
```yaml
---
name: my-skill-name
description: >-
  Action-oriented description under 200 chars. Third person.
  "This skill should be used when..."
---
```

- `name`: kebab-case (lowercase letters, digits, hyphens). No leading/trailing/consecutive hyphens.
- `description`: <200 characters. Specific trigger phrases and use cases. No angle brackets.
- Optional fields: `license`, `version`

**Body:**
- <150 lines total
- Imperative/infinitive writing style
- Practical instructions, not documentation
- Reference `references/` files for detailed content

## config.yaml Requirements

```yaml
categories:
  - category-name
```

All category names must be from the valid list (see `references/categories.md`).
Unknown categories produce warnings during `just sync-groups`.

## Reference Files

- Each file <150 lines
- Kebab-case filenames
- Practical instructions for Claude, not educational docs
- Can reference other reference files or scripts

## File Size Limits

| File Type | Max Lines |
|-----------|-----------|
| SKILL.md body | 150 |
| Each reference file | 150 |
| Description metadata | 200 chars |
| Scripts | No limit |

## What NOT to Include

- `assets/` directory (not used in kettleofskills plugins)
- `scripts/` directory within individual skills (repo-level scripts handle tooling)
- `.env` files or secrets
- Generated files (marketplace.json, group symlinks are auto-generated)
