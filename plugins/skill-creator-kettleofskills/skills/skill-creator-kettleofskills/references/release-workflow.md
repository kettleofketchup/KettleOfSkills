# Release Workflow

## Pre-Release Checklist

1. All new/modified skills have valid SKILL.md with frontmatter
2. All config.yaml files list only valid categories
3. Validation passes for all new/modified skills
4. Reference files are under 150 lines each

## Sync Commands

Run from the repo root:

```bash
# Sync both groups and marketplace (recommended)
just sync

# Or run individually:
just sync-groups        # Read config.yaml files, create group symlinks
just sync-marketplace   # Read SKILL.md descriptions, generate marketplace.json
```

### What sync-groups does
- Reads every `plugins/*/skills/*/config.yaml`
- Creates symlinks in group directories: `plugins/<category>/skills/<skill> -> ../../<plugin>/skills/<skill>`
- Adds every skill to the `all` group automatically
- Warns on unknown category names
- Reports skill count per group

### What sync-marketplace does
- Reads SKILL.md frontmatter for descriptions (truncates >120 chars)
- Generates individual + group entries
- Writes `.claude-plugin/marketplace.json`
- Reports total plugin count

## Version Bump and Release

```bash
just git::version <major|minor|hotfix>
```

This single command:
1. Bumps the version in `VERSION` file
2. Runs `just sync` (groups + marketplace)
3. Stages and commits: `release: v<new-version>`
4. Creates annotated git tag: `v<new-version>`

Then manually push:
```bash
git push origin main --tags
```

## Version Bump Types

| Bump | When to Use | Example |
|------|-------------|---------|
| `major` | Breaking changes, large reorganizations | 1.0.0 -> 2.0.0 |
| `minor` | New skills added, new categories | 1.0.0 -> 1.1.0 |
| `hotfix` | Fixes to existing skills, typos | 1.0.0 -> 1.0.1 |

## Adding Multiple Skills

When adding multiple skills in one release:
1. Create all plugin directories and files
2. Run validation on each
3. Run `just sync` once (covers all changes)
4. Use `just git::version minor` for the release commit
