from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENT = ROOT / "agents" / "comment-reviewer.md"
COMMAND = ROOT / "commands" / "comment-review.md"


def test_agent_grants_the_tools_it_needs():
    """Without Edit and Bash the agent cannot rewrite a comment or commit."""
    front = AGENT.read_text().split("---")[1]
    for tool in ("Read", "Edit", "Bash", "Glob", "Grep"):
        assert tool in front


def test_agent_pins_the_commit_message_and_forbids_trailers():
    body = AGENT.read_text()
    lower = body.lower()
    assert "comments:" in body
    # Anchored to the prohibition context, not the bare token: a file that
    # instructs the agent TO add a trailer also contains the bare word
    # "Co-Authored-By" and would satisfy a bare-token check just as well.
    assert "no `co-authored-by` trailer" in lower
    assert "no watermark" in lower
    # Negative: the exact inversion a corrupted edit would introduce -- an
    # instruction to add the trailer -- must be absent, not merely optional.
    assert "always add a co-authored-by" not in lower
    assert "must add a co-authored-by" not in lower


def test_agent_forbids_commit_all_flags():
    body = AGENT.read_text()
    lower = body.lower()
    # Anchored to the negation phrasing, not the bare flag -- "always run
    # `git commit -a`" contains the flag too, so a bare-flag check cannot
    # distinguish the two.
    assert "never `git commit -a`" in lower
    assert "explicit" in lower
    # Negative: the exact inversion must be absent.
    assert "always run `git commit -a`" not in lower
    assert "run `git commit -a` to commit" not in lower


def test_agent_forbids_dash_capital_a_and_bare_commit():
    body = AGENT.read_text()
    lower = body.lower()
    # Case-sensitive for -A: lowercasing would collapse it onto -a and the
    # two are different git flags with different (both forbidden) effects.
    assert "never `-A`" in body
    assert "never a bare `git commit`" in lower
    assert "always run `git commit -A`" not in body
    assert "always run a bare `git commit`" not in lower


def test_agent_states_the_no_receipt_failure_paths():
    body = AGENT.read_text()
    lower = body.lower()
    for condition in ("base_unresolved", "in progress", "commit fail"):
        assert condition in lower
    # Anchored: each failure path must be paired with the abort action, not
    # merely mentioned in passing. Three failure paths from the original
    # pipeline (base_unresolved, in-progress, commit-fail) plus the
    # cap-overflow path all resolve to "write no receipt" -- at least three
    # occurrences is the floor, not an exact count, so the caps-section fix
    # doesn't make this brittle.
    assert lower.count("no receipt") >= 3
    assert "write the receipt anyway" not in lower
    assert "continue and write the receipt" not in lower


def test_agent_uses_the_plugin_root_variable_for_scripts():
    assert "${CLAUDE_PLUGIN_ROOT}" in AGENT.read_text()


def test_agent_ties_cap_overflow_to_verify_and_commit_before_partial_receipt():
    """Edits made before a cap trips are not exempt from the ordinary
    pipeline: they must still be verified and committed, in order, before the
    partial receipt is written, and the usual abort-on-failed-commit rule
    must still apply on that path. Otherwise a partial receipt could certify
    review credit for edits the tree never received -- the same failure mode
    rule 9 (abort if HEAD did not move) exists to prevent, reappearing
    through the cap path."""
    body = AGENT.read_text()
    lower = body.lower()
    assert "## caps" in lower
    caps_section = lower.split("## caps", 1)[1].split("## no-edit runs", 1)[0]
    assert "verify" in caps_section
    assert "commit" in caps_section
    assert "partial" in caps_section
    assert "abort" in caps_section
    assert "before" in caps_section


def test_command_only_dispatches_the_agent():
    """The method lives in one place. A command that re-explains the rules is a
    second copy that will drift."""
    body = COMMAND.read_text()
    assert "comment-reviewer" in body
    assert len(body.splitlines()) <= 40
