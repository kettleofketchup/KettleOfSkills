# IDE Integration

Use Claude Code with Visual Studio Code and JetBrains IDEs.

- **Visual Studio Code** — installation, inline chat, code actions, diff view, configuration, shortcuts, workflows: `references/ide-vscode.md`
- **JetBrains IDEs** — IntelliJ, PyCharm, WebStorm, and more; AI panel, inline suggestions, code reviews, configuration: `references/ide-jetbrains.md`

## Quick Reference

**VS Code:**
- Install: Extensions → Search "Claude Code"
- Inline chat: `Ctrl+I` (Cmd+I on Mac)
- Code actions: Right-click → "Ask Claude"

**JetBrains:**
- Install: Settings → Plugins → Search "Claude Code"
- Ask Claude: `Ctrl+Shift+A`
- Quick fixes: `Alt+Enter`

Both IDEs support CLI usage from the integrated terminal:
```bash
claude "explain this project structure"
```

## See Also

- VS Code extension: https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code
- JetBrains plugin: https://plugins.jetbrains.com/plugin/claude-code
- Configuration: `references/configuration-core.md`
