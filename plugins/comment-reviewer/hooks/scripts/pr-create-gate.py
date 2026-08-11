#!/usr/bin/env python3
"""PreToolUse gate: hold `pr create` until this branch's comments are reviewed.

Reads the hook event as JSON on stdin and emits at most a permission decision on
stdout. Three outcomes, never two:

  pass    the command is not a PR creation, a skip was requested, or a valid
          receipt exists for HEAD's tree
  deny    a receipt is genuinely absent, stale, or unreadable for a repository
          whose state resolved cleanly
  pass    ANY resolution failure -- not a repo, no commits, unresolvable trunk,
          unreadable git dir

That last row is the important one. An infrastructure error is not evidence of an
unreviewed branch, and denying on it would lock the user out with advice that
cannot help: running the reviewer would hit the same failure. The repo's own hook
precedent (dotfiles/.claude/hooks/preexisting-nudge.py) exits 0 on malformed
input for the same reason.

The exit code is always 0. A crashing hook is a broken turn.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gitpaths  # noqa: E402
import prmatch  # noqa: E402
import receipt  # noqa: E402

SENTINEL_NAME = "skip"

REASON = (
    "Comment review has not run for this branch's current content.\n"
    "Dispatch the comment-reviewer agent (or run /comment-review), then retry "
    "this command -- the review writes the receipt that releases this gate.\n"
    f"To bypass once: prefix the command with {prmatch.SKIP_VAR}=1"
)


def _deny(reason):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def decide(event):
    """Return a deny payload, or None to pass through."""
    if event.get("tool_name") != "Bash":
        return None
    command = (event.get("tool_input") or {}).get("command") or ""
    # matches() already excludes any segment carrying its own skip assignment.
    if not prmatch.matches(command):
        return None

    # The event's `cwd` is the SESSION's directory. If the command cd's into
    # another repository first, that is the repository whose comments are about
    # to ship, so it is the one whose receipt must be checked. Judging the
    # session directory instead denies a reviewed branch -- and, in the
    # direction that actually matters, PASSES an unreviewed one whenever the
    # session directory happens to hold a valid receipt of its own.
    session_cwd = event.get("cwd") or "."
    cwd = prmatch.pr_create_cwd(command, session_cwd) or session_cwd
    try:
        root = gitpaths.receipt_root(cwd)
        # An unreadable root (e.g. `chmod 000`) resolves differently by Python
        # version: on 3.12+, Path.exists() swallows PermissionError and this
        # returns False, falling through to a genuine deny; on the 3.9-3.11
        # floor, .exists() re-raises and the `except OSError` below fails
        # open instead. Both outcomes exit 0 and are safe -- deny is "review
        # again", fail-open is "infrastructure can't help you either" -- so
        # this is left alone rather than pinned to one behaviour.
        if (root / SENTINEL_NAME).exists():
            return None
        tree = gitpaths.head_tree(cwd)
    except gitpaths.GitError:
        return None  # fail open
    except OSError:
        return None  # fail open

    stored = receipt.read(root, tree)

    # Prefer re-resolving the base from the receipt's OWN resolved_base_ref
    # (an explicit ref /comment-review <ref> may have used) over the gate's
    # own trunk pick. Without this, a receipt written against any base other
    # than whatever this gate would independently resolve can never validate
    # -- the review succeeds, commits, and the gate denies "not reviewed"
    # forever. Fall back to the gate's own trunk resolution when there is no
    # stored ref, or it no longer resolves (deleted branch, force-pushed
    # history, etc.) -- that keeps the original retargeting protection intact.
    base = None
    resolved_ref = stored.get("resolved_base_ref") if stored else None
    if resolved_ref:
        try:
            base = gitpaths.merge_base(resolved_ref, cwd)
        except gitpaths.GitError:
            base = None

    if base is None:
        try:
            trunk = gitpaths.resolve_trunk(cwd)
            base = gitpaths.merge_base(trunk, cwd)
        except gitpaths.GitError:
            return None  # fail open
        except OSError:
            return None  # fail open

    if receipt.is_valid(stored, tree, base):
        return None
    return _deny(REASON)


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("event is not an object")
    except (ValueError, OSError):
        return  # malformed input never breaks the turn

    try:
        result = decide(event)
    except Exception:  # noqa: BLE001 - a gate must not crash a turn
        return

    if result:
        json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
