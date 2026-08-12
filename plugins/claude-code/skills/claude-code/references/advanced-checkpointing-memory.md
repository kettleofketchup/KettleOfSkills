# Advanced Features — Checkpointing and Memory Management

## Checkpointing

Automatically track and rewind changes.

### Enable

```bash
claude config set checkpointing.enabled true
```

```json
{
  "checkpointing": {
    "enabled": true,
    "autoSave": true,
    "interval": 300,
    "maxCheckpoints": 50
  }
}
```

### Commands

```bash
# List checkpoints
claude checkpoint list

# View checkpoint details
claude checkpoint show checkpoint-123

# Restore to checkpoint
claude checkpoint restore checkpoint-123

# Restore to time
claude checkpoint restore --time "2025-11-06T10:00:00Z"

# Restore specific files
claude checkpoint restore checkpoint-123 --files src/main.js

# Create manual checkpoint
claude checkpoint create "before refactoring auth module"
```

### Strategies

**Auto-save:** before major changes, after successful tests, every N minutes, before destructive operations.

**Manual:** before risky refactors, at working states, before experiments, after milestones.

### Example Workflow

```bash
# Create checkpoint before risky change
claude checkpoint create "before performance optimization"

# Make changes
claude "optimize database queries for 10x performance"

# If something breaks
claude checkpoint restore "before performance optimization"
```

## Memory Management

Control how Claude remembers context across sessions.

### Configure

```bash
claude config set memory.location project
claude config set memory.enabled true
```

```json
{
  "memory": {
    "enabled": true,
    "location": "project",
    "ttl": 86400,
    "maxSize": "10MB",
    "autoSummarize": true
  }
}
```

### Commands

```bash
claude memory list                   # View stored memories
claude memory show memory-123        # View specific memory
claude memory clear                  # Clear all memories
claude memory clear --older-than 7d  # Clear old memories
claude memory clear --project        # Clear project memories
```

### What Gets Remembered

**Automatically:** project structure, coding patterns, preferences, common commands, file locations.

**Explicitly stored:** important context, design decisions, architecture notes, team conventions.

### Memory Locations

| Location | Use case |
|----------|----------|
| `global` | Personal preferences, cross-project learnings |
| `project` | Project-specific context (shared via `.claude/memory/`) |
| `none` | Disable memory |

### When to Disable Memory

- Working with sensitive data
- One-off tasks or experiments
- Testing / troubleshooting

### Example

```bash
# Store project architecture
claude "Remember: This project uses Clean Architecture with:
- Domain layer (core business logic)
- Application layer (use cases)
- Infrastructure layer (external dependencies)"

# Future sessions recall this context automatically
```

## See Also

- Extended thinking and caching: `references/advanced-thinking-caching.md`
- Configuration: `references/configuration-core.md`
