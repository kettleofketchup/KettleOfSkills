"""Resolve git repository state for comment-reviewer.

The gate and the review scripts need the same answers: where receipts live, what
HEAD's tree is, and what to diff against. Two git facts drive every choice here:

  * `.git` is a directory only in a primary clone. In a linked worktree or a
    submodule it is a file holding a `gitdir:` pointer, so a path built from a
    literal `.git/` raises NotADirectoryError. Always ask git.
  * A branch's own upstream is the wrong diff base. After `git push -u origin
    feat`, `@{u}` is `origin/feat` and `git diff @{u}...HEAD` is empty.

This file is vendored to two directories that cannot import each other:
    scripts/gitpaths.py            (source of truth)
    hooks/scripts/gitpaths.py      (copy)
tests/test_vendoring.py fails if they drift.
"""

import json
import subprocess
import sys
from pathlib import Path

RECEIPT_SUBDIR = ("claude", "comment-review")
GIT_TIMEOUT_SECONDS = 10

# Files and directories git leaves behind mid-operation, mapped to the operation
# name. A sweep that commits during any of these would corrupt the operation.
IN_PROGRESS_MARKERS = (
    ("rebase", ("rebase-merge", "rebase-apply")),
    ("merge", ("MERGE_HEAD",)),
    ("cherry-pick", ("CHERRY_PICK_HEAD",)),
    ("revert", ("REVERT_HEAD",)),
    ("bisect", ("BISECT_LOG",)),
)


class GitError(Exception):
    """Git could not answer a question about this directory."""


def _git(args, cwd):
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise GitError(f"git {' '.join(args)}: {exc}") from exc
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def git_dir(cwd):
    """This worktree's git dir, always a real directory."""
    return Path(_git(["rev-parse", "--absolute-git-dir"], cwd))


def receipt_root(cwd):
    """Per-worktree, so two worktrees on different branches cannot satisfy each
    other's gate."""
    return git_dir(cwd).joinpath(*RECEIPT_SUBDIR)


def head_commit(cwd):
    return _git(["rev-parse", "HEAD"], cwd)


def head_tree(cwd):
    """Receipts key on the tree, not the commit, so a reword, squash, or rebase
    that leaves content unchanged still validates."""
    return _git(["rev-parse", "HEAD^{tree}"], cwd)


def resolve_trunk(cwd):
    """Trunk ref to diff against -- never the branch's own upstream."""
    for remote in ("origin", "upstream"):
        try:
            return _git(["symbolic-ref", f"refs/remotes/{remote}/HEAD"], cwd).removeprefix(
                "refs/remotes/"
            )
        except GitError:
            pass
    for candidate in ("origin/main", "origin/master", "main", "master"):
        try:
            _git(["rev-parse", "--verify", "--quiet", candidate], cwd)
            return candidate
        except GitError:
            pass
    raise GitError("cannot resolve a trunk ref")


def merge_base(trunk, cwd):
    return _git(["merge-base", trunk, "HEAD"], cwd)


def touched_files(base, cwd):
    """Paths added, copied, modified, or renamed since `base`.

    ACMR excludes deletions, which would otherwise reach the extractor as
    nonexistent files."""
    out = _git(["diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"], cwd)
    return [line for line in out.splitlines() if line]


def in_progress_operation(cwd):
    """Name of an in-flight git operation, or None."""
    directory = git_dir(cwd)
    for name, markers in IN_PROGRESS_MARKERS:
        if any((directory / marker).exists() for marker in markers):
            return name
    return None


def main():
    """Print resolved repository state as JSON.

    The agent has Bash, not a Python import path, so every value it needs to run
    a sweep is available from one command.
    """
    cwd = sys.argv[1] if len(sys.argv) > 1 else "."
    trunk = resolve_trunk(cwd)
    base = merge_base(trunk, cwd)
    json.dump({
        "receipt_root": str(receipt_root(cwd)),
        "head_commit": head_commit(cwd),
        "head_tree": head_tree(cwd),
        "trunk": trunk,
        "base": base,
        "in_progress": in_progress_operation(cwd),
        "touched": touched_files(base, cwd),
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
