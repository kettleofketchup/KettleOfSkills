#!/usr/bin/env python3
"""Extract comment spans from source files.

A character scanner per language, tracking string state, rather than line
regexes. The asymmetry that drives the design: missing a comment is a miss, but
mistaking a string literal for a comment means the reviewer edits live code. So
every ambiguity resolves toward skipping.

Reads newline-separated paths on stdin (not argv -- a wide rename can exceed
argv limits) and writes one JSON object on stdout.

Note: a path containing an embedded newline cannot be represented in this
protocol -- it fragments into multiple stdin lines, each looked up as its own
(almost certainly nonexistent) path. Out of scope: this is a limitation of the
newline-separated protocol itself, not something this module works around.

Paths are expected repo-relative, the way `git diff --name-only` emits them.
An absolute path whose ancestry cannot be related to the current working
directory only gets filename-shaped skip patterns applied (see
`file_skip_reason`) -- directory-shaped patterns like `(^|/)build/` are
unsafe to apply to an unrelativizable absolute path, since any ancestor
directory sharing that name would skip the entire repository.
"""

import json
import re
import sys
from collections import namedtuple
from pathlib import Path

MAX_BYTES = 1_000_000
BINARY_SNIFF_BYTES = 8192

# line:       tokens that start a comment running to end of line
# block:      (open, close, nests) -- Rust nests /* */ by language rule, so the
#             first closer is not necessarily the end of the comment
# strings:    (open, close, escapes, multiline) -- escapes means a backslash
#             escapes the next character; multiline=False means a literal whose
#             closer is not on the same line is not a literal at all. Without
#             that, an apostrophe in YAML or HTML prose ("don't") opens a string
#             that swallows every comment in the rest of the file.
# docstrings: whether a 3-character string delimiter in docstring position is a
#             reviewable comment (Python) rather than data
# heredocs:   whether `<<[-]DELIM` / `<<[-]'DELIM'` / `<<[-]"DELIM"` opens a shell
#             heredoc whose body is skipped outright. The body is literal data
#             passed to a command, not shell syntax -- a `#` inside it is not a
#             comment, and scanning it as ordinary code would emit one anyway.
Lang = namedtuple("Lang", "line block strings docstrings heredocs", defaults=(False, False))

_C_STRINGS = (('"', '"', True, False), ("'", "'", True, False))

# A triple-quoted literal is a docstring only as the first statement of a module,
# class, or function. Anywhere else it is data, and rewriting it would change what
# the program does -- so the same delimiter has to be read two ways.
_DOCSTRING_OWNER = re.compile(r"^(async\s+def|def|class)\b")

# Reimplemented locally rather than imported from hooks/scripts/prmatch.py --
# that module installs to a different path and cannot be imported from here.
# Matches `<<EOF`, `<<-EOF`, `<<'EOF'`, `<<"EOF"`.
_HEREDOC_START = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

