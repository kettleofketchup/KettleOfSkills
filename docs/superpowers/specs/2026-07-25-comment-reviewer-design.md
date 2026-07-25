# comment-reviewer — Design

**Date:** 2026-07-25
**Status:** Revised after multi-agent adversarial review; ready for implementation planning

## Purpose

Comments written during implementation carry the shape of the process that produced them:
references to a plan step, a spec requirement, a review comment, or a bug someone found. They
also drift out of sync with the code and grow longer than the knowledge they carry. None of
that survives usefully into the life of the code.

`comment-reviewer` sweeps a development branch before its pull request is opened, rewrites the
comments that fail three tests, and gates PR creation until it has run.

## Scope

Comments in **every file the branch touched**, compared against the merge base with trunk — not
only the lines the branch changed. A change that makes a nearby comment wrong is exactly the
case worth catching, and comment cleanup is cheap to review.

Both readings of "multiple languages" are in scope:

- **Programming languages** — extraction covers `//`, `#`, `--`, `%`, `;`, `/* */`, `"""`,
  `'''`, `<!-- -->`, `(* *)`, `=begin`/`=end`, `<# #>`, `{/* */}`, `{{/* */}}`, `{{! }}`.
  Multi-language files (`.vue`, `.svelte`, `.astro`, `.html`) require per-block token selection;
  where that is not implemented, the file is skipped and counted.
- **Natural languages** — every rewrite is written in the same natural language as the comment
  it replaces. Nothing is ever translated. For a mixed comment, the language is that of the
  prose. If the agent cannot confidently write in that language, it reports instead of editing.

**Markdown is out of scope.** `.md` files are skipped entirely. This repository alone has 628
tracked `.md` files whose `# Step 1:`-style headings and fenced examples are content, not
commentary.

## Architecture

One marketplace plugin, `comment-reviewer`, carrying four parts. It is the first plugin in the
catalog that is more than a skill.

```
plugins/comment-reviewer/
├── .claude-plugin/
│   └── plugin.json                  # name + description; components are AUTO-DISCOVERED
├── skills/comment-reviewer/
│   ├── SKILL.md                     # the review method (<150 lines)
│   ├── config.yaml                  # categories: claude-tooling
│   ├── references/
│   │   ├── comment-classes.md       # the three finding classes, rules, examples
│   │   ├── never-touch.md           # mechanical and judgment skip tiers
│   │   └── rewrite-guidelines.md    # how to generalize, rephrase, condense
│   └── scripts/
│       ├── gitpaths.py              # THE path resolver — receipt root, repo state
│       ├── extract_comments.py      # touched files → JSON comment worklist
│       └── receipt.py               # write/read the receipt
├── agents/
│   └── comment-reviewer.md          # dispatchable subagent; runs the sweep in its own context
├── hooks/
│   ├── hooks.json                   # PreToolUse: Bash
│   └── scripts/pr-create-gate.py    # the sha-receipt gate
├── commands/
│   └── comment-review.md            # /comment-review → dispatches the agent, nothing more
└── tests/                           # pytest suites for gate, extractor, resolver
```

**The manifest lives at `.claude-plugin/plugin.json`, not the plugin root.** Verified: 46 of the
52 installed manifests on this machine are at `.claude-plugin/plugin.json`, and
`plugin-dev/skills/plugin-structure/references/manifest-reference.md:9` states "Claude Code will
not recognize plugins without this file in the correct location." The manifest carries `name`
and `description` only — components are discovered by directory convention, not declared. The
`hookify` plugin's manifest lists no components yet ships working `agents/`, `commands/`,
`hooks/`, and `skills/`.

> **Do not follow `~/.claude/skills/claude-code/references/plugins.md` or `hooks.md`.** Both are
> stale: they show a root-level `plugin.json` with `"hooks": "hooks/hooks.json"` wiring and
> `pre-tool`/`$TOOL_NAME` hook shapes. Use
> `plugin-dev/skills/plugin-structure` and `plugin-dev/skills/hook-development` instead.

