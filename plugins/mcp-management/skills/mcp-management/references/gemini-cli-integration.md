# Gemini CLI Integration Guide

## Overview

Gemini CLI provides automatic MCP tool discovery and execution via natural language prompts. This is the recommended primary method for executing MCP tools.

## Installation

```bash
npm install -g gemini-cli
```

Verify installation:
```bash
gemini --version
```

## Configuration

### Symlink Setup

Gemini CLI reads MCP servers from `.gemini/settings.json`. Create a symlink to `.claude/.mcp.json`:

```bash
# Create .gemini directory
mkdir -p .gemini

# Create symlink (Unix/Linux/macOS)
ln -sf .claude/.mcp.json .gemini/settings.json

# Create symlink (Windows - requires admin or developer mode)
mklink .gemini\settings.json .claude\.mcp.json
```

### Security

Add to `.gitignore`:
```
.gemini/settings.json
```

This prevents committing sensitive API keys and server configurations.

## Usage

### Basic Syntax

```bash
gemini [flags] -p "<prompt>"
```

### Essential Flags

- `-y`: Skip confirmation prompts (auto-approve tool execution)
- `-m <model>`: Model selection
  - `gemini-2.5-flash` (fast, recommended for MCP)
  - `gemini-2.5-flash` (balanced)
  - `gemini-pro` (high quality)
- `-p "<prompt>"`: Task description

### Examples

**Screenshot Capture**:
```bash
gemini -y -m gemini-2.5-flash -p "Take a screenshot of https://www.google.com.vn"
```

**Memory Operations**:
```bash
gemini -y -m gemini-2.5-flash -p "Remember that Alice is a React developer working on e-commerce projects"
```

**Web Research**:
```bash
gemini -y -m gemini-2.5-flash -p "Search for latest Next.js 15 features and summarize the top 3"
```

**Multi-Tool Orchestration**:
```bash
gemini -y -m gemini-2.5-flash -p "Search for Claude AI documentation, take a screenshot of the homepage, and save both to memory"
```

**Browser Automation**:
```bash
gemini -y -m gemini-2.5-flash -p "Navigate to https://example.com, click the signup button, and take a screenshot"
```

## How It Works

1. **Configuration Loading**: Reads `.gemini/settings.json` (symlinked to `.claude/.mcp.json`)
2. **Server Connection**: Connects to all configured MCP servers
3. **Tool Discovery**: Lists all available tools from servers
4. **Prompt Analysis**: Gemini model analyzes the prompt
5. **Tool Selection**: Automatically selects relevant tools
6. **Execution**: Calls tools with appropriate parameters
7. **Result Synthesis**: Combines tool outputs into coherent response

See [gemini-cli-advanced.md](gemini-cli-advanced.md) for advanced configuration (trusted servers, tool filtering, env vars), troubleshooting (MCP status, symlink verification, debug mode), and method comparison.

**Recommendation**: Use Gemini CLI as primary method, fallback to scripts/subagent when unavailable.