# `$(( ... ))` arithmetic expansion contains `<<` (shift) that reads exactly
# like a heredoc opener to a scanner that only looks at the token in
# isolation -- `mask=$((1 << SHIFT))` would otherwise make `_HEREDOC_START`
# match with delimiter `SHIFT` and swallow every line up to the next one that
# happens to read `SHIFT`, silently eating real comments in between and
# reporting "skipped": null as if the file were fully scanned. Same guard as
# `prmatch._heredoc_start`, ported here since this module cannot import that
# one (see the note on `_HEREDOC_START` above).
#
# Spans are found by depth-tracked forward scan, not a DOTALL regex, and
# deliberately NOT line-scoped: `_HEREDOC_START`'s own `\s*` matches a
# newline, so `mask=$((1 <<\n  SHIFT))` -- a `$((` opened on one line and
# closed on the next, a normal bash formatting style -- has its `<<` on a
# different line than the delimiter, and a check confined to "the current
# line" never sees the closing `))` at all. A lazy DOTALL regex would fix
# that but introduces the opposite bug: `\$\(\(.*?\)\)` pairs the FIRST
# `$((` in the file with the NEXT `))` anywhere after it, which can belong to
# a second, unrelated arithmetic expression -- wrongly swallowing everything
# between them, including a real heredoc's `<<`. Depth tracking (mirroring
# `prmatch._arith_end`) pairs each `$((` with its own matching close and
# nothing else's.
def _arith_spans(text):
    """(start, end) index pairs for every `$(( ... ))` in `text`, in order,
    non-overlapping. An unterminated `$((` runs to end of text rather than
    being dropped -- the same "resolve toward skipping" rule as elsewhere in
    this module: better to over-protect a stray unclosed expansion than to
    treat its dangling `<<` as a real heredoc opener."""
    spans = []
    length = len(text)
    cursor = 0
    while True:
        start = text.find("$((", cursor)
        if start == -1:
            break
        depth = 2
        j = start + 3
        while j < length and depth > 0:
            if text[j] == "(":
                depth += 1
            elif text[j] == ")":
                depth -= 1
            j += 1
        spans.append((start, j))
        cursor = j
    return spans


def _in_arith_spans(spans, index):
    return any(start <= index < end for start, end in spans)


def _skip_heredoc(text, index, match):
    """Index just past a heredoc body opened by `match` at `index`.

    The body runs from the line after the opener to the first line whose
    stripped content equals the delimiter (leading tabs, permitted by `<<-`,
    fall out of the strip along with everything else). A heredoc with no
    closing delimiter runs to end of file rather than raising -- the same
    "resolve toward skipping" rule as everywhere else in this module.
    """
    delimiter = match.group(2)
    length = len(text)
    line_end = text.find("\n", index)
    if line_end == -1:
        return length
    cursor = line_end + 1
    while True:
        next_nl = text.find("\n", cursor)
        segment_end = next_nl if next_nl != -1 else length
        segment = text[cursor:segment_end]
        if segment.strip() == delimiter or next_nl == -1:
            return segment_end + 1 if next_nl != -1 else length
        cursor = next_nl + 1


def _in_docstring_position(text, index):
    """True when the literal opening at `index` is a docstring, not data."""
    preceding = [line.strip() for line in text[:index].splitlines()]
    meaningful = [line for line in preceding if line and not line.startswith("#")]
    if not meaningful:
        return True  # module docstring, possibly preceded by comments
    last = meaningful[-1]
    return last.endswith(":") and bool(_DOCSTRING_OWNER.match(last))


# TOML basic strings (`"`, `"""`) process backslash escapes; literal strings
# (`'`, `'''`) do not -- a backslash there is just a character.
_TOML_STRINGS = (
    ('"""', '"""', True, True),
    ("'''", "'''", False, True),
    ('"', '"', True, False),
    ("'", "'", False, False),
)

# Kotlin raw (triple-quoted) strings do not process escapes either; Java text
# blocks do.
_KOTLIN_STRINGS = (('"""', '"""', False, True),) + _C_STRINGS
_JAVA_STRINGS = (('"""', '"""', True, True),) + _C_STRINGS

_JS_FAMILY_STRINGS = _C_STRINGS + (("`", "`", True, True),)