### hooks.json

The top-level `hooks` wrapper is required; an unwrapped file registers nothing. Verified against
the three working `hooks.json` files installed on this machine, all of which use
`${CLAUDE_PLUGIN_ROOT}`.

```json
{"hooks": {"PreToolUse": [{"matcher": "Bash",
  "hooks": [{"type": "command",
    "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/pr-create-gate.py\"",
    "timeout": 5}]}]}}
```

`${CLAUDE_PLUGIN_ROOT}` is mandatory in every path the plugin references, including the agent's
and command's invocation of `extract_comments.py`. Installed plugins live under a per-version
cache path, so any relative path fails.

### Component boundaries

| Unit | Knows | Does not know |
|---|---|---|
| `gitpaths.py` | how to resolve the receipt root and repo state from a cwd | comments, gates |
| `pr-create-gate.py` | whether a valid receipt exists for the current HEAD | anything about comments |
| `extract_comments.py` | where comment spans are, and which are mechanically off-limits | comment quality |
| skill + agent | how to judge and rewrite a comment | how the gate or extractor work |

The skill holds the method. The agent is a thin wrapper that runs the method in its own context
so a forty-file sweep does not flood the main session. `/comment-review` does nothing but
dispatch the agent, optionally with an explicit base ref — the method lives in exactly one place.

`hooks/scripts/` and `skills/comment-reviewer/scripts/` cannot import each other, so
`gitpaths.py` is vendored to both locations from one source of truth, and the promotion tooling
copies it to both. A single test asserts the two copies are byte-identical.

## The gate

A `PreToolUse` hook on `Bash`. It decides between three outcomes, never two.

| Condition | Outcome |
|---|---|
| Command is not a PR-create invocation | exit 0, pass through |
| Skip requested (below) | exit 0, pass through |
| Valid receipt exists for HEAD tree | exit 0, pass through |
| Receipt genuinely absent for a resolved HEAD | `deny` with instructions |
| **Any resolution error** — not a repo, `rev-parse` fails, no commits, git dir unreadable or unwritable, trunk unresolvable | **exit 0 with a warning note** |
| Receipt present but unparseable | `deny` — see below |

**The gate fails open.** As originally written, every infrastructure error was
indistinguishable from "unreviewed" and denied — and because running the reviewer hits the same
wall, the user would be locked out with advice that cannot help. The repo's own hook precedent
(`~/dotfiles/.claude/hooks/preexisting-nudge.py`) exits 0 on malformed input for the same reason.

**An unparseable receipt is the one exception, and it denies.** Fail-open is for cases where the
reviewer itself cannot run. A corrupt receipt is not one of those: it is indistinguishable from no
receipt, and re-running the review overwrites it. Denying there costs one review and loses
nothing, whereas passing would let a PR ship on the strength of a file nobody can read.

Denial shape:

```json
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny",
  "permissionDecisionReason": "Run comment-reviewer on this branch first, then retry."}}
```

Denial is not fatal: the tool call is refused and the reason is fed back as text.

### Command matching

Tokenised, never a substring regex over the raw command. A regex matches
`git commit -m "prep for gh pr create"`, which the verification layer explicitly forbids.

**Lex first, then split.** Splitting the raw string before lexing cuts through quotes:
`gh pr create --title "fix; refactor"` becomes two unbalanced halves, `shlex` raises on both, and
a genuine PR creation goes invisible to the gate. A multi-line `--body` fails identically, and
both are mainline shapes. Verified by reproduction.

1. Strip heredoc bodies — their contents are data, not commands.
2. Lex the whole command with `shlex.shlex(..., posix=True, punctuation_chars=True)` and
   `whitespace_split = True`. On `ValueError` (unbalanced quotes), pass through.
3. Split the resulting token stream on the operator tokens `;`, `&&`, `||`, `|`, `&`, newline.
   `posix=True` already removes unquoted `#` comments.
