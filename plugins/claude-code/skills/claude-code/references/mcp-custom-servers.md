# MCP Integration — Custom Servers

Build and configure custom Model Context Protocol servers.

## Creating Custom MCP Servers

### Python Server

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("my-server")

@server.tool()
async def my_tool(arg: str) -> str:
    """Tool description"""
    return f"Result: {arg}"

if __name__ == "__main__":
    stdio_server(server)
```

Configuration:
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["path/to/server.py"]
    }
  }
}
```

### Node.js Server

```javascript
import { Server } from "@modelcontextprotocol/server-node";

const server = new Server("my-server");

server.tool({
  name: "my-tool",
  description: "Tool description",
  parameters: { arg: "string" }
}, async ({ arg }) => {
  return `Result: ${arg}`;
});

server.listen();
```

## Connection Timeout Configuration

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

## Best Practices

### Configuration Management
- Use environment variables for secrets
- Document server purposes
- Version control `mcp.json` (without secrets)
- Test configurations thoroughly

### Performance
- Use local servers when possible
- Implement caching within servers
- Set appropriate timeouts
- Monitor resource usage

### Maintenance
- Update servers regularly
- Monitor server health
- Review access logs
- Clean up unused servers

### Security
- Validate all inputs
- Implement request signing for remote servers
- Monitor for anomalies
- Use least-privilege access

## Permission Errors

```bash
# Check file permissions
ls -la /path/to/mcp/server
chmod +x /path/to/mcp/server

# Check directory access
ls -ld /path/to/allowed/directory
```

## Tool Not Found

- Verify server is running
- Check server configuration syntax
- Inspect server capabilities with MCP Inspector
- Review tool registration code

## See Also

- MCP configuration and common servers: `references/mcp-configuration.md`
- MCP specification: https://modelcontextprotocol.io
- Security best practices: `references/best-practices-organization.md`