LANGS = {
    "go": Lang(("//",), (("/*", "*/", False),), _C_STRINGS + (("`", "`", False, True),)),
    # Rust is the one language here that nests block comments by specification.
    "rust": Lang(("//",), (("/*", "*/", True),), _C_STRINGS),
    "typescript": Lang(("//",), (("/*", "*/", False),), _JS_FAMILY_STRINGS),
    # Same lexical rules as TypeScript -- kept as a distinct key (rather than
    # aliasing .js/.jsx onto "typescript") so `extract()`'s reported `lang`
    # is honest. The JSDoc `@param` carve-out in comment-classes.md depends on
    # that label: it tells the agent JSDoc blocks are off-limits in .js/.jsx
    # because there they are the only type information available, but
    # condensable in a typed language. A `.js` file reported as "typescript"
    # made every signal say "typed language, condensable" instead.
    "javascript": Lang(("//",), (("/*", "*/", False),), _JS_FAMILY_STRINGS),
    "c": Lang(("//",), (("/*", "*/", False),), _C_STRINGS),
    # Kotlin block comments nest by specification, like Rust's.
    "kotlin": Lang(("//",), (("/*", "*/", True),), _KOTLIN_STRINGS),
    "java": Lang(("//",), (("/*", "*/", False),), _JAVA_STRINGS),
    "python": Lang(
        ("#",), (),
        (('"""', '"""', True, True), ("'''", "'''", True, True)) + _C_STRINGS,
        docstrings=True,
    ),
    # Heredoc bodies are data passed to a command, not shell syntax.
    "shell": Lang(("#",), (), _C_STRINGS, heredocs=True),
    "yaml": Lang(("#",), (), _C_STRINGS),
    "nix": Lang(("#",), (("/*", "*/", False),), _C_STRINGS),
    "sql": Lang(("--",), (("/*", "*/", False),), (("'", "'", False, False),)),
    "lua": Lang(("--",), (("--[[", "]]", False),), _C_STRINGS),
    "html": Lang((), (("<!--", "-->", False),), _C_STRINGS),
    "toml": Lang(("#",), (), _TOML_STRINGS),
}

EXTENSIONS = {
    ".go": "go", ".rs": "rust",
    ".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".jsx": "javascript",
    ".c": "c", ".h": "c", ".cc": "c", ".cpp": "c", ".hpp": "c",
    ".java": "java", ".kt": "kotlin",
    ".py": "python", ".pyi": "python",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".nix": "nix",
    ".sql": "sql",
    ".lua": "lua",
    ".html": "html", ".htm": "html", ".xml": "html",
}

# Per-block token selection (`//` inside <script> versus `<!--` in the template)
# is not implemented, so these are skipped and counted rather than half-scanned
# with the HTML table, which would silently miss every script-block comment.
MULTI_LANGUAGE_SUFFIXES = {".vue", ".svelte", ".astro"}

SHEBANGS = (
    ("python", "python"), ("bash", "shell"), ("sh", "shell"), ("zsh", "shell"),
)

# Out of scope by decision, not by limitation: this repo alone has 628 tracked
# .md files whose `# Step 1:` headings and fenced examples are content.
OUT_OF_SCOPE_SUFFIXES = {".md", ".markdown", ".mdx"}


# --- File-level skips -------------------------------------------------------

# Directory-shaped: matches an ancestor directory component by name. Only safe
# to apply to a path known relative to the repo root -- an absolute path whose
# ancestry is unknown (main() invoked from outside the repo) could have any of
# these names above it by coincidence, and applying them there would skip the
# entire repository rather than the intended subtree.
SKIP_DIRECTORY_PATTERNS = tuple(re.compile(p) for p in (
    r"(^|/)vendor/", r"(^|/)node_modules/", r"(^|/)third_party/", r"(^|/)\.venv/",
    r"(^|/)target/", r"(^|/)build/", r"(^|/)out/", r"(^|/)gen/", r"(^|/)generated/",
    r"(^|/)dist/", r"(^|/)\.terraform/", r"(^|/)Pods/",
    r"(^|/)testdata/", r"(^|/)fixtures?/", r"(^|/)__fixtures__/", r"(^|/)golden/",
    r"(^|/)snapshots?/",
    # Comments inside migration sources are consumed by generators.
    r"(^|/)migrations?/.*\.sql$",
))

