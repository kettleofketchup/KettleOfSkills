# MCP Integration Strategy

## Execution Priority

1. **Gemini CLI** (Primary): Fast, automatic, intelligent tool selection
   - Check: `command -v gemini`
   - Execute: `gemini -y -m gemini-2.5-flash -p "<task>"`
   - Best for: All tasks when available

2. **Direct CLI Scripts** (Secondary): Manual tool specification
   - Use when: Need specific tool/server control
   - Execute: `npx tsx scripts/cli.ts call-tool <server> <tool> <args>`

3. **mcp-manager Subagent** (Fallback): Context-efficient delegation
   - Use when: Gemini unavailable or failed
   - Keeps main context clean

## Integration with Agents

The `mcp-manager` agent uses this skill to:
- Check Gemini CLI availability first
- Execute via `gemini` command if available
- Fallback to direct script execution
- Discover MCP capabilities without loading into main context
- Report results back to main agent

This keeps main agent context clean and enables efficient MCP integration.

## Multi-Server Orchestration

Coordinate tools across multiple servers. Each tool knows its source server for proper routing.

Configure multiple servers in `.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "$BRAVE_API_KEY" }
    }
  }
}
```

`list-tools` output includes server name per tool for correct routing in `call-tool`.
