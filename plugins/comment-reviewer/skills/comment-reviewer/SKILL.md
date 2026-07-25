---
name: comment-reviewer
description: Reviews code comments across languages before a PR opens. Use when finishing a development branch, before merging, or when a pr create was blocked pending comment review.
---

# comment-reviewer

Sweep every comment in every file the current branch touched, rewrite the ones that fail
three tests, and leave a receipt so `gh pr create` (and `fj`/`glab pr|mr create`) is not
blocked again for the same tree. Use this skill when finishing a development branch, right
before opening its PR, or whenever a `pr create`/`mr create` call was denied pending review.

`.md`/`.markdown`/`.mdx` files are out of scope entirely — do not open them for review.

## Pipeline

1. **Resolve trunk**, then **base = `git merge-base <trunk> HEAD`.** Never resolve the base
   from the branch's own upstream (`@{u}`). After `git push -u origin feat`,
   `git diff @{u}...HEAD` is empty — the sweep would silently examine zero files and still be
   able to write a receipt that satisfies the gate. `merge-base` against trunk is the only
   correct base. If trunk or the merge-base cannot be resolved, write **no receipt** and
   report `base_unresolved` rather than guessing.
2. **Touched files** — `git diff --name-only --diff-filter=ACMR <base>...HEAD`. Skip any file
   with pre-existing staged or unstaged modifications (reason `dirty`); never mix this sweep's
   edits with work already in progress.
3. **Extract** — pipe the touched paths (repo-relative, newline-separated on stdin) to
   `scripts/extract_comments.py`. It returns every comment span per file, each already tagged
   with a mechanical skip reason where one applies. Do not re-derive those reasons yourself.
4. **Judge** every remaining span using the precedence order below.
5. **Edit** — apply accepted fixes **per file, in descending `start_line` order.** Deletions
   and multi-line condensing invalidate every later line number in that file; editing
   bottom-up is what keeps them valid throughout.
6. **Verify** — re-check that every never-touch span in each edited file is still
   byte-identical to the original, then run the repo's build/lint/test step. Revert the whole
   sweep on any failure rather than leaving a partial edit.
7. **Commit** — see Commit rules below.
8. **Receipt** — see Receipt rules below.
9. Return per-class fixed counts plus the report-only findings list
   (`{file, line, class, reason}`) so the caller can echo it before retrying `pr create`.

## Precedence — any skip beats any class

```
mechanical never-touch → commented-out code → judgment never-touch → Class A → B → C
```

A span can match both a never-touch entry and a class tell-tale with opposite actions (for
example `// NOTE: as requested by the security review, retry twice` reads as both a
`protected-prefix` never-touch and a Class A tell-tale). The never-touch tiers and the
commented-out-code tiebreak always win; a class is only reached once both tiers have cleared
the span. Full rule tables: `references/never-touch.md`.

## Classes — full rules and examples in `references/comment-classes.md`

| Class | Problem | Typical action |
|---|---|---|
| **A** — spec/plan leakage | comment only makes sense to someone holding the plan, ticket, or review thread | drop the provenance, keep the fact — or delete outright; **report, never delete or invent an ID**, when the reason is unrecoverable or the comment is ID-shaped traceability |
| **B** — comment vs. code mismatch | drifted, over-specific to one caller, or just restates the code | rewrite to match, generalize only to what's verifiable (**never widen a stated guarantee**), or delete a pure restatement |
| **C** — verbosity | comment carries more words than load-bearing facts | condense under the no-loss test, emitting the fact enumeration; **leave alone and report** if no version is both shorter and at least as informative |

Never-touch rules, both the mechanical tier the extractor enforces and the judgment tier that
requires reading, are in `references/never-touch.md` — including the exact `skip` reason
strings (`position-locked`, `directive`, `licence`, `test-oracle`, `protected-prefix`,
`excluded-path`, `generated`) so they can be reported verbatim. How to actually write an
accepted rewrite — generalizing without over-claiming, rephrasing to *why* not *what*,
condensing, and staying in the comment's original natural language with no translation — is
in `references/rewrite-guidelines.md`.

## Commit rules

- Commit with an **explicit file list** — `git commit -m "comments: <n> rewritten across <m>
  files" -- <edited paths>`. **Never `git commit -a`, never `-A`, never a bare `git commit`** —
  either would ship whatever else was staged or dirty under a message that claims only comment
  changes.
- One subject line only. **No body, no watermark, no `Co-Authored-By` trailer** — this plugin
  ships publicly and is not installed by every user who has that convention in their own
  `CLAUDE.md`.
- If `git commit` exits non-zero, or `HEAD` did not move while edits were pending (a
  reformatting or rejecting pre-commit hook, for instance), **abort and write no receipt.**
  Certifying an unfixed tree is worse than leaving the PR blocked.

## Receipt rule

Write the receipt **only after a successful commit, or after a sweep that made no edits at
all** (nothing to fix, or everything found was report-only). Never write a receipt against a
tree that still contains the violations this sweep found.

## Install caveat

The `PreToolUse` hook and the dispatchable agent ship **only** with the direct plugin install,
`comment-reviewer@kettleofskills`. A group install carries this skill and its `scripts/` (group
sync symlinks the whole skill directory), but **not** `hooks/`, `agents/`, or `commands/` — so
a group-only install can judge comments if invoked manually, but the `pr create` gate will
never fire and `/comment-review` will not exist. Do not enable both the direct plugin and a
group containing it; install the plugin directly if the gate matters.
