# Hooks

Shell commands executing in response to Claude Code events.

## Hook Types

- **Pre-tool**: Execute before tool calls
- **Post-tool**: Execute after tool calls
- **User-prompt-submit**: Execute when user submits prompts

## Configuration

Configure in `.claude/hooks.json`:

```json
{
  "hooks": {
    "pre-tool": {
      "bash": "echo 'Running: $TOOL_ARGS'",
      "write": "./scripts/validate-write.sh"
    },
    "post-tool": {
      "write": "./scripts/format-code.sh",
      "edit": "prettier --write $FILE_PATH"
    },
    "user-prompt-submit": "./scripts/validate-request.sh"
  }
}
```

## Environment Variables

**All hooks:**
- `$TOOL_NAME`: Name of the tool being called
- `$TOOL_ARGS`: JSON string of tool arguments

**Post-tool only:** `$TOOL_RESULT`

**User-prompt-submit only:** `$USER_PROMPT`

## Hook Examples

### Pre-tool: Security Validation

```bash
#!/bin/bash
# .claude/scripts/validate-bash.sh
if echo "$TOOL_ARGS" | grep -E "rm -rf /|format|mkfs"; then
  echo "Dangerous command blocked"
  exit 1
fi
echo "Command validated"
```

```json
{ "hooks": { "pre-tool": { "bash": "./.claude/scripts/validate-bash.sh" } } }
```

### Post-tool: Auto-format

```bash
#!/bin/bash
# .claude/scripts/format-code.sh
FILE_PATH=$(echo "$TOOL_ARGS" | jq -r '.file_path')
case "$FILE_PATH" in
  *.js|*.ts|*.jsx|*.tsx) prettier --write "$FILE_PATH" ;;
  *.py) black "$FILE_PATH" ;;
  *.go) gofmt -w "$FILE_PATH" ;;
esac
```

```json
{ "hooks": { "post-tool": {
  "write": "./.claude/scripts/format-code.sh",
  "edit": "./.claude/scripts/format-code.sh"
} } }
```

### User-prompt-submit: Cost Tracking

```bash
#!/bin/bash
echo "$(date): $USER_PROMPT" >> .claude/usage.log
```

```json
{ "hooks": { "user-prompt-submit": "./.claude/scripts/track-usage.sh" } }
```

## Behavior

- Pre-tool hook failure **blocks** tool execution
- Post-tool hook failure is logged but does not block
- Strict mode can be configured to block on all failures

## Best Practices

- Keep hooks fast (under 100ms)
- Handle errors gracefully
- Validate all inputs
- Log important actions
- Test hooks thoroughly

## Security

- Validate all inputs in hook scripts
- Use whitelists for allowed commands
- Implement timeouts
- Log all executions
- Review hook scripts regularly

## Troubleshooting

```bash
# Verify hooks.json syntax
cat .claude/hooks.json | jq .

# Check script permissions
chmod +x .claude/scripts/hook.sh

# Test script manually
.claude/scripts/hook.sh

# Check logs
cat ~/.claude/logs/hooks.log
```

## See Also

- Plugins: `references/plugins.md`
- Configuration: `references/configuration-core.md`
