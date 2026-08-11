# Template Parameters

## coder_parameter

```hcl
data "coder_parameter" "region" {
  name         = "region"
  display_name = "Region"
  description  = "Where to deploy the workspace"
  type         = "string"          # string | number | bool | list(string)
  default      = "us-east"
  icon         = "/emojis/1f30e.png"
  mutable      = true              # false = fixed after creation
  order        = 1

  option {
    name  = "US East"
    value = "us-east"
    icon  = "/emojis/1f1fa-1f1f8.png"
  }
  option {
    name  = "EU West"
    value = "eu-west"
    icon  = "/emojis/1f1ea-1f1fa.png"
  }
}
```

### Arguments

| Argument | Notes |
|----------|-------|
| `name` | Stable identifier — renaming breaks existing workspaces |
| `display_name`, `description` | UI text (description supports markdown) |
| `type` | `string`, `number`, `bool`, `list(string)` |
| `default` | Omit to make the parameter required |
| `mutable` | `false` blocks changes after create — use for disk size, anything destructive |
| `ephemeral` | Value applies to one build only, then resets (e.g. `force_rebuild`) |
| `icon` | `/emojis/<codepoint>.png` or any URL |
| `order` | Ascending display order |
| `option` | Repeatable block: `name`, `value`, `icon`, `description` |
| `validation` | `regex` + `error` for strings; `min`/`max`/`monotonic` for numbers |
| `form_type` | UI widget override (`dropdown`, `radio`, `slider`, `input`, `textarea`, `multi-select`, `switch`, `tag-select`) |

### Validation

```hcl
data "coder_parameter" "instances" {
  name = "instances"
  type = "number"
  validation {
    min       = 1
    max       = 8
    monotonic = "increasing"     # subsequent builds may only raise it
    error     = "Maximum limit: {max}, wanted: {value}."
  }
}

data "coder_parameter" "hostname" {
  name = "hostname"
  type = "string"
  validation {
    regex = "^[a-z0-9-]{3,32}$"
    error = "Lowercase letters, digits and hyphens; 3-32 chars."
  }
}
```

`monotonic = "increasing"` is the safe choice for disk size — it prevents a user shrinking a volume and losing
data. `mutable = false` is stricter still.

### Lists & Ephemeral

```hcl
data "coder_parameter" "security_groups" {
  name    = "security_groups"
  type    = "list(string)"
  mutable = true
  default = jsonencode(["default-sg"])     # list defaults must be JSON-encoded
}

data "coder_parameter" "force_rebuild" {
  name      = "force_rebuild"
  type      = "bool"
  ephemeral = true
  default   = false
}
```

Read a list back with `jsondecode(data.coder_parameter.security_groups.value)`.

Presets and prebuilt pools: → `presets-prebuilds.md`
