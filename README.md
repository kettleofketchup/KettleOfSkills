# kettleofskills

A Claude Code marketplace that packages curated skills as individually installable plugins and grouped bundles. Install exactly the skills you need, or grab a themed bundle to get productive fast.

## Install

```bash
# Add the marketplace (one-time)
/plugin marketplace add kettleofketchup/kettleofskills

# Install everything
/plugin install all@kettleofskills

# Install a group
/plugin install k8s-core@kettleofskills

# Install a single skill
/plugin install helm@kettleofskills
```

## Group plugins

| Plugin | Description | Skills |
|--------|-------------|--------|
| `all` | Everything | 47 skills |
| `k8s-core` | Kubernetes core infrastructure | helm, kustomize, argocd, k3s, talos, calico, cert-manager, traefik, kubectx |
| `k8s-storage` | Kubernetes storage | rook-ceph, cloudnative-pg |
| `k8s-apps` | Kubernetes applications | authentik, cloudflare, nextcloud, grafana, opentelemetry, openwebui, copyparty, foundry-vtt, dicebear, traefik, cert-manager, helm, kustomize, argocd |
| `homelab` | Homelab infrastructure | nixos, vsphere, k3s, talos, pikvm, kubectx, rook-ceph, cloudnative-pg, grafana, traefik, cert-manager, authentik, cloudflare |
| `devops` | DevOps tooling | docker, github, gitlab-ci, gitlab-tickets, goss, kustomize, helm, argocd, just |
| `frontend` | Frontend development | react, zustand, ui-styling, playwright, svg-logo-designer |
| `golang` | Go development | golang-viper, go-dota2-steam, wails |
| `docs` | Documentation | mkdocs-documentation, documentation-reviewer, mermaidjs-v11, zensical |
| `claude-tooling` | Claude Code tooling | claude-code, context-engineering, mcp-management, skill-creator |
| `shell` | Shell tooling | zinit-zsh, zsh-completions |
| `discord` | Discord bot development | discord |

## Individual skills

| Skill | Description |
|-------|-------------|
| `argocd` | GitOps continuous delivery for Kubernetes with ArgoCD |
| `authentik` | Self-hosted identity provider for Kubernetes |
| `calico` | Calico CNI and network policy engine via Tigera Operator |
| `cert-manager` | Kubernetes certificate management and debugging |
| `claude-code` | Claude Code CLI features, setup, and integration |
| `cloudflare` | Cloudflare Tunnel deployment, Access tokens, and DNS management |
| `cloudnative-pg` | CloudNativePG (CNPG) Kubernetes operator for PostgreSQL |
| `context-engineering` | Context engineering for AI agent systems |
| `copyparty` | Portable file server with resumable uploads, dedup, and WebDAV |
| `dicebear` | DiceBear avatar generation and Gravatar API integration |
| `discord` | Discord API, slash commands, components, webhooks, and embeds |
| `docker` | Dockerfile optimization, multi-stage builds, and Compose |
| `documentation-reviewer` | Review and update MkDocs documentation when code changes |
| `foundry-vtt` | Foundry VTT virtual tabletop development and module creation |
| `github` | GitHub CLI (gh) and GitHub Actions workflow development |
| `gitlab-ci` | GitLab CI/CD multi-project pipeline orchestration |
| `gitlab-tickets` | Create GitLab issues through conversational brainstorming |
| `go-dota2-steam` | Go libraries for Steam and Dota 2 Game Coordinator |
| `golang-viper` | Go Viper configuration library |
| `goss` | Goss YAML-based server validation and testing |
| `grafana` | Grafana observability stack with kube-prometheus-stack |
| `helm` | Kubernetes package management with Helm |
| `just` | Just command runner for task automation |
| `k3s` | K3s lightweight Kubernetes distribution |
| `kubectx` | kubectx and kubens for switching Kubernetes contexts and namespaces |
| `kustomize` | Kustomize Kubernetes manifest composition without templating |
| `mcp-management` | Discover and manage Model Context Protocol (MCP) servers |
| `mermaidjs-v11` | Diagrams and visualizations with Mermaid.js v11 syntax |
| `mkdocs-documentation` | MkDocs Material documentation management |
| `nextcloud` | Nextcloud deployment on Kubernetes with Helm and SSO |
| `nixos` | NixOS and Nix flake development |
| `opentelemetry` | OpenTelemetry distributed tracing, metrics, and log correlation |
| `openwebui` | Open WebUI self-hosted AI chat interface |
| `pikvm` | PiKVM HTTP API Python library and Ansible modules |
| `playwright` | Playwright browser automation for E2E testing and scraping |
| `react` | React 19 with async components, Server Components, and modern patterns |
| `rook-ceph` | Multi-node Rook Ceph deployment for Kubernetes |
| `skill-creator` | Guide for creating effective Claude Code skills |
| `svg-logo-designer` | Create professional SVG logos from descriptions |
| `talos` | Talos Linux Kubernetes operating system management |
| `traefik` | Traefik v3 reverse proxy and load balancer |
| `ui-styling` | UI development with shadcn/ui, Tailwind CSS, and Radix UI |
| `vsphere` | VMware vSphere management with govc CLI and Ansible |
| `wails` | Wails v2 Go desktop application framework |
| `zensical` | Zensical static site generator for project documentation |
| `zinit-zsh` | Zinit zsh plugin manager configuration and binary installs |
| `zsh-completions` | Write zsh completion scripts with descriptions and colors |
| `zustand` | Zustand state management for React applications |

## Maintenance

After adding new skills, updating categories, or changing `config.yaml` files:

```bash
# Regenerate everything (groups + marketplace.json)
just sync

# Or run steps individually
just sync-groups       # regenerate group symlinks
just sync-marketplace  # regenerate marketplace.json
```

## Structure

Each individual skill lives in its own plugin directory:

```
plugins/<name>/
  skills/
    <name>/
      SKILL.md          # skill content (markdown with frontmatter)
      config.yaml       # categories this skill belongs to
      references/       # optional reference files
```

The `config.yaml` declares which groups a skill belongs to:

```yaml
categories:
  - k8s-core
  - devops
```

Group plugins (like `k8s-core`, `homelab`, `all`) are directories under `plugins/` that contain only symlinks in their `skills/` folder, pointing back to the individual skill directories. Running `just sync-groups` reads every skill's `config.yaml` and rebuilds these symlinks. Running `just sync-marketplace` regenerates `.claude-plugin/marketplace.json` from all plugin directories.

## License

[MIT](LICENSE)