4. Per segment, drop leading `VAR=value` assignments and a leading `env`.
5. Match when a segment's first token is `gh`, `fj`, `mj`, or `glab` **and** an adjacent
   `(pr|mr, create)` token pair appears in it. Scanning for the adjacent pair rather than the
   first two non-option arguments is what handles option *values* such as
   `fj -H codeberg.org pr create`.
6. A skip assignment releases only **its own segment**. In
   `CLAUDE_SKIP_COMMENT_REVIEW=1 ls; gh pr create` the skip belongs to `ls`; treating it as
   global would be a free bypass.

**Accepted bypasses**, documented rather than pretended away: `gh api .../pulls -X POST`, user
`gh` aliases, the web UI, and wrapper recipes such as `just pr`. The last is concrete here —
`just-interceptor` is enabled in the tracked settings and redirects raw commands to just
recipes, so in the most carefully configured repos the gate may never fire.

### The receipt

**The path is resolved by git, never constructed from a literal `.git/`.** Reproduced on this
machine: in a linked worktree `.git` is a regular file containing a `gitdir:` pointer, so
`os.makedirs('.git/claude/comment-review')` raises `NotADirectoryError`. `receipt.py write`
would fail, the gate would then deny forever, and the escape hatch would not help. Worktrees are
this user's mandated workflow, not an edge case.

Receipt root: `$(git rev-parse --absolute-git-dir)/claude/comment-review/`. **Per-worktree is
chosen deliberately over `--git-common-dir`** so that two worktrees on different branches cannot
satisfy each other's gate. Resolution runs against the `cwd` supplied in the hook's stdin JSON.

Each receipt is a file named `<tree-sha>` containing one JSON object:

```json
{"commit_sha": "…", "tree_sha": "…", "base_sha": "…", "resolved_base_ref": "origin/main",
 "written_at": "…", "fixed": {"A": 3, "B": 1, "C": 2}, "skipped": [...],
 "reported": [...], "partial": false}
```

**Keyed on `git rev-parse HEAD^{tree}`, not the commit sha.** A reword, squash, or rebase that
does not change content still validates, which stops the loop that would otherwise re-block on
every amend. The gate's pass condition is: the file exists, parses, and its `resolved_base_ref`
still resolves to the same base — recomputing the base closes the hole where retargeting the PR
widens the touched-file set while an old receipt still passes.

`receipt.py write` keeps the newest K receipts and stores a timestamp; the gate treats receipts
past a stated TTL as absent. `git reset --hard <reviewed-sha>` restoring a stale-but-valid
receipt is an accepted limitation.

### Skip mechanism

`CLAUDE_SKIP_COMMENT_REVIEW=1 gh pr create` — the form anyone would type — **does not work as an
environment variable**: the hook is spawned by Claude Code and inherits Claude Code's
environment, not the environment of the command it inspects. Two mechanisms that do work:

1. A leading `CLAUDE_SKIP_COMMENT_REVIEW=1` assignment **in the inspected command string**,
   which the tokeniser already strips and can therefore detect.
2. A sentinel file under the receipt root, for a durable per-repo opt-out.

Both are implemented; the tests assert mechanism 1. A `settings.json` `env` entry also works but
requires a session restart, which is stated in the skill.

## Control flow

