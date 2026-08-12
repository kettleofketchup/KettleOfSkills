# Troubleshooting — Auth, Installation, and Network

Common issues with authentication, installation, and connectivity.

## Authentication Issues

### API Key Not Recognized

Symptoms: "Invalid API key", 401 Unauthorized

```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Re-login
claude logout && claude login

# Check format (should start with sk-ant-)
echo $ANTHROPIC_API_KEY | grep "^sk-ant-"

# Test API key directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-5-20250929","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

### Environment Variable Issues

```bash
# Add to shell profile
echo 'export ANTHROPIC_API_KEY=sk-ant-xxxxx' >> ~/.bashrc
source ~/.bashrc

# Or use .env file
echo 'ANTHROPIC_API_KEY=sk-ant-xxxxx' > .claude/.env

# Verify
claude config get apiKey
```

## Installation Problems

### npm Installation Failures

```bash
npm cache clean --force
npm uninstall -g @anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code

# Verify
which claude && claude --version
```

### Permission Errors

```bash
sudo chown -R $USER ~/.claude
chmod -R 755 ~/.claude

# Or install without sudo (nvm)
nvm install 18 && npm install -g @anthropic-ai/claude-code
```

### Python Installation Issues

```bash
pip install --upgrade pip
python -m venv claude-env && source claude-env/bin/activate
pip install claude-code
```

### WSL2 Issues (Windows)

```bash
wsl --update
node --version  # Should be 18+
```

## Connection & Network Issues

### Proxy Configuration

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1

# Configure in settings
claude config set proxy http://proxy.company.com:8080

# Test
curl -x $HTTP_PROXY https://api.anthropic.com
```

### SSL/TLS Errors

```bash
# Trust custom CA
export NODE_EXTRA_CA_CERTS=/path/to/ca-bundle.crt

# Update CA certificates
sudo update-ca-certificates  # Debian/Ubuntu
sudo update-ca-trust         # RHEL/CentOS
```

### Firewall Issues

```bash
ping api.anthropic.com
telnet api.anthropic.com 443
curl -v https://api.anthropic.com
```

## Collect Diagnostic Info

```bash
claude --version && node --version && npm --version
claude config list --all
tail -n 100 ~/.claude/logs/session.log
env | grep -E 'CLAUDE|ANTHROPIC'
```

## Getting Help

1. Check existing issues: https://github.com/anthropics/claude-code/issues
2. Gather diagnostic info
3. Create minimal reproduction
4. Submit with: Claude Code version, OS, error messages, steps to reproduce

Support: support.claude.com | Discord: discord.gg/anthropic

## See Also

- Tool and hook errors: `references/troubleshooting-tools-hooks.md`
- Getting started: `references/getting-started.md`
- Configuration: `references/configuration-core.md`
