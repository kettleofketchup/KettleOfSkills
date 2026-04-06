#!/usr/bin/env python3
"""
Validate a skill plugin in the kettleofskills repo.

Usage:
    validate-plugin.py <skill-name>
    validate-plugin.py --all

Checks:
  - Directory structure (plugins/<name>/skills/<name>/)
  - SKILL.md exists with valid YAML frontmatter
  - name field matches directory name, is kebab-case
  - description field exists and is <200 characters
  - config.yaml exists with valid categories
  - SKILL.md body is <150 lines
  - Each reference file is <150 lines
"""

import re
import sys
from pathlib import Path

VALID_CATEGORIES = {
    "k8s-core", "k8s-storage", "k8s-apps", "homelab", "devops",
    "frontend", "golang", "docs", "claude-tooling", "shell", "discord",
}

# Group plugin names (these are auto-generated, not individual skills)
GROUP_NAMES = VALID_CATEGORIES | {"all"}


def find_repo_root() -> Path:
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "justfile").exists() and (parent / "plugins").is_dir():
            return parent
    return cwd


def extract_frontmatter(text: str) -> tuple[str | None, int]:
    """Extract YAML frontmatter and return (frontmatter_str, body_start_line)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, 0
    end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end < 0:
        return None, 0
    return "\n".join(lines[1:end]), end + 1


def extract_description(frontmatter: str) -> str:
    """Parse description from frontmatter, handling multiline YAML scalars."""
    desc = ""
    in_desc = False
    for line in frontmatter.split("\n"):
        if line.startswith("description:"):
            val = line.split(":", 1)[1].strip()
            if val in (">-", ">", "|", "|-"):
                in_desc = True
                continue
            desc = val
            break
        elif in_desc:
            if line and line[0] in (" ", "\t"):
                desc += (" " if desc else "") + line.strip()
            else:
                break
    # Strip surrounding quotes
    for q in ('"', "'"):
        if desc.startswith(q) and desc.endswith(q):
            desc = desc[1:-1]
            break
    return desc


def validate_plugin(name: str, repo_root: Path) -> list[str]:
    """Validate a single plugin. Returns list of error strings (empty = valid)."""
    errors = []
    warnings = []
    plugin_dir = repo_root / "plugins" / name / "skills" / name

    # Directory structure
    if not plugin_dir.is_dir():
        return [f"Plugin directory not found: plugins/{name}/skills/{name}/"]

    # SKILL.md
    skill_md = plugin_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
    else:
        content = skill_md.read_text()
        fm, body_start = extract_frontmatter(content)

        if fm is None:
            errors.append("SKILL.md missing YAML frontmatter (--- delimiters)")
        else:
            # Check name field
            name_match = re.search(r"^name:\s*(.+)", fm, re.MULTILINE)
            if not name_match:
                errors.append("SKILL.md frontmatter missing 'name' field")
            else:
                fm_name = name_match.group(1).strip()
                if fm_name != name:
                    errors.append(f"Frontmatter name '{fm_name}' does not match directory name '{name}'")
                if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", fm_name) and not re.match(r"^[a-z0-9]$", fm_name):
                    errors.append(f"Name '{fm_name}' is not valid kebab-case")
                if "--" in fm_name:
                    errors.append(f"Name '{fm_name}' contains consecutive hyphens")

            # Check description field
            if "description:" not in fm:
                errors.append("SKILL.md frontmatter missing 'description' field")
            else:
                desc = extract_description(fm)
                if not desc or desc.startswith("TODO"):
                    warnings.append("Description is still a TODO placeholder")
                elif len(desc) > 200:
                    errors.append(f"Description is {len(desc)} chars (max 200)")
                if "<" in desc or ">" in desc:
                    errors.append("Description contains angle brackets")

        # Body line count
        body_lines = content.split("\n")[body_start:]
        # Strip trailing empty lines
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()
        if len(body_lines) > 150:
            errors.append(f"SKILL.md body is {len(body_lines)} lines (max 150)")

    # config.yaml
    config_yaml = plugin_dir / "config.yaml"
    if not config_yaml.exists():
        errors.append("config.yaml not found")
    else:
        config_text = config_yaml.read_text()
        if "categories:" not in config_text:
            errors.append("config.yaml missing 'categories:' key")
        else:
            cats = re.findall(r"^\s*-\s*(\S+)", config_text, re.MULTILINE)
            if not cats:
                errors.append("config.yaml has no categories listed")
            for cat in cats:
                if cat == "TODO":
                    warnings.append("config.yaml still has TODO placeholder category")
                elif cat == "all":
                    warnings.append("Do not list 'all' in config.yaml (auto-assigned)")
                elif cat not in VALID_CATEGORIES:
                    errors.append(f"Unknown category '{cat}' in config.yaml")

    # Reference file sizes
    refs_dir = plugin_dir / "references"
    if refs_dir.is_dir():
        for ref_file in refs_dir.rglob("*.md"):
            line_count = len(ref_file.read_text().split("\n"))
            if line_count > 150:
                errors.append(f"Reference {ref_file.name} is {line_count} lines (max 150)")

    # Print warnings
    for w in warnings:
        print(f"  WARNING: {w}")

    return errors


def main():
    repo_root = find_repo_root()

    if len(sys.argv) < 2:
        print("Usage: validate-plugin.py <skill-name>")
        print("       validate-plugin.py --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        # Find all individual plugins (those with a real config.yaml, not symlinked)
        names = []
        for config in sorted((repo_root / "plugins").glob("*/skills/*/config.yaml")):
            skill_dir = config.parent
            if not skill_dir.is_symlink():
                names.append(skill_dir.name)
        names = sorted(set(names))
    else:
        names = [sys.argv[1]]

    total_errors = 0
    for name in names:
        if name in GROUP_NAMES:
            continue  # Skip group directories
        print(f"Validating: {name}")
        errors = validate_plugin(name, repo_root)
        if errors:
            for e in errors:
                print(f"  ERROR: {e}")
            total_errors += len(errors)
        else:
            print("  OK")

    if total_errors > 0:
        print(f"\n{total_errors} error(s) found")
        sys.exit(1)
    else:
        print(f"\nAll {len(names)} plugin(s) valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
