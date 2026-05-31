---
name: kettle-skill-creator
description: >-
  Create, promote, categorize, and validate skills for the kettleofskills marketplace.
  Use when syncing dotfiles skills into the marketplace, adding skills, assigning categories,
  or preparing a release.
---

# Kettle Skill Creator

Manage the kettleofskills marketplace from the dotfiles source of truth. Skills are authored
in `~/.claude/skills/<name>/` (dotfiles) and published as marketplace plugins at
`plugins/<name>/skills/<name>/` with a `config.yaml`. This skill promotes dotfiles changes
into the marketplace and creates new marketplace skills.

## Repo Context

- **Source of truth:** `~/.claude/skills/<name>/` (symlinked to the dotfiles repo)
- **Marketplace repo root:** the current working directory (kettleofskills repo)
- **Plugin dir:** `plugins/<name>/skills/<name>/`
- **Scripts:** `~/.claude/skills/kettle-skill-creator/scripts/` (auto-locate the repo root; run
  from anywhere inside the kettleofskills repo)
- **Sync recipes:** `just sync` (= `just sync-groups` + `just sync-marketplace`)
- **Release:** `just git::version <major|minor|hotfix>`

## Promote a dotfiles skill into the marketplace

Use when a skill already authored in dotfiles needs its marketplace copy updated, or when a
dotfiles skill is not yet in the marketplace.

```bash
# Update an existing marketplace skill (config.yaml is preserved)
python3 ~/.claude/skills/kettle-skill-creator/scripts/promote-skill.py <name>

# Create a new marketplace plugin from a dotfiles skill (categories required)
python3 ~/.claude/skills/kettle-skill-creator/scripts/promote-skill.py <name> --categories linux

# Preview without writing
python3 ~/.claude/skills/kettle-skill-creator/scripts/promote-skill.py <name> --dry-run
```

`promote-skill.py` copies `SKILL.md` and mirrors `references/` and `scripts/` from the dotfiles
skill into the plugin dir. It **never** overwrites an existing `config.yaml`. For a new plugin
it requires `--categories` and writes the `config.yaml`. Then run `just sync` and validate.

## Create a new skill from scratch

When the skill does not exist in dotfiles yet, author it in `~/.claude/skills/<name>/` first
(see the generic `skill-creator` skill for authoring guidance), then promote it. To scaffold a
plugin directly in the marketplace instead:

```bash
python3 ~/.claude/skills/kettle-skill-creator/scripts/init-plugin.py <name> --categories devops,k8s-core
```

This creates `plugins/<name>/skills/<name>/` with a SKILL.md template, config.yaml, and
references/ directory. Fill in:
- **Frontmatter:** `name` (kebab-case, matches dir) and `description` (<200 chars, action-oriented, third person)
- **Body:** practical instructions for Claude Code (<150 lines)
- **References:** detailed content split into `references/` files (<150 lines each)

Writing style: imperative/infinitive form ("To accomplish X, do Y"), not second person.

## Assign categories

Edit `plugins/<name>/skills/<name>/config.yaml`. See `references/categories.md` for the valid
categories. Every skill is automatically added to the `all` group -- do NOT list `all`.

## Validate

```bash
python3 ~/.claude/skills/kettle-skill-creator/scripts/validate-plugin.py <name>
python3 ~/.claude/skills/kettle-skill-creator/scripts/validate-plugin.py --all
```

Checks: SKILL.md frontmatter, name matches dir, description <200 chars and no angle brackets,
config.yaml categories valid, SKILL.md body <150 lines, each reference file <150 lines.

## Sync and verify

```bash
just sync-groups        # Regenerate group symlinks from config.yaml
just sync-marketplace   # Regenerate .claude-plugin/marketplace.json
```

Verify the skill appears in the correct groups and in `marketplace.json`.

## Release

See `references/release-workflow.md` for version bumping and tagging via
`just git::version <major|minor|hotfix>`.

## References

- `references/categories.md` -- valid categories with descriptions (incl. `linux`)
- `references/plugin-structure.md` -- required directory layout
- `references/release-workflow.md` -- sync, version bump, and release process
