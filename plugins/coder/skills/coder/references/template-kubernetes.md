# Complete Kubernetes Workspace Template

Working reference template: PVC-backed home directory, code-server, resource parameters.

```hcl
terraform {
  required_providers {
    coder      = { source = "coder/coder" }
    kubernetes = { source = "hashicorp/kubernetes" }
  }
}

provider "kubernetes" {
  # In-cluster: leave empty and rely on the provisioner's service account.
  config_path = null
}

variable "namespace" {
  type        = string
  description = "Namespace where workspace pods are created"
  default     = "coder-workspaces"
}

data "coder_workspace" "me" {}
data "coder_workspace_owner" "me" {}

data "coder_parameter" "cpu" {
  name         = "cpu"
  display_name = "CPU"
  description  = "Cores"
  type         = "number"
  default      = 2
  mutable      = true
  icon         = "/icon/memory.svg"
  validation { min = 1, max = 16 }
}

data "coder_parameter" "memory" {
  name         = "memory"
  display_name = "Memory (GiB)"
  type         = "number"
  default      = 4
  mutable      = true
  validation { min = 2, max = 64 }
}

data "coder_parameter" "home_disk_size" {
  name         = "home_disk_size"
  display_name = "Home disk size (GiB)"
  type         = "number"
  default      = 20
  mutable      = false          # resizing down would destroy data
  validation { min = 10, max = 500 }
}

resource "coder_agent" "main" {
  os                      = "linux"
  arch                    = "amd64"
  startup_script_behavior = "non-blocking"

  env = {
    GIT_AUTHOR_NAME     = coalesce(data.coder_workspace_owner.me.full_name, data.coder_workspace_owner.me.name)
    GIT_AUTHOR_EMAIL    = data.coder_workspace_owner.me.email
    GIT_COMMITTER_NAME  = coalesce(data.coder_workspace_owner.me.full_name, data.coder_workspace_owner.me.name)
    GIT_COMMITTER_EMAIL = data.coder_workspace_owner.me.email
  }

  metadata {
    key = "cpu_usage"    display_name = "CPU Usage"
    script = "coder stat cpu"   interval = 10  timeout = 1
  }
  metadata {
    key = "mem_usage"    display_name = "Memory Usage"
    script = "coder stat mem"   interval = 10  timeout = 1
  }
  metadata {
    key = "home_disk"    display_name = "Home Disk"
    script = "coder stat disk --path $HOME"  interval = 60  timeout = 1
  }
}

resource "coder_script" "code_server" {
  agent_id     = coder_agent.main.id
  display_name = "code-server"
  icon         = "/icon/code.svg"
  run_on_start = true
  log_path     = "/tmp/code-server.log"
  script       = <<-EOT
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v code-server >/dev/null; then
      curl -fsSL https://code-server.dev/install.sh | sh -s -- --method=standalone \
        --prefix=/home/coder/.local
    fi
    /home/coder/.local/bin/code-server --auth none --port 13337 \
      >/tmp/code-server-run.log 2>&1 &
  EOT
}

resource "coder_app" "code_server" {
  agent_id     = coder_agent.main.id
  slug         = "code-server"
  display_name = "VS Code"
  url          = "http://localhost:13337?folder=/home/coder"
  icon         = "/icon/code.svg"
  subdomain    = false
  share        = "owner"
  healthcheck {
    url       = "http://localhost:13337/healthz"
    interval  = 5
    threshold = 6
  }
}

# Persistent home — NO start_count. Must survive stop/start.
resource "kubernetes_persistent_volume_claim_v1" "home" {
  metadata {
    name      = "coder-${lower(data.coder_workspace_owner.me.name)}-${lower(data.coder_workspace.me.name)}-home"
    namespace = var.namespace
    labels = {
      "app.kubernetes.io/name"     = "coder-pvc"
      "app.kubernetes.io/instance" = data.coder_workspace.me.id
    }
  }
  wait_until_bound = false
  spec {
    access_modes = ["ReadWriteOnce"]
    resources { requests = { storage = "${data.coder_parameter.home_disk_size.value}Gi" } }
  }
}

# Ephemeral compute — gated on start_count.
resource "kubernetes_deployment_v1" "main" {
  count      = data.coder_workspace.me.start_count
  depends_on = [kubernetes_persistent_volume_claim_v1.home]

  metadata {
    name      = "coder-${lower(data.coder_workspace_owner.me.name)}-${lower(data.coder_workspace.me.name)}"
    namespace = var.namespace
  }

  spec {
    replicas = 1
    selector { match_labels = { "app.kubernetes.io/instance" = data.coder_workspace.me.id } }
    template {
      metadata { labels = { "app.kubernetes.io/instance" = data.coder_workspace.me.id } }
      spec {
        security_context {
          run_as_user = 1000
          fs_group    = 1000
        }
        container {
          name              = "dev"
          image             = "codercom/enterprise-base:ubuntu"
          image_pull_policy = "Always"
          command           = ["sh", "-c", coder_agent.main.init_script]

          env {
            name  = "CODER_AGENT_TOKEN"
            value = coder_agent.main.token
          }

          resources {
            requests = { "cpu" = "250m", "memory" = "512Mi" }
            limits = {
              "cpu"    = "${data.coder_parameter.cpu.value}"
              "memory" = "${data.coder_parameter.memory.value}Gi"
            }
          }

          volume_mount {
            mount_path = "/home/coder"
            name       = "home"
            read_only  = false
          }
        }

        volume {
          name = "home"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim_v1.home.metadata.0.name
            read_only  = false
          }
        }
      }
    }
  }
}

resource "coder_metadata" "home_info" {
  resource_id = kubernetes_persistent_volume_claim_v1.home.id
  item { key = "size", value = "${data.coder_parameter.home_disk_size.value} GiB" }
}
```

## The Two Non-Negotiables

1. `command = ["sh", "-c", coder_agent.main.init_script]` — how the agent starts.
2. `CODER_AGENT_TOKEN = coder_agent.main.token` — how it authenticates.

Missing either yields a workspace that builds green and never connects.

## Resource Lifecycle Rules

| Resource | `count = start_count`? |
|----------|------------------------|
| Deployment / Pod | **Yes** — must vanish on stop |
| PersistentVolumeClaim | **No** — must persist |
| Service, ConfigMap for the pod | Yes |
| Secret holding long-lived data | No |

## Push It

```bash
coder templates push kubernetes -d . --yes
coder create --template kubernetes my-workspace
```

## Namespace Permissions

The provisioner's service account needs, in `var.namespace`: `pods`, `deployments`, `persistentvolumeclaims`,
`services`, `secrets`, `events` (get/list/watch/create/update/patch/delete). With the built-in provisioner,
`coder.serviceAccount.workspacePerms: true` covers the release namespace only — a separate workspace namespace
needs its own Role/RoleBinding.
