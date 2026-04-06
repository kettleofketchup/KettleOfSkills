#!/usr/bin/env python3
"""
Initialize a new skill plugin in the kettleofskills repo.

Usage:
    init-plugin.py <skill-name> [--categories cat1,cat2,...]

Examples:
    init-plugin.py my-new-skill
    init-plugin.py my-new-skill --categories devops,k8s-core
"""

import re
import sys
from pathlib import Path

VALID_CATEGORIES = [
    "k8s-core", "k8s-storage", "k8s-apps", "homelab", "devops",
    "frontend", "golang", "docs", "claude-tooling", "shell", "discord",
]

SKILL_MD_TEMPLATE = """---
name: {name}
description: >-
  TODO: Action-oriented description under 200 chars. Include when to use this skill
  and specific trigger scenarios. Third person ("This skill should be used when...").
---

# {title}

TODO: Practical instructions for Claude Code. Keep under 150 lines.

## Overview

TODO: 1-2 sentences explaining what this skill enables.

## Usage

TODO: Add workflow steps, commands, code examples.

## References

TODO: Link to reference files if needed:
- `references/example.md` -- description
"""

CONFIG_YAML_TEMPLATE = """categories:
{categories}"""

REFERENCE_TEMPLATE = """# {title}

TODO: Add detailed reference content here. Keep under 150 lines.
"""


def title_case(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split("-"))


def validate_name(name: str) -> tuple[bool, str]:
    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", name) and not re.match(r"^[a-z0-9]$", name):
        return False, f"Name '{name}' must be kebab-case (lowercase, digits, hyphens, no leading/trailing hyphens)"
    if "--" in name:
        return False, f"Name '{name}' cannot contain consecutive hyphens"
    if len(name) > 60:
        return False, f"Name '{name}' exceeds 60 characters"
    return True, ""


def find_repo_root() -> Path:
    """Find the kettleofskills repo root by looking for the justfile + plugins/ dir."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "justfile").exists() and (parent / "plugins").is_dir():
            return parent
    return cwd


def main():
    if len(sys.argv) < 2:
        print("Usage: init-plugin.py <skill-name> [--categories cat1,cat2,...]")
        print(f"\nValid categories: {', '.join(VALID_CATEGORIES)}")
        sys.exit(1)

    name = sys.argv[1]

    # Parse optional categories
    categories = []
    if "--categories" in sys.argv:
        idx = sys.argv.index("--categories")
        if idx + 1 < len(sys.argv):
            categories = [c.strip() for c in sys.argv[idx + 1].split(",") if c.strip()]

    # Validate name
    valid, err = validate_name(name)
    if not valid:
        print(f"Error: {err}")
        sys.exit(1)

    # Validate categories
    for cat in categories:
        if cat not in VALID_CATEGORIES:
            print(f"Error: Unknown category '{cat}'")
            print(f"Valid categories: {', '.join(VALID_CATEGORIES)}")
            sys.exit(1)

    # Check for existing plugin
    repo_root = find_repo_root()
    plugin_dir = repo_root / "plugins" / name / "skills" / name
    if plugin_dir.exists():
        print(f"Error: Plugin already exists at {plugin_dir}")
        sys.exit(1)

    # Create directories
    plugin_dir.mkdir(parents=True)
    refs_dir = plugin_dir / "references"
    refs_dir.mkdir()

    # Write SKILL.md
    skill_md = SKILL_MD_TEMPLATE.format(name=name, title=title_case(name))
    (plugin_dir / "SKILL.md").write_text(skill_md)

    # Write config.yaml
    if not categories:
        cat_lines = "  - TODO  # Replace with valid category"
    else:
        cat_lines = "\n".join(f"  - {c}" for c in categories)
    (plugin_dir / "config.yaml").write_text(CONFIG_YAML_TEMPLATE.format(categories=cat_lines))

    # Write example reference
    ref_content = REFERENCE_TEMPLATE.format(title=title_case(name) + " Reference")
    (refs_dir / "example.md").write_text(ref_content)

    # Report
    print(f"Created plugin: plugins/{name}/skills/{name}/")
    print(f"  SKILL.md         -- edit frontmatter and body")
    print(f"  config.yaml      -- {'set' if categories else 'assign'} categories")
    print(f"  references/      -- add detailed reference docs")
    print()
    print("Next steps:")
    print("  1. Edit SKILL.md: fill in description and body")
    print("  2. Edit config.yaml: assign categories" if not categories else "  2. config.yaml already set")
    print("  3. Add/edit reference files in references/")
    print("  4. Validate: python3 plugins/skill-creator-kettleofskills/skills/skill-creator-kettleofskills/scripts/validate-plugin.py " + name)
    print("  5. Sync: just sync")


if __name__ == "__main__":
    main()