# Filename-shaped: anchored to the final path component. Safe to apply
# regardless of whether the path could be related to the repo root, since
# they identify the file itself rather than an ancestor directory.
SKIP_FILENAME_PATTERNS = tuple(re.compile(p) for p in (
    r"\.min\.js$", r"_pb2\.py$", r"\.pb\.go$", r"\.pb\.gw\.go$", r"_grpc\.pb\.py$",
    r"_generated\.go$", r"\.g\.dart$", r"\.freezed\.dart$",
    r"\.snap$", r"\.golden$", r"\.pot?$",
    r"(^|/)(package-lock\.json|yarn\.lock|poetry\.lock|Cargo\.lock|go\.sum)$",
    # Comments inside schema sources are consumed by generators.
    r"\.proto$", r"\.graphql$",
))

SKIP_FILE_PATH_PATTERNS = SKIP_DIRECTORY_PATTERNS + SKIP_FILENAME_PATTERNS

SKIP_FILE_MARKERS = re.compile(
    r"@generated|[Cc]ode generated|[Aa]uto-?generated|DO NOT (EDIT|MODIFY)|<auto-generated>"
)
GENERATED_MARKER_LINES = 30

# --- Span-level skips ------------------------------------------------------

# Anything a compiler, linter, bundler, database, or interpreter reads. Matched
# as a family: enumerating every tool is a losing game, and a missed entry means
# a silently disabled suppression and a broken build. golangci-lint honours
# `//nolint:` only with no space after the slashes, so these are preserved
# byte-for-byte -- a whitespace tidy is enough to break them.
DIRECTIVE_PATTERN = re.compile(
    r"""(?x)
    ^\s*
    (?:
        /\*[!+]                                 # SQL /*! version gate, /*+ hint -- opener-
                                                 # specific: /*!50001, /*+INDEX, with nothing
                                                 # between /* and the marker. A bare [!+] on
                                                 # any opener also matched Rust `//!` doc
                                                 # comments, Go "// +1 to that", shell
                                                 # "# +x is fine", and banner comments --
                                                 # ordinary prose this tool exists to review.
      |
        (?://|\#|--|/\*|<!--)\#?\s*
        (?:
            \+ \w{2,}                           # +goose, +kubebuilder, +migrate, +build --
                                                 # {2,} excludes "+1" / "+x", single-token
                                                 # prose no real directive name is that short
          | name:\s*\w+\s*:\w                   # sqlc -- name: GetUser :one
          | go\s*: | export\b                   # //go:embed ; //export MyFunc (no colon)
          | nolint | noqa | nocover | no\s?cover | noinspection | NOSONAR
          | type\s*: | pragma\s*: | pylint\s*: | mypy\s*:
          | (?:eslint|ts|prettier|black|isort|shellcheck|rubocop|hadolint|checkov|tfsec
            |tflint|trivy|semgrep|yamllint|ansible-lint|markdownlint|vale|istanbul|c8
            |coverage|swiftlint|clang-format|checkstyle|reek|stylelint|deno|biome|oxlint)
            \b[-\s:]*(?:disable|enable|ignore|skip|expect|off|on)
          | @(?:formatter|ts-|jsx|flow|deprecated\b|pure|__PURE__)
          | Deprecated\s*:                      # Go convention: no leading @
          | fmt\s*:\s*(?:off|on)
          | sourceMappingURL                     # opener above may be followed by `#`
          | \#__PURE__
          | (?:svelte-ignore|prettier-ignore)
          | syntax\s*= | escape\s*= | check\s*=
          | migrate\s*:\s*(?:up|down) | atlas\s*:
          | <reference\s
        )
    )
    """,
    re.IGNORECASE,
)

# Comments whose text is compared by a test runner. Rewording them fails a suite
# in a way nobody connects to a comment sweep.
TEST_ORACLE_MARKERS = (">>>", "```", ".. code-block::", "// Output:", "# Output:",
                       "Usage:", "@example")

# Never deleted; condensable only under the no-loss test.
PROTECTED_PREFIXES = ("NOTE", "WARNING", "CAUTION", "SAFETY", "HACK", "XXX", "FIXME", "TODO")

LICENCE_PATTERN = re.compile(r"SPDX-License-Identifier|Copyright\s|Licensed under|"
                             r"GNU General Public|MIT License|Apache License", re.IGNORECASE)

