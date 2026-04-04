---
name: kubectx
description: "kubectx and kubens CLI tools for switching Kubernetes contexts and namespaces. This skill should be used when switching kubectl contexts, switching Kubernetes namespaces, listing available contexts or namespaces, renaming or deleting contexts, setting up kubectx/kubens with fzf interactive selection, configuring shell completions for kubectx/kubens, integrating kube-ps1 shell prompts, managing multiple kubeconfig files via KUBECONFIG env var, or troubleshooting context/namespace switching issues."
last_updated: 2026-03-18
---

# kubectx & kubens

CLI tools by ahmetb for fast Kubernetes context and namespace switching. Written in Go, single binaries. Both support fzf for interactive fuzzy selection.

## Installation

```bash
# Homebrew (macOS/Linux)
brew install kubectx

# Arch
pacman -S kubectx

# Manual binary
curl -Lo kubectx https://github.com/ahmetb/kubectx/releases/latest/download/kubectx
curl -Lo kubens https://github.com/ahmetb/kubectx/releases/latest/download/kubens
chmod +x kubectx kubens && mv kubectx kubens /usr/local/bin/

# With fzf (enables interactive mode automatically)
brew install fzf
```

## kubectx - Context Switching

```bash
kubectx                     # List all contexts (current highlighted)
kubectx <name>              # Switch to context
kubectx -                   # Switch to previous context (toggle)
kubectx -c                  # Show current context name
kubectx <new>=<old>         # Rename context
kubectx -d <name>           # Delete context
kubectx -d <name1> <name2>  # Delete multiple contexts
kubectx -u                  # Unset current context
```

With fzf installed, bare `kubectx` opens interactive fuzzy finder instead of listing.

## kubens - Namespace Switching

```bash
kubens                      # List all namespaces (current highlighted)
kubens <name>               # Switch to namespace
kubens -                    # Switch to previous namespace (toggle)
kubens -c                   # Show current namespace
```

With fzf installed, bare `kubens` opens interactive fuzzy finder instead of listing.

## How It Works

- kubectx modifies `~/.kube/config` (or file(s) in `$KUBECONFIG`)
- Equivalent to `kubectl config use-context <name>`
- kubens sets namespace in current context's config
- Equivalent to `kubectl config set-context --current --namespace=<name>`
- The `-` toggle stores previous selection in `~/.kube/kubectx` and `~/.kube/kubens`

## KUBECONFIG with Multiple Files

```bash
# Merge multiple kubeconfig files
export KUBECONFIG=~/.kube/config:~/.kube/cluster-a:~/.kube/cluster-b

# kubectx sees all contexts across all files
kubectx    # lists contexts from all kubeconfig files
```

When `KUBECONFIG` contains multiple files, kubectx operates across all of them. Changes are written to the first file in the list that contains the modified context.

## Common Patterns

### Quick Context+Namespace Switch

```bash
kubectx production && kubens monitoring
```

### Scripting (Non-Interactive)

```bash
# Force non-interactive even with fzf installed
KUBECTX_IGNORE_FZF=1 kubectx my-cluster
KUBECTX_IGNORE_FZF=1 kubens kube-system

# Use in scripts
current=$(kubectx -c)
kubectx staging
# ... do work ...
kubectx "$current"  # restore
```

### Context Naming Convention

```bash
# Rename long auto-generated names to short memorable ones
kubectx prod=arn:aws:eks:us-east-1:123456:cluster/production
kubectx staging=gke_myproject_us-central1_staging
kubectx homelab=kubernetes-admin@homelab
```

## Reference Files

| File | Content |
|------|---------|
| `references/shell-integration.md` | zsh/bash completions, kube-ps1 prompt, fzf config, zinit setup |

## Cross-References

- **K3s clusters**: Use `k3s` skill for cluster setup, then kubectx to manage contexts
- **Shell config**: Use `zinit-zsh` skill for plugin installation in this dotfiles repo
