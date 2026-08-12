# MCP Integration

Model Context Protocol — connect Claude Code to external tools and services.

- **Configuration and Common Servers** — mcp.json format, filesystem/GitHub/PostgreSQL/Brave/Puppeteer servers, remote servers, env vars, testing, security: `references/mcp-configuration.md`
- **Custom Servers** — building Python/Node.js MCP servers, timeout config, best practices: `references/mcp-custom-servers.md`

## Quick Reference

`.claude/mcp.json`:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
```

Test with MCP Inspector:
```bash
npx @modelcontextprotocol/inspector
```

## See Also

- MCP specification: https://modelcontextprotocol.io
- Troubleshooting MCP: `references/troubleshooting-tools-hooks.md`