```
gh pr create ...
  └─ PreToolUse(Bash) → pr-create-gate.py → pass | deny | fail-open

comment-reviewer agent
  ├─ resolve trunk: git symbolic-ref refs/remotes/<remote>/HEAD, else main, else master
  ├─ base = git merge-base <trunk> HEAD        ← NEVER the branch's own upstream
  ├─ if base unresolved → write NO receipt, return base_unresolved
  ├─ preconditions: no rebase/merge/cherry-pick in progress, else refuse, no receipt
  ├─ git diff --name-only --diff-filter=ACMR <base>...HEAD    → touched files
  ├─ extract_comments.py (paths via stdin)     → worklist (file, start_line, end_line, lang, text)
  ├─ judge each span: mechanical skips → commented-out code → judgment skips → A → B → C
  ├─ apply edits per file in DESCENDING start_line order
  ├─ verify never-touch spans byte-identical; run repo build/lint/test; revert sweep on failure
  ├─ git commit -m "comments: <n> rewritten across <m> files" -- <explicit edited paths>
  ├─ if commit fails or HEAD did not move while edits were pending → abort, NO receipt
  ├─ receipt.py write                          → keyed to the resulting HEAD tree
  └─ return per-class counts + report-only findings
```

**Base resolution never uses the branch's own upstream.** Reproduced: after the routine
`git push -u origin feat`, `@{u}` is `origin/feat`, so `git diff --name-only @{u}...HEAD` is
empty — the sweep examines zero files, makes no edits, and would still write a receipt that
satisfies the gate. That is a silent self-bypass on a mainstream workflow. `merge-base
origin/main` correctly yields the branch's files.

**"Ask the user" is not available** to a non-interactive subagent. Unresolvable base returns
`base_unresolved` to the main session, which resolves it and re-dispatches with an explicit ref.

### Commit discipline

- Commit an **explicit file list** — never `git commit -a`, never `-A`, never a bare
  `git commit`. A bare commit would ship whatever was already staged under a `comments:` message;
  `-a` would sweep in every unrelated work-in-progress edit, recoverable only by interactive
  rebase.
- **Dirty-file precondition:** any file with pre-existing staged or unstaged modifications is
  skipped with reason `dirty`. The sweep never mixes its edits with work in progress.
- **Commit-success check:** if `git commit` exits non-zero, or HEAD did not move while edits were
  pending, the agent aborts and writes **no** receipt. Without this, a reformatting or rejecting
  pre-commit hook leaves HEAD unmoved while `receipt.py write` certifies the unfixed tree — the
  gate passes and the PR ships with none of the rewrites.
- No edits means no commit; the receipt is written against the current HEAD tree.
- The commit message is pinned in `agents/comment-reviewer.md`: one subject line, no body, **no
  watermark and no `Co-Authored-By` trailer**. This plugin ships publicly, so the convention
  lives in the agent file rather than being inherited from the installing user's CLAUDE.md.

### Edit application

Edits are applied per file in **descending `start_line` order**, or by unique-text match with
line numbers used only to locate context. Deletion and multi-line condensing are first-class
actions here, so every edit after the first in a file would otherwise invalidate the remaining
line numbers and silently corrupt code. After editing, never-touch spans in the file are checked
byte-identical before staging.

### Worklist bounds

- `--diff-filter=ACMR` excludes deleted paths, which would otherwise be handed to the extractor
  as nonexistent files.
- Extension→language table, with a shebang fallback; unknown extension → skip, counted.
- Binary sniff (NUL byte in the first 8 KiB) → skip. Per-file size ceiling.
- Caps on files and edits per run. On overflow the agent reports and writes the receipt with
  `partial: true`, and persists the remaining worklist so a repeated dispatch makes progress
  rather than hitting the same wall.
- Paths are passed via stdin, not argv, to avoid length limits.

## Review rules

Precedence, applied in this order, with any skip winning over any class:

**mechanical never-touch → commented-out code → judgment never-touch → Class A → B → C**

This ordering is stated because rules genuinely collide:
`// NOTE: as requested by the security review, retry twice` matches both a never-touch entry and
a Class A tell-tale with opposite actions.

### Class A — spec and plan leakage

Comments that only make sense to a reader holding the plan, ticket, or review thread.

