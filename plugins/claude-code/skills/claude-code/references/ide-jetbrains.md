# IDE Integration — JetBrains IDEs

Use Claude Code with IntelliJ IDEA, PyCharm, WebStorm, PhpStorm, GoLand, RubyMine, CLion, Rider.

## Installation

1. Open Settings (Ctrl+Alt+S)
2. Go to Plugins
3. Search "Claude Code"
4. Click Install
5. Restart IDE
6. Authenticate with API key

## Features

- **AI Assistant Panel**: Dedicated Claude panel with context-aware suggestions
- **Inline Suggestions**: As-you-type completions, contextual generation, refactoring hints
- **Code Reviews**: Automated security detection, best practice recommendations
- **Refactoring Support**: Smart rename, extract method, inline variable, move class

## Configuration

**Settings → Tools → Claude Code:**
```
API Key: [Your API Key]
Model: claude-sonnet-4-5-20250929
Max Tokens: 8192
Auto-complete: Enabled
Code Review: Enabled
```

**.idea/claude.xml:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ClaudeSettings">
    <option name="model" value="claude-sonnet-4-5-20250929" />
    <option name="skillsPath" value=".claude/skills" />
    <option name="autoReview" value="true" />
  </component>
</project>
```

## Keyboard Shortcuts

Default: `Ctrl+Shift+A` (Ask Claude), `Alt+Enter` (Quick fixes), `Ctrl+Alt+L` (Format suggestions)

Custom (Settings → Keymap → Claude Code):
```
Ask Claude: Ctrl+Shift+C
Refactor with Claude: Ctrl+Alt+R
Generate Tests: Ctrl+Alt+T
Code Review: Ctrl+Alt+V
```

## IDE Feature Integrations

**Version Control:** review commit diffs, generate commit messages, analyze merge conflicts.

**Debugger:** explain stack traces, suggest fixes, analyze variable states.

**Database Tools:** generate SQL queries, optimize schema, write migration scripts.

## Common Workflows

| Task | Steps |
|------|-------|
| Generate Boilerplate | Right-click → Generate → Claude Code |
| Review Changes | Version Control panel → right-click changeset → Review with Claude |
| Debug Error | Hit breakpoint → right-click in debugger → "Ask Claude about this" |

## CLI Integration

```bash
# In JetBrains terminal
claude "add error handling to current file"
```

## Troubleshooting

**Plugin Not Responding:**
```
File → Invalidate Caches / Restart
Settings → Plugins → Claude Code → Reinstall
```

**Performance Issues:**
- Increase IDE memory: `Help → Edit Custom VM Options`
- Disable unused features
- Clear caches
- Update plugin version

## See Also

- VS Code: `references/ide-vscode.md`
- Plugin: https://plugins.jetbrains.com/plugin/claude-code
- Configuration: `references/configuration-core.md`
