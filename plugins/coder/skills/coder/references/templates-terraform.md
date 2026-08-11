# Coder Terraform Provider Reference

```hcl
terraform {
  required_providers {
    coder      = { source = "coder/coder" }
    kubernetes = { source = "hashicorp/kubernetes" }
  }
}
```

No provider credentials — `coderd` injects context into the provisioner at build time.

## Resources

| Resource | Purpose |
|----------|---------|
| `coder_agent` | The agent process inside a workspace; exports `init_script` and `token` |
| `coder_agent_instance` | Binds an agent to a cloud instance ID for instance-identity auth |
| `coder_app` | A URL/command surfaced as a button in the dashboard |
| `coder_script` | Lifecycle/cron scripts attached to an agent |
| `coder_env` | Injects an env var into the agent's session |
| `coder_metadata` | Attaches display metadata to any resource in the UI |
| `coder_devcontainer` | Declares a devcontainer for the agent to build and run |
| `coder_ai_task` | Marks a template as an AI task (→ `ai-tasks.md`) |
| `coder_external_agent` | Agent running outside the provisioned infra |

## Data Sources

| Data source | Purpose |
|-------------|---------|
| `coder_workspace` | Build context: `start_count`, `transition`, `access_url`, prebuild flags |
| `coder_workspace_owner` | `id`, `name`, `full_name`, `email`, `groups`, `ssh_public_key`, `oidc_access_token` |
| `coder_parameter` | User-facing build input (→ `parameters.md`) |
| `coder_workspace_preset` | Named parameter bundle + prebuild pool |
| `coder_workspace_tags` | Dynamic provisioner tags computed from parameters |
| `coder_external_auth` | Git provider token passthrough (→ `external-auth.md`) |
| `coder_provisioner` | Info about the provisioner running this build (`arch`, `os`) |
| `coder_task` | Task context for AI-agent templates |

## coder_agent

```hcl
resource "coder_agent" "main" {
  os                     = "linux"          # linux | darwin | windows  (required)
  arch                   = "amd64"          # amd64 | arm64 | armv7     (required)
  auth                   = "token"          # or *-instance-identity
  connection_timeout     = 120
  troubleshooting_url    = "https://wiki.example.com/coder"
  api_key_scope          = "all"            # or no_user_data
  startup_script_behavior = "non-blocking"  # blocking blocks login until done

  env = { GIT_AUTHOR_NAME = data.coder_workspace_owner.me.full_name }

  display_apps {
    vscode                 = true
    vscode_insiders        = false
    web_terminal           = true
    ssh_helper             = true
    port_forwarding_helper = true
  }

  metadata {
    key          = "cpu"
    display_name = "CPU Usage"
    script       = "coder stat cpu"
    interval     = 10
    timeout      = 1
  }

  resources_monitoring {
    memory { enabled = true, threshold = 80 }
    volume { path = "/home/coder", enabled = true, threshold = 90 }
  }
}
```

Exports: `id`, `init_script` (run as the container command), `token` (sensitive — set as `CODER_AGENT_TOKEN`).

`dir` is deprecated; set the working directory in the workspace image or via `coder_script`.

## coder_app

```hcl
resource "coder_app" "code-server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"                # hostname-safe, no leading/trailing/double hyphens
  display_name = "VS Code"
  url          = "http://localhost:13337?folder=/home/coder"
  icon         = "/icon/code.svg"
  subdomain    = false          # true needs CODER_WILDCARD_ACCESS_URL
  share        = "owner"        # owner | authenticated | public
  open_in      = "slim-window"  # or tab
  order        = 1
  group        = "Editors"

  healthcheck {
    url       = "http://localhost:13337/healthz"
    interval  = 5
    threshold = 6
  }
}
```

`command` and `subdomain` are mutually exclusive. `external = true` opens the URL on the client machine
instead of proxying.

## coder_script

```hcl
resource "coder_script" "install" {
  agent_id           = coder_agent.main.id
  display_name       = "Install tooling"
  icon               = "/icon/terminal.svg"
  run_on_start       = true
  run_on_stop        = false
  start_blocks_login = false
  timeout            = 300
  log_path           = "/tmp/install.log"
  script             = <<-EOT
    #!/usr/bin/env bash
    set -euo pipefail
    curl -fsSL https://code-server.dev/install.sh | sh
    code-server --auth none --port 13337 >/tmp/code-server.log 2>&1 &
  EOT
}
```

Prefer `coder_script` over `coder_agent.startup_script`: multiple scripts run in parallel, each gets its own
log stream and dashboard entry, and `cron` (6-field, seconds first) enables recurring jobs.

## coder_metadata

```hcl
resource "coder_metadata" "home" {
  resource_id = kubernetes_persistent_volume_claim_v1.home.id
  item { key = "size", value = "${data.coder_parameter.home_disk_size.value} GiB" }
  item { key = "token", value = "secret", sensitive = true }
}
```

Also accepts `hide = true` to remove noisy resources from the workspace view.

## coder_workspace / coder_workspace_owner

| Attribute | Meaning |
|-----------|---------|
| `start_count` | `1` when starting, `0` when stopped — gate ephemeral resources with this |
| `transition` | `start` or `stop` |
| `id`, `name` | Workspace UUID and name |
| `access_url`, `access_port` | Deployment URL the agent dials |
| `template_id`, `template_name`, `template_version` | Template context |
| `is_prebuild` | `true` while unclaimed in the prebuild pool |
| `is_prebuild_claim` | `true` on the first apply after a user claims a prebuild |
| `prebuild_count` | `1` if an unassigned prebuild |

`coder_workspace_owner.me` exposes `name`, `full_name`, `email`, `groups`, `ssh_public_key`,
`session_token`, and `oidc_access_token` (useful for passing IdP tokens to in-workspace tooling).

## Dev Containers

```hcl
resource "coder_devcontainer" "project" {
  agent_id         = coder_agent.main.id
  workspace_folder = "/home/coder/project"
  config_path      = "/home/coder/project/.devcontainer/devcontainer.json"
}
```

Two approaches: the **dev containers integration** (agent runs `@devcontainers/cli` against a Docker socket in
the workspace) or **envbuilder** (builds the devcontainer image without Docker, useful on Kubernetes where a
docker socket isn't available). Envbuilder replaces the workspace image itself rather than nesting a container.

## Template Lifecycle

```bash
coder templates init                # scaffold from a starter
coder templates push <name>         # publish a new version from ./
coder templates push --activate=false <name>   # stage without promoting
coder templates edit <name> --display-name "..." --icon "/emojis/2b50.png"
coder templates versions list <name>
coder templates pull <name> ./dir
```

Templates are versioned; existing workspaces keep their version until updated. `--activate=false` lets you test
a version against one workspace before making it the default.