POSITION_LOCKED_LINES = 2

_COMMENT_OPENERS = re.compile(r"^\s*(?://+|\#|--+|/\*+|<!--|\"\"\"|''')\s*")


def _body(text):
    """Comment text with its opener and closer stripped, for prefix tests."""
    stripped = _COMMENT_OPENERS.sub("", text.strip())
    for closer in ("*/", "-->", '"""', "'''"):
        if stripped.endswith(closer):
            stripped = stripped[: -len(closer)]
    return stripped.strip()


def _match_path(path):
    """Posix-form path, plus whether directory-shaped patterns are safe on it.

    Directory patterns are repo-relative. An absolute path such as
    /home/u/build/proj/x.go, if matched against `(^|/)build/` directly, would
    skip the entire repository -- a silent, total no-op that looks like a
    clean sweep. So a directory pattern is only safe once the path is known
    relative to the repo (either it was already relative, or it is absolute
    and relativizable to `Path.cwd()`); the caller must fall back to
    filename-only patterns otherwise, since `main()` never chdirs and nothing
    upstream guarantees the invoker did either.
    """
    path = Path(path)
    if path.is_absolute():
        try:
            return path.relative_to(Path.cwd()).as_posix(), True
        except ValueError:
            return path.as_posix(), False
    return path.as_posix(), True


def file_skip_reason(path, head_text):
    posix, directory_patterns_safe = _match_path(path)
    patterns = SKIP_FILE_PATH_PATTERNS if directory_patterns_safe else SKIP_FILENAME_PATTERNS
    if any(pattern.search(posix) for pattern in patterns):
        return "excluded-path"
    head = "\n".join(head_text.splitlines()[:GENERATED_MARKER_LINES])
    if SKIP_FILE_MARKERS.search(head):
        return "generated"
    return None


def span_skip_reason(span, lang, path):
    text = span["text"]
    # Directives first: a directive in the first two lines is still a directive,
    # but position-locked is the more actionable label for a shebang.
    if span["start_line"] <= POSITION_LOCKED_LINES:
        return "position-locked"
    if DIRECTIVE_PATTERN.search(text):
        return "directive"
    if LICENCE_PATTERN.search(text):
        return "licence"
    if any(marker in text for marker in TEST_ORACLE_MARKERS):
        return "test-oracle"
    body = _body(text)
    for prefix in PROTECTED_PREFIXES:
        if body.upper().startswith(prefix):
            return "protected-prefix"
    return None


def detect_language(path):
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in EXTENSIONS:
        return EXTENSIONS[suffix]
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            first = fh.readline()
    except OSError:
        return None
    if first.startswith("#!"):
        for needle, lang in SHEBANGS:
            if needle in first:
                return lang
    return None


