# MCP, Skills & Hooks

## MCP Servers

Configure via Settings → MCP, or the `[mcp]` section of `config.toml`.

```toml
[mcp]
sse_servers = [
  "http://localhost:8080/mcp",
  {url = "https://api.example.com/mcp", api_key = "key"},
]

shttp_servers = [
  "https://api.example.com/shttp",
  {url = "https://files.example.com/mcp", timeout = 1800},
]

stdio_servers = [
  {name = "fetch", command = "uvx", args = ["mcp-server-fetch"]},
  {name = "gh", command = "npx", args = ["-y", "@modelcontextprotocol/server-github"],
   env = {GITHUB_TOKEN = "ghp_..."}},
]
```

| Type | Fields |
|------|--------|
| `sse_servers` | String URL, or `{url, api_key}` |
| `shttp_servers` | String URL, or `{url, api_key, timeout}` — timeout 1–3600s, default 60 |
| `stdio_servers` | `{name, command, args, env}`; `name` = letters/digits/underscore/hyphen |

Upstream recommends fronting stdio servers with an MCP proxy (e.g. SuperGateway) that exposes them over
HTTP/SSE — stdio servers are spawned as child processes and are the flakier path, especially in containers
where the command may not exist inside the sandbox image.

SDK equivalent:

```python
agent = Agent(
    llm=llm,
    tools=[Tool(name=TerminalTool.name)],
    mcp_config={"mcpServers": {"fetch": {"command": "uvx", "args": ["mcp-server-fetch"]}}},
)
```

## Repository Customization: `.openhands/`

A `.openhands/` directory at the repo root customizes agent behavior per project.

```
.openhands/
├── setup.sh              # runs when OpenHands starts on this repo
├── hooks.json            # lifecycle hooks
├── hooks/
│   └── quality_gate.sh
└── microagents/          # skills: repo knowledge and triggered guidance
    └── repo.md
```

## setup.sh

```bash
#!/bin/bash
export MY_ENV_VAR="my value"
sudo apt-get update
sudo apt-get install -y lsof
cd frontend && npm install ; cd ..
```

Runs on every session start. Keep it fast and idempotent — a slow setup script is paid on every conversation.
Guard expensive steps with existence checks.

## Skills (Microagents)

Markdown files under `.openhands/microagents/` that extend the system prompt with project knowledge. `repo.md`
is always loaded; trigger-based skills load only when keywords appear.

```markdown
---
name: database
triggers: [migration, alembic, schema]
---

Migrations live in `db/migrations/`. Always create them with
`alembic revision --autogenerate -m "<message>"` and never hand-edit applied revisions.
```

Trigger-based skills keep the base prompt small — put universal facts in `repo.md` and everything conditional
behind triggers. Verify frontmatter keys against the installed version; the skills format has evolved from the
older microagent format.

`AGENTS.md` at the repo root is also read as project instructions, matching the cross-tool convention.

Disable specific ones with `AGENT_DISABLED_MICROAGENTS`, or all prompt extensions with
`AGENT_ENABLE_PROMPT_EXTENSIONS=false`.

## Hooks

`.openhands/hooks.json` runs shell scripts at lifecycle points — blocking dangerous commands, enforcing
linting, logging tool use, gating completion.

```json
{
  "stop": [
    {
      "matcher": "*",
      "hooks": [
        { "command": ".openhands/hooks/quality_gate.sh", "timeout": 120 }
      ]
    }
  ]
}
```

### Stop Hook as a Quality Gate

```bash
#!/bin/bash
# .openhands/hooks/quality_gate.sh
cd "${OPENHANDS_PROJECT_DIR:-$PWD}"
if ! make test 2>&1; then
  echo '{"decision":"deny","reason":"Quality checks failed."}'
  exit 2
fi
exit 0
```

Emitting `{"decision":"deny","reason":...}` with exit code 2 prevents the agent from declaring completion and
feeds the reason back so it keeps working. This is the most effective single customization for a repo: the
agent stops claiming success while tests fail.

Make hook scripts executable (`chmod +x`) and keep timeouts realistic — a hook that exceeds its timeout is
treated as a failure.

## Precedence

1. `AGENTS.md` + `.openhands/microagents/repo.md` — always loaded
2. Trigger-based skills — loaded on keyword match
3. `setup.sh` — environment, at session start
4. `hooks.json` — enforcement at lifecycle points

Instructions guide; hooks enforce. Anything that must not be skipped belongs in a hook, because prompt
instructions are advisory to the model.
