"""Decide whether a shell command creates a pull or merge request.

Tokenised, never a substring regex. `git commit -m "prep for gh pr create"`
contains the phrase but creates nothing, and denying it would be worse than
missing a real invocation.

Known and accepted blind spots: `gh api .../pulls -X POST`, user-defined `gh`
aliases, the web UI, wrapper recipes such as `just pr`, and any invocation
hidden behind a shell string a subprocess re-interprets -- `sh -c '...'`,
`bash -c "..."`, `eval '...'` -- where the real command is a single quoted
token that would need a second, recursive pass of this same lexing to reach.
"""

import posixpath
import os
import re
import shlex

SKIP_VAR = "CLAUDE_SKIP_COMMENT_REVIEW"
FORGE_CLIS = frozenset({"gh", "fj", "mj", "glab"})
REQUEST_NOUNS = frozenset({"pr", "mr"})
CREATE_VERB = "create"

_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# Wrapper CLIs that pass their remaining argv straight through to the real
# command without changing it. `sudo`/`nohup`/`time`/`command` are the
# non-`env` ones people actually type in front of `gh`/`glab`/etc.
_WRAPPER_CLIS = frozenset({"env", "sudo", "nohup", "time", "command"})
_HEREDOC_START = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
# `$(( ... ))` arithmetic expansion contains `<<` (shift) that reads exactly
# like a heredoc opener to a regex that only looks at one line in isolation --
# `x=$((1 << SHIFT))` would otherwise make the heredoc scanner swallow every
# line up to the next line that happens to read `SHIFT`, silently eating a
# real `gh pr create` sitting in between. Skip any heredoc-shaped match that
# falls inside one of these spans.
_ARITH_SPAN = re.compile(r"\$\(\(.*?\)\)")
_SKIP_TRUTHY = frozenset({"1", "true", "yes", "on"})
# `--help` prints usage and creates nothing; denying it is pure friction --
# but only when it is actually the flag being invoked, not the *value* of a
# preceding option. See the position check in `is_pr_create`.
_NON_CREATING_FLAGS = frozenset({"--help", "-h"})

# Characters that separate independently-executed segments when they appear
# outside any quoting. `&&`/`||` are checked as two-character pairs before
# falling through to the single-character set.
_MULTI_CHAR_OPERATORS = frozenset({"&", "|"})
_SINGLE_CHAR_OPERATORS = frozenset({";", "|", "&", "\n"})


def strip_heredocs(command):
    """Remove heredoc bodies. Their contents are data, not commands -- a body
    mentioning `gh pr create` must not trigger the gate."""
    lines = command.split("\n")
    kept, index = [], 0
    while index < len(lines):
        line = lines[index]
        kept.append(line)
        match = _heredoc_start(line)
        index += 1
        if not match:
            continue
        delimiter = match.group(2)
        while index < len(lines) and lines[index].strip() != delimiter:
            index += 1
        index += 1  # drop the delimiter line too
    return "\n".join(kept)


def _heredoc_start(line):
    """Like `_HEREDOC_START.search`, but refuses to fire on a `<<` that is
    actually inside a `$(( ... ))` arithmetic span on the same line."""
    match = _HEREDOC_START.search(line)
    if match is None:
        return None
    for span in _ARITH_SPAN.finditer(line):
        if span.start() <= match.start() < span.end():
            return None
    return match


class _Frame:
    """One level of quoting/substitution context while scanning.

    `kind` is `"top"` for the outermost context, `"paren"` for the inside of
    a `$( ... )`, or `"backtick"` for the inside of a `` ` ... ` ``. Each
    frame tracks its own quote state because entering a substitution starts
    a fresh quoting context in real shells, independent of whatever quote
    the substitution itself is nested inside.
    """

    __slots__ = ("kind", "buffer", "in_squote", "in_dquote")

    def __init__(self, kind):
        self.kind = kind
        self.buffer = []
        self.in_squote = False
        self.in_dquote = False


