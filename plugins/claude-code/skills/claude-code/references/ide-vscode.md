# IDE Integration — Visual Studio Code

Use Claude Code with VS Code.

## Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Claude Code"
4. Click Install
5. Authenticate with API key

## Features

- **Inline Chat** (Ctrl+I / Cmd+I): Ask questions, get contextual suggestions, apply changes
- **Code Actions**: Right-click → "Ask Claude" for refactoring, bug fixes
- **Diff View**: Review proposed changes before applying
- **Terminal Integration**: Built-in Claude terminal with real-time output

## Configuration

**.vscode/settings.json:**
```json
{
  "claude.apiKey": "${ANTHROPIC_API_KEY}",
  "claude.model": "claude-sonnet-4-5-20250929",
  "claude.maxTokens": 8192,
  "claude.autoSave": true,
  "claude.inlineChat.enabled": true,
  "claude.terminalIntegration": true
}
```

**.vscode/keybindings.json (custom shortcuts):**
```json
[
  { "key": "ctrl+alt+c", "command": "claude.openChat" },
  { "key": "ctrl+alt+r", "command": "claude.refactor" }
]
```

Default shortcuts: `Ctrl+I` inline chat, `Ctrl+Shift+C` open panel, `Ctrl+Shift+Enter` submit, `Escape` close.

## Workspace Integration

**.vscode/claude.json:**
```json
{
  "skills": [".claude/skills/project-skill"],
  "commands": [".claude/commands"],
  "mcpServers": ".claude/mcp.json",
  "outputStyle": "technical-writer"
}
```

## Common Workflows

| Task | Steps |
|------|-------|
| Explain Code | Select code → Right-click → "Ask Claude" → "Explain this code" |
| Refactor | Select function → Ctrl+I → "Refactor for better performance" |
| Fix Bug | Click on error → Ctrl+I → "Fix this error" |
| Generate Tests | Select function → Right-click → "Ask Claude" → "Write tests" |

## Best Practices

- Use workspace settings for team consistency
- Share `.vscode/claude.json` in version control
- Limit inline suggestions in large files
- Use specific prompts for better results

## Troubleshooting

```bash
# Check extension status
code --list-extensions | grep claude

# Reinstall
code --uninstall-extension anthropic.claude-code
code --install-extension anthropic.claude-code
```

Authentication issues: verify API key in settings, re-authenticate in extension, review proxy settings.

## See Also

- JetBrains IDE: `references/ide-jetbrains.md`
- Extension: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
- Configuration: `references/configuration-core.md`
