---
name: nextcloud
description: Use when deploying Nextcloud on Kubernetes with Helm, configuring Rook-Ceph storage, Traefik ingress, Authentik SAML SSO, Collabora CODE office suite, PostgreSQL/Redis subcharts, ArgoCD GitOps, or troubleshooting Nextcloud day-2 operations (upgrades, backups, occ commands, cron jobs, trusted domains/proxies).
---

# Nextcloud on Kubernetes

Self-hosted Nextcloud deployment on Kubernetes using the official Helm chart with PostgreSQL, Redis, Rook-Ceph storage, Traefik ingress, Authentik SAML SSO, and Collabora CODE.

## Stack

| Component | Solution | License |
|-----------|----------|---------|
| Nextcloud | Official Helm chart `nextcloud/nextcloud` | AGPL v3 |
| Database | PostgreSQL (Bitnami subchart) | PostgreSQL License |
| Cache/Locking | Redis (Bitnami subchart) | BSD-3 |
| Storage | Rook-Ceph (`ceph-block` RWO, `ceph-filesystem` RWX) | Apache 2.0 |
| Ingress | Traefik IngressRoute CRD | MIT |
| SSO | Authentik SAML (free tier, unlimited users) | MIT |
| Office | Collabora CODE (bundled subchart) | MPL-2.0 |
| GitOps | ArgoCD app-of-apps | Apache 2.0 |

## Helm Chart

```bash
helm repo add nextcloud https://nextcloud.github.io/helm/
# Chart: nextcloud/nextcloud (v8.9+, app v32+)
# Requires: Kubernetes 1.24+, Helm 3.7.0+
```

## Deployment Workflow

1. Create namespace and secrets (admin password, PostgreSQL, Redis, Collabora)
2. Write `values.yaml` -- see references/deployment.md for full values template
3. Create ArgoCD Application -- see references/deployment.md
4. Sync and wait for first boot (2-5 min for DB migrations)
5. Configure Authentik SAML -- see references/authentik-saml.md
6. Enable Nextcloud apps -- see references/apps-config.md

## Quick Reference

| Task | Reference |
|------|-----------|
| Full Helm values template | references/deployment.md |
| Authentik SAML SSO setup | references/authentik-saml.md |
| App configuration (Calendar, Contacts, Talk, Collabora) | references/apps-config.md |
| Upgrades, backups, occ commands, troubleshooting | references/day2-operations.md |

## Critical Gotchas

- **trusted_proxies**: MUST include pod CIDR and node network or Nextcloud rejects forwarded headers
- **Redis required**: Without Redis, file locking uses DB and causes deadlocks under load
- **Cron**: Enable sidecar cron or background jobs fall back to AJAX (performance disaster)
- **Sequential upgrades only**: Nextcloud requires 28->29->30, NOT 28->30
- **SAML + encryption**: NEVER use SAML with Nextcloud server-side encryption (irrevocable data loss)
- **First boot probes**: Default `initialDelaySeconds: 10` is too low; use startupProbe with 5min timeout
- **Deployment strategy**: Must use `Recreate` with RWO volumes (default); `RollingUpdate` only with RWX + sticky sessions
- **phpClientHttpsFix**: Enable when Traefik terminates TLS or internal URLs break

## Common Mistakes

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Access through untrusted domain" | Missing trusted_proxies or trustedDomains | Add pod/node CIDRs to trusted_proxies config |
| Login redirect loop | overwriteprotocol not set behind TLS proxy | Set `phpClientHttpsFix.enabled: true` |
| Slow background jobs | Cron not enabled, using AJAX mode | Enable `cronjob.enabled` with sidecar |
| File lock timeout errors | No Redis, using DB locking | Enable Redis subchart |
| Pod stuck in CrashLoop on upgrade | Major version skip | Restore backup, upgrade sequentially |
| Collabora "WOPI host not allowed" | aliasgroups misconfigured | Set aliasgroups host to Nextcloud external URL |