def scan(text, lang):
    """Comment spans in `text`, as 1-indexed inclusive line ranges."""
    spans = []
    index, line, length = 0, 1, len(text)
    # Longest tokens first so `--[[` wins over `--` and `"""` over `"`.
    line_tokens = sorted(lang.line, key=len, reverse=True)
    blocks = sorted(lang.block, key=lambda pair: len(pair[0]), reverse=True)
    strings = sorted(lang.strings, key=lambda triple: len(triple[0]), reverse=True)
    # Computed once up front (not on demand per `<<`) so a `$((` opened on one
    # line and closed several lines later is still recognised as a single span.
    arith_spans = _arith_spans(text) if lang.heredocs else ()

    while index < length:
        char = text[index]

        if char == "\n":
            line += 1
            index += 1
            continue

        if lang.heredocs and text.startswith("<<", index):
            heredoc_match = _HEREDOC_START.match(text, index)
            if heredoc_match and not _in_arith_spans(arith_spans, index):
                new_index = _skip_heredoc(text, index, heredoc_match)
                line += text.count("\n", index, new_index)
                index = new_index
                continue

        matched_string = next(
            (s for s in strings if text.startswith(s[0], index)), None
        )
        if matched_string:
            opener, closer, escapes, multiline = matched_string
            if not multiline:
                # A single-line literal whose closer is not on this line is not a
                # literal: it is an apostrophe in prose. Treating it as one would
                # swallow every comment in the rest of the file.
                probe = text.find(closer, index + len(opener))
                newline = text.find("\n", index + len(opener))
                if probe == -1 or (newline != -1 and newline < probe):
                    index += 1
                    continue
            # A docstring is a string literal to the parser but a comment to a
            # reader, so it is the one string we emit rather than skip.
            is_docstring = (
                lang.docstrings
                and len(opener) == 3
                and _in_docstring_position(text, index)
            )
            start_line = line
            start_index = index
            index += len(opener)
            while index < length:
                if escapes and text[index] == "\\":
                    if text[index + 1: index + 2] == "\n":
                        line += 1
                    index += 2
                    continue
                if text.startswith(closer, index):
                    index += len(closer)
                    break
                if text[index] == "\n":
                    line += 1
                index += 1
            if is_docstring:
                spans.append({
                    "start_line": start_line, "end_line": line,
                    "text": text[start_index:index], "kind": "docstring",
                })
            continue

        matched_block = next(
            (b for b in blocks if text.startswith(b[0], index)), None
        )
        if matched_block:
            opener, closer, nests = matched_block
            start_line = line
            # Walk to the matching closer by depth. Taking the first closer would
            # end a nested Rust comment early, and rewriting that span would leave
            # a dangling tail behind -- the reviewer editing live code.
            cursor, depth = index + len(opener), 1
            while cursor < length:
                if nests and text.startswith(opener, cursor):
                    depth += 1
                    cursor += len(opener)
                    continue
                if text.startswith(closer, cursor):
                    depth -= 1
                    cursor += len(closer)
                    if depth == 0:
                        break
                    continue
                cursor += 1
            end = cursor
            body = text[index:end]
            line += body.count("\n")
            spans.append({
                "start_line": start_line, "end_line": line,
                "text": body, "kind": "block",
            })
            index = end
            continue

        matched_line = next(
            (t for t in line_tokens if text.startswith(t, index)), None
        )
        if matched_line:
            end = text.find("\n", index)
            end = length if end == -1 else end
            spans.append({
                "start_line": line, "end_line": line,
                "text": text[index:end], "kind": "line",
            })
            index = end
            continue

        index += 1

    return spans


def extract(path):
    path = Path(path)
    record = {"file": str(path), "lang": None, "comments": [], "skipped": None}

    if path.suffix.lower() in OUT_OF_SCOPE_SUFFIXES:
        record["skipped"] = "markdown-out-of-scope"
        return record
    if path.suffix.lower() in MULTI_LANGUAGE_SUFFIXES:
        record["skipped"] = "multi-language-unsupported"
        return record
    try:
        raw = path.read_bytes()
    except OSError:
        record["skipped"] = "unreadable"
        return record
    if len(raw) > MAX_BYTES:
        record["skipped"] = "too-large"
        return record
    if b"\x00" in raw[:BINARY_SNIFF_BYTES]:
        record["skipped"] = "binary"
        return record

    # Decoded without universal-newline translation, so a CRLF file's comment
    # `text` keeps its trailing `\r`. That is deliberate: `text` is used to
    # locate and replace the span, so it must match the file's bytes exactly.
    text = raw.decode("utf-8", errors="replace")

    reason = file_skip_reason(path, text)
    if reason:
        record["skipped"] = reason
        return record

    lang = detect_language(path)
    if lang is None:
        record["skipped"] = "unknown-language"
        return record

    record["lang"] = lang
    spans = scan(text, LANGS[lang])
    for span in spans:
        span["skip"] = span_skip_reason(span, lang, path)
    record["comments"] = spans
    return record


def main():
    paths = [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]
    json.dump({"files": [extract(p) for p in paths]}, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
