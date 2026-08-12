# Plugins

Packaged collections of commands, skills, hooks, and MCP servers.

## Plugin Structure

```
my-plugin/
├── plugin.json          # Plugin metadata
├── commands/            # Slash commands
│   ├── my-command.md
│   └── another-command.md
├── skills/              # Agent skills
│   └── my-skill/
│       ├── skill.md
│       └── skill.json
├── hooks/               # Hook scripts
│   ├── hooks.json
│   └── scripts/
├── mcp/                 # MCP server configurations
│   └── mcp.json
└── README.md
```

## plugin.json

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": "Your Name",
  "homepage": "https://github.com/user/plugin",
  "license": "MIT",
  "commands": ["commands/*.md"],
  "skills": ["skills/*/"],
  "hooks": "hooks/hooks.json",
  "mcpServers": "mcp/mcp.json",
  "dependencies": { "node": ">=18.0.0" }
}
```

## Installing Plugins

```bash
# From GitHub
claude plugin install gh:username/repo
claude plugin install gh:username/repo@v1.0.0

# From npm
claude plugin install npm:package-name

# From local path
claude plugin install ./path/to/plugin

# From URL
claude plugin install https://example.com/plugin.zip
```

## Managing Plugins

```bash
claude plugin list
claude plugin update my-plugin
claude plugin update --all
claude plugin uninstall my-plugin
claude plugin disable my-plugin
claude plugin enable my-plugin
```

## Creating Plugins

Initialize:
```bash
mkdir my-plugin && cd my-plugin
```

Add slash command:
```bash
mkdir -p commands
cat > commands/my-command.md <<EOF
# My Command
Do something awesome with {{input}}.
EOF
```

Package:
```bash
tar -czf my-plugin.tar.gz .
# or: zip -r my-plugin.zip .
```

Publish to GitHub:
```bash
git init && git add . && git commit -m "Initial commit"
git tag v1.0.0 && git push origin main --tags
```

## Private Marketplace

Configure organization marketplace:
```json
{
  "marketplaces": [{
    "name": "company-internal",
    "url": "https://plugins.company.com/catalog.json",
    "auth": { "type": "bearer", "token": "${COMPANY_PLUGIN_TOKEN}" }
  }]
}
```

Install from marketplace:
```bash
claude plugin install company-internal:company-plugin
```

## Security

- Verify plugin sources before installation
- Review code before installing
- Use signed packages when available
- Monitor plugin behavior and resource usage
- Keep plugins updated
- Regular security audits

## Troubleshooting

### Installation Failures
- Verify internet connectivity
- Check plugin URL or path
- Clear cache: `claude plugin cache clear`

### Plugin Conflicts
- Check for conflicting commands
- Disable conflicting plugins
- Update plugins to compatible versions

## See Also

- Hooks: `references/hooks.md`
- Slash commands: `references/slash-commands-dev.md`
- Agent skills: `references/agent-skills-creating.md`
