import pytest
import prmatch


@pytest.mark.parametrize("command", [
    "gh pr create",
    "gh pr create --fill",
    "gh pr create --title 'x' --body 'y'",
    "fj pr create",
    "fj -H codeberg.org pr create",          # option VALUE must not shift the pair
    "glab mr create --fill",
    "mj pr create",
    "PAGER= gh pr create",                    # leading assignment stripped
    "env GH_TOKEN=x gh pr create",            # `env` prefix stripped
    "gh  pr   create",                        # extra whitespace
    "git push && gh pr create",               # later segment
    "gh pr list; gh pr create",
    "make build || gh pr create --draft",
    # Shell metacharacters INSIDE quotes. Splitting the raw string first cuts
    # through the quotes and loses the invocation entirely -- these are the cases
    # that make the difference between a working gate and a decorative one.
    'gh pr create --title "fix; refactor"',
    'gh pr create --body "a|b"',
    'gh pr create --title "A && B"',
    'gh pr create --title t --body "line one\nline two"',
    # A skip on a DIFFERENT segment must not release this one.
    "CLAUDE_SKIP_COMMENT_REVIEW=1 ls; gh pr create",
    "gh pr create && CLAUDE_SKIP_COMMENT_REVIEW=1 echo x",
    # --- Fix-round regressions (coordinator review) ---
    "git push\ngh pr create --fill",           # F1: newline-separated segments
    "url=$(gh pr create --fill)",              # F2: command substitution
    "`gh pr create`",                          # F2: backtick substitution
    "gh pr create --title --help",             # F3: --help as an option VALUE
    "/usr/bin/gh pr create",                   # F4: path-qualified CLI
    "sudo gh pr create",                       # F5: sudo wrapper
    "nohup gh pr create --fill",               # F5: nohup wrapper
    "time gh pr create",                       # F5: time wrapper
    "command gh pr create",                    # F5: command wrapper
    "gh pr \\\ncreate",                        # F7: backslash-newline line continuation
    "x=$((1 << SHIFT))\ngh pr create\nSHIFT",  # F8: arithmetic `<<` must not read as a heredoc
])
def test_matches_real_invocations(command):
    assert prmatch.matches(command)


@pytest.mark.parametrize("command", [
    'git commit -m "prep for gh pr create"',  # the guard the spec requires
    'echo "run gh pr create next"',
    "gh pr list",
    "gh pr view 12",
    "gh issue create --title 'pr create'",
    "gh alias set prc 'pr create'",
    "gh repo create",
    "git pr create",                          # not a forge CLI
    "cat <<EOF\ngh pr create\nEOF",           # heredoc body is data
    "cat <<'EOF'\ngh pr create\nEOF",
    "# gh pr create",                         # commented out
    "gh pr create --help",                    # help text, not a creation
])
def test_does_not_match(command):
    assert not prmatch.matches(command)


def test_unbalanced_quotes_pass_through_rather_than_raising():
    """shlex raises on unbalanced quotes; the gate must never crash the turn."""
    assert prmatch.matches('gh pr create --title "unclosed') is False


@pytest.mark.parametrize("command", [
    "CLAUDE_SKIP_COMMENT_REVIEW=1 gh pr create",
    "CLAUDE_SKIP_COMMENT_REVIEW=true gh pr create --fill",
])
def test_skip_assignment_in_the_command_is_detected(command):
    """An env var set on the inspected command never reaches the hook process,
    so the assignment must be read out of the command string itself."""
    assert prmatch.wants_skip(command)


def test_skip_not_detected_when_absent():
    assert not prmatch.wants_skip("gh pr create")


def test_skip_zero_is_not_a_skip():
    assert not prmatch.wants_skip("CLAUDE_SKIP_COMMENT_REVIEW=0 gh pr create")


def test_skip_is_segment_local():
    """A shell assignment applies only to the command it prefixes."""
    assert not prmatch.matches("CLAUDE_SKIP_COMMENT_REVIEW=1 gh pr create")
    assert prmatch.matches("CLAUDE_SKIP_COMMENT_REVIEW=1 ls; gh pr create")


def test_quoted_metacharacters_do_not_hide_the_invocation():
    """Regression: the splitter used to run before the lexer, so a quoted ';'
    produced two unbalanced halves and the gate saw nothing."""
    for command in ('gh pr create --title "fix; refactor"',
                    'gh pr create --body "a|b"',
                    'gh pr create --body "one\ntwo"'):
        assert prmatch.segments(command), command
        assert prmatch.matches(command), command


# --- Fix-round regressions (coordinator review) ---
#
# The brief's own reference implementation had real false-negative gaps.
# Every one of these mirrors a command shape that used to sail through the
# gate unrecognised.


def test_newline_between_commands_splits_segments():
    """F1: `shlex` classifies '\\n' as whitespace and never yields it as a
    token, so having '\\n' in an operator set that is only ever checked
    against *tokens* is dead code -- the splitter must recognise the newline
    boundary itself. `git push\\ngh pr create --fill` must become two
    segments, and the second one must still be recognised."""
    result = prmatch.segments("git push\ngh pr create --fill")
    assert result == [["git", "push"], ["gh", "pr", "create", "--fill"]]


