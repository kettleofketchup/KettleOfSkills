"""The marketplace validator enforces these limits repo-wide. Catching them here
means a promotion never lands a plugin that fails validation.

Paths come from paths.py, not from ROOT: after promotion SKILL.md and references/
move under skills/<name>/ while tests/ stays at the plugin root, and `just test`
runs the promoted tree.

The structural tests above catch a missing file or a blown line budget. They would
not catch a well-meaning copy edit that quietly deleted a safety valve -- the class
rules and never-touch tiers could be replaced with plausible-sounding nonsense and
every test above would still pass. `test_safety_valve_survives` and
`test_never_touch_lists_exactly_the_extractors_skip_reason_strings` close that gap.
"""

import ast
import inspect
import re

import extract_comments
import paths
import pytest

MAX_BODY_LINES = 150
MAX_DESCRIPTION_CHARS = 200
REQUIRED_REFERENCES = {"comment-classes.md", "never-touch.md", "rewrite-guidelines.md"}


def skill_text():
    assert paths.SKILL_MD.is_file(), f"SKILL.md not found at {paths.SKILL_MD}"
    return paths.SKILL_MD.read_text()


def frontmatter_and_body(text):
    assert text.startswith("---\n")
    _, front, body = text.split("---\n", 2)
    return front, body


def test_the_three_references_exist():
    """The class rules and both never-touch tiers live only in these files. The
    loop-based tests below pass on an empty directory, so this one carries them."""
    assert {p.name for p in paths.REFERENCES.glob("*.md")} == REQUIRED_REFERENCES


def test_skill_frontmatter_name_matches_the_directory():
    front, _ = frontmatter_and_body(skill_text())
    assert "name: comment-reviewer" in front


def test_skill_description_fits_the_validator_limits():
    front, _ = frontmatter_and_body(skill_text())
    line = next(l for l in front.splitlines() if l.startswith("description:"))
    description = line.split("description:", 1)[1].strip()
    assert 0 < len(description) <= MAX_DESCRIPTION_CHARS
    assert "<" not in description and ">" not in description


def test_skill_body_is_within_the_line_budget():
    _, body = frontmatter_and_body(skill_text())
    assert len(body.splitlines()) <= MAX_BODY_LINES


def test_every_reference_is_within_the_line_budget():
    for reference in paths.REFERENCES.glob("*.md"):
        assert len(reference.read_text().splitlines()) <= MAX_BODY_LINES, reference


def test_skill_documents_the_group_install_limitation():
    assert "comment-reviewer@kettleofskills" in skill_text()


def test_references_are_all_linked_from_the_skill():
    body = skill_text()
    for reference in paths.REFERENCES.glob("*.md"):
        assert reference.name in body, f"{reference.name} is unreachable"


# --- Safety-valve survival ---------------------------------------------------
#
# String matching, not quality judgment: the goal is to detect deletion of a
# rule, not to grade its prose. Fragments are whitespace-normalized before
# comparison so an ordinary rewrap (these files hard-wrap around 90 columns)
# can't turn a real deletion into a false pass, or a harmless line-break shift
# into a false failure.

def _normalize(text):
    return re.sub(r"\s+", " ", text)


def _reference_text(filename):
    return (paths.REFERENCES / filename).read_text()


CLASSES_MD = "comment-classes.md"
NEVER_TOUCH_MD = "never-touch.md"
REWRITE_MD = "rewrite-guidelines.md"

