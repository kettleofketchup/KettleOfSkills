import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

import gitpaths
import paths
import receipt

T0 = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)


def payload(**over):
    base = dict(
        commit_sha="c" * 40, tree_sha="t" * 40, base_sha="b" * 40,
        resolved_base_ref="origin/main", fixed={"A": 1, "B": 0, "C": 2},
        skipped=[], reported=[], partial=False, now=T0,
    )
    base.update(over)
    return receipt.build(**base)


def test_write_then_read_roundtrips(repo):
    receipt.write(repo, payload(), now=T0)
    root = gitpaths.receipt_root(repo)
    assert receipt.read(root, "t" * 40)["resolved_base_ref"] == "origin/main"


def test_write_names_the_file_after_the_tree_sha(repo):
    path = receipt.write(repo, payload(), now=T0)
    assert path.name == "t" * 40


def test_write_cleans_up_temp_file_on_failure(repo):
    """A failed dump must not leak a temp file into the receipt directory --
    prune() treats every file there as a receipt, so an orphan could evict a
    legitimate one and block a user from opening a PR they did review."""
    root = gitpaths.receipt_root(repo)
    unserializable = payload(fixed={"A": object()})
    with pytest.raises(TypeError):
        receipt.write(repo, unserializable, now=T0)
    assert list(root.iterdir()) == []


def test_write_succeeds_in_a_worktree(worktree):
    """Guards the NotADirectoryError that a literal .git/ path would raise."""
    assert receipt.write(worktree, payload(), now=T0).is_file()


def test_read_returns_none_when_absent(repo):
    assert receipt.read(gitpaths.receipt_root(repo), "z" * 40) is None


def test_read_returns_none_on_unparseable_json(repo):
    root = gitpaths.receipt_root(repo)
    root.mkdir(parents=True, exist_ok=True)
    (root / ("t" * 40)).write_text("{not json")
    assert receipt.read(root, "t" * 40) is None


def test_is_valid_requires_matching_tree(repo):
    p = payload()
    assert receipt.is_valid(p, "t" * 40, "b" * 40, now=T0)
    assert not receipt.is_valid(p, "OTHER" + "t" * 35, "b" * 40, now=T0)


def test_is_valid_requires_matching_base(repo):
    """Retargeting the PR widens the touched-file set, so the old receipt must
    stop counting."""
    p = payload()
    assert not receipt.is_valid(p, "t" * 40, "different" + "b" * 31, now=T0)


def test_is_valid_expires_after_ttl(repo):
    p = payload()
    later = T0 + timedelta(days=receipt.TTL_DAYS + 1)
    assert not receipt.is_valid(p, "t" * 40, "b" * 40, now=later)


def test_prune_keeps_only_the_newest(repo):
    """Asserts identity, not just count: a sort-direction bug that kept the
    OLDEST KEEP_NEWEST instead of the newest would still satisfy a bare count
    check, so this pins down exactly which tree shas must survive."""
    root = gitpaths.receipt_root(repo)
    total = receipt.KEEP_NEWEST + 5
    for i in range(total):
        receipt.write(repo, payload(tree_sha=f"{i:040d}"), now=T0 + timedelta(minutes=i))
    receipt.prune(root, now=T0 + timedelta(hours=1))
    survivors = {p.name for p in root.iterdir()}
    expected = {f"{i:040d}" for i in range(total - receipt.KEEP_NEWEST, total)}
    assert survivors == expected


def test_cli_write_survives_empty_stdin(repo):
    """Piping from /dev/null (or any malformed body) must degrade to a
    zero-count receipt rather than crash -- this file is vendored into
    hooks/scripts/, where an uncaught traceback breaks the turn."""
    result = subprocess.run(
        [sys.executable, str(paths.SCRIPTS / "receipt.py"),
         "write", "--base-ref", "main", "--cwd", str(repo)],
        input="", capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    tree_sha = gitpaths.head_tree(repo)
    written = receipt.read(gitpaths.receipt_root(repo), tree_sha)
    assert written["fixed"] == {"A": 0, "B": 0, "C": 0}
