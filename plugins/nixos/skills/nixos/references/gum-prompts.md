# Charmbracelet Gum Prompts Reference

Use `gum` for TUI prompts in NixOS install scripts. Collect site-specific config at runtime without changing the ISO's flake closure.

Nix package: `pkgs.gum`

## Prompt Patterns

```bash
# Text input
hostname=$(gum input --placeholder "node01" --header "Hostname:")

# Selection
role=$(gum choose "server" "agent" --header "K3s role:")

# Multi-select
features=$(gum choose --no-limit "monitoring" "logging" "ingress" \
  --header "Select features:")

# Confirmation
gum confirm "Proceed with installation?" || exit 1

# Password/secret
passphrase=$(gum input --password --header "Disk encryption passphrase:")

# Filtered list (large dynamic lists)
disk=$(lsblk -dno NAME,SIZE,MODEL | gum filter --header "Select install disk:")
disk="/dev/$(echo "$disk" | awk '{print $1}')"
```

## Styling

```bash
# Banner
gum style --border double --padding "1 2" \
  --border-foreground "#0ff" --foreground "#0ff" \
  "NixOS Automated Installer"

# Status message
gum style --foreground "#0f0" --bold "Installation complete!"
```

## YAML Config Persistence

### Write config after prompts

```bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="/mnt/etc/nixos/site-config.yaml"

hostname=$(gum input --placeholder "node01" --header "Hostname:")
role=$(gum choose "server" "agent" --header "K3s role:")
ip=$(gum input --placeholder "10.0.0.10/24" --header "Static IP (CIDR):")
gateway=$(gum input --placeholder "10.0.0.1" --header "Gateway:")
token=$(gum input --password --header "Cluster token:")

cat > "$CONFIG_FILE" <<EOF
version: "1"
hostname: ${hostname}
role: ${role}
network:
  ip: ${ip}
  gateway: ${gateway}
cluster:
  token: ${token}
EOF

gum style --foreground "#0f0" "Config written to ${CONFIG_FILE}"
```

### Load existing config for upgrades

```bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="/etc/nixos/site-config.yaml"

if [[ -f "$CONFIG_FILE" ]]; then
  gum style --foreground "#ff0" "Existing config found — loading defaults"

  existing_hostname=$(yq '.hostname' "$CONFIG_FILE")
  existing_role=$(yq '.role' "$CONFIG_FILE")
  existing_ip=$(yq '.network.ip' "$CONFIG_FILE")

  # Pre-fill with existing values
  hostname=$(gum input --value "$existing_hostname" --header "Hostname:")
  role=$(gum choose "server" "agent" --header "K3s role:" \
    --selected "$existing_role")
  ip=$(gum input --value "$existing_ip" --header "Static IP (CIDR):")
else
  # Fresh install
  hostname=$(gum input --placeholder "node01" --header "Hostname:")
  role=$(gum choose "server" "agent" --header "K3s role:")
  ip=$(gum input --placeholder "10.0.0.10/24" --header "Static IP (CIDR):")
fi
```

### Config versioning

```bash
CONFIG_VERSION="2"

if [[ -f "$CONFIG_FILE" ]]; then
  file_version=$(yq '.version // "1"' "$CONFIG_FILE")
  if [[ "$file_version" != "$CONFIG_VERSION" ]]; then
    gum style --foreground "#ff0" \
      "Config v${file_version} → v${CONFIG_VERSION}: will prompt for new fields"
  fi
fi
```

## Example site-config.yaml Schema

```yaml
version: "2"
hostname: node01
role: server           # server | agent
network:
  ip: 10.0.0.10/24
  gateway: 10.0.0.1
  dns:
    - 10.0.0.1
    - 1.1.1.1
cluster:
  token: secret-token
  server_url: https://10.0.0.10:6443  # agent only
disk:
  device: /dev/sda
  encrypt: true
features:
  - monitoring
  - ingress
```

## Full Installer Script Pattern

```bash
#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="/tmp/site-config.yaml"

gum style --border double --padding "1 2" \
  --border-foreground "#0ff" "NixOS Automated Installer"

# Load existing config if upgrading
[[ -f /etc/nixos/site-config.yaml ]] && cp /etc/nixos/site-config.yaml "$CONFIG_FILE"

# Collect (pre-fill from existing config if available)
# ... prompts per patterns above ...

# Review and confirm
gum style --border rounded --padding "1 2" "$(yq '.' "$CONFIG_FILE")"
gum confirm "Apply this configuration?" || exit 1

# Partition, mount, install
mkdir -p /mnt/etc/nixos
cp "$CONFIG_FILE" /mnt/etc/nixos/site-config.yaml
nixos-install --flake /opt/flake#"$(yq '.hostname' "$CONFIG_FILE")" --no-root-passwd

gum style --foreground "#0f0" --bold "Installation complete!"
gum confirm "Reboot now?" && reboot
```

## Other Charm Tools

| Tool | Nix Package | Use |
|------|-------------|-----|
| `glow` | `pkgs.glow` | Render markdown in terminal (show install docs) |
| `vhs` | `pkgs.vhs` | Record terminal GIFs (document installer flow) |
| `freeze` | `pkgs.charm-freeze` | Screenshot terminal output |
