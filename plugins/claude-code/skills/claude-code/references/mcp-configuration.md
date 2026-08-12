# MCP Integration — Configuration and Common Servers

Model Context Protocol integration for connecting Claude Code to external tools.

## What is MCP?

Enables Claude Code to connect to external tools, access resources (files, databases, APIs), and use custom tools.

## Configuration

MCP servers are configured in `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"],
      "env": { "VAR_NAME": "value" }
    }
  }
}
```

## Common MCP Servers

### Filesystem

```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"]
  }
}
```

Capabilities: read/write files, list directories, file search, path restrictions.

### GitHub

```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
  }
}
```

Capabilities: repository access, issues/PRs, code search, workflow management.

### PostgreSQL

```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres"],
    "env": { "DATABASE_URL": "${DATABASE_URL}" }
  }
}
```

### Brave Search

```json
{
  "brave-search": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-brave-search"],
    "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
  }
}
```

### Puppeteer (Browser Automation)

```json
{
  "puppeteer": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
  }
}
```

## Remote MCP Servers

```json
{
  "remote-service": {
    "url": "https://api.example.com/mcp",
    "headers": { "Authorization": "Bearer ${API_TOKEN}" },
    "proxy": "http://proxy.company.com:8080"
  }
}
```

## Environment Variables

Store secrets in `.claude/.env`:
```bash
GITHUB_TOKEN=ghp_xxxxx
DATABASE_URL=postgresql://user:pass@localhost/db
BRAVE_API_KEY=BSAxxxxx
```

Reference in `mcp.json` with `${VAR_NAME}` syntax.

## Testing MCP Servers

```bash
# Use MCP Inspector
npx @modelcontextprotocol/inspector

# Manual test
npx -y @modelcontextprotocol/server-filesystem /tmp
```

## Security

- Restrict filesystem to specific directories
- Use environment variables for credentials
- Whitelist allowed domains, use HTTPS only
- Validate remote server certificates

## Troubleshooting

```bash
# Check server command
npx -y @modelcontextprotocol/server-filesystem /tmp

# Verify env vars
echo $GITHUB_TOKEN

# Check logs
cat ~/.claude/logs/mcp-*.log

# Test network
curl https://api.example.com/mcp
```

## See Also

- Custom MCP servers: `references/mcp-custom-servers.md`
- MCP specification: https://modelcontextprotocol.io
