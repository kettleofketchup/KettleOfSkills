# CI/CD Catalog: Runner Gotchas, Verification, and Failure Recovery

Continuation of [cicd-catalog-publishing.md](cicd-catalog-publishing.md).

## Heterogeneous runner gotchas

Self-managed GitLab fleets often mix executor types. Behaviors that bit during `inf/s3-sync` setup:

| Symptom | Cause | Fix |
|---|---|---|
| `bash: yamllint: command not found` | Job landed on shell executor; `image:` ignored | Dual-mode script (`command -v yamllint \|\| nix shell`) |
| `No module named pip` | NixOS shell executor; Python has no pip | Use `nix shell nixpkgs#<pkg> --command ...` |
| `release-cli: not found` | Docker executor with default `docker:latest`; no release-cli | Explicit `image: registry.gitlab.com/gitlab-org/release-cli:latest` |
| `Permission denied` on `/etc/ssl/certs` | Shell executor host file is read-only | Use temp bundle + `SSL_CERT_FILE` env var |
| `x509: certificate signed by unknown authority` | release-cli's glab doesn't trust org CA | Inject CA into temp bundle + `export SSL_CERT_FILE` BEFORE `release:` step |

## Verifying publication

After tagging `vX.Y.Z`, check:

1. **GitLab Release exists:** `GET /api/v4/projects/<id>/releases` — should list `tag_name: vX.Y.Z`

2. **Component resolves via `include:`:**
   ```
   POST /api/v4/projects/<id>/ci/lint
   {"content":"include:\n  - component: <server>/<project-path>/<name>@<version>\n    inputs: {...}\nstages: [deploy]\n"}
   ```
   Response `valid: true` is the real source of truth. Catalog browse API may 404 on some tiers while `include: component:` still works.

3. **Catalog browse (may 404 on some tiers):**
   ```
   GET /api/v4/ci/catalog/resources
   GET /api/v4/ci/catalog/resources/<encoded-path>
   ```

## Failure recovery: bad first publish

If publish-component fails AFTER creating the git tag but BEFORE landing a GitLab Release:

1. Fix the `.gitlab-ci.yml` issue, commit, push to main.
2. Force-retag the same version at the fixed commit:
   ```bash
   git tag -d vX.Y.Z
   git push origin :refs/tags/vX.Y.Z
   git tag -a vX.Y.Z -m "<reason>" <commit>
   git push origin vX.Y.Z
   ```

This works only when no Release was created yet. Once a Release exists, cut `vX.Y.Z+1` instead — consumers may have pinned to the version.

If the Release IS created but catalog resource doesn't appear (catalog flag was off), cut `vX.Y.Z+1` after enabling the flag.