def _split_top_level(command):
    """Quote-aware split into raw (still-quoted) segment strings.

    Splits on `;` `&&` `||` `|` `&` and newline wherever they appear outside
    any quoting, and peels `$( ... )` / backtick command substitutions out
    into their own segment(s) so a captured invocation such as
    `url=$(gh pr create --fill)` stays visible. Never raises: an unmatched
    substitution opener, like an unmatched quote, just runs to the end of the
    string instead of aborting the scan.

    A backslash-newline pair is a line continuation -- consumed with no
    output -- everywhere EXCEPT inside single quotes, where bash gives
    backslash no special meaning at all: a single-quoted argument that
    contains a backslash immediately followed by a newline keeps both
    characters (plus whatever comes after) as one literal argument
    spanning two lines, rather than joining into a plain word on one line.
    Line continuation has to live here, inside the same quote-tracking
    state machine, rather than as a preprocessing pass over the raw string:
    a blind pass can't tell single-quoted backslash-newline apart from the
    unquoted or double-quoted kind, and folding them together would read
    a `gh` invocation whose real, single-quoted argument merely *looks
    like* "pr" split across two lines as an actual `gh pr create` --
    a false positive.
    """
    results = []
    stack = [_Frame("top")]
    i, n = 0, len(command)

    def flush(frame):
        piece = "".join(frame.buffer)
        frame.buffer = []
        if piece.strip():
            results.append(piece)

    while i < n:
        frame = stack[-1]
        ch = command[i]

        if ch == "\\" and not frame.in_squote:
            if command[i + 1 : i + 2] == "\n":
                # Line continuation outside single quotes (unquoted or
                # inside double quotes): consume both characters, emit
                # nothing, same as the shell does.
                i += 2
                continue
            frame.buffer.append(ch)
            if i + 1 < n:
                frame.buffer.append(command[i + 1])
            i += 2
            continue

        if frame.in_squote:
            frame.buffer.append(ch)
            if ch == "'":
                frame.in_squote = False
            i += 1
            continue

        if ch == "'" and not frame.in_dquote:
            frame.buffer.append(ch)
            frame.in_squote = True
            i += 1
            continue

        if ch == '"':
            frame.buffer.append(ch)
            frame.in_dquote = not frame.in_dquote
            i += 1
            continue

        if frame.in_dquote:
            # Command substitution still expands inside double quotes; only
            # the operator/segment split below is suppressed by them.
            if ch == "$" and command[i + 1 : i + 3] == "((":
                j = _arith_end(command, i, n)
                frame.buffer.append(command[i:j])
                i = j
                continue
            if ch == "$" and command[i + 1 : i + 2] == "(":
                flush(frame)
                stack.append(_Frame("paren"))
                i += 2
                continue
            if ch == "`" and frame.kind != "backtick":
                flush(frame)
                stack.append(_Frame("backtick"))
                i += 1
                continue
            frame.buffer.append(ch)
            i += 1
            continue

        # Neutral state: not inside any quote in this frame.
        if ch == "$" and command[i + 1 : i + 3] == "((":
            j = _arith_end(command, i, n)
            frame.buffer.append(command[i:j])
            i = j
            continue

        if ch == "$" and command[i + 1 : i + 2] == "(":
            flush(frame)
            stack.append(_Frame("paren"))
            i += 2
            continue

        if ch == "`":
            if frame.kind == "backtick":
                flush(frame)
                stack.pop()
                i += 1
                continue
            flush(frame)
            stack.append(_Frame("backtick"))
            i += 1
            continue

        if frame.kind == "paren" and ch == ")":
            flush(frame)
            stack.pop()
            i += 1
            continue

        if ch in _MULTI_CHAR_OPERATORS and i + 1 < n and command[i + 1] == ch:
            flush(frame)
            i += 2
            continue

        if ch in _SINGLE_CHAR_OPERATORS:
            flush(frame)
            i += 1
            continue

        frame.buffer.append(ch)
        i += 1

    # EOF: an unclosed substitution just runs out here rather than raising.
    while stack:
        flush(stack.pop())
    return results


def _arith_end(command, start, n):
    """Index just past the matching `))` for a `$((` beginning at `start`,
    tracking nested parens; runs to `n` if the expansion is never closed."""
    depth = 2
    j = start + 3
    while j < n and depth > 0:
        if command[j] == "(":
            depth += 1
        elif command[j] == ")":
            depth -= 1
        j += 1
    return j


def segments(command):
    """Token lists for each independently-executed part of the command.

    Splits the raw text on quote-aware boundaries FIRST (see
    `_split_top_level`), then lexes each resulting piece with `shlex.split`.
    Lexing the whole command in one pass before splitting was the original
    design, and its bug: splitting on the raw string first, or lexing with a
    single shared lexer that aborts on the first error, both let one
    malformed or quoted-metacharacter segment blind the matcher to a
    perfectly real `gh pr create` sitting next to it. A piece that still
    fails to lex (a genuinely unbalanced quote) is dropped rather than
    aborting the whole command, so a good segment before or after it is never
    hidden by one that got mangled.
    """
    pieces = _split_top_level(strip_heredocs(command))
    out = []
    for piece in pieces:
        try:
            tokens = shlex.split(piece, comments=True)
        except ValueError:
            continue  # unbalanced quotes in this piece: skip it, never raise
        if tokens:
            out.append(tokens)
    return out


