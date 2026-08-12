# Configuration — Core Settings

Settings hierarchy, key settings, model selection, and environment variables.

## Settings Hierarchy

1. Command-line flags (highest priority)
2. Environment variables
3. Project settings (`.claude/settings.json`)
4. Global settings (`~/.claude/settings.json`)

## Settings File Format

`~/.claude/settings.json`:
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "maxTokens": 8192,
  "temperature": 1.0,
  "thinking": { "enabled": true, "budget": 10000 },
  "outputStyle": "default",
  "memory": { "enabled": true, "location": "global" }
}
```

`.claude/settings.json` (project-level):
```json
{
  "model": "claude-sonnet-4-5-20250929",
  "maxTokens": 4096,
  "sandboxing": { "enabled": true, "allowedPaths": ["/workspace"] },
  "memory": { "enabled": true, "location": "project" }
}
```

## Key Settings

**model**: `claude-sonnet-4-5-20250929` (default) | `claude-opus-4-20250514` | `claude-haiku-4-20250408`
Aliases: `sonnet`, `opus`, `haiku`, `opusplan` (Opus + extended thinking)

**maxTokens**: 1–200000 (default 8192)

**temperature**: 0.0–1.0 (default 1.0; lower = more focused)

**thinking**: `{ "enabled": true, "budget": 10000, "mode": "auto" }`
Modes: `auto` | `manual` | `disabled`

**sandboxing**:
```json
{ "enabled": true, "allowedPaths": ["/workspace"],
  "networkAccess": "restricted", "allowedDomains": ["api.example.com"] }
```

**memory**: `{ "enabled": true, "location": "project", "ttl": 86400 }`
Locations: `global` | `project` | `none`

**logging**: `{ "level": "info", "file": ".claude/logs/session.log" }`

## Model Selection Guide

| Model | Use case |
|-------|----------|
| Sonnet | Default, balanced performance/cost |
| Opus | Complex reasoning, architecture, design |
| Haiku | Fast, cost-effective, simple tasks |
| opusplan | Deep planning, extended thinking |

## Environment Variables

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
export ANTHROPIC_BASE_URL=https://api.anthropic.com
export HTTP_PROXY=http://proxy.company.com:8080
export NODE_EXTRA_CA_CERTS=/path/to/ca-bundle.crt
export CLAUDE_DEBUG=1
export CLAUDE_LOG_LEVEL=debug
```

## Command-Line Flags

```bash
claude --model opus
claude --max-tokens 16384
claude --temperature 0.8
claude --debug
claude --output-style technical-writer
claude --no-memory
```

Configuration commands:
```bash
claude config list            # View current settings
claude config set model opus  # Set global setting
claude config get model       # Get specific setting
claude config reset           # Reset to defaults
```

## Output Styles

Built-in: `default`, `technical-writer`, `code-reviewer`, `minimal`

Custom style — create `~/.claude/output-styles/my-style.md`:
```markdown
You are a senior software architect focused on scalability.
Guidelines: prioritize performance, consider distributed patterns...
```

Use: `claude --output-style my-style` or `"outputStyle": "my-style"` in settings.

## See Also

- Advanced config (custom tools, caching, HA): `references/configuration-advanced.md`
- Enterprise settings: `references/enterprise-iam-security.md`
- Troubleshooting settings: `references/troubleshooting-auth-install.md`
