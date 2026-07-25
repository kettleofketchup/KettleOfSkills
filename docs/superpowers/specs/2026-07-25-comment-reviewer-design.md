# comment-reviewer — Design

**Date:** 2026-07-25
**Status:** Approved, ready for implementation planning

## Purpose

Comments written during implementation carry the shape of the process that produced them:
references to a plan step, a spec requirement, a review comment, or a bug someone found. They
also drift out of sync with the code and grow longer than the knowledge they carry. None of
that survives usefully into the life of the code.

`comment-reviewer` sweeps a development branch before its pull request is opened, rewrites the
comments that fail three tests, and gates PR creation until it has run.

## Scope

Comments in **every file the branch touched**, compared against the base branch — not only the
lines the branch changed. A change that makes a nearby comment wrong is exactly the case worth
catching, and comment cleanup is cheap to review.

Both readings of "multiple languages" are in scope:

- **Programming languages** — extraction covers `//`, `#`, `--`, `%`, `;`, `/* */`, `"""`,
  `'''`, `<!-- -->`, `(* *)`, `=begin`/`=end`, `<# #>`.
- **Natural languages** — rewrites preserve the comment's original natural language. The agent
  never silently translates. A comment written in a different natural language from the rest of
  the repo is reported as a finding, not fixed.

## Architecture

One marketplace plugin, `comment-reviewer`, carrying four parts. It is the first plugin in the
catalog that is more than a skill.

```
plugins/comment-reviewer/
├── plugin.json                      # name, version, wires hooks/agents/commands
├── skills/comment-reviewer/
│   ├── SKILL.md                     # the review method (<150 lines)
│   ├── config.yaml                  # categories: claude-tooling, docs
│   ├── references/
│   │   ├── comment-classes.md       # the three finding classes, rules, examples
│   │   ├── never-touch.md           # pragmas, licences, directives, generated files
│   │   └── rewrite-guidelines.md    # how to generalize, rephrase, condense
│   └── scripts/
│       ├── extract_comments.py      # touched files → JSON comment worklist
│       └── receipt.py               # write/check .git/claude/comment-review/<sha>
├── agents/
│   └── comment-reviewer.md          # dispatchable subagent; runs the sweep in its own context
├── hooks/
│   ├── hooks.json                   # PreToolUse: Bash
│   └── scripts/pr-create-gate.py    # the sha-receipt gate
└── commands/
    └── comment-review.md            # /comment-review for manual runs
```

### Component boundaries

Three units, each independently testable, each ignorant of the others' concerns.

| Unit | Knows | Does not know |
|---|---|---|
| `pr-create-gate.py` | whether a receipt exists for the current HEAD | anything about comments |
| `extract_comments.py` | where comment spans are in a set of files | anything about comment quality |
| skill + agent | how to judge and rewrite a comment | how the gate or extractor work |

The skill holds the method. The agent is a thin wrapper that runs the method in its own context
so a forty-file sweep does not flood the main session.

### Control flow

```
gh pr create ...
  └─ PreToolUse(Bash) → pr-create-gate.py
       ├─ CLAUDE_SKIP_COMMENT_REVIEW=1 ................. exit 0, pass through
       ├─ no (gh|fj|mj|glab) (pr|mr) create in command .. exit 0, pass through
       ├─ receipt exists for HEAD sha .................. exit 0, pass through
       └─ otherwise → permissionDecision: deny
            reason: "dispatch the comment-reviewer agent, then retry"

comment-reviewer agent
  ├─ resolve base branch (upstream → merge-base → ask)
  ├─ git diff --name-only <base>...HEAD           → touched files
  ├─ extract_comments.py <files>                  → worklist (file, line, lang, text)
  ├─ judge each comment against classes A/B/C, skipping the never-touch set
  ├─ apply edits in place
  ├─ git commit -m "comments: …"   (only when edits were made)
  ├─ receipt.py write                             → receipt for the NEW HEAD
  └─ return summary: fixed by class, skipped with reasons

gh pr create ... → receipt matches HEAD → passes
```

### The gate

