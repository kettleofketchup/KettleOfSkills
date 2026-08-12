# Troubleshooting

Common issues and solutions for Claude Code.

- **Auth, Installation, and Network** — API key issues, npm/pip install errors, proxy, SSL, firewall: `references/troubleshooting-auth-install.md`
- **Tools, Hooks, MCP, and Performance** — MCP server problems, slow responses, rate limiting, tool failures, hook errors, debug mode: `references/troubleshooting-tools-hooks.md`

## Quick Diagnostics

```bash
# Collect system info
claude --version && node --version
claude config list --all
tail -n 100 ~/.claude/logs/session.log
env | grep -E 'CLAUDE|ANTHROPIC'
```

## Common Error Quick Fixes

| Error | Fix |
|-------|-----|
| "Invalid API key" | `claude logout && claude login` |
| "Rate limit exceeded" | `sleep 60`, check `claude usage show` |
| "Model not found" | `npm update -g @anthropic-ai/claude-code` |
| "Context length exceeded" | `claude config set maxTokens 100000` |
| MCP server not starting | Check `~/.claude/logs/mcp-*.log` |

## Debug Mode

```bash
export CLAUDE_DEBUG=1
claude --debug "task"
tail -f ~/.claude/logs/debug.log
```

## Getting Help

- Documentation: https://docs.claude.com/claude-code
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Support: support.claude.com