def _strip_wrapper_clis(tokens):
    """Drop leading wrapper-CLI tokens (`env`, `sudo`, `nohup`, `time`,
    `command`) but leave leading assignments in place. Callers that need to
    inspect the assignments themselves (`_has_skip`) start from here rather
    than from `_drop_env_prefix`, which discards assignments outright."""
    index = 0
    while index < len(tokens) and tokens[index] in _WRAPPER_CLIS:
        index += 1
    return tokens[index:]


def _drop_env_prefix(tokens):
    index = 0
    while index < len(tokens) and (
        _ASSIGNMENT.match(tokens[index]) or tokens[index] in _WRAPPER_CLIS
    ):
        index += 1
    return tokens[index:]


def is_pr_create(tokens):
    """True when these tokens invoke a forge CLI to create a PR or MR.

    Looks for an adjacent (pr|mr, create) token pair rather than the first two
    non-option arguments, because option values such as the host in
    `fj -H codeberg.org pr create` are not option-shaped. Compares the CLI
    name by basename so `/usr/bin/gh pr create` still matches.
    """
    tokens = _drop_env_prefix(tokens)
    if not tokens or posixpath.basename(tokens[0]) not in FORGE_CLIS:
        return False
    for index, token in enumerate(tokens):
        if token not in _NON_CREATING_FLAGS:
            continue
        # `--help` only disqualifies when it is the flag being passed, not
        # when it is the *value* of a preceding option (`--title --help`).
        # A stray `--fill --help` at the end is deliberately NOT
        # disqualified either: mistaking a real creation for a help request
        # is a silent bypass, denying an actual help request is mild
        # friction, and the two failure directions are not symmetric.
        preceded_by_option = index > 0 and tokens[index - 1].startswith("-")
        if not preceded_by_option:
            return False
    rest = tokens[1:]
    return any(
        noun in REQUEST_NOUNS and verb == CREATE_VERB
        for noun, verb in zip(rest, rest[1:])
    )


def _has_skip(tokens):
    """True when this segment's own leading assignments request a skip.

    Reading it from the command string is the only thing that works: the hook is
    spawned by Claude Code and inherits Claude Code's environment, not the
    environment of the command being inspected. A leading `env` is stripped
    first so `env CLAUDE_SKIP_COMMENT_REVIEW=1 gh pr create` is recognised the
    same way `is_pr_create` recognises the `gh` invocation underneath it.
    """
    for token in _strip_wrapper_clis(tokens):
        if not _ASSIGNMENT.match(token):
            return False
        name, _, value = token.partition("=")
        if name == SKIP_VAR and value.lower() in _SKIP_TRUTHY:
            return True
    return False


def _apply_cd(tokens, cwd):
    """Directory after running this segment, or None if it cannot be resolved.

    Only plain `cd` forms are honoured. `cd -` depends on shell history the hook
    cannot see, so it returns None and the caller falls back to the event cwd --
    guessing there would be worse than admitting ignorance.
    """
    tokens = _strip_wrapper_clis(_drop_env_prefix(tokens))
    if not tokens or tokens[0] != "cd":
        return cwd
    operands = [t for t in tokens[1:] if not t.startswith("-")]
    if "-" in tokens[1:]:
        return None
    if not operands:
        return os.path.expanduser("~")
    target = os.path.expanduser(operands[0])
    if not os.path.isabs(target):
        target = os.path.join(cwd, target)
    return os.path.normpath(target)


def pr_create_cwd(command, cwd):
    """The directory the PR-creating segment actually runs in, or None.

    The hook event's `cwd` is the SESSION's directory, not the directory a `cd`
    earlier in the same command moved to. Without this, `cd other-repo && gh pr
    create` is judged against the wrong repository -- which denies a reviewed
    branch, and worse, PASSES an unreviewed one whenever the session directory
    happens to hold a valid receipt.

    Segments run left to right in one shell, so a `cd` applies to everything
    after it. Returns None when the command creates no PR.
    """
    current = cwd
    for tokens in segments(command):
        if is_pr_create(tokens) and not _has_skip(tokens):
            return current
        moved = _apply_cd(tokens, current)
        if moved is None:
            return current
        current = moved
    return None


def wants_skip(command):
    return any(_has_skip(tokens) for tokens in segments(command))


def matches(command):
    """True when some segment creates a PR and that same segment carries no skip.

    Per-segment, because a shell assignment applies only to the command it
    prefixes: in `CLAUDE_SKIP_COMMENT_REVIEW=1 ls; gh pr create` the skip belongs
    to `ls`, and treating it as global would hand out a free bypass.
    """
    return any(
        is_pr_create(tokens) and not _has_skip(tokens) for tokens in segments(command)
    )
