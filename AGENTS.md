# AGENTS.md — kettleofskills

Guidance for AI coding agents working in this repo. This is a **Claude Code marketplace**:
it packages curated skills as individually installable plugins and grouped bundles.

## The one thing to get right

**This repo is not the source of truth for its own skills.** Skills are authored in the
dotfiles repo at `~/.claude/skills/<name>/` and *promoted* here. Editing
`plugins/<name>/skills/<name>/SKILL.md` directly gets silently overwritten on the next
promotion.

```bash
# Correct: edit ~/.claude/skills/<name>/, then promote
python3 ~/.claude/skills/kettle-skill-creator/scripts/promote-skill.py <name>
```

The `kettle-skill-creator` skill owns this workflow — read it before changing anything
under `plugins/`.

## Ground rules

- Run tasks through `just`. `just sync` after any plugin change, `just test` before
  committing.
- **Never hand-edit generated artifacts**: `.claude-plugin/marketplace.json` and every
  `plugins/<group>/` directory (`all`, `devops`, `k8s-core`, …) are produced by
  `just sync-groups` / `just sync-marketplace`. Group directories are symlinks.
- `config.yaml` categories are set on a plugin's **first** promotion and ignored
  afterwards, so get them right the first time.
- Never list `all` as a category — every skill joins it automatically.

## Layout

```
plugins/<name>/
├── skills/<name>/
│   ├── SKILL.md          # name must equal <name>; description under 200 chars
│   ├── config.yaml       # categories
│   ├── references/       # each file under 150 lines
│   └── scripts/          # optional, plus scripts/tests/
└── .claude-plugin/       # only for plugins shipping agents/hooks/commands
```

Hard limits enforced by `validate-plugin.py`: SKILL.md body under 150 lines, each
reference under 150 lines, description under 200 characters with no angle brackets,
`name` matching the directory at both levels.

## Workflow

```bash
python3 ~/.claude/skills/kettle-skill-creator/scripts/promote-skill.py <name> [--categories x,y]
python3 ~/.claude/skills/kettle-skill-creator/scripts/validate-plugin.py --all
just sync
just test
just git::version <major|minor|hotfix>   # release
```

## Skills for other harnesses

Every skill here is a `SKILL.md`, the open Agent Skills format (agentskills.io), which
Codex, Cursor, Amp, opencode, and Copilot CLI read natively — only the directory each
tool scans differs. The `agent-harness` plugin in this marketplace wires a *consuming*
repo's `.claude/skills/` up to those tools.

That mapping does not apply to this repo: the skills under `plugins/` are published
products, not this repo's own working knowledge, so there is no `.claude/skills/` here
and nothing to expose. This file is the whole story for agents working on the
marketplace itself.
