---
name: skill-creator-kettleofskills
description: >-
  Create, categorize, and validate new skills for the kettleofskills marketplace.
  Use when adding skills, assigning categories, or preparing releases.
---

# Skill Creator for kettleofskills

Create new skills in the kettleofskills marketplace repo and prepare them for release.

## Repo Context

- **Repo root:** The current working directory (kettleofskills repo)
- **Plugin dir:** `plugins/<skill-name>/skills/<skill-name>/`
- **Sync recipes:** `just sync-groups` and `just sync-marketplace`
- **Release:** `just git::version <major|minor|hotfix>`

## Creating a New Skill

### Step 1: Initialize

Run the init script to scaffold the plugin directory structure:

```bash
python3 plugins/skill-creator-kettleofskills/skills/skill-creator-kettleofskills/scripts/init-plugin.py <skill-name>
```

This creates `plugins/<skill-name>/skills/<skill-name>/` with SKILL.md template, config.yaml, and references/ directory.

### Step 2: Assign Categories

Edit `plugins/<skill-name>/skills/<skill-name>/config.yaml` to assign categories.
See `references/categories.md` for the full list of valid categories and their descriptions.

Every skill is automatically added to the `all` group -- do NOT add `all` to config.yaml.

### Step 3: Write SKILL.md

Fill in the SKILL.md with:
- **Frontmatter:** `name` (kebab-case) and `description` (<200 chars, action-oriented, third-person)
- **Body:** Practical instructions for Claude Code (<150 lines)
- **References:** Split detailed content into `references/` files (<150 lines each)

Writing style: imperative/infinitive form ("To accomplish X, do Y"), not second person.

### Step 4: Add References (Optional)

Add detailed reference docs in `references/`. Each file <150 lines.
Reference them from SKILL.md so Claude knows they exist.

### Step 5: Validate

Run the validation script to check the plugin meets all requirements:

```bash
python3 plugins/skill-creator-kettleofskills/skills/skill-creator-kettleofskills/scripts/validate-plugin.py <skill-name>
```

Checks: SKILL.md frontmatter, description length, config.yaml categories, file sizes, directory structure.

### Step 6: Sync and Verify

```bash
just sync-groups        # Regenerate group symlinks from config.yaml
just sync-marketplace   # Regenerate .claude-plugin/marketplace.json
```

Verify the skill appears in the correct groups and in marketplace.json.

### Step 7: Release

See `references/release-workflow.md` for version bumping and tagging.

## Validation Criteria

- SKILL.md exists with valid YAML frontmatter (name + description)
- Description <200 characters, no angle brackets
- Name is kebab-case, matches directory name
- config.yaml exists with valid categories from the known list
- SKILL.md body <150 lines; each reference file <150 lines
- See `references/plugin-structure.md` for full directory layout requirements

## References

- `references/categories.md` -- valid categories with descriptions
- `references/plugin-structure.md` -- required directory layout
- `references/release-workflow.md` -- sync, version bump, and release process