| Found | Action |
|---|---|
| `// As per step 3 of the plan, retry twice` | drop the provenance, keep the fact: `// Retry twice: upstream 502s on cold start` |
| `# New implementation (was using requests before)` | delete |
| `// TODO from the spec: handle the empty case` | if handled **with confirmed evidence in the same function**, delete; else `// TODO:` retaining the text |
| `// Changed this to fix the bug Mark found` | **report, do not delete** — the reason is recoverable from neither the comment nor the code |
| `// This satisfies requirement 4.2` | **report** — never delete an ID-shaped traceability comment |

The tell-tale words — *plan, spec, step N, phase, requirement, ticket, as requested, as
discussed, per the design doc, previously, now we, I changed* — are **candidates requiring a
second test**: the referenced artifact must be a development-process artifact, not the code's
subject matter. Explicit non-triggers: RFC, standard, and protocol references; algorithm step
and phase numbering; concurrency state descriptions. `# Step 1: CRDs for target version` exists
in this very repository, where the ordering *is* the content.

**Class A has the same safety valve as Class C:** when a comment references a fix, bug,
incident, or abandoned approach and the reason is not recoverable from surrounding code, it is
reported, not deleted. **Never invent an issue, ticket, or PR reference** — carry over only an
identifier already present in the comment or supplied by the user. And "history belongs in git"
is false under squash-merge, so it is not a justification on its own.

### Class B — comment does not match the code's purpose

- **Drifted** — describes behaviour the code no longer has. Rewrite to match, or delete when the
  code is now self-evident.
- **Over-specific** — describes one caller's use of a general function. Generalize *only* to what
  is verifiable from the body and signature; **never widen a stated guarantee.** Prefer dropping
  the caller name over asserting a new contract. If generalizing requires a claim the code does
  not support, report instead. Turning `// used by the login form` into "validates any email
  address" produces a confidently wrong comment that invites callers to rely on behaviour that
  may not exist — worse than the stale comment it replaced. A `// used by` pointing at a
  non-obvious consumer is retained where no other cross-reference exists.
- **Restates the code** — `// increment counter` above `counter += 1`. Delete, or replace with
  the rationale when one exists.

The governing bias: comments say **why**, not **what**.

### Class C — verbosity, judged by a no-loss test

Condensing is measured by density, never by length. Before replacing a comment the agent must
enumerate every load-bearing fact in the original and point to it in the replacement — a
constraint, unit, range, rationale, invariant, caveat, or ownership rule. **The enumeration is
emitted in the returned summary for every Class C rewrite**, so the test leaves an auditable
artifact instead of being self-refereed.

- If condensing would drop a load-bearing fact, the fact stays and only surrounding words are cut.
- If no version is both shorter **and** at least as informative, the comment is left alone and
  reported.
- **Shorter but vaguer is a regression, not a fix.**
- No rewrite may drop a numeric literal, unit, or identifier present in the original — asserted
  by test.
- "Shorter" is measured in clauses, not characters: raw length is not comparable across scripts.

Parameter documentation that only repeats the signature goes — **but only where the language's
signature actually carries the type.** All JSDoc tag blocks in `.js`/`.jsx` are off-limits,
because there the tags are the only type information.

### Never touch — mechanical tier

Expressible as regexes and path globs, enforced by the extractor.

- **Position-locked and executable:** any comment in the **first two lines of a file**; shebangs
  and `#!nix-shell` continuations; PEP 263 encoding lines; Ruby `# frozen_string_literal:` and
  `# typed:`; Dockerfile `# syntax=`, `# escape=`, `# check=`; vim and emacs modelines.
- **Consumed by a compiler, bundler, database, or interpreter:** the cgo preamble above
  `import "C"` and `//export`; SQL `/*! */` version-gated blocks and `/*+ */` optimizer hints;
  `//# sourceMappingURL=`; JSX/Flow/TS pragmas (`/** @jsx */`, `// @flow`, `/// <reference`);
  bundler magic comments and `/*#__PURE__*/`.
