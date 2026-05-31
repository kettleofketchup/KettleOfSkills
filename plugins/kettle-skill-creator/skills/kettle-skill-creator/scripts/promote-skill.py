#!/usr/bin/env python3
"""
Promote a skill from the dotfiles source-of-truth into the kettleofskills marketplace.

Copies SKILL.md, references/, and scripts/ from a dotfiles skill into
plugins/<name>/skills/<name>/. An existing config.yaml is always preserved. For a
brand-new plugin, --categories is required and a config.yaml is written.

Usage:
    promote-skill.py <skill-name> [--categories cat1,cat2,...] [--source <dir>] [--dry-run]

Examples:
    # Update an existing marketplace skill from dotfiles (config.yaml preserved)
    promote-skill.py authentik

    # Create a new marketplace plugin from a dotfiles skill
    promote-skill.py hyprland --categories linux

    # Preview without writing
    promote-skill.py grafana --dry-run

Source defaults to ~/.claude/skills (which symlinks to the dotfiles skills dir).
Run from anywhere inside the kettleofskills repo; the repo root is auto-located.
"""

import os
import shutil
import sys
from pathlib import Path

VALID_CATEGORIES = {
    "k8s-core", "k8s-storage", "k8s-apps", "homelab", "devops",
    "frontend", "golang", "docs", "claude-tooling", "shell", "discord",
    "linux",
}

# Subdirectories mirrored from source into the marketplace plugin.
MIRRORED_DIRS = ("references", "scripts")

# Generated artifacts never copied into the marketplace.
IGNORE = shutil.ignore_patterns(
    "__pycache__", "*.pyc", "*.pyo", ".pytest_cache", ".coverage", ".DS_Store",
)


def find_repo_root() -> Path:
    """Find the kettleofskills repo root by looking for the justfile + plugins/ dir."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "justfile").exists() and (parent / "plugins").is_dir():
            return parent
    return cwd


def parse_args(argv: list[str]) -> tuple[str, list[str], Path, bool]:
    if len(argv) < 2 or argv[1].startswith("-"):
        print(__doc__.strip())
        sys.exit(1)

    name = argv[1]
    categories: list[str] = []
    source = Path(os.path.expanduser("~/.claude/skills"))
    dry_run = False

    i = 2
    while i < len(argv):
        arg = argv[i]
        if arg == "--categories":
            i += 1
            if i >= len(argv):
                print("Error: --categories requires a value")
                sys.exit(1)
            categories = [c.strip() for c in argv[i].split(",") if c.strip()]
        elif arg == "--source":
            i += 1
            if i >= len(argv):
                print("Error: --source requires a value")
                sys.exit(1)
            source = Path(os.path.expanduser(argv[i]))
        elif arg == "--dry-run":
            dry_run = True
        else:
            print(f"Error: unknown argument '{arg}'")
            sys.exit(1)
        i += 1

    return name, categories, source, dry_run


def mirror_dir(src: Path, dst: Path, dry_run: bool) -> None:
    """Replace dst with a fresh copy of src, ignoring generated artifacts.

    An empty source dir (or one holding only ignored files) is treated as absent:
    the dst is removed and nothing is copied.
    """
    src_has_content = src.is_dir() and any(src.iterdir())
    existed = dst.exists() or dst.is_symlink()

    if existed:
        print(f"  ~ replace {dst.name}/" if src_has_content else f"  - remove {dst.name}/ (stale)")
        if not dry_run:
            shutil.rmtree(dst)

    if src_has_content:
        if not existed:
            print(f"  + copy {src.name}/")
        if not dry_run:
            shutil.copytree(src, dst, ignore=IGNORE)
            # Drop the dir if everything in it was ignored.
            if not any(dst.rglob("*")):
                shutil.rmtree(dst)


def main() -> None:
    name, categories, source_root, dry_run = parse_args(sys.argv)

    # Validate any provided categories up front.
    for cat in categories:
        if cat == "all":
            print("Error: do not pass 'all' (auto-assigned by sync-groups)")
            sys.exit(1)
        if cat not in VALID_CATEGORIES:
            print(f"Error: unknown category '{cat}'")
            print(f"Valid categories: {', '.join(sorted(VALID_CATEGORIES))}")
            sys.exit(1)

    source_skill = source_root / name
    source_md = source_skill / "SKILL.md"
    if not source_skill.is_dir():
        print(f"Error: source skill not found: {source_skill}")
        sys.exit(1)
    if not source_md.is_file():
        print(f"Error: source SKILL.md not found: {source_md}")
        sys.exit(1)

    repo_root = find_repo_root()
    dest = repo_root / "plugins" / name / "skills" / name
    config_yaml = dest / "config.yaml"
    is_new = not dest.exists()

    print(f"Promoting '{name}'")
    print(f"  source: {source_skill}")
    print(f"  dest:   plugins/{name}/skills/{name}/")
    if dry_run:
        print("  (dry run — no changes written)")

    if is_new:
        if not categories:
            print("Error: new plugin requires --categories (e.g. --categories linux)")
            sys.exit(1)
        print(f"  NEW plugin — categories: {', '.join(categories)}")
        if not dry_run:
            dest.mkdir(parents=True)
            cat_lines = "\n".join(f"  - {c}" for c in categories)
            config_yaml.write_text(f"categories:\n{cat_lines}\n")
        print("  + config.yaml")
    else:
        if categories:
            print("  note: --categories ignored; existing config.yaml is preserved")
        if not config_yaml.is_file():
            print(f"  WARNING: existing plugin has no config.yaml at {config_yaml}")

    # Copy SKILL.md
    print("  ~ SKILL.md")
    if not dry_run:
        shutil.copy2(source_md, dest / "SKILL.md")

    # Mirror references/ and scripts/ (config.yaml untouched)
    for sub in MIRRORED_DIRS:
        mirror_dir(source_skill / sub, dest / sub, dry_run)

    print("Done." if not dry_run else "Dry run complete.")


if __name__ == "__main__":
    main()
