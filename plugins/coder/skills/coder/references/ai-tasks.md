# AI Agents in Coder Workspaces

Coder can run coding agents (OpenHands, Claude Code, Aider, Goose) inside workspaces, with a chat UI surfaced
in the dashboard. Pairs with the `openhands` skill.

## coder_ai_task

Marks a template as task-capable. Coder then shows the Tasks UI and passes a prompt into the workspace.

```hcl
resource "coder_ai_task" "task" {
  app_id = coder_app.agent_ui.id     # the app providing the chat interface
}
```

Read-only attributes (Coder v2.28+):

| Attribute | Meaning |
|-----------|---------|
| `enabled` | `true` when the build runs in Task context, `false` for a plain workspace |
| `prompt` | The prompt text Coder passed to the task |

The `sidebar_app` block is deprecated — use `app_id`.

## Prompt Parameter

Task templates conventionally accept the prompt as a parameter so it's available during provisioning:

```hcl
data "coder_parameter" "ai_prompt" {
  name         = "AI Prompt"
  display_name = "Prompt"
  type         = "string"
  form_type    = "textarea"
  mutable      = true
  default      = ""
}
```

## Registry Modules First

Before hand-rolling, check the registry — `claude-code`, `aider`, `goose`, `agentapi`, and `mux` modules wire
an agent plus its `coder_app` in a few lines, and `agent-firewall` restricts its egress:

```hcl
module "claude-code" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/claude-code/coder"
  version  = "..."                       # pin; check the module page
  agent_id = coder_agent.main.id
}
```

There is no OpenHands module at present, so the hand-rolled pattern below applies. → `modules.md`

## Running OpenHands as the Agent

The agent runs headless inside the workspace and exposes an HTTP UI that `coder_app` proxies.

```hcl
resource "coder_script" "openhands" {
  agent_id     = coder_agent.main.id
  display_name = "OpenHands"
  icon         = "/icon/widgets.svg"
  run_on_start = true
  log_path     = "/tmp/openhands.log"
  script       = <<-EOT
    #!/usr/bin/env bash
    set -euo pipefail
    export PATH="$HOME/.local/bin:$PATH"
    command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
    uv tool install openhands --python 3.12
    openhands serve >/tmp/openhands-run.log 2>&1 &
  EOT
}

resource "coder_app" "openhands" {
  agent_id     = coder_agent.main.id
  slug         = "openhands"
  display_name = "OpenHands"
  url          = "http://localhost:3000"
  icon         = "/icon/widgets.svg"
  subdomain    = true          # agent UIs generally need their own origin
  share        = "owner"
  healthcheck {
    url       = "http://localhost:3000/health"
    interval  = 10
    threshold = 30
  }
}

resource "coder_ai_task" "task" {
  app_id = coder_app.openhands.id
}
```

Verify the health endpoint against the OpenHands version you deploy — if it 404s the app shows unhealthy while
working fine. Drop the `healthcheck` block if unsure.

## LLM Credentials

Never bake keys into the template. Inject from a Kubernetes Secret at the pod level:

```hcl
env {
  name = "LLM_API_KEY"
  value_from {
    secret_key_ref { name = "llm-credentials", key = "api-key" }
  }
}
env {
  name  = "LLM_BASE_URL"
  value = "http://litellm.litellm.svc.cluster.local:4000"
}
env {
  name  = "LLM_MODEL"
  value = "litellm_proxy/claude-sonnet-4-5"
}
```

Routing every workspace through a LiteLLM gateway is the right pattern here: per-user virtual keys, budget
caps, and spend attribution, without distributing provider keys to sandboxes users control. See the `litellm`
skill.

## coder_external_agent

For an agent process running **outside** the provisioned infrastructure that still reports into the workspace:

```hcl
resource "coder_external_agent" "remote" {
  agent_id = coder_agent.main.id
}
```

Use when the agent runs on dedicated GPU capacity or a separate runtime pool rather than inside the workspace
pod.

## Sandbox Boundary

A coding agent with terminal access inherits everything the workspace can reach. In a template that runs
agents:

- Give workspaces their own namespace and a restrictive egress NetworkPolicy.
- Set `api_key_scope = "no_user_data"` on `coder_agent` so a compromised agent can't read the owner's Coder
  data through the agent token.
- Do not mount cloud credentials or kubeconfigs into task workspaces.
- Prefer per-user LiteLLM virtual keys with hard budget caps over shared provider keys.

```hcl
resource "coder_agent" "main" {
  os            = "linux"
  arch          = "amd64"
  api_key_scope = "no_user_data"
}
```