A `PreToolUse` hook on `Bash`, matching `(gh|fj|mj|glab)\s+(pr|mr)\s+create` in the command.
Denial is not fatal: the tool call is refused and the reason is fed back as text.

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny",
  "permissionDecisionReason": "Run comment-reviewer on this branch first, then retry."}}
```

The receipt lives at `.git/claude/comment-review/<sha>` — per-clone, never committed, removed
with the clone.

Keying on the **HEAD sha** rather than the session is what makes the gate honest:

- Retrying `pr create` without reviewing is still denied, so the gate cannot be walked past by
  repeating the command.
- New commits or an `--amend` produce a new sha, so the review runs against the code that ships.
- The receipt is written by the review, never by the hook, so the gate cannot rubber-stamp
  itself.

Because the agent commits its own edits, the receipt is written **after** that commit, against
the resulting HEAD. The loop closes on the next `pr create` attempt.

Escape hatch: `CLAUDE_SKIP_COMMENT_REVIEW=1` makes the hook exit 0 immediately.

## Review rules

### Class A — spec and plan leakage

Comments that only make sense to a reader holding the plan, ticket, or review thread. The code
outlives all three.

| Found | Action |
|---|---|
| `// As per step 3 of the plan, retry twice` | drop the provenance, keep the fact: `// Retry twice: upstream 502s on cold start` |
| `# New implementation (was using requests before)` | delete — history belongs in git |
| `// TODO from the spec: handle the empty case` | if handled, delete; if not, `// TODO(#142): empty input is unhandled` |
| `// Changed this to fix the bug Mark found` | delete, or restate as intent |
| `// This satisfies requirement 4.2` | delete unless requirement IDs are a real traceability convention in the repo |

Tell-tales: *plan, spec, step N, phase, requirement, ticket, as requested, as discussed, per the
design doc, previously, now we, I changed*.

### Class B — comment does not match the code's purpose

- **Drifted** — describes behaviour the code no longer has: a renamed variable, a changed
  default, a removed branch. Rewrite to match, or delete when the code is now self-evident.
- **Over-specific** — describes one caller's use of a general function (`// used by the login
  form` above a generic validator). Generalize to the function's contract.
- **Restates the code** — `// increment counter` above `counter += 1`. Delete, or replace with
  the rationale when one exists.

The governing bias: comments say **why**, not **what**. A comment earns its place when it
carries something the code cannot express — a constraint, a rationale, a non-obvious invariant,
a workaround and its reason.

### Class C — verbosity, judged by a no-loss test

Condensing is measured by density, never by length. Before replacing a comment the agent must
name every load-bearing fact in the original and point to it in the replacement. Load-bearing
means a constraint, unit, range, rationale, invariant, caveat, or ownership rule.

- If condensing would drop a load-bearing fact, the fact stays and only the surrounding words
  are cut.
- If no version is both shorter **and** at least as informative, the comment is left alone and
  reported.
- **Shorter but vaguer is a regression, not a fix.**

Hedging preambles go. Parameter documentation that only repeats the signature goes; the same
documentation carrying a unit, a range, or an ownership rule stays.

### Never touch

Enforced twice: as skip patterns in the extractor, and restated as rules in the skill.

- Licence headers, SPDX identifiers, copyright blocks
- Compiler and tool directives: `//go:embed`, `//go:build`, `# type:`, `# noqa`, `# pylint:`,
  `// eslint-disable`, `// @ts-`, `# fmt: off`, `<!-- prettier-ignore -->`, `// nolint`,
  `#pragma`
- Doc comments whose **structure** is load-bearing: godoc first-word convention, rustdoc
  intra-doc links, Sphinx, JSDoc, and Doxygen tag blocks. Reword inside them; never restructure.
- Generated-file markers (`Code generated by … DO NOT EDIT`) — skip the whole file
- Vendored and generated paths: `vendor/`, `node_modules/`, `*_pb2.py`, `*.pb.go`, `dist/`,
  `*.min.js`