- **Suppression directives** — matched by family, not enumeration: any comment matching
  `(disable|enable|ignore|skip|noqa|nolint|nocover|no cover|off|on)\b` in directive position
  after a known tool prefix. Covers golangci-lint, eslint, ts, prettier, black, isort, mypy,
  pylint, shellcheck, rubocop, hadolint, checkov, tfsec, tflint, trivy, semgrep, yamllint,
  ansible-lint, NOSONAR, noinspection, ReSharper, `@formatter:off`, CHECKSTYLE, markdownlint,
  vale, coverage pragmas (`# pragma: no cover`, `/* istanbul ignore next */`, `// c8 ignore`).
  **Preserved byte-for-byte including whitespace** — golangci-lint honours `//nolint:` only with
  no space after the slashes, so a Class C spacing tidy would silently disable the suppression
  and break the build on the original lint.
- **Test oracles** — hard skip, not "reword inside": any doc comment containing `>>>`, a code
  fence, `.. code-block::`, `// Output:`, or `# Output:`; any module docstring that is a docopt
  usage block; any Sphinx label. Rewording is permitted only in doc comments containing none of
  these markers.
- **Codegen sources:** all `// +`-prefixed Go markers (kubebuilder, deepcopy-gen, genclient);
  doc comments on exported fields under `api/` and `apis/`; comments in `.proto`, `.graphql`, and
  OpenAPI schema files.
- **SQL migrations:** `+goose`, `migrate:up`/`down`, `+migrate`, `-- name: … :one`, `atlas:`.
  Simplest form: skip `.sql` under any `migration*` path entirely.
- **Licence and provenance:** licence headers, SPDX identifiers, copyright blocks.
- **Generated files** — marker regex `@generated|[Cc]ode generated|[Aa]uto-?generated|DO NOT
  (EDIT|MODIFY)|<auto-generated>` over the first 30 lines skips the whole file.
- **Paths:** `vendor/`, `node_modules/`, `third_party/`, `.venv/`, `target/`, `build/`, `out/`,
  `gen/`, `generated/`, `.terraform/`, `Pods/`, `dist/`, `*.min.js`, `*_pb2.py`, `*.pb.go`,
  `*.pb.gw.go`, `*_grpc.pb.py`, `*_generated.go`, `*.g.dart`, `*.freezed.dart`, lockfiles.
- **Fixtures and byte-compared data** — `testdata/`, `fixtures/`, `__fixtures__/`, `golden/`,
  `snapshots/`, `*.snap`, `*.golden`, and `.po`/`.pot` (where `#, fuzzy` is a functional flag).
  Fixture files are byte-compared by the tests that consume them, so an edit inside one fails a
  test nobody will connect to a comment sweep — including this plugin's own extractor fixtures.
- **Template comments:** `svelte-ignore`, HTML conditional comments, Helm and Handlebars template
  comments, `<!-- BEGIN/END … -->` region markers. Helm comment deletion can change rendered
  whitespace through adjacent `{{-` trimming, altering an applied manifest.

### Never touch — judgment tier

Requires reading, so it lives in the skill, not the extractor.

- Doc comments whose **structure** is load-bearing: godoc first-word convention, rustdoc
  intra-doc links, Sphinx, JSDoc, and Doxygen tag blocks.
- **Commented-out code** — report, never delete. Mechanical tiebreak, tested *before* Class B:
  the body lexes as a statement, or contains an assignment, a call with parentheses, a block
  delimiter, or a keyword in statement position. Mixed prose and code counts as code.
- Comments whose first token is `NOTE`, `WARNING`, `CAUTION`, `SAFETY`, `HACK`, `XXX`, or
  `FIXME` are never deleted — only condensable under the no-loss test.
- TODOs carrying an issue link.
- Translator and i18n notes.

### Report-only findings

Three rules mandate reporting rather than fixing, so the destination is defined: the agent
returns per-class fixed counts plus a list of `{file, line, class, reason}`. The main session
echoes it to the user before the `pr create` retry, and it is recorded in the receipt body.
Report-only findings never block the receipt.

## Marketplace tooling changes

