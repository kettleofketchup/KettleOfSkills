---
name: agent-harness
description: >-
  Make a repo's .claude/ skills visible to Codex, OpenHands, Copilot, and Cursor.
  Use when another agent cannot see project skills, when wiring AGENTS.md, or when
  adding cross-harness support to a repo.
---

# Agent Harness Interop

Make one repo's skills work in every agent harness, without maintaining copies.

`.claude/` stays the single source of truth. Everything else is a generated
**pointer** back into it, so no second copy exists to drift.

## Wire up a repo

Run once with the harnesses to target, then without flags forever after:

```bash
SYNC=~/.claude/skills/agent-harness/scripts/sync_harnesses.py
uv run "$SYNC" --harness codex,openhands   # first run, in the repo root
uv run "$SYNC"                             # regenerate
uv run "$SYNC" --check                     # exit 1 + diff if stale
```

Choices persist in `.agents/harnesses.json`, so later runs and CI need no flags.
Plain `python3` works too when pyyaml is installed. Then hand-write `AGENTS.md`
(see below) and commit everything.

## What gets created

| Path | Kind | Read by |
| --- | --- | --- |
| `.claude/skills/` | source of truth | Claude Code |
| `.agents/skills` to `../.claude/skills` | symlink | Codex, and any spec-compliant client |
| `.codex/skills/` | generated | Codex |
| `.openhands/microagents/` | generated | OpenHands |
| `.github/instructions/` | generated | Copilot |
| `.cursor/rules/` | generated | Cursor |
| `AGENTS.md` | hand-written | all of them, plus ~25 other tools |

**The symlink is the whole mechanism for skills.** A directory-level symlink means
skills added, renamed, or deleted propagate with no sync step that can fall behind,
and it preserves the spec rule that a skill's `name` match its parent directory.
Generation exists only for artifacts with no `SKILL.md` form (slash commands,
subagents) and for harnesses that use a different file format.

## AGENTS.md carries the conventions

Generated files are pointers and deliberately contain **no** repo rules. Put the
task runner, the forge CLI, the setup command, and any must-know constraint in
`AGENTS.md` at the repo root, which every one of these harnesses reads. Restating
rules per generated file would be duplication that can drift — exactly what this
skill exists to prevent. See `references/agents-md.md`.

## Per-skill scope

Copilot and Cursor load rules by file glob. Set the glob in the skill's own
frontmatter, keeping the override in the source of truth:

```yaml
metadata:
  applies-to: "src/**/*.tsx"
  triggers: "brand, tokens, css"
```

`applies-to` defaults to `**`. `triggers` is for OpenHands keyword matching; when
absent it is derived from the skill name plus quoted and backticked terms in the
description, which is thin for descriptions containing neither.

## Keep it honest

Re-run `--check` in review or CI. It fails when a generated file is missing,
hand-edited, or orphaned by a deleted source. Repair by re-running the script —
never by editing a generated file, which the next sync overwrites.

The script hard-errors on a skill whose `name` does not match its directory, or
whose `description` is empty. Both are silent-failure modes: strict clients skip
such a skill entirely, so it disappears from the harness with no error.

It refuses to replace `.agents/skills` when that path is a real directory rather
than a symlink, on the assumption a human put it there.

## Verify it worked

For Codex, render the real model-visible prompt without spending an API call:

```bash
codex debug prompt-input "hi" | grep -c 'Available skills'
```

Every project skill and adapter should appear exactly once. If none appear, check
workspace trust before suspecting the mapping. Details and the per-harness
capability matrix are in `references/harness-matrix.md`.

## References

- `references/harness-matrix.md` — what each harness reads, and how it was verified
- `references/agents-md.md` — what belongs in AGENTS.md
- `references/adding-a-harness.md` — add an emitter for a new tool

## Standards

Skills follow the open Agent Skills spec at agentskills.io; `AGENTS.md` follows
agents.md. The spec designates `.agents/skills/` as the cross-client path, so this
layout is the standard answer rather than a local invention.
