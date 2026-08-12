# Getting Started with Claude Code

Installation, authentication, and first run.

## What is Claude Code?

Anthropic's agentic coding tool that lives in the terminal. Features: autonomous planning/execution, terminal integration, VS Code/JetBrains IDE extensions, plugins, skills, slash commands, MCP servers, and enterprise SSO/sandboxing.

## Prerequisites

- **OS**: macOS, Linux, or Windows (WSL2)
- **Runtime**: Node.js 18+ or Python 3.10+
- **API Key**: from console.anthropic.com

## Installation

```bash
# npm (recommended)
npm install -g @anthropic-ai/claude-code

# pip
pip install claude-code

# Verify
claude --version
```

## Authentication

```bash
# Method 1: Interactive
claude login

# Method 2: Environment variable (add to ~/.bashrc or ~/.zshrc)
export ANTHROPIC_API_KEY=your_api_key_here

# Method 3: Config file (~/.claude/config.json)
# { "apiKey": "your_api_key_here" }

# Verify
claude "hello"
```

## Basic Usage

```bash
# Interactive session
claude

# One-shot
claude "implement user authentication"

# With file context
claude "explain this code" --file app.js
claude "refactor this function" --file utils.js --context "make it async"
```

## Common First Commands

```bash
claude "explain the project structure"
claude "run the test suite"
claude "fix all TypeScript errors"
claude "add input validation to the login form"
```

## Directory Structure

Claude Code creates `.claude/` in your project:
```
project/
├── .claude/
│   ├── settings.json   # Project settings
│   ├── commands/       # Custom slash commands
│   ├── skills/         # Custom skills
│   ├── hooks.json      # Hook configurations
│   └── mcp.json        # MCP server configurations
```

## Quick Troubleshooting

```bash
# Authentication issues
claude logout && claude login
echo $ANTHROPIC_API_KEY

# Permission errors
sudo chown -R $USER ~/.claude

# Installation issues
npm cache clean --force
npm uninstall -g @anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code

# WSL2 (Windows)
wsl --update && node --version  # should be 18+
```

## Next Steps

- **Slash Commands**: `/help` to see available, or `references/slash-commands-dev.md`
- **Agent Skills**: `references/agent-skills-creating.md`
- **MCP Servers**: `references/mcp-configuration.md`
- **Hooks**: `references/hooks.md`
- **Settings**: `references/configuration-core.md`

## Getting Help

- Documentation: https://docs.claude.com/claude-code
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Support: support.claude.com
- Community: discord.gg/anthropic
