---
name: claude-code
description: Claude Code CLI expert for installation, setup, slash commands, hooks, plugins, MCP servers, IDE integration, agent skills, CI/CD pipelines, enterprise SSO/sandboxing, configuration, and API usage.
---

# Claude Code Expert

Claude Code is Anthropic's agentic coding tool that lives in the terminal. It combines autonomous planning, execution, and validation with extensibility through skills, plugins, MCP servers, and hooks.

## Core Architecture

**Agent Skills**: Modular capabilities with instructions and resources that Claude uses automatically

**Slash Commands**: User-defined operations in `.claude/commands/` that expand to prompts

**Hooks**: Shell commands executing in response to events (pre/post-tool, user-prompt-submit)

**MCP Servers**: Model Context Protocol integrations connecting external tools and services

**Plugins**: Packaged collections of commands, skills, hooks, and MCP servers

## Quick Reference

### Getting Started
- **Installation, auth, first run**: `references/getting-started.md`

### Development Workflows
- **Slash Commands**: `references/slash-commands-dev.md`, `references/slash-commands-other.md`
- **Agent Skills**: `references/agent-skills-creating.md`, `references/agent-skills-examples.md`

### Integration & Extension
- **MCP**: `references/mcp-integration.md` → `references/mcp-configuration.md`, `references/mcp-custom-servers.md`
- **Hooks**: `references/hooks.md`
- **Plugins**: `references/plugins.md`

### Configuration & Settings
- **Core config**: `references/configuration-core.md`
- **Advanced config**: `references/configuration-advanced.md`

### Enterprise & Production
- **Enterprise IAM/Security**: `references/enterprise-iam-security.md`
- **Enterprise Deployment/Monitoring**: `references/enterprise-deployment.md`
- **IDE Integration**: `references/ide-vscode.md`, `references/ide-jetbrains.md`
- **CI/CD**: `references/cicd-github.md`, `references/cicd-gitlab.md`

### Advanced Usage
- **Extended Thinking, Caching**: `references/advanced-thinking-caching.md`
- **Checkpointing, Memory**: `references/advanced-checkpointing-memory.md`
- **Troubleshooting auth/install**: `references/troubleshooting-auth-install.md`
- **Troubleshooting tools/hooks**: `references/troubleshooting-tools-hooks.md`
- **API (Admin/Models/Skills)**: `references/api-admin.md`
- **API (Messages/Files/SDKs)**: `references/api-messages-files.md`
- **Best Practices**: `references/best-practices-organization.md`, `references/best-practices-performance.md`

## Common Workflows

### Feature Implementation
```bash
/cook implement user authentication with JWT
/plan implement payment integration with Stripe
```

### Bug Fixing
```bash
/fix:fast the login button is not working
/debug the API returns 500 errors intermittently
/fix:types
```

### Code Review & Testing
```bash
claude "review my latest commit"
/test
/fix:test the user service tests are failing
```

### Git Operations
```bash
/git:cm    # Stage and commit
/git:cp    # Stage, commit, and push
/git:pr feature-branch main
```

## Instructions for Claude

1. **Identify the topic** from the user's question
2. **Load relevant references** — use the Quick Reference above to find the right file
3. **Provide specific guidance** with examples when helpful

**Documentation links:**
- Main docs: https://docs.claude.com/claude-code
- GitHub: https://github.com/anthropics/claude-code
- Support: support.claude.com
