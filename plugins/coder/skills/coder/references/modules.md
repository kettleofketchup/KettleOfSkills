# Registry Modules

Terraform modules from `registry.coder.com` replace hand-written `coder_script` + `coder_app` pairs. Prefer
them: they handle install, health checks, icons, and ordering, and they're maintained upstream.

## Usage

```hcl
module "code-server" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/code-server/coder"
  version  = "1.5.2"
  agent_id = coder_agent.main.id
}
```

`count = data.coder_workspace.me.start_count` is required on nearly every module — without it the module's
resources persist while the workspace is stopped.

Always pin `version`. Modules are versioned independently of the Coder release, and an unpinned module changes
under you on the next `terraform init`.

## Official Modules

| Module | Purpose |
|--------|---------|
| `code-server` | VS Code in the browser |
| `vscode-web` | Microsoft's VS Code Web build |
| `jetbrains` / `jetbrains-gateway` | JetBrains IDEs via Gateway |
| `cursor`, `kiro`, `antigravity` | Desktop AI editors (deep-link to the workspace) |
| `git-clone` | Clone a repo on start |
| `git-config` | Set user name/email from the workspace owner |
| `git-commit-signing` | GPG/SSH commit signing |
| `github-upload-public-key` | Push the workspace key to GitHub |
| `dotfiles` | Apply the user's dotfiles repo |
| `personalize` | Run a user-owned `personalize` script |
| `coder-login` | Authenticate the CLI inside the workspace |
| `devcontainers-cli` | Install `@devcontainers/cli` |
| `filebrowser` | Web file manager |
| `jupyter-notebook`, `jupyterlab`, `rstudio-server` | Data-science IDEs |
| `kasmvnc`, `portabledesktop`, `local-windows-rdp`, `amazon-dcv-windows` | Desktop/GUI access |
| `claude-code`, `aider`, `goose`, `agentapi`, `mux` | AI coding agents (→ `ai-tasks.md`) |
| `agent-firewall` | Restrict agent egress |
| `aibridge-proxy` | LLM proxy for in-workspace agents |
| `jfrog-oauth`, `jfrog-token`, `jfrog-xray` | Artifactory integration |
| `vault-cli`, `vault-github` | HashiCorp Vault auth |
| `aws-region`, `azure-region`, `gcp-region`, `fly-region` | Region picker parameters |
| `slackme` | Slack notification when a command finishes |
| `coder-utils` | Shared helpers |

Browse: `https://registry.coder.com/modules`. Source: `github.com/coder/registry` under
`registry/coder/modules/`.

## code-server Options

```hcl
module "code-server" {
  count           = data.coder_workspace.me.start_count
  source          = "registry.coder.com/coder/code-server/coder"
  version         = "1.5.2"
  agent_id        = coder_agent.main.id
  install_version = "4.106.3"          # pin code-server itself
  folder          = "/home/coder/project"
  extensions      = ["dracula-theme.theme-dracula", "ms-azuretools.vscode-docker"]
  settings = {
    "workbench.colorTheme" = "Dracula"
  }
  order = 1
  group = "Editors"
}
```

`workspace = "/home/coder/project/my.code-workspace"` opens a multi-root workspace file instead of `folder`.

## Common Composition

```hcl
module "git-config" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/git-config/coder"
  version  = "1.0.15"
  agent_id = coder_agent.main.id
}

module "git-clone" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/git-clone/coder"
  version  = "1.1.0"
  agent_id = coder_agent.main.id
  url      = "https://github.com/example/project.git"
  base_dir = "/home/coder"
}

module "dotfiles" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/dotfiles/coder"
  version  = "1.2.1"
  agent_id = coder_agent.main.id
}

module "jetbrains" {
  count    = data.coder_workspace.me.start_count
  source   = "registry.coder.com/coder/jetbrains/coder"
  version  = "1.0.3"
  agent_id = coder_agent.main.id
  folder   = "/home/coder/project"
}
```

Version numbers above are illustrative — check each module's page for the current one. `terraform init` fails
loudly on a nonexistent version, so a wrong pin is caught at push time, not at build time.

## Air-Gapped

`registry.coder.com` is a Terraform registry and must be reachable from the **provisioner**, not the browser.
In air-gapped deployments, vendor the modules into your template repo and switch `source` to a local path:

```hcl
module "code-server" {
  source   = "./modules/code-server"
  agent_id = coder_agent.main.id
}
```

Copy from `github.com/coder/registry` at the version you want and commit it. → `helm-deploy.md` for the
provider mirror that the same constraint requires.

## When to Hand-Roll Instead

Write `coder_script` + `coder_app` directly when the tool isn't in the registry, when you need install logic
tied to your base image, or when the module's abstraction hides something you must control (custom auth,
non-standard ports). Modules are a convenience layer over exactly those two resources —
→ `templates-terraform.md`.
