import subprocess
import pytest
from conftest import run
import gitpaths


def test_git_dir_is_a_real_directory_in_a_worktree(worktree):
    """In a linked worktree .git is a file; the resolved git dir must still be a dir."""
    assert (worktree / ".git").is_file()
    assert gitpaths.git_dir(worktree).is_dir()


def test_receipt_root_is_creatable_in_a_worktree(worktree):
    """The bug this module exists for: mkdir under a literal .git/ raises
    NotADirectoryError in a worktree."""
    root = gitpaths.receipt_root(worktree)
    root.mkdir(parents=True, exist_ok=True)
    assert root.is_dir()


def test_receipt_root_is_per_worktree(repo, worktree):
    assert gitpaths.receipt_root(repo) != gitpaths.receipt_root(worktree)


def test_head_tree_is_stable_across_a_reword(repo):
    before = gitpaths.head_tree(repo)
    run(repo, "git", "commit", "-q", "--amend", "-m", "reworded")
    assert gitpaths.head_tree(repo) == before
    assert gitpaths.head_commit(repo) != before


def test_resolve_trunk_prefers_remote_head(cloned_with_remote):
    assert gitpaths.resolve_trunk(cloned_with_remote) == "origin/main"


def test_resolve_trunk_uses_symbolic_ref_when_target_is_not_a_literal_candidate(
    cloned_with_symref_pointing_elsewhere,
):
    """origin/HEAD -> origin/trunk. No literal-candidate check can produce
    "origin/trunk", so returning it proves the symbolic-ref loop ran and
    succeeded, rather than coincidentally matching the fallback list."""
    assert gitpaths.resolve_trunk(cloned_with_symref_pointing_elsewhere) == "origin/trunk"


def test_resolve_trunk_checks_upstream_remote_in_symbolic_ref_loop(
    cloned_with_upstream_remote_only,
):
    """No `origin` remote exists; only `upstream` does. Returning an
    upstream/... ref proves the "upstream" entry in the first loop's remote
    tuple was actually tried."""
    assert gitpaths.resolve_trunk(cloned_with_upstream_remote_only) == "upstream/main"


def test_resolve_trunk_falls_back_to_local_main(repo):
    """No remote at all: the symbolic-ref loop must fail entirely and land on
    the literal `main` candidate."""
    assert gitpaths.resolve_trunk(repo) == "main"


def test_resolve_trunk_falls_back_to_local_master(repo_master_only):
    """No remote, and the only trunk-ish branch is `master`."""
    assert gitpaths.resolve_trunk(repo_master_only) == "master"


def test_resolve_trunk_prefers_remote_tracking_ref_over_local_branch(cloned_without_symref):
    """No origin/HEAD symref, but origin/main still exists as a remote-tracking
    ref alongside a local `main` -- the remote-tracking candidate must win."""
    assert gitpaths.resolve_trunk(cloned_without_symref) == "origin/main"


def test_resolve_trunk_raises_when_no_trunk_candidate_exists(repo_no_trunk_candidate):
    with pytest.raises(gitpaths.GitError):
        gitpaths.resolve_trunk(repo_no_trunk_candidate)


def test_base_is_merge_base_not_upstream(cloned_with_remote):
    """After `push -u`, @{u} is origin/feat and the diff would be empty."""
    upstream = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "@{u}"],
        cwd=cloned_with_remote, capture_output=True, text=True,
    ).stdout.strip()
    assert upstream == "origin/feat"

    trunk = gitpaths.resolve_trunk(cloned_with_remote)
    base = gitpaths.merge_base(trunk, cloned_with_remote)
    assert gitpaths.touched_files(base, cloned_with_remote) == ["b.go"]


def test_touched_files_excludes_deletions(cloned_with_remote):
    run(cloned_with_remote, "git", "rm", "-q", "a.txt")
    run(cloned_with_remote, "git", "commit", "-q", "-m", "drop a")
    base = gitpaths.merge_base(gitpaths.resolve_trunk(cloned_with_remote), cloned_with_remote)
    assert "a.txt" not in gitpaths.touched_files(base, cloned_with_remote)


def test_in_progress_operation_none_when_clean(repo):
    assert gitpaths.in_progress_operation(repo) is None


def test_in_progress_operation_detects_merge(repo):
    (gitpaths.git_dir(repo) / "MERGE_HEAD").write_text("deadbeef\n")
    assert gitpaths.in_progress_operation(repo) == "merge"


def test_non_repo_raises_giterror(empty_dir):
    with pytest.raises(gitpaths.GitError):
        gitpaths.git_dir(empty_dir)


def test_repo_without_commits_raises_on_head(repo_no_commits):
    with pytest.raises(gitpaths.GitError):
        gitpaths.head_tree(repo_no_commits)
