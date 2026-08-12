# Harness Capability Matrix

What each harness actually reads. Codex rows were verified empirically; the rest come
from vendor documentation and are marked as such. Re-verify after a major upgrade —
these paths move.

## Verified: Codex

Measured against `codex-cli 0.147.0` with `codex debug prompt-input`, which renders the
real model-visible prompt without spending an API call. That command is the fastest way
to re-verify anything in this table.

| Behaviour | Result |
| --- | --- |
| `repo/.agents/skills/*/SKILL.md` | discovered |
| `repo/.codex/skills/*/SKILL.md` | discovered |
| `repo/.claude/skills/` | ignored |
| Root `AGENTS.md` | injected into the prompt |
| Frontmatter | `name` + `description`; unknown keys tolerated |
| Directory-level symlinks | followed |
| Skill display name | comes from frontmatter `name`, not the directory |
| Subagents / Task tool | none |
| Project slash commands | none in 0.147 |

Two consequences drive the design:

- A **directory-level symlink works**, so the whole skills tree maps with one link.
- There is **no Task tool**, so any subagent procedure must say "run this inline".

### Trust gating

Codex tracks workspace trust in `~/.codex/config.toml` as
`[projects."/abs/path"] trust_level = "trusted"`. The Agent Skills client guide
recommends gating project skills on such a check. Measured on 0.147.0, an untrusted
repo still loaded all its project skills, so trust does not gate discovery today. It
remains the first thing to rule out when nothing appears, because it would present as
silence rather than an error.

## Documented: OpenHands

Uses `.openhands/microagents/*.md` — flat files, not `SKILL.md` directories, so the
`.agents/skills` symlink does nothing for it.

| Item | Value |
| --- | --- |
| Always loaded | `microagents/repo.md` |
| Conditionally loaded | any file whose `triggers` keywords match |
| Frontmatter | `name` + `triggers: [a, b]` |
| Root `AGENTS.md` | read |
| Subagents | none |

The frontmatter format has changed across versions. Because of that, the emitter writes
a `repo.md` index of every artifact in addition to per-skill trigger files: if the
trigger frontmatter is wrong for an installed version, the always-loaded index still
routes the agent to the right file. Treat that redundancy as deliberate.

## Documented: GitHub Copilot

| Item | Value |
| --- | --- |
| Repo-wide | `.github/copilot-instructions.md` |
| Path-scoped | `.github/instructions/*.instructions.md` |
| Frontmatter | `applyTo:` glob |
| Root `AGENTS.md` | read |

Copilot does not follow file references the way Claude Code does — it loads matching
files literally. Keep each generated file short and pointer-shaped; it exists so review
catches the most common drift, not to teach Copilot the whole convention.

## Documented: Cursor

| Item | Value |
| --- | --- |
| Rules | `.cursor/rules/*.mdc` |
| Frontmatter | `description`, `globs`, `alwaysApply` |
| Root `AGENTS.md` | read |

Generated rules set `alwaysApply: false` and rely on `globs`, so they cost nothing until
a matching file is touched.

## The universal floor

`AGENTS.md` is read by all of the above plus roughly 25 other tools. When a harness is
not worth a dedicated emitter, `AGENTS.md` alone is a legitimate answer — it is the one
file every agent already looks for.

## Cross-platform installers

`npx skills` (vercel-labs/skills) fans a `SKILL.md` out to 40+ platforms and is the right
tool for **consuming published skills**. It is the wrong tool for exposing a repo's own
first-party skills, because it copies files into each agent directory, and a copy can
drift where a symlink cannot. Reach for it when installing someone else's skills, not
when publishing your repo's.
