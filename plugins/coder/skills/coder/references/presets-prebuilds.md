# Presets & Prebuilt Workspaces

Parameter syntax itself: → `parameters.md`

## Presets

A preset is a named bundle of parameter values. Users pick the preset instead of filling the form.

```hcl
data "coder_workspace_preset" "goland_large" {
  name = "GoLand: Large"
  parameters = {
    (data.coder_parameter.ide.name)    = "GO"
    (data.coder_parameter.cpu.name)    = "8"
    (data.coder_parameter.memory.name) = "16"
  }
}
```

Parameter values in a preset are strings regardless of the parameter's declared type.

## Prebuilt Workspaces (Premium)

Requires a Premium license and `coder/coder` provider >= 2.4.1. Coder keeps a warm pool owned by a system
`prebuilds` user; when a developer creates a workspace matching the preset, ownership transfers and the
workspace is instantly ready.

```hcl
data "coder_workspace_preset" "goland_large" {
  name = "GoLand: Large"
  parameters = {
    (data.coder_parameter.cpu.name)    = "8"
    (data.coder_parameter.memory.name) = "16"
  }

  prebuilds {
    instances = 3

    expiration_policy {
      ttl = 86400        # seconds an unclaimed prebuild may live
    }

    scheduling {
      timezone = "UTC"
      schedule {
        cron      = "* 8-18 * * 1-5"   # warm during business hours
        instances = 3
      }
      schedule {
        cron      = "* 19-23 * * 1-5"
        instances = 0
      }
    }
  }
}
```

### Claiming

On claim, `terraform apply` re-runs with the new owner. Anything derived from
`data.coder_workspace_owner.me` changes at that moment. Resources that would be *replaced* by that change must
ignore it, or claiming becomes a full rebuild and the prebuild bought nothing:

```hcl
resource "kubernetes_persistent_volume_claim_v1" "home" {
  # ...
  lifecycle {
    ignore_changes = [metadata[0].name, metadata[0].labels]
  }
}
```

Use `data.coder_workspace.me.is_prebuild` to skip user-specific setup while unclaimed, and
`is_prebuild_claim` to run it exactly once at claim time:

```hcl
resource "coder_script" "personalize" {
  agent_id     = coder_agent.main.id
  display_name = "Personalize"
  run_on_start = true
  script       = data.coder_workspace.me.is_prebuild ? "echo skipped" : "$HOME/.dotfiles/install.sh"
}
```

### Cost Control

Prebuilds consume real infrastructure while idle. Pair `scheduling` with `expiration_policy` so pools drain
overnight, and keep `instances` at the observed concurrent-create rate, not headcount.
