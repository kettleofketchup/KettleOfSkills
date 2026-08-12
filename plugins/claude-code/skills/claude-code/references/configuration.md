# Configuration and Settings

Configure Claude Code behavior with settings files, models, and environment variables.

- **Core settings** — hierarchy, settings files, model selection, environment variables, CLI flags, output styles: `references/configuration-core.md`
- **Advanced settings** — custom tools, rate limiting, caching, troubleshooting: `references/configuration-advanced.md`

## Quick Reference

Settings hierarchy (highest to lowest priority):
1. Command-line flags
2. Environment variables
3. `.claude/settings.json` (project)
4. `~/.claude/settings.json` (global)

```bash
claude config list           # View all settings
claude config set model opus # Set global setting
claude config reset          # Reset to defaults
```

Models: `sonnet` (default), `opus` (complex tasks), `haiku` (fast/cheap), `opusplan` (deep planning).
