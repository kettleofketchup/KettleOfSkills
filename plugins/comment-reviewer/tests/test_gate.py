import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import gitpaths
import receipt

GATE = Path(__file__).resolve().parent.parent / "hooks" / "scripts" / "pr-create-gate.py"
T0 = datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc)


def invoke(command, cwd):
    """Run the gate exactly as Claude Code does: JSON on stdin."""
    event = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(cwd)}
    proc = subprocess.run(
        [sys.executable, str(GATE)], input=json.dumps(event),
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, f"gate must always exit 0, got {proc.returncode}: {proc.stderr}"
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def decision(out):
    return (out or {}).get("hookSpecificOutput", {}).get("permissionDecision")


def seed_receipt(cwd, now=T0):
    trunk = gitpaths.resolve_trunk(cwd)
    base = gitpaths.merge_base(trunk, cwd)
    payload = receipt.build(
        commit_sha=gitpaths.head_commit(cwd), tree_sha=gitpaths.head_tree(cwd),
        base_sha=base, resolved_base_ref=trunk, fixed={"A": 0, "B": 0, "C": 0},
        skipped=[], reported=[], partial=False, now=now,
    )
    return receipt.write(cwd, payload, now=now)


def test_non_pr_command_passes(cloned_with_remote):
    assert decision(invoke("ls -la", cloned_with_remote)) is None


def test_quoted_mention_passes(cloned_with_remote):
    out = invoke('git commit -m "prep for gh pr create"', cloned_with_remote)
    assert decision(out) is None


def test_pr_create_without_receipt_denies(cloned_with_remote):
    out = invoke("gh pr create --fill", cloned_with_remote)
    assert decision(out) == "deny"
    assert "comment" in out["hookSpecificOutput"]["permissionDecisionReason"].lower()


def test_pr_create_with_valid_receipt_passes(cloned_with_remote):
    seed_receipt(cloned_with_remote)
    assert decision(invoke("gh pr create --fill", cloned_with_remote)) is None


def test_stale_tree_denies(cloned_with_remote):
    seed_receipt(cloned_with_remote)
    (cloned_with_remote / "c.go").write_text("// new\n")
    subprocess.run(["git", "add", "c.go"], cwd=cloned_with_remote, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "more"], cwd=cloned_with_remote, check=True)
    assert decision(invoke("gh pr create", cloned_with_remote)) == "deny"


def test_reword_keeps_the_receipt_valid(cloned_with_remote):
    """Content unchanged -> same tree -> no re-review."""
    seed_receipt(cloned_with_remote)
    subprocess.run(["git", "commit", "-q", "--amend", "-m", "reworded"],
                   cwd=cloned_with_remote, check=True)
    assert decision(invoke("gh pr create", cloned_with_remote)) is None


def test_skip_assignment_passes(cloned_with_remote):
    out = invoke("CLAUDE_SKIP_COMMENT_REVIEW=1 gh pr create", cloned_with_remote)
    assert decision(out) is None


def test_sentinel_file_passes(cloned_with_remote):
    root = gitpaths.receipt_root(cloned_with_remote)
    root.mkdir(parents=True, exist_ok=True)
    (root / "skip").write_text("")
    assert decision(invoke("gh pr create", cloned_with_remote)) is None


def test_non_repo_fails_open(empty_dir):
    assert decision(invoke("gh pr create", empty_dir)) is None


def test_repo_without_commits_fails_open(repo_no_commits):
    assert decision(invoke("gh pr create", repo_no_commits)) is None


def test_unresolvable_trunk_fails_open(repo):
    """A local-only repo on a branch with no main/master: infrastructure gap,
    not evidence of an unreviewed branch."""
    subprocess.run(["git", "checkout", "-q", "-b", "solo"], cwd=repo, check=True)
    subprocess.run(["git", "branch", "-q", "-D", "main"], cwd=repo, check=False)
    assert decision(invoke("gh pr create", repo)) is None


def test_unparseable_receipt_denies_rather_than_crashing(cloned_with_remote):
    root = gitpaths.receipt_root(cloned_with_remote)
    root.mkdir(parents=True, exist_ok=True)
    (root / gitpaths.head_tree(cloned_with_remote)).write_text("{not json")
    assert decision(invoke("gh pr create", cloned_with_remote)) == "deny"


