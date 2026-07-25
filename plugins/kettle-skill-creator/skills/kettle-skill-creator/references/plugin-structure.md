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

## Plugins that ship more than a skill

Some plugins are more than a single skill — they also ship agents, hooks, or slash commands at
the plugin root. `comment-reviewer` is an example:

```
plugins/comment-reviewer/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── agents/
│   └── comment-reviewer.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
├── commands/
│   └── comment-review.md
├── tests/                    # Plugin-root test suite (see PLUGIN_ROOT_DIRS)
└── skills/
    └── comment-reviewer/
        ├── SKILL.md
        ├── config.yaml
        ├── references/
        └── scripts/
```

`agents/`, `hooks/`, `commands/`, and `tests/` are auto-discovered by Claude Code from the
plugin root — no manifest entry is required beyond `.claude-plugin/plugin.json` declaring the
plugin itself. Any command invoked from `hooks/hooks.json` must reference scripts via
`${CLAUDE_PLUGIN_ROOT}` (never a relative or hardcoded path) — the plugin can be installed at
any path once distributed through the marketplace.

Group bundles (`all`, `claude-tooling`, …) only symlink each skill's `skills/<name>/` directory.
A group install carries the skill and its `scripts/`, but **not** the plugin-root `hooks/`,
`agents/`, or `commands/`. Plugins that depend on those must be installed directly by name.

## What NOT to Include

- `assets/` directory (not used in kettleofskills plugins)
- `.env` files or secrets
- Generated files (marketplace.json, group symlinks are auto-generated)
