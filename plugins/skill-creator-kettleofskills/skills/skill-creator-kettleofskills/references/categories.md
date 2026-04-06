# Valid Categories

Every skill's `config.yaml` lists categories from this table. Skills can belong to multiple categories.
Every skill is automatically added to `all` -- never list `all` in config.yaml.

| Category | Description | Example Skills |
|----------|-------------|----------------|
| `k8s-core` | Kubernetes core infrastructure | helm, kustomize, argocd, k3s, talos, calico, cert-manager, traefik, kubectx |
| `k8s-storage` | Kubernetes storage | rook-ceph, cloudnative-pg |
| `k8s-apps` | Kubernetes applications | authentik, cloudflare, nextcloud, grafana, opentelemetry, openwebui |
| `homelab` | Homelab infrastructure | nixos, vsphere, k3s, talos, pikvm, grafana, traefik |
| `devops` | DevOps tooling | docker, github, gitlab-ci, goss, helm, argocd, just |
| `frontend` | Frontend development | react, zustand, ui-styling, playwright, svg-logo-designer |
| `golang` | Go development | golang-viper, go-dota2-steam, wails |
| `docs` | Documentation tools | mkdocs-documentation, mermaidjs-v11, zensical, documentation-reviewer |
| `claude-tooling` | Claude Code tooling | claude-code, context-engineering, mcp-management, skill-creator |
| `shell` | Shell tooling | zinit-zsh, zsh-completions |
| `discord` | Discord bot development | discord |

## config.yaml Format

```yaml
categories:
  - k8s-core
  - devops
```

## Adding a New Category

To add a new category, update the `group_descriptions` associative array in **both** the
`sync-groups` and `sync-marketplace` recipes in the root `justfile`. Also add the group name
to the `GROUPS_CSV` variable in `sync-marketplace`.

After adding, run `just sync` to generate the new group plugin directory.
