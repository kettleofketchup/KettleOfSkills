# Advanced Features — Extended Thinking and Prompt Caching

## Extended Thinking

Deep reasoning for complex problems.

### Enable

```bash
claude config set thinking.enabled true
claude config set thinking.budget 15000
claude --thinking "architect microservices system"
```

`.claude/settings.json`:
```json
{
  "thinking": {
    "enabled": true,
    "budget": 10000,
    "mode": "auto",
    "budgetPerRequest": 5000,
    "adaptive": true
  }
}
```

### Modes

- **auto**: Claude decides when to use extended thinking
- **manual**: User explicitly requests thinking
- **disabled**: No extended thinking

### Best Use Cases

Architecture design, complex algorithm development, system refactoring, performance optimization, security analysis, bug investigation.

### Example

```bash
claude --thinking "Design a distributed caching system with:
- High availability
- Consistency guarantees
- Horizontal scalability
- Fault tolerance"
```

## Prompt Caching

Reduce costs by caching repeated context.

### Enable Caching

**API usage:**
```typescript
const response = await client.messages.create({
  model: 'claude-sonnet-4-5-20250929',
  system: [{
    type: 'text',
    text: 'You are a coding assistant...',
    cache_control: { type: 'ephemeral' }
  }],
  messages: [...]
});
```

**CLI configuration:**
```json
{
  "caching": { "enabled": true, "ttl": 300, "maxSize": "100MB" }
}
```

### Cache Strategy

What to cache: large codebases, documentation, API specifications, system prompts, project context.

What NOT to cache: user queries, dynamic content, temporary data, session-specific info.

### Cache Control

```typescript
// Cache large context
{ type: 'text', text: largeCodebase, cache_control: { type: 'ephemeral' } }

// Dynamic query - not cached
{ type: 'text', text: newUserQuery }
```

### Cost Savings

- Cache TTL: 5 minutes
- Cached tokens: ~90% discount

Example:
```
Without caching:  2 requests × 10,000 tokens @ $3/M = $0.06
With caching:     Request 1 full + Request 2 (2k new + 8k cached @ $0.30/M)
                  Total: $0.0324 (46% savings)
```

## Context Windows

Model context limits: 200k tokens (Sonnet, Opus, Haiku)

Context management:
```json
{
  "context": {
    "maxTokens": 200000,
    "autoTruncate": true,
    "prioritize": ["recent", "relevant"],
    "summarizeLong": true
  }
}
```

Strategies: auto-summarize old context, prioritize recent/relevant files, chunk large codebases, process in parallel.

## See Also

- Checkpointing and memory: `references/advanced-checkpointing-memory.md`
- Pricing: https://docs.claude.com/about-claude/pricing
- Configuration: `references/configuration-core.md`
