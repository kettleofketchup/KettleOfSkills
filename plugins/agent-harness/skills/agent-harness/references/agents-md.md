# Writing AGENTS.md

`AGENTS.md` at the repo root is the one file every agent harness reads. It follows the
spec at agents.md: plain Markdown, no required fields, nearest-file-wins in monorepos
(a package may carry its own, and the closest to the edited file takes precedence).

It is **hand-written**, never generated. Generated pointer files deliberately carry no
repo rules, so this is where the rules live.

## What belongs in it

Keep it to what an agent would get wrong on its first commit:

- **The task runner.** If commands must go through `just`, `make`, or a script, say so
  and say what not to call directly. This is the single highest-value line in the file.
- **The forge.** `gh` versus `fj` versus `glab`. An agent that guesses wrong hits the
  wrong host and fails confusingly.
- **First-run setup.** The one command that makes a fresh clone or worktree work.
- **Hard constraints.** Gates that must not be bypassed, generated files that must not
  be hand-edited, directories that are off limits.
- **A short index of the skills** and where they live, so an agent that missed the
  catalog can still find them.
- **How the harness mapping works**, and that generated directories are generated.

## What does not belong

- Anything a skill already says well. Point at the skill instead.
- Long walkthroughs or full API schemas. Agents load this file every session; every
  line costs context on every task.
- Anything that varies by environment or feature flag.

## Shape

Aim for roughly one screen. A skeleton that works:

```markdown
# AGENTS.md — <repo>

Guidance for AI coding agents. Detailed conventions live in `.claude/skills/`,
the single source of truth; this file is the floor.

## Ground rules
- Run everything through `<runner>`. Never call `<tool>` directly.
- This forge is <forge>: use `<cli>`.
- First-run setup is `<command>`.

## Stack
<two or three sentences, plus any load-bearing rule that is easy to get wrong>

## Where the knowledge lives
| skill | use it when |
| --- | --- |

## How each harness sees this
<which directories are generated, and the command to regenerate them>
```

## Keeping it current

`AGENTS.md` is hand-written, so nothing detects when it drifts. Two habits help: list
skills by name and purpose rather than restating their content, so adding a skill is a
one-line edit; and have whatever reviews skills for staleness treat `AGENTS.md` as one
of the artifacts it checks.
