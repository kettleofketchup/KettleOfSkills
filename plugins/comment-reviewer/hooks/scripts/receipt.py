"""Read and write the comment-review receipt.

A receipt is one JSON file named after HEAD's tree sha. The tree key -- rather
than the commit sha -- means a reword, squash, or rebase that leaves content
unchanged still validates, so the gate does not re-fire on every amend.

The receipt is written by the review, never by the gate: a gate that could write
its own receipt would rubber-stamp itself.
"""

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import gitpaths

TTL_DAYS = 14
KEEP_NEWEST = 20

# A receipt is named after a full git tree sha: 40 lowercase hex characters.
# prune() must not treat every file in the receipt root as a receipt -- the
# gate's durable opt-out sentinel (SENTINEL_NAME in pr-create-gate.py) lives
# in the same directory, and being the oldest file there, was evicted first
# under mtime-based pruning that had no name filter.
_RECEIPT_NAME = re.compile(r"[0-9a-f]{40}")


def _now(now):
    return now or datetime.now(timezone.utc)


def build(commit_sha, tree_sha, base_sha, resolved_base_ref, fixed, skipped, reported,
          partial, now=None):
    return {
        "commit_sha": commit_sha,
        "tree_sha": tree_sha,
        "base_sha": base_sha,
        "resolved_base_ref": resolved_base_ref,
        "written_at": _now(now).isoformat(),
        "fixed": fixed,
        "skipped": skipped,
        "reported": reported,
        "partial": partial,
    }


def write(cwd, payload, now=None):
    root = gitpaths.receipt_root(cwd)
    root.mkdir(parents=True, exist_ok=True)
    target = root / payload["tree_sha"]
    # Write-then-rename: a half-written receipt read by a concurrent gate would
    # parse as absent, denying a PR that was in fact reviewed.
    handle, temp = tempfile.mkstemp(dir=str(root))
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
        os.replace(temp, target)
    except Exception:
        # A failed dump-and-replace must not leave an orphan in the receipt
        # directory: prune() treats every file here as a receipt, so a leaked
        # temp file would consume a KEEP_NEWEST slot and could evict a
        # legitimate one -- blocking a user from opening a PR they did review.
        try:
            os.unlink(temp)
        except OSError:
            pass
        raise
    prune(root, now=now)
    return target


def read(root, tree_sha):
    path = Path(root) / tree_sha
    try:
        with open(path, encoding="utf-8") as fh:
            loaded = json.load(fh)
    except (OSError, ValueError):
        return None
    return loaded if isinstance(loaded, dict) else None


def is_valid(payload, tree_sha, base_sha, now=None):
    if not payload or payload.get("tree_sha") != tree_sha:
        return False
    if payload.get("base_sha") != base_sha:
        return False
    try:
        written = datetime.fromisoformat(payload["written_at"])
    except (KeyError, TypeError, ValueError):
        return False
    if written.tzinfo is None:
        return False
    return _now(now) - written <= timedelta(days=TTL_DAYS)


def prune(root, now=None):
    root = Path(root)
    if not root.is_dir():
        return
    entries = [
        p for p in root.iterdir() if p.is_file() and _RECEIPT_NAME.fullmatch(p.name)
    ]
    entries.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for stale in entries[KEEP_NEWEST:]:
        try:
            stale.unlink()
        except OSError:
            pass


def main(argv=None):
    """CLI, so the agent can write a receipt with Bash alone.

        receipt.py write --base-ref origin/main [--cwd .] [--partial]

    The report body arrives as JSON on stdin:
        {"fixed": {"A": 3, "B": 1, "C": 2}, "skipped": [], "reported": []}
    """
    import argparse

    parser = argparse.ArgumentParser(prog="receipt.py")
    sub = parser.add_subparsers(dest="command", required=True)
    writer = sub.add_parser("write")
    writer.add_argument("--cwd", default=".")
    writer.add_argument("--base-ref", required=True)
    writer.add_argument("--partial", action="store_true")
    args = parser.parse_args(argv)

    body = {}
    if not sys.stdin.isatty():
        try:
            body = json.load(sys.stdin) or {}
        except (ValueError, OSError) as exc:
            # A malformed or empty report body must degrade to a zero-count
            # receipt, not crash: this file is vendored into hooks/scripts/,
            # where an uncaught traceback breaks the turn.
            print(f"receipt.py: stdin was not valid JSON ({exc}); using empty body",
                  file=sys.stderr)
            body = {}
    payload = build(
        commit_sha=gitpaths.head_commit(args.cwd),
        tree_sha=gitpaths.head_tree(args.cwd),
        base_sha=gitpaths.merge_base(args.base_ref, args.cwd),
        resolved_base_ref=args.base_ref,
        fixed=body.get("fixed") or {"A": 0, "B": 0, "C": 0},
        skipped=body.get("skipped") or [],
        reported=body.get("reported") or [],
        partial=args.partial,
    )
    print(write(args.cwd, payload))


if __name__ == "__main__":
    main()
