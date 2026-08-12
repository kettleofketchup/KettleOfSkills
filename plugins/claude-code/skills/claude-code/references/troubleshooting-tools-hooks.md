# Troubleshooting — Tools, Hooks, MCP, and Performance

Common issues with tool execution, hooks, MCP servers, and performance.

## MCP Server Problems

### Server Not Starting

```bash
# Test MCP server command manually
npx -y @modelcontextprotocol/server-filesystem /tmp

# Check server logs
cat ~/.claude/logs/mcp-*.log

# Verify environment variables
echo $GITHUB_TOKEN

# Test with MCP Inspector
npx @modelcontextprotocol/inspector
```

### Connection Timeouts

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-example"],
      "timeout": 30000,
      "retries": 3
    }
  }
}
```

## Performance Issues

### Slow Responses

```bash
# Check network latency
ping api.anthropic.com

# Use faster model
claude --model haiku "simple task"
```

```json
{
  "maxTokens": 4096,
  "caching": { "enabled": true },
  "context": { "autoTruncate": true }
}
```

### High Memory Usage

```bash
rm -rf ~/.claude/cache/*
claude config set maxTokens 8192
claude config set memory.enabled false
claude session list && claude session close session-123
```

### Rate Limiting

```bash
claude usage show
sleep 60 && claude "retry task"
```

## Tool Execution Errors

### Bash Command Failures

```json
{
  "sandboxing": {
    "enabled": true,
    "allowedPaths": ["/workspace", "/tmp"]
  }
}
```

```bash
chmod +x script.sh
echo $PATH && which command-name
```

### File Access Denied

```bash
ls -la file.txt
sudo chown $USER file.txt
chmod 644 file.txt
```

### Write Tool Failures

```bash
df -h
mkdir -p /path/to/directory
touch /path/to/directory/test.txt
```

## Hook Errors

### Hooks Not Running

```bash
cat .claude/hooks.json | jq .        # Check syntax
chmod +x .claude/scripts/hook.sh    # Check permissions
.claude/scripts/hook.sh             # Test manually
cat ~/.claude/logs/hooks.log        # Check logs
```

### Hook Script Debugging

Add `set -e; set -u; set -x` to hook scripts for verbose output. Check logs at `~/.claude/logs/hooks.log`.

## Debug Mode

```bash
export CLAUDE_DEBUG=1
claude --debug "task"
tail -f ~/.claude/logs/debug.log
claude --verbose "task"
```

## Common Error Messages

| Error | Fix |
|-------|-----|
| "Model not found" | Use correct model ID; run `npm update -g @anthropic-ai/claude-code` |
| "Rate limit exceeded" | `sleep 60`, check `claude usage show` |
| "Context length exceeded" | `claude config set maxTokens 100000`, summarize content |
| "Timeout waiting for response" | `claude config set timeout 300`, retry with smaller request |

## See Also

- Auth and install issues: `references/troubleshooting-auth-install.md`
- MCP configuration: `references/mcp-configuration.md`
- Configuration: `references/configuration-core.md`
