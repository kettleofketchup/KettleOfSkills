# Advanced Features

Extended capabilities for power users.

- **Extended Thinking and Prompt Caching** — thinking modes, budget control, cache strategy, cost savings: `references/advanced-thinking-caching.md`
- **Checkpointing and Memory Management** — checkpoint commands, restore strategies, memory locations, memory operations: `references/advanced-checkpointing-memory.md`

## Quick Reference

**Extended thinking:**
```bash
claude --thinking "architect microservices system"
claude config set thinking.enabled true
```

**Prompt caching** reduces repeated context costs by ~90% on cached tokens (5-min TTL).

**Checkpointing:**
```bash
claude checkpoint create "before risky change"
claude checkpoint list
claude checkpoint restore checkpoint-123
```

**Memory:**
```bash
claude config set memory.location project
claude memory list && claude memory clear
```

## See Also

- Configuration: `references/configuration-core.md`
- Pricing: https://docs.claude.com/about-claude/pricing
