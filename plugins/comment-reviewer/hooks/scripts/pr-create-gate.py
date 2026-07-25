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

    cwd = event.get("cwd") or "."
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
        trunk = gitpaths.resolve_trunk(cwd)
        base = gitpaths.merge_base(trunk, cwd)
    except gitpaths.GitError:
        return None  # fail open
    except OSError:
        return None  # fail open

    stored = receipt.read(root, tree)
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
