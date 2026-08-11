# OpenHands Python SDK

Programmatic agents without the web UI. Repo: `github.com/OpenHands/software-agent-sdk`
(packages: `openhands-sdk`, `openhands-tools`, `openhands-agent-server`, `openhands-workspace`).

## Install

```bash
pip install -U openhands-sdk openhands-tools
export LLM_API_KEY=...
```

## Minimal Agent

```python
import os
from openhands.sdk import LLM, Agent, Conversation, Tool
from openhands.tools.file_editor import FileEditorTool
from openhands.tools.task_tracker import TaskTrackerTool
from openhands.tools.terminal import TerminalTool

llm = LLM(
    model=os.getenv("LLM_MODEL", "anthropic/claude-sonnet-4-5-20250929"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL", None),
)

agent = Agent(
    llm=llm,
    tools=[
        Tool(name=TerminalTool.name),
        Tool(name=FileEditorTool.name),
        Tool(name=TaskTrackerTool.name),
    ],
)

conversation = Conversation(agent=agent, workspace=os.getcwd())
conversation.send_message("Write 3 facts about the current project into FACTS.txt.")
conversation.run()
```

`workspace=os.getcwd()` runs tools against the local directory with no container. For untrusted work, use a
Docker workspace instead (below).

## Core Concepts

| Concept | Role |
|---------|------|
| `LLM` | Provider-agnostic model interface (LiteLLM-backed) |
| `Agent` | Reasoning loop + tool set + system prompt |
| `Conversation` | State, event stream, execution driver |
| `Tool` | Capability registration by name |
| `Workspace` | Where tools execute — local dir, Docker, or remote |
| Event | Everything is an event: actions, observations, messages |
| Condenser | History compaction for long runs |

## Sandboxed Workspaces

```python
from openhands.workspace import DockerWorkspace

with DockerWorkspace(
    base_image="nikolaik/python-nodejs:python3.12-nodejs22",
    host_port=8010,
) as workspace:
    conversation = Conversation(agent=agent, workspace=workspace)
    conversation.send_message("Run the test suite and fix failures.")
    conversation.run()
```

Also available: API sandbox (hosted) and Apptainer (HPC/rootless). Check the installed version's
`openhands.workspace` exports — constructor signatures vary across releases.

## Confirmation Policy

```python
from openhands.sdk.security.confirmation_policy import AlwaysConfirm

conversation.set_confirmation_policy(AlwaysConfirm())
```

Pauses before each action for approval. Combine with a security analyzer to gate only risky actions rather
than everything.

## Secrets

```python
conversation = Conversation(
    agent=agent,
    workspace=cwd,
    secrets={"GITHUB_TOKEN": os.environ["GITHUB_TOKEN"]},
)
```

Secrets are injected into the tool environment and masked in the event stream — pass them here rather than
interpolating into prompts, where they'd persist in history and logs.

## LLM Routing, Fallback & Profiles

The SDK ships an LLM registry and profile store supporting fallback chains, routing rules, streaming, and
reasoning-effort presets. Typical use: a strong model for the agent, a cheap one for condensing.

```python
from openhands.sdk import LLM

primary  = LLM(model="anthropic/claude-sonnet-4-5-20250929", api_key=key, service_id="primary")
fallback = LLM(model="openai/gpt-5.2", api_key=okey, service_id="fallback")
```

Docs: `sdk/guides/llm-routing`, `llm-fallback`, `llm-registry`, `llm-profile-store`.

## Subscription Login

```python
llm = LLM.subscription_login(vendor="openai", model="gpt-5.2-codex")
```

→ `llm-subscriptions.md`

## MCP Tools

```python
agent = Agent(
    llm=llm,
    tools=[Tool(name=TerminalTool.name)],
    mcp_config={
        "mcpServers": {
            "fetch": {"command": "uvx", "args": ["mcp-server-fetch"]},
        }
    },
)
```

→ `mcp-skills-hooks.md`

## Custom Tools

Subclass the tool base, declare a schema, register it, and pass `Tool(name=...)`. See
`sdk/guides/agent-server/custom-tools`. Prefer an MCP server when the capability is useful outside
OpenHands — it works with any MCP client rather than only this SDK.

## Agent Server

A REST/WebSocket service wrapping conversations — the same component the web UI drives. Run it standalone to
build your own frontend or to host agents remotely:

```bash
docker run -p 8000:8000 ghcr.io/openhands/agent-server:1.26.0-python
```

Guides: `sdk/guides/agent-server/{local-server,docker-sandbox,api-sandbox,custom-tools}`.

## Observability

```python
print(conversation.state.stats)     # token usage and cost
```

Built-in metrics plus OpenTelemetry-compatible tracing — see `sdk/guides/observability` and
`sdk/guides/metrics`. Cost tracking depends on correct per-token pricing; set it explicitly for local or
gateway-fronted models.

## GitHub Workflows

Prebuilt recipes for PR review, review assignment, and TODO management run the SDK inside Actions:
`sdk/guides/github-workflows/*`. Repo-level automation (issue → PR) uses the OpenHands GitHub Action —
`openhands/usage/run-openhands/github-action`.

## API Reference

`openhands.sdk.{agent,conversation,event,llm,security,tool,utils,workspace}` at
`docs.openhands.dev/sdk/api-reference/`.

## Version Caution

The SDK is pre-1.0 and moves quickly; import paths and constructor arguments change between minor versions.
Pin versions in anything durable and verify signatures against the installed package rather than trusting
older examples:

```bash
python -c "import openhands.sdk as s; print(s.__version__)"
```
