# Best Practices: Performance, Cost & Workflows

## Model Selection

**Haiku** - Fast, cost-effective:
```bash
claude --model haiku "fix typo in README"
claude --model haiku "format code"
```

**Sonnet** - Balanced (default):
```bash
claude "implement user authentication"
claude "review this PR"
```

**Opus** - Complex tasks:
```bash
claude --model opus "architect microservices system"
claude --model opus "optimize algorithm performance"
```

## Prompt Caching

```typescript
const response = await client.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  system: [{
    type: 'text',
    text: largeCodebase,
    cache_control: { type: 'ephemeral' }
  }],
  messages: [...]
});
```

**Benefits:** 90% cost reduction on cached tokens, faster responses

## Token Management

```bash
claude usage show
claude config set maxTokens 8192
claude analytics cost --group-by project
```

## Cost Management

### Budget Limits

```bash
#!/bin/bash
MONTHLY_BUDGET=1000
CURRENT_SPEND=$(claude analytics cost --format json | jq '.total')

if (( $(echo "$CURRENT_SPEND > $MONTHLY_BUDGET" | bc -l) )); then
  echo "Monthly budget exceeded: \$$CURRENT_SPEND / \$$MONTHLY_BUDGET"
  exit 1
fi
```

### Cost Optimization

- Use Haiku for simple tasks (formatting, typos)
- Enable caching for iterative development
- Batch operations instead of multiple requests
- Track per-project costs with `--project` flag

### Usage Monitoring

```bash
claude analytics usage --start $(date -d '1 day ago' +%Y-%m-%d)
claude analytics cost --group-by user
claude analytics export --format csv > usage.csv
```

## Team Collaboration

### Standardize Commands

```markdown
# .claude/commands/test.md
Run test suite with coverage report.
Options:
- {{suite}}: Specific test suite (optional)
```

### Consistent Settings

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "maxTokens": 8192,
  "thinking": { "enabled": true, "budget": 10000 }
}
```

### Project Memory

```json
{
  "memory": { "enabled": true, "location": "project" }
}
```

Benefits: shared project knowledge, consistent behavior, reduced onboarding

## Development Workflows

### Feature Development

```bash
claude /plan "implement user authentication"
claude /cook "implement user authentication"
claude /test
claude "review authentication implementation"
claude /git:cm
```

### Bug Fixing

```bash
claude /debug "login button not working"
claude /fix:fast "fix login button issue"
claude /test
claude /git:cm
```

### Code Review

```bash
claude "review PR #123"
claude "review for security vulnerabilities"
claude "check test coverage"
```
