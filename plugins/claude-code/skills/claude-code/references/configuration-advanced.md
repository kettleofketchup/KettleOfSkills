# Configuration — Advanced Settings

Custom tools, rate limiting, caching, and troubleshooting settings.

## Advanced Configuration

### Custom Tools

Register custom tools in `.claude/settings.json`:

```json
{
  "tools": [
    {
      "name": "custom-tool",
      "description": "Custom tool",
      "command": "./scripts/custom-tool.sh",
      "parameters": { "arg1": "string" }
    }
  ]
}
```

### Rate Limiting

```json
{
  "rateLimits": {
    "requestsPerMinute": 100,
    "tokensPerMinute": 100000,
    "retryStrategy": "exponential"
  }
}
```

### Caching

Prompt caching configuration:

```json
{
  "caching": {
    "enabled": true,
    "ttl": 3600,
    "maxSize": "100MB"
  }
}
```

## Best Practices

### Project Settings
- Keep project-specific config in `.claude/settings.json`
- Commit to version control for team sharing
- Document custom settings with comments

### Global Settings
- Personal preferences only
- Use for API keys and auth
- Don't override project settings unnecessarily

### Security
- Never commit API keys — use environment variables
- Enable sandboxing in production
- Restrict network access where possible

### Performance
- Use appropriate model for task complexity
- Set reasonable token limits
- Enable caching for repeated context
- Configure rate limits to avoid throttling

## Troubleshooting Settings Issues

### Settings Not Applied
```bash
# Check settings hierarchy
claude config list --all

# Verify settings file syntax
cat .claude/settings.json | jq .

# Reset to defaults
claude config reset
```

### Environment Variables Not Recognized
```bash
# Verify export
echo $ANTHROPIC_API_KEY

# Check shell profile
grep ANTHROPIC ~/.bashrc

# Reload shell
source ~/.bashrc
```

## See Also

- Core settings: `references/configuration-core.md`
- Model selection: https://docs.claude.com/about-claude/models
- Enterprise security: `references/enterprise-iam-security.md`