### `promote-skill.py`

From the single source directory `~/dotfiles/.claude/plugin-skills/comment-reviewer/`, two
destination roots:

| Source | Destination | Mechanism |
|---|---|---|
| `SKILL.md`, `references/`, `scripts/` | `plugins/<n>/skills/<n>/` | existing `MIRRORED_DIRS` |
| new `PLUGIN_ROOT_DIRS = ("agents", "hooks", "commands", "tests", ".claude-plugin")` | `plugins/<n>/` | new second destination root, with its own mkdir on the `is_new` path |

All of these are **mirrored** (rmtree + recopy via `mirror_dir`), not copied-once.
`config.yaml` remains the only preserved file — it is preserved precisely *because* it is never
copied. `copytree`/`copy2` already preserve the executable bit. `tests/` is in
`PLUGIN_ROOT_DIRS` because `pr-create-gate.py` lives outside the directories promotion currently
mirrors, so its tests would otherwise have nowhere to live that survives promotion.

### `validate-plugin.py`

Purely additive — `validate_plugin()` only ever inspects `plugins/<name>/skills/<name>/`, so it
does not flag plugin-root directories today. New static checks:

- manifest present at `.claude-plugin/plugin.json` with `name` matching the directory
- `hooks.json` parses and has a top-level `hooks` key
- every hook `command` string contains `${CLAUDE_PLUGIN_ROOT}`
- referenced scripts exist and are executable
- the two `gitpaths.py` copies are byte-identical

### Unchanged, and one correction

`just sync-groups` / `sync-marketplace` need no change. The group-install limitation is
**narrower than first stated**: `sync-groups` symlinks the whole skill directory
(`ln -s "../../${plugin}/skills/${skill}"`), so group installs *do* carry `scripts/`. Only
`agents/`, `hooks/`, `commands/`, and the manifest are dropped. The gate therefore requires
installing `comment-reviewer@kettleofskills` directly.

**Category: `claude-tooling` only.** The `docs` group is documentation *tooling* (mkdocs,
zensical), which this is not. `promote-skill.py` ignores `--categories` on an existing plugin, so
it must be right on the first promotion.

**Do not enable both** `comment-reviewer@kettleofskills` and a group containing it —
`sync-groups` publishes every skill into `all` plus each category, so both would load the
identical skill under two namespaces. The direct install wins and is the documented choice.

### Repo docs this design invalidates

- `kettle-skill-creator/references/plugin-structure.md` — must document both plugin shapes, and
  drop the "no `scripts/` within individual skills" prohibition (9 marketplace plugins already
  ship one).
- `kettle-skill-creator/SKILL.md` — its description of what promotion mirrors.
- The manifest `version` field is **omitted**: nothing in the release path maintains it, and
  `just git::version` does not rewrite plugin manifests.

## Delivery

Follows the `charm-tui` precedent, because a hook installs only via the plugin path.

- Source of truth: `~/dotfiles/.claude/plugin-skills/comment-reviewer/` — deliberately **not**
  `~/.claude/skills/`, which is stow-symlinked and would load the skill twice.
- `plugin-skills` is already in `.stow-local-ignore`; no change needed.
- `promote-skill.py comment-reviewer --source ~/dotfiles/.claude/plugin-skills --categories claude-tooling`
- Enable in the tracked `~/dotfiles/.claude/settings.json` under `enabledPlugins`.
- This machine's `~/.claude/settings.json` is a real file rather than the stowed symlink, so the
  entry must be applied to both copies.

## Verification

Tests live in `tests/` at the plugin root and run via a new `just test` recipe (pytest over
`plugins/*/skills/*/scripts/tests` and plugin-root `tests/`). The repo currently has no test
runner and its two existing test directories are orphans with no invoking recipe.