def test_help_disqualification_is_position_sensitive():
    """F3: `--help` only disqualifies when it is the flag actually being
    passed. When it is the *value* of a preceding option, scanning the whole
    token list for the literal string `--help` is a trivial bypass."""
    assert prmatch.matches("gh pr create --title --help")
    assert not prmatch.matches("gh pr create --help")  # unchanged: real --help


def test_env_prefixed_skip_is_honored():
    """F6: `_has_skip` used to bail out on the first non-assignment token, so
    a leading `env` (which `is_pr_create` already strips) hid the skip
    assignment sitting right behind it -- the gate fired despite an explicit,
    well-formed skip."""
    assert not prmatch.matches("env CLAUDE_SKIP_COMMENT_REVIEW=1 gh pr create")
    assert prmatch.wants_skip("env CLAUDE_SKIP_COMMENT_REVIEW=1 gh pr create")


@pytest.mark.parametrize("command", [
    "git push\ngh pr create --fill",           # F1
    "url=$(gh pr create --fill)",              # F2
    "`gh pr create`",                          # F2
    "gh pr create --title --help",             # F3
    "/usr/bin/gh pr create",                   # F4
    "sudo gh pr create",                       # F5
    "nohup gh pr create --fill",               # F5
    "time gh pr create",                       # F5
    "command gh pr create",                    # F5
    "gh pr \\\ncreate",                        # F7
    "x=$((1 << SHIFT))\ngh pr create\nSHIFT",  # F8
])
def test_fix_round_findings_match(command):
    """One assertion per numbered finding from the coordinator's review,
    kept as a separate table (in addition to their entries in
    `test_matches_real_invocations`) so a future regression in any single
    one of them fails under a name that names the finding."""
    assert prmatch.matches(command)


# --- Round 2 (coordinator review of the fix round) ---
#
# `_collapse_line_continuations` was a blunt regex pre-pass over the raw
# string, applied before any quote tracking. Confirmed against real bash:
# inside single quotes backslash has no special meaning at all, so a
# backslash-newline pair there is NOT a continuation -- it is two literal
# characters that stay part of one quoted argument. The blind pre-pass
# joined them anyway, producing a false-positive `matches()` for commands
# that never actually invoke `gh pr create`. Line continuation now lives
# inside `_split_top_level`'s own quote-tracking state machine instead.


def test_single_quoted_backslash_newline_is_not_a_continuation():
    """A backslash-newline pair inside single quotes is two literal
    characters in bash, not a continuation. `gh 'p\\nr' create` never
    invokes `gh pr create` -- the second argument is the four characters
    p, backslash, newline, r, not `pr`."""
    assert not prmatch.matches("gh 'p\\\nr' create")


def test_single_quoted_backslash_newline_in_the_cli_name_is_not_a_continuation():
    """Same rule, but the mangled token is the CLI name itself: folding the
    backslash-newline together would turn a single-quoted non-`gh` argument
    into what looks like a bare `gh` invocation."""
    assert not prmatch.matches("'g\\\nh' pr create")


def test_unquoted_line_continuation_still_matches():
    """Finding 7 from round 1 must still hold: outside any quoting,
    backslash-newline IS a continuation, and `gh pr create` split across
    two lines this way is still recognised."""
    assert prmatch.matches("gh pr \\\ncreate")


def test_double_quoted_line_continuation_still_matches():
    """Backslash-newline inside DOUBLE quotes is also a continuation in
    bash (unlike single quotes) -- it only affects the quoted argument's
    contents, not the invocation itself, which must still match."""
    assert prmatch.matches('gh pr create --title "a\\\nb"')


@pytest.mark.parametrize("command,base,expected", [
    ("gh pr create --fill", "/repo", "/repo"),
    ("cd /other && gh pr create", "/repo", "/other"),
    ("cd sub && gh pr create", "/repo", "/repo/sub"),
    ("cd /a && cd /b && gh pr create", "/repo", "/b"),
    ("cd /a && cd .. && gh pr create", "/repo", "/"),
    ("gh pr create && cd /other", "/repo", "/repo"),   # cd AFTER: irrelevant
    ("cd /other; ls; gh pr create", "/repo", "/other"),
    ("sudo cd /other && gh pr create", "/repo", "/other"),
    ("ls -la", "/repo", None),                          # no pr create at all
])
def test_pr_create_cwd_tracks_directory_changes(command, base, expected):
    assert prmatch.pr_create_cwd(command, base) == expected


def test_pr_create_cwd_falls_back_when_cd_is_unresolvable():
    """`cd -` depends on shell history the hook cannot see. Falling back to the
    known directory beats guessing."""
    assert prmatch.pr_create_cwd("cd - && gh pr create", "/repo") == "/repo"


def test_pr_create_cwd_is_not_confused_by_a_quoted_cd():
    """A `cd` inside a quoted argument is data, not a directory change."""
    assert prmatch.pr_create_cwd(
        'gh pr create --title "cd /elsewhere"', "/repo"
    ) == "/repo"
