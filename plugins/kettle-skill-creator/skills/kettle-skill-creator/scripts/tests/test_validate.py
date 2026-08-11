"""These checks exist because no runtime test can catch them: a manifest in the
wrong place, a hooks.json without its wrapper, or a hook command with a relative
path all leave the plugin silently inert."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path.home() / ".claude/skills/kettle-skill-creator/scripts/validate-plugin.py"


def make_plugin(tmp_path, *, manifest_at_root=False, wrap_hooks=True,
                plugin_root_var=True, executable=True):
    repo = tmp_path / "market"
    plugin = repo / "plugins" / "demo"
    skill = plugin / "skills" / "demo"
    skill.mkdir(parents=True)
    (repo / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (repo / "justfile").write_text("")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)

    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: d\n---\n\nBody\n")
    (skill / "config.yaml").write_text("categories:\n  - claude-tooling\n")

    manifest_dir = plugin if manifest_at_root else plugin / ".claude-plugin"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    (manifest_dir / "plugin.json").write_text(json.dumps({"name": "demo", "description": "d"}))

    scripts = plugin / "hooks" / "scripts"
    scripts.mkdir(parents=True)
    gate = scripts / "gate.py"
    gate.write_text("#!/usr/bin/env python3\n")
    if executable:
        gate.chmod(0o755)

    prefix = "${CLAUDE_PLUGIN_ROOT}/" if plugin_root_var else ""
    entry = {"PreToolUse": [{"matcher": "Bash", "hooks": [
        {"type": "command", "command": f'python3 "{prefix}hooks/scripts/gate.py"', "timeout": 10}
    ]}]}
    payload = {"hooks": entry} if wrap_hooks else entry
    (plugin / "hooks" / "hooks.json").write_text(json.dumps(payload))
    return repo


def validate(repo, name="demo"):
    return subprocess.run([sys.executable, str(SCRIPT), name],
                          cwd=repo, capture_output=True, text=True)


def test_well_formed_plugin_validates(tmp_path):
    assert validate(make_plugin(tmp_path)).returncode == 0


def test_manifest_at_plugin_root_is_rejected(tmp_path):
    result = validate(make_plugin(tmp_path, manifest_at_root=True))
    assert result.returncode != 0
    assert ".claude-plugin" in result.stdout + result.stderr


def test_unwrapped_hooks_json_is_rejected(tmp_path):
    result = validate(make_plugin(tmp_path, wrap_hooks=False))
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    # Distinctive fragment of the top-level-wrapper message specifically, not
    # any hooks.json-related error -- a substring like "hooks" would also
    # match if the wrapper check were removed but some other error remained.
    assert "top-level 'hooks' key" in combined


def test_relative_hook_command_is_rejected(tmp_path):
    result = validate(make_plugin(tmp_path, plugin_root_var=False))
    assert result.returncode != 0
    assert "CLAUDE_PLUGIN_ROOT" in result.stdout + result.stderr


def test_non_executable_hook_script_is_rejected(tmp_path):
    result = validate(make_plugin(tmp_path, executable=False))
    assert result.returncode != 0
    assert "executable" in (result.stdout + result.stderr).lower()


def test_malformed_hooks_json_reports_an_error_not_a_traceback(tmp_path):
    """Under --all a traceback aborts the whole catalog run."""
    repo = make_plugin(tmp_path)
    (repo / "plugins" / "demo" / "hooks" / "hooks.json").write_text(
        json.dumps({"hooks": {"PreToolUse": ["Bash"]}})
    )
    result = validate(repo)
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Traceback" not in combined
    assert "objects" in combined or "must" in combined


def test_non_object_manifest_reports_an_error_not_a_traceback(tmp_path):
    """Valid JSON that isn't an object (e.g. a bare list) must not crash
    validate_plugin_root when it calls .get('name') on the parsed value."""
    repo = make_plugin(tmp_path)
    (repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json").write_text("[]")
    result = validate(repo)
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Traceback" not in combined
    assert "JSON object" in combined


def test_non_object_hooks_json_is_rejected_not_silently_ok(tmp_path):
    """A hooks.json whose top-level value is not an object (e.g. a bare list)
    must not be silently treated as absent -- that is a hook that can never
    register, and the validator must not print OK for it."""
    repo = make_plugin(tmp_path)
    (repo / "plugins" / "demo" / "hooks" / "hooks.json").write_text("[]")
    result = validate(repo)
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Traceback" not in combined
    assert "JSON object" in combined


def test_skill_only_plugin_still_validates(tmp_path):
    """The other 60+ plugins have no plugin-root dirs at all."""
    repo = tmp_path / "market"
    skill = repo / "plugins" / "plain" / "skills" / "plain"
    skill.mkdir(parents=True)
    (repo / ".claude-plugin").mkdir(parents=True)
    (repo / "justfile").write_text("")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (skill / "SKILL.md").write_text("---\nname: plain\ndescription: d\n---\n\nBody\n")
    (skill / "config.yaml").write_text("categories:\n  - claude-tooling\n")
    assert validate(repo, "plain").returncode == 0


def test_string_author_is_rejected(tmp_path):
    """Claude Code's loader requires an author OBJECT. A bare string makes the
    plugin fail to load with 'author: expected object, received string' -- a
    failure only a live install surfaces, so the validator must catch it."""
    repo = make_plugin(tmp_path)
    manifest = repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json"
    manifest.write_text(json.dumps({"name": "demo", "description": "d", "author": "Someone"}))
    result = validate(repo)
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert "author" in combined
    assert "Traceback" not in combined


def test_object_author_is_accepted(tmp_path):
    repo = make_plugin(tmp_path)
    manifest = repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json"
    manifest.write_text(json.dumps(
        {"name": "demo", "description": "d", "author": {"name": "someone"}}
    ))
    assert validate(repo).returncode == 0


def test_author_object_without_name_is_rejected(tmp_path):
    repo = make_plugin(tmp_path)
    manifest = repo / "plugins" / "demo" / ".claude-plugin" / "plugin.json"
    manifest.write_text(json.dumps(
        {"name": "demo", "description": "d", "author": {"email": "a@b.c"}}
    ))
    assert validate(repo).returncode != 0