- **Commented-out code** — report, never delete. Deleting parked code is not a comment fix.
- Translator and i18n notes, `NOTE:` and `WARNING:` blocks carrying a real caveat, TODOs with
  issue links

## Marketplace tooling changes

Both scripts currently assume skill-only plugins and must grow:

- **`promote-skill.py`** mirrors only `SKILL.md`, `references/`, and `scripts/` into
  `plugins/<name>/skills/<name>/`. It must also mirror the plugin-root `agents/`, `hooks/`, and
  `commands/` directories plus `plugin.json`, preserving them the way it already preserves
  `config.yaml`.
- **`validate-plugin.py`** must accept a plugin root containing those directories rather than
  flagging them, and should additionally check that `hooks.json` parses and that hook scripts
  are executable.
- **`just sync-groups` / `sync-marketplace`** need no change; they iterate `config.yaml` and
  pick up the skill unmodified.

### Known limitation: group installs carry the skill only

Group plugins symlink the **skill directory**, so `plugins/<group>/skills/comment-reviewer`
delivers `SKILL.md` and its references but not `agents/` or `hooks/`. Installing
`claude-tooling@kettleofskills` therefore yields the method without the gate. The gate requires
installing `comment-reviewer@kettleofskills` directly. This is documented in the skill body.

## Delivery

Follows the `charm-tui` precedent, because a hook installs only via the plugin path.

- Source of truth: `~/dotfiles/.claude/plugin-skills/comment-reviewer/` — deliberately **not**
  `~/.claude/skills/`, which is stow-symlinked and would load the skill twice, once as a
  personal skill and once as `comment-reviewer:comment-reviewer`.
- `plugin-skills` is already listed in `.stow-local-ignore`; no change needed.
- Promote with
  `promote-skill.py comment-reviewer --source ~/dotfiles/.claude/plugin-skills --categories claude-tooling,docs`.
- Enable in the tracked `~/dotfiles/.claude/settings.json` under `enabledPlugins` as
  `comment-reviewer@kettleofskills`.
- This machine's `~/.claude/settings.json` is a real file rather than the stowed symlink, so the
  `enabledPlugins` entry must be applied to both copies.

## Verification

Three layers. Only the last needs a model.

| Layer | Test |
|---|---|
| `pr-create-gate.py` | Hook JSON on stdin: non-PR command passes; `gh pr create` without a receipt denies; with a matching receipt passes; a stale sha denies; `CLAUDE_SKIP_COMMENT_REVIEW=1` passes. Also `fj pr create`, `glab mr create`, and a command that merely mentions the phrase inside a quoted argument, which must not trigger. |
| `extract_comments.py` | Fixture files for Go, Python, Rust, TypeScript, Shell, Lua, SQL, HTML, Nix, and YAML with known comment positions. Adversarial cases: `#` inside a Python string, `//` inside a Go string literal, a URL containing `//`, nested `/* */`. Assert exact spans and assert never-touch lines are skipped. |
| End to end | A scratch git repository whose branch seeds violations of all three classes plus one example of every never-touch category. Assert the violations are fixed, the never-touch lines are byte-identical, a commit exists, and the receipt matches the new HEAD. |

The adversarial extractor cases carry more weight than their size suggests. Missing a comment is
a miss; editing a string literal that looked like a comment is a bug. The extractor therefore
errs toward skipping when a span is ambiguous, and the agent confirms each span is genuinely a
comment before editing it.

## Decisions taken

| Question | Decision |
|---|---|
| Trigger | `PreToolUse` gate on `pr create`, plus skill and dispatchable agent |
| Gate behaviour | Deny once per HEAD sha; receipt written by the review |
| Fix mode | Auto-fix all three classes |
| Extraction | Script-assisted, per-language comment token table |
| Scope | Every comment in every file the branch touched |
| Commit | The agent commits its own fixes, then writes the receipt |
| Condensing | No-loss test; density over length |

## Open item

`mj` is not installed on this machine (`gh` and `fj` are; `glab` is present as the GitLab CLI).
The gate's pattern includes `mj` so the command is covered regardless, but the intended tool
should be confirmed in case its subcommand is not `pr create`.
