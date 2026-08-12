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
  - description field exists and is <1024 characters (Agent Skills spec limit)
  - config.yaml exists with valid categories
  - SKILL.md body is <500 lines (Agent Skills spec recommendation)
  - Each reference file is <250 lines (warns above 150)
"""

import json
import os
import re
import sys
from pathlib import Path

VALID_CATEGORIES = {
    "k8s-core", "k8s-storage", "k8s-apps", "homelab", "devops",
    "frontend", "golang", "cli", "tui", "docs", "claude-tooling", "shell", "discord",
    "linux",
}

# Group plugin names (these are auto-generated, not individual skills)
GROUP_NAMES = VALID_CATEGORIES | {"all"}

# Size limits, aligned to the Agent Skills spec (agentskills.io/specification).
#
# The description cap was previously 200, well under the spec's 1024. That is the
# wrong direction to squeeze: the description is what an agent matches a task
# against, so trimming it removes trigger keywords and hurts discovery, and
# marketplace.json truncates to 120 for display anyway. The body cap was 150
# against the spec's recommended 500.
#
# References are a house style rather than a spec rule. Files above the warn line
# are worth splitting, but making that an error meant 240 of 1078 files failed and
# the output was ignored. Erroring only on genuinely unwieldy files keeps the
# signal actionable; the warning still records the rest.
DESCRIPTION_MAX = 1024
BODY_MAX_LINES = 500
REFERENCE_MAX_LINES = 250
REFERENCE_WARN_LINES = 150

PLUGIN_ROOT_VAR = "${CLAUDE_PLUGIN_ROOT}"


def validate_plugin_root(plugin_dir: Path, name: str) -> list[str]:
    """Wiring checks for plugins that ship more than a skill.

    Purely additive: a skill-only plugin has none of these files and collects no
    errors. Each check covers a failure that is invisible at runtime -- the
    plugin simply does nothing.

    `plugin_dir` here is the PLUGIN ROOT (repo_root/plugins/<name>/), not the
    skill directory used elsewhere in this file.
    """
    errors = []

    stray = plugin_dir / "plugin.json"
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    if stray.is_file() and not manifest.is_file():
        errors.append(
            f"{name}: plugin.json must live in .claude-plugin/, not the plugin root"
        )
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{name}: .claude-plugin/plugin.json does not parse: {exc}")
        else:
            if not isinstance(data, dict):
                errors.append(
                    f"{name}: .claude-plugin/plugin.json must contain a JSON object"
                )
            elif data.get("name") != name:
                errors.append(
                    f"{name}: manifest name {data.get('name')!r} does not match the directory"
                )
            # Claude Code's runtime schema requires `author` to be an OBJECT.
            # plugin-dev's manifest-reference.md documents a bare string as an
            # "alternative format" -- the loader rejects it, and the plugin fails
            # to load with "author: expected object, received string". Caught only
            # by a live install, so it is checked here.
            if isinstance(data, dict) and "author" in data:
                author = data["author"]
                if not isinstance(author, dict):
                    errors.append(
                        f"{name}: manifest 'author' must be an object such as "
                        f'{{"name": "you"}}, not {type(author).__name__} '
                        f"-- Claude Code refuses to load the plugin otherwise"
                    )
                elif not author.get("name"):
                    errors.append(f"{name}: manifest 'author' object needs a 'name'")

    hooks_file = plugin_dir / "hooks" / "hooks.json"
    if hooks_file.is_file():
        parsed_ok = True
        try:
            payload = json.loads(hooks_file.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append(f"{name}: hooks/hooks.json does not parse: {exc}")
            parsed_ok = False
            payload = None
        if parsed_ok and not isinstance(payload, dict):
            errors.append(f"{name}: hooks/hooks.json must contain a JSON object")
        elif isinstance(payload, dict):
            if "hooks" not in payload:
                errors.append(
                    f"{name}: hooks/hooks.json needs a top-level 'hooks' key; "
                    "an unwrapped file registers nothing"
                )
            # Every level is type-checked. A validator that raises on the malformed
            # input it exists to catch is worse than none: under --all it aborts
            # the whole catalog run with a traceback.
            hooks_map = payload.get("hooks")
            if "hooks" in payload and not isinstance(hooks_map, dict):
                errors.append(f"{name}: hooks/hooks.json 'hooks' must be an object")
                hooks_map = {}
            for event, entries in (hooks_map or {}).items():
                if not isinstance(entries, list):
                    errors.append(f"{name}: hooks.json {event} must map to a list")
                    continue
                for entry in entries:
                    if not isinstance(entry, dict):
                        errors.append(f"{name}: hooks.json {event} entries must be objects")
                        continue
                    for hook in entry.get("hooks") or []:
                        if not isinstance(hook, dict):
                            errors.append(f"{name}: hooks.json {event} hooks must be objects")
                            continue
                        command = hook.get("command", "")
                        if not isinstance(command, str) or PLUGIN_ROOT_VAR not in command:
                            errors.append(
                                f"{name}: hook command must use {PLUGIN_ROOT_VAR}: {command!r}"
                            )
                            continue
                        if PLUGIN_ROOT_VAR + "/" not in command:
                            errors.append(
                                f"{name}: cannot locate hook script relative to "
                                f"{PLUGIN_ROOT_VAR}: {command!r}"
                            )
                            continue
                        relative = command.split(PLUGIN_ROOT_VAR + "/", 1)[1]
                        relative = relative.strip().strip('"').strip("'")
                        target = plugin_dir / relative
                        if not target.is_file():
                            errors.append(f"{name}: hook script not found: {relative}")
                        elif not os.access(target, os.X_OK):
                            errors.append(f"{name}: hook script is not executable: {relative}")

    scripts = plugin_dir / "skills" / name / "scripts"
    vendored = plugin_dir / "hooks" / "scripts"
    for shared in ("gitpaths.py", "receipt.py"):
        left, right = scripts / shared, vendored / shared
        if left.is_file() and right.is_file() and left.read_bytes() != right.read_bytes():
            errors.append(f"{name}: vendored {shared} has drifted from skills/*/scripts/")

    return errors


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

    # Plugin-root wiring checks (manifest location, hooks.json, hook scripts).
    # Note: plugin_dir above is the SKILL directory; the plugin root is one
    # level up, so this is computed independently rather than reused.
    errors.extend(validate_plugin_root(repo_root / "plugins" / name, name))

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
                elif len(desc) > DESCRIPTION_MAX:
                    errors.append(
                        f"Description is {len(desc)} chars (max {DESCRIPTION_MAX})"
                    )
                if "<" in desc or ">" in desc:
                    errors.append("Description contains angle brackets")

        # Body line count
        body_lines = content.split("\n")[body_start:]
        # Strip trailing empty lines
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()
        if len(body_lines) > BODY_MAX_LINES:
            errors.append(
                f"SKILL.md body is {len(body_lines)} lines (max {BODY_MAX_LINES})"
            )

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
            if line_count > REFERENCE_MAX_LINES:
                errors.append(
                    f"Reference {ref_file.name} is {line_count} lines "
                    f"(max {REFERENCE_MAX_LINES})"
                )
            elif line_count > REFERENCE_WARN_LINES:
                warnings.append(
                    f"Reference {ref_file.name} is {line_count} lines "
                    f"(prefer under {REFERENCE_WARN_LINES}; split it when convenient)"
                )

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
