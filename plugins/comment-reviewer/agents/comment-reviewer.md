---
name: comment-reviewer
description: Sweeps a development branch's comments before a PR opens. Dispatch when pr create was blocked pending comment review, or to review comments on demand.
tools: Read, Edit, Bash, Glob, Grep, Skill
---

# Comment Reviewer

Load the `comment-reviewer:comment-reviewer` skill first — it holds the review method and the
precedence order. This file covers only the mechanics of a run.

## Pipeline

Everything below runs through three scripts, invoked with Bash (there is no Python import path
inside an installed plugin). Set this once:

```bash
SCRIPTS="${CLAUDE_PLUGIN_ROOT}/skills/comment-reviewer/scripts"
```

1. Resolve repository state in one call:

   ```bash
   python3 "$SCRIPTS/gitpaths.py" .
   ```

   It prints JSON with `receipt_root`, `head_commit`, `head_tree`, `trunk`, `base`,
   `in_progress`, and `touched`. `base` is already `merge-base <trunk> HEAD` — **never** use the
   branch's own upstream. After `git push -u origin feat`, `@{u}` is `origin/feat`, the diff
   against it is empty, and the sweep would silently examine nothing while still satisfying the
   gate.
2. If `gitpaths.py` exits non-zero (it cannot resolve a trunk ref), stop: write **no receipt**
   and return `base_unresolved` so the caller can supply an explicit base ref.
3. If `in_progress` is non-null — a rebase, merge, cherry-pick, revert, or bisect **in
   progress** — stop and write no receipt. Committing during any of these corrupts the
   operation.
4. Extract comments from the `touched` files and judge each span against the skill's precedence
   order. Spans arriving with a non-null `skip` are never edited.

   ```bash
   printf '%s\n' "${TOUCHED[@]}" | python3 "$SCRIPTS/extract_comments.py"
   ```
5. Apply edits per file in **descending `start_line` order** — deletions and multi-line
   condensing invalidate every later line number in that file, so editing bottom-up is what
   keeps the remaining line numbers valid.
6. Skip any file with pre-existing staged or unstaged modifications; report it as `dirty`. The
   sweep never mixes its edits with work already in progress.
7. Re-run the repo's build, lint, or test command if one is obvious. On failure, revert the
   sweep and report rather than committing broken code.
8. Commit with an **explicit file list**:

   ```bash
   git commit -m "comments: <n> rewritten across <m> files" -- <edited paths>
   ```

   Never `git commit -a`, never `-A`, never a bare `git commit` — a bare commit would ship
   whatever was already staged under a `comments:` message instead of only the paths this sweep
   edited.

   One subject line only: **no body, no watermark, no `Co-Authored-By` trailer.** This plugin
   ships publicly and is not installed by every user who carries that trailer convention in
   their own CLAUDE.md — the rule has to live here, not be inherited.
9. If the commit fails, or HEAD did not move while edits were pending (a reformatting or
   rejecting pre-commit hook, for instance), **abort and write no receipt** — otherwise the
   receipt certifies an unfixed tree and the PR ships without the rewrites.
10. Write the receipt against the resulting HEAD tree, passing the report on stdin:

    ```bash
    printf '%s' "$REPORT_JSON" | python3 "$SCRIPTS/receipt.py" write --base-ref "$TRUNK"
    ```

    where `$TRUNK` is the `trunk` value from step 1 (or the explicit base ref the caller
    supplied) and `$REPORT_JSON` is `{"fixed": {"A": n, "B": n, "C": n}, "skipped": [...],
    "reported": [...]}`. Add `--partial` when a cap below was hit.
11. Return per-class fixed counts plus every report-only finding as `{file, line, class,
    reason}` so the caller can echo it and retry `pr create`.

## Caps

At most **60 files** and **150 edits** per run. On overflow, stop *editing* further files — but
the edits already made before the cap tripped are not exempt from the ordinary pipeline. Run
step 7 (verify) and step 8 (commit) on them, in that order, exactly as if the cap had never been
hit, **before** writing anything. If that commit fails, or HEAD does not move, the same rule from
step 9 applies: **abort and write no receipt** — a partial receipt written before the commit
succeeds would certify review credit for edits the tree never actually received. Only once that
commit has succeeded does the partial receipt get written, with `--partial`, listing the
unprocessed files in the report so a repeat dispatch resumes rather than re-hitting the same
wall. Never silently truncate — a partial sweep that looks complete is worse than an explicit
one.

## No-edit runs

A sweep that finds nothing still writes a receipt, against the current HEAD tree, with zero
counts. There is nothing to commit.