| Layer | Test |
|---|---|
| `gitpaths.py` | primary clone, **linked worktree**, **submodule**, non-repo directory, repo with no commits, unwritable git dir. Assert a real directory is returned or a clean failure signalled. |
| `pr-create-gate.py` | Hook JSON on stdin: non-PR command passes; `gh pr create` without a receipt denies; with a valid receipt passes; stale tree denies; retargeted base denies; expired receipt denies; skip assignment in the command passes; sentinel file passes. Fail-open cases: non-repo, `rev-parse` failure, unparseable receipt — all exit 0. False-positive guard: `git commit -m "prep for gh pr create"` must **not** trigger. Variants: `fj pr create`, `fj -H host pr create`, `glab mr create`, `PAGER= gh pr create`, `x && gh pr create`, heredocs. |
| `extract_comments.py` | Fixtures for Go, Python, Rust, TypeScript, Shell, Lua, SQL, HTML, Nix, YAML with known spans. Adversarial: `#` inside a Python string, `//` inside a Go string literal, a URL containing `//`, nested `/* */`. Assert exact `(start_line, end_line)` spans. Assert every mechanical never-touch category is skipped. Assert binary, oversized, unknown-extension, and deleted files are skipped and counted. |
| Class rules | **Negative fixtures whose correct outcome is "left alone and reported":** a dense comment carrying a unit, a range, and a rationale; a JSDoc `@param` in `.js`; `# Step 1:` where ordering is the content; `//nolint:errcheck`. Assert no rewrite drops a numeric literal, unit, or identifier. |
| End to end | Scratch repo seeding violations of all three classes plus one example of every never-touch category. Assert violations fixed, never-touch lines byte-identical, one commit with the pinned message and no trailer, receipt matching the new HEAD tree. **Idempotency:** a second run makes zero edits and still writes a receipt. Pre-commit-rejection and pre-staged-unrelated-changes cases. |
| **Wiring** | Install the plugin from the local marketplace path, start a fresh session, run a real `gh pr create` in the scratch repo and assert the denial reason appears; run the agent and assert the same command then passes. |

The wiring layer exists because the others cannot catch wiring: they pipe JSON straight into the
script and assert on files, so manifest location, the `hooks.json` wrapper,
`${CLAUDE_PLUGIN_ROOT}` expansion, `matcher: "Bash"`, and the fact that plugin hooks load only at
session start would all pass green while the plugin does nothing.

The adversarial extractor cases carry more weight than their size suggests. Missing a comment is
a miss; editing a string literal that looked like a comment is a bug. The extractor errs toward
skipping when a span is ambiguous, and the agent confirms each span is genuinely a comment before
editing it.

## Decisions taken

| Question | Decision |
|---|---|
| Trigger | `PreToolUse` gate on `pr create`, plus skill and dispatchable agent |
| Gate behaviour | Deny once per HEAD tree; fail open on any error; receipt written by the review |
| Fix mode | Auto-fix all three classes |
| Extraction | Script-assisted, per-language token table plus mechanical skip tiers |
| Scope | Every comment in every file the branch touched; `.md` excluded |
| Base | `merge-base` with trunk; never the branch's own upstream |
| Commit | Agent commits its own fixes with an explicit file list, then writes the receipt |
| Condensing | No-loss test with an emitted fact enumeration; density over length |
| Category | `claude-tooling` only |

## Honest limits

- The receipt is a file the agent could `touch`. The tree key defeats accidental retries and
  stale reviews and is a nudge a cooperating agent cannot forget — it is **not** a control
  against an agent that chooses to bypass it.
- The gate does not see `gh api`, `gh` aliases, the web UI, or `just pr` wrappers.
- Auto-fixing across whole touched files, then auto-committing, will put comment changes in a PR
  on lines the branch did not otherwise touch. The mechanical skip tiers, the report-only valves,
  and the post-edit build/test check are what keep that in bounds.

## Open item

`mj` is not installed on this machine (`gh` and `fj` are; `glab` is present). The matcher includes
`mj` regardless, but its actual subcommand should be confirmed in case it is not `pr create`.