def test_malformed_stdin_passes(cloned_with_remote):
    proc = subprocess.run([sys.executable, str(GATE)], input="not json",
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert proc.stdout.strip() in ("", "{}")


def test_worktree_without_receipt_denies(worktree):
    """The receipt path bug lands here if it lands anywhere: `.git` is a FILE in
    a linked worktree, so a literal `.git/`-path implementation raises
    NotADirectoryError and the gate fails OPEN -- silently passing every PR
    created from a worktree regardless of receipt validity. Proving resolution
    succeeds here first is what makes the "deny" below mean something: it is
    a real absence-of-receipt denial, not a fail-open masquerading as one.
    """
    trunk = gitpaths.resolve_trunk(worktree)
    gitpaths.merge_base(trunk, worktree)  # both raise nothing -> resolution is clean
    out = invoke("gh pr create", worktree)
    assert decision(out) == "deny"


def test_worktree_with_valid_receipt_passes(worktree):
    seed_receipt(worktree)
    assert decision(invoke("gh pr create", worktree)) is None


def test_explicit_non_trunk_base_ref_receipt_passes(cloned_with_remote):
    """I2: `/comment-review <explicit-ref>` writes a receipt whose
    `resolved_base_ref` is that explicit ref, not the gate's own trunk pick.
    The gate used to compare the receipt's `base_sha` only against a base it
    re-derived from ITS OWN `resolve_trunk()`, so any explicit ref that
    disagrees with the gate's trunk choice produced a receipt the gate could
    never accept -- the review succeeds, commits, and the gate denies "not
    reviewed" forever. This constructs exactly that disagreement: a branch
    ("explicit-base") that is an ancestor of HEAD closer than trunk is, so
    merge-base against it differs from merge-base against trunk."""
    cwd = cloned_with_remote
    first_feat_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, check=True,
    ).stdout.strip()
    subprocess.run(["git", "branch", "explicit-base", first_feat_commit], cwd=cwd, check=True)
    (cwd / "c.go").write_text("// second\n")
    subprocess.run(["git", "add", "c.go"], cwd=cwd, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "second"], cwd=cwd, check=True)

    explicit_base = gitpaths.merge_base("explicit-base", cwd)
    trunk_base = gitpaths.merge_base(gitpaths.resolve_trunk(cwd), cwd)
    assert explicit_base != trunk_base  # the whole point: the two bases disagree

    payload = receipt.build(
        commit_sha=gitpaths.head_commit(cwd), tree_sha=gitpaths.head_tree(cwd),
        base_sha=explicit_base, resolved_base_ref="explicit-base",
        fixed={"A": 0, "B": 0, "C": 0}, skipped=[], reported=[], partial=False, now=T0,
    )
    receipt.write(cwd, payload, now=T0)

    assert decision(invoke("gh pr create --fill", cwd)) is None


def test_explicit_base_ref_that_no_longer_resolves_falls_back_to_trunk(cloned_with_remote):
    """When the receipt's resolved_base_ref has been deleted (branch removed,
    force-pushed away, etc.), the gate must fall back to its own trunk
    resolution rather than crash or fail open -- the retargeting protection
    the original trunk-only comparison existed for."""
    cwd = cloned_with_remote
    trunk_base = gitpaths.merge_base(gitpaths.resolve_trunk(cwd), cwd)
    payload = receipt.build(
        commit_sha=gitpaths.head_commit(cwd), tree_sha=gitpaths.head_tree(cwd),
        base_sha=trunk_base, resolved_base_ref="refs/heads/does-not-exist",
        fixed={"A": 0, "B": 0, "C": 0}, skipped=[], reported=[], partial=False, now=T0,
    )
    receipt.write(cwd, payload, now=T0)
    assert decision(invoke("gh pr create --fill", cwd)) is None


def test_primary_clone_receipt_does_not_satisfy_worktree_gate(repo, worktree):
    """receipt_root resolves via `--absolute-git-dir`, not `--git-common-dir`,
    precisely so a receipt written for the primary clone's tree cannot leak
    into a linked worktree sitting on a different branch."""
    seed_receipt(repo)
    assert decision(invoke("gh pr create", worktree)) == "deny"
