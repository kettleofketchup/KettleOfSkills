---
name: coder
last_updated: 2026-08-07
version: chart 2.34.0 (mainline), 2.33.6 (stable); terraform-provider-coder v2.x
description: Self-hosted Coder cloud dev environments. Use for Helm/Kubernetes deploys, OIDC/Authentik SSO, IdP group-role sync, RBAC, Terraform workspace templates, provisioners, prebuilds, or workspace proxies.
---

# Coder

Self-hosted platform provisioning developer workspaces from Terraform templates. A `coderd` control plane
authenticates users and schedules builds; a `coder_agent` inside each workspace tunnels SSH, IDEs, and apps back.

## Mental Model

```
coderd (Helm release)  ──► PostgreSQL (required, external in prod)
   │                   ──► provisioner daemons (built-in or external) ──► terraform apply
   │                                                                        │
   └── OIDC (Authentik) ── users/groups/roles                               ▼
                                                          workspace pod/VM + coder_agent
                                                          └─ coder_app (code-server, JetBrains…)
```

Three things must agree or nothing works: `CODER_ACCESS_URL` (what agents dial home to),
`CODER_WILDCARD_ACCESS_URL` (per-app subdomains), and the TLS cert covering both.

## Quick Start (Kubernetes)

```bash
kubectl create namespace coder
kubectl create secret generic coder-db-url -n coder \
  --from-literal=url="postgres://coder:coder@postgres.coder.svc.cluster.local:5432/coder?sslmode=disable"

helm repo add coder-v2 https://helm.coder.com/v2 && helm repo update
helm install coder coder-v2/coder -n coder -f values.yaml --version 2.34.0
```

Minimum `values.yaml`:

```yaml
coder:
  env:
    - name: CODER_PG_CONNECTION_URL
      valueFrom: { secretKeyRef: { name: coder-db-url, key: url } }
    - name: CODER_ACCESS_URL
      value: "https://coder.example.com"
    - name: CODER_WILDCARD_ACCESS_URL
      value: "*.coder.example.com"
    - name: CODER_OAUTH2_GITHUB_DEFAULT_PROVIDER_ENABLE
      value: "false"
```

Stable channel via OCI: `helm install coder oci://ghcr.io/coder/chart/coder --version 2.33.6`.

## Reference Index

### Deployment & Operations
- [Helm & Kubernetes](references/helm-deploy.md) — chart values, PostgreSQL, ingress/TLS, HA, upgrades, air-gap
- [Networking](references/networking.md) — access URLs, wildcard apps, workspace proxies, TLS termination
- [Provisioners](references/provisioners.md) — built-in vs external, provisioner keys, tags, `coder-provisioner` chart
- [CLI & Day-2 Ops](references/cli-ops.md) — essential commands, template lifecycle, debugging builds

### Authentication & Access
- [OIDC Authentication](references/oidc-auth.md) — every `CODER_OIDC_*` variable, claim mapping, troubleshooting
- [Authentik Integration](references/authentik-oidc.md) — concrete Authentik provider + Coder wiring, group claims
- [IdP Sync & RBAC](references/idp-sync-rbac.md) — group/role/org sync JSON, built-in roles, custom roles
- [External Auth](references/external-auth.md) — git provider token passthrough into workspaces

### Templates & Workspaces
- [Terraform Provider](references/templates-terraform.md) — every resource/data source with schema cheat sheet
- [Registry Modules](references/modules.md) — `registry.coder.com` modules for IDEs, git, dotfiles, agents
- [Kubernetes Template](references/template-kubernetes.md) — complete working workspace template
- [Scheduling & Quotas](references/scheduling-quotas.md) — autostop, dormancy, credit budgets, cost control
- [Parameters](references/parameters.md) — `coder_parameter` arguments, validation, ephemeral, list types
- [Presets & Prebuilds](references/presets-prebuilds.md) — parameter bundles, warm pools, claim semantics
- [AI Agents in Workspaces](references/ai-tasks.md) — `coder_ai_task`, `coder_external_agent`, running OpenHands

## Critical Rules

**Never let the built-in provisioner touch production infra.** It runs inside the `coderd` pod with the chart's
service account. Use external provisioners with scoped keys so template Terraform can't reach the control plane's
credentials. → `references/provisioners.md`

**Templates are Terraform, but not ordinary Terraform.** Every resource that should disappear when a workspace
stops needs `count = data.coder_workspace.me.start_count`. Persistent volumes must NOT have that count, or
you delete user data on every stop.

**The agent needs two injected values**: `coder_agent.main.init_script` as the container command and
`CODER_AGENT_TOKEN=coder_agent.main.token` as an env var. Omitting either produces a workspace that builds
successfully and then never connects.

**Groups/roles sync only on login.** Changing an Authentik group does nothing until the user re-authenticates.

**Pin the chart version.** `helm upgrade` without `--version` jumps to mainline. Coder ships mainline and stable
channels; run stable unless you need a specific new feature.

## Version Channels

| Channel | Chart | Use |
|---------|-------|-----|
| Stable | `oci://ghcr.io/coder/chart/coder` (2.33.6) | Production |
| Mainline | `coder-v2/coder` (2.34.0) | New features, monthly cadence |

Premium-licensed features: HA (`replicaCount > 1`), prebuilds, organizations, custom roles, workspace proxies,
role sync, audit log. OSS covers OIDC login, group sync, templates, external provisioners.

## Common Failure Modes

| Symptom | Cause |
|---------|-------|
| Workspace builds, agent never connects | `CODER_ACCESS_URL` unreachable from workspace network, or missing `CODER_AGENT_TOKEN` |
| Apps 404 on subdomain | `CODER_WILDCARD_ACCESS_URL` unset or wildcard DNS/TLS cert missing |
| OIDC login creates duplicate users | `CODER_OIDC_USERNAME_FIELD` claim not stable; use `preferred_username` or `sub` |
| `template push` fails to provision | No provisioner matching the template's tags |
| Groups empty after login | `CODER_OIDC_GROUP_FIELD` unset, or claim not in ID token — check `CODER_LOG_FILTER=".*got oidc claims.*"` |
| PVC deleted on workspace stop | `count = start_count` wrongly applied to the PVC resource |
