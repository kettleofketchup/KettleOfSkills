"""Resolve this plugin's layout, which differs between the two trees it lives in.

    source:    <root>/SKILL.md          <root>/scripts/       <root>/tests/
    promoted:  <root>/skills/<name>/SKILL.md, .../scripts/    <root>/tests/

`just test` globs plugins/*/tests, so the promoted layout is the one CI exercises.
Every test module imports its paths from here rather than deriving them.
"""

from pathlib import Path

NAME = "comment-reviewer"

ROOT = Path(__file__).resolve().parent.parent
_PROMOTED_SKILL = ROOT / "skills" / NAME

SKILL_DIR = _PROMOTED_SKILL if _PROMOTED_SKILL.is_dir() else ROOT
SCRIPTS = SKILL_DIR / "scripts"
REFERENCES = SKILL_DIR / "references"
SKILL_MD = SKILL_DIR / "SKILL.md"
HOOK_SCRIPTS = ROOT / "hooks" / "scripts"

# Named samples/, never fixtures/: `fixtures?/` is one of the extractor's own
# skip patterns, so samples stored there would be skipped by the code under test.
SAMPLES = Path(__file__).resolve().parent / "samples"
NEGATIVE_SAMPLES = SAMPLES / "negative"
