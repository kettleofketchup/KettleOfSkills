# Hooks and Plugins

Customize and extend Claude Code behavior.

- **Hooks** — pre-tool, post-tool, user-prompt-submit hooks, configuration, environment variables, examples, security: `references/hooks.md`
- **Plugins** — plugin structure, plugin.json, installing/managing/creating/publishing plugins, private marketplaces: `references/plugins.md`

## Quick Reference

**Hooks** are configured in `.claude/hooks.json`:
```json
{
  "hooks": {
    "pre-tool": { "bash": "./scripts/validate.sh" },
    "post-tool": { "write": "./scripts/format.sh" },
    "user-prompt-submit": "./scripts/track.sh"
  }
}
```

**Plugins** install from GitHub, npm, or local path:
```bash
claude plugin install gh:username/repo
claude plugin install npm:package-name
claude plugin list
```

## See Also

- Slash commands: `references/slash-commands-dev.md`
- Agent skills: `references/agent-skills-creating.md`
