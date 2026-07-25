"""Wiring tests. Every other suite pipes JSON straight into a script, so none of
them would notice a manifest in the wrong directory, a hooks.json missing its
wrapper, or a relative command path -- all of which make the plugin silently do
nothing."""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_manifest_lives_in_claude_plugin_dir():
    """A root-level plugin.json is not read. 46 of the 52 manifests installed on
    this machine are at .claude-plugin/plugin.json, and the authoritative
    reference says Claude Code will not recognise the plugin otherwise."""
    assert (ROOT / ".claude-plugin" / "plugin.json").is_file()
    assert not (ROOT / "plugin.json").exists()


def test_manifest_name_matches_the_directory():
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert manifest["name"] == "comment-reviewer"
    assert manifest["description"]


def test_manifest_declares_no_component_paths():
    """Components are auto-discovered. Declaring them invites drift."""
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert not {"hooks", "agents", "commands", "skills"} & set(manifest)


def test_hooks_json_has_the_top_level_wrapper():
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    assert "hooks" in hooks
    assert "PreToolUse" in hooks["hooks"]


def test_hook_matcher_is_bash():
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    assert hooks["hooks"]["PreToolUse"][0]["matcher"] == "Bash"


def test_every_hook_command_uses_the_plugin_root_variable():
    """Installed plugins live under a per-version cache path, so a relative
    command path resolves to nothing."""
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    for entry in hooks["hooks"]["PreToolUse"]:
        for hook in entry["hooks"]:
            assert "${CLAUDE_PLUGIN_ROOT}" in hook["command"]


def test_referenced_hook_scripts_exist_and_are_executable():
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    for entry in hooks["hooks"]["PreToolUse"]:
        for hook in entry["hooks"]:
            relative = hook["command"].split("${CLAUDE_PLUGIN_ROOT}/")[1].rstrip('"')
            target = ROOT / relative
            assert target.is_file(), target
            assert os.access(target, os.X_OK), f"chmod +x {target}"


def test_hook_declares_a_timeout():
    hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())
    for entry in hooks["hooks"]["PreToolUse"]:
        for hook in entry["hooks"]:
            assert isinstance(hook.get("timeout"), int)
