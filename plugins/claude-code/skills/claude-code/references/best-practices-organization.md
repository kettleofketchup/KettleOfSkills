# Best Practices: Project Organization & Security

## Project Organization

### Directory Structure

```
project/
├── .claude/
│   ├── settings.json       # Project settings
│   ├── commands/           # Custom slash commands
│   ├── skills/            # Project-specific skills
│   ├── hooks.json         # Hooks configuration
│   ├── mcp.json           # MCP servers (no secrets!)
│   └── .env.example       # Environment template
├── .gitignore
└── README.md
```

### Team Sharing

**What to commit:**
- `.claude/settings.json`, `.claude/commands/`, `.claude/skills/`
- `.claude/hooks.json`, `.claude/mcp.json` (without secrets)
- `.claude/.env.example`

**What NOT to commit:**
- `.claude/.env` (contains secrets)
- `.claude/memory/`, `.claude/cache/`, `.claude/logs/`
- API keys or tokens

**.gitignore:**
```
.claude/.env
.claude/memory/
.claude/cache/
.claude/logs/
```

## Security

### API Key Management

```bash
# Use environment variables
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Or .env file (gitignored)
echo 'ANTHROPIC_API_KEY=sk-ant-xxxxx' > .claude/.env
```

- Rotate keys regularly
- Use workspace keys for team projects

### Sandboxing

```json
{
  "sandboxing": {
    "enabled": true,
    "allowedPaths": ["/workspace"],
    "networkAccess": "restricted",
    "allowedDomains": ["api.company.com"]
  }
}
```

### Hook Security

```bash
# Review hooks before execution
cat .claude/hooks.json | jq .

# Validate inputs in hooks
if [[ ! "$TOOL_ARGS" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "Invalid input"
  exit 1
fi
```

### Plugin Security

```bash
# Audit plugins before installation
gh repo view username/plugin
cat plugin.json

# Install from trusted sources only
claude plugin install gh:anthropics/official-plugin
```