# (id, reference filename, fragment or tuple of fragments all required)
SAFETY_VALVES = [
    ("class-a-unrecoverable-reason-reported-not-deleted", CLASSES_MD,
     "not recoverable from surrounding code, report it — never delete it and "
     "never guess a replacement"),
    ("class-a-id-shaped-traceability-never-deleted", CLASSES_MD,
     "never delete an ID-shaped traceability comment"),
    ("class-a-never-invent-an-issue-reference", CLASSES_MD,
     "never invent an issue, ticket, or PR reference"),
    ("class-a-history-belongs-in-git-is-false-under-squash-merge", CLASSES_MD,
     '"History belongs in git" is false under squash-merge'),
    ("class-a-tell-tales-are-candidates-needing-a-second-test", CLASSES_MD,
     ("Tell-tales are candidates, not verdicts", "second test")),
    ("class-a-non-triggers", CLASSES_MD,
     ("RFC, standard, and protocol references",
      "Algorithm-step and phase numbering",
      "Concurrency-state descriptions")),
    ("class-b-never-widen-a-guarantee-report-instead", CLASSES_MD,
     ("Never widen a stated guarantee", "report instead of rewriting")),
    ("class-c-fact-enumeration-emitted-in-the-summary", CLASSES_MD,
     "Emit that enumeration in the returned summary for every Class C rewrite"),
    ("class-c-shorter-is-clauses-not-characters", CLASSES_MD,
     '"Shorter" is measured in clauses, not characters'),
    ("class-c-no-rewrite-drops-a-numeric-literal", CLASSES_MD,
     "No rewrite may drop a numeric literal, unit, or identifier"),
    ("class-c-leave-alone-and-report-when-nothing-wins", CLASSES_MD,
     "the comment is left alone and reported"),
    ("precedence-any-skip-beats-any-class", "SKILL.md",
     ("mechanical never-touch → commented-out code → judgment never-touch → "
      "Class A → B → C", "any skip beats any class")),
    ("commented-out-code-report-never-delete", NEVER_TOUCH_MD,
     ("Commented-out code", "report, never delete")),
    ("natural-language-never-translate", REWRITE_MD, "Nothing is ever translated"),
]


@pytest.mark.parametrize(
    "filename, fragment", [valve[1:] for valve in SAFETY_VALVES],
    ids=[valve[0] for valve in SAFETY_VALVES],
)
def test_safety_valve_survives(filename, fragment):
    """Each of these fragments came from the design spec's 'Review rules' section
    by way of a code-review round that found the first test suite (structure-only)
    would not notice any of them being deleted. See SAFETY_VALVES for the list --
    the parametrize id above names which valve failed."""
    text = skill_text() if filename == "SKILL.md" else _reference_text(filename)
    normalized = _normalize(text)
    fragments = fragment if isinstance(fragment, tuple) else (fragment,)
    for piece in fragments:
        assert _normalize(piece) in normalized, f"{filename} is missing: {piece!r}"


def _returned_string_literals(func_name):
    """String literals a function in extract_comments.py can `return`.

    AST, not a hardcoded list: the point of the paired test below is that the
    doc and the code cannot silently drift apart. Hardcoding this set here
    would just move the drift risk from the doc into the test.
    """
    tree = ast.parse(inspect.getsource(extract_comments))
    func = next(
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == func_name
    )
    return {
        node.value.value
        for node in ast.walk(func)
        if isinstance(node, ast.Return)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    }


def _never_touch_mechanical_table_reasons():
    """Reason strings listed in never-touch.md's mechanical-tier table.

    Scoped to that one table (not the separate six-whole-file-skip-reasons
    table added alongside it) by anchoring on its header row, so this can't
    accidentally start asserting equality against unrelated skip reasons.
    """
    doc = _reference_text(NEVER_TOUCH_MD)
    header = r"\| Reason string \| What it means \|\n.*?\n"
    match = re.search(header + r"((?:\|.*\n)+)", doc)
    assert match, "mechanical-tier table not found in never-touch.md"
    return set(re.findall(r"^\|\s*`([a-z-]+)`", match.group(1), re.MULTILINE))


def test_never_touch_lists_exactly_the_extractors_skip_reason_strings():
    """Task 6 changed these strings once already. Deriving the code side from
    the module (rather than hardcoding it here) means a future rename shows up
    as a doc/code mismatch instead of two independent things silently drifting."""
    code_reasons = _returned_string_literals(
        "span_skip_reason"
    ) | _returned_string_literals("file_skip_reason")
    assert _never_touch_mechanical_table_reasons() == code_reasons
