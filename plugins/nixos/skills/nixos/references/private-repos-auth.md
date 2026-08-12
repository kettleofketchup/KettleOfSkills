# Private Repos: HTTPS Tokens & Input Overrides

Split out of `private-repos.md`; see it for the preceding sections.

## HTTPS + Access Tokens (Alternative to SSH)

Avoids SSH entirely. Good for environments where SSH is difficult.

### nix.conf access-tokens

```nix
# configuration.nix
nix.settings.access-tokens = [
  "gitlab.example.com=glpat-XXXXXXXXXXXXX"
];
```

Or for type-prefixed tokens:
```
access-tokens = gitlab.example.com=type:PAT:glpat-XXXXXXXXXXXXX
```

### Git URL Rewriting (Hybrid)

Keep `git+ssh://` in flake.nix but use HTTPS on CI:
```bash
git config --global url."https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.example.com/".insteadOf "git@gitlab.example.com:"
```

## --override-input: When and Why

`--override-input` replaces a flake input with a local path at evaluation time:

```bash
nix build .#package \
  --override-input myflake path:./local-checkout
```

### When to Use
- **Local development**: Test changes to a dependency without pushing
- **Broken SSH on CI**: Bypass fetchGit entirely using checked-out submodules

### When NOT to Use
- **Production CI builds**: `path:` inputs produce different derivation hashes than `git+ssh://` inputs (different narHash, timestamps). This breaks binary cache sharing between CI and local machines.

### The Hash Divergence Problem

```
flake.lock input:
  git+ssh://gitlab.example.com/repo?rev=abc123
  narHash: sha256-AAAA...

--override-input:
  path:./repo?lastModified=1234&narHash=sha256-BBBB...

Same content, DIFFERENT hashes → DIFFERENT derivations → cache miss
```

This means:
- Packages built on CI with `--override-input` won't be found by local `nix build`
- ISO derivation hashes differ between CI and local, breaking deployment automation
- Binary cache (Attic/Cachix) hits fail

**Fix: Make SSH work on CI** so `--override-input` is unnecessary.

## DynamicUser and Namespace Isolation

systemd's `DynamicUser=true` creates problems for SSH:

| Issue | Cause | Fix |
|-------|-------|-----|
| `~/.ssh/config` not found | `~` resolves to `/` or tmpdir | Use `GIT_SSH_COMMAND` with absolute paths |
| Permission denied on SSH key | Namespace isolation hides files | Use `StateDirectory` + pre-provisioning service |
| known_hosts not found | Ephemeral home, no persistent state | Explicit `-o UserKnownHostsFile=` |

**Best practice**: Create a static system user and use `GIT_SSH_COMMAND` with absolute paths.

## Debugging SSH Issues

```bash
# Test SSH from the runner user's perspective
sudo -u gitlab-runner GIT_SSH_COMMAND="ssh -vvv -F /var/lib/gitlab-runner/.ssh/config" \
  git ls-remote git@gitlab.example.com:group/repo.git

# Check what user nix evaluates as
nix eval --expr 'builtins.getEnv "USER"'

# Verify SSH key is accessible
sudo -u gitlab-runner ls -la /var/lib/gitlab-runner/.ssh/

# Test fetchGit directly
nix eval --expr 'builtins.fetchGit { url = "git+ssh://git@gitlab.example.com/group/repo.git"; }'

# Check GIT_SSH_COMMAND is set in CI
echo $GIT_SSH_COMMAND
```

## Troubleshooting

### "Permission denied" on SSH config/key
- fetchGit runs as the **calling user**, not root
- Check `GIT_SSH_COMMAND` is set and points to accessible files
- If using DynamicUser, `~/.ssh/` won't work — use absolute paths

### "Host key verification failed"
- SSH connects but can't verify host key
- Set `StrictHostKeyChecking accept-new` in SSH config
- Or use explicit `-o UserKnownHostsFile=` with a pre-populated file
- Run `ssh-keyscan gitlab.example.com >> /path/to/known_hosts` in setup service

### Derivation hash mismatch between CI and local
- CI likely using `--override-input path:` which produces different hashes
- Fix: Make SSH work on CI so flake.lock inputs resolve identically
- Verify: `nix path-info --derivation .#package` should match on both

### "error: unable to download 'git+ssh://...': ... (255)"
- Generic git/SSH failure. Add `-vvv` to SSH for details:
  ```bash
  GIT_SSH_COMMAND="ssh -vvv" nix build .#package
  ```

### fetchGit works locally but fails on CI
- Different user context (your user vs gitlab-runner)
- Check: `whoami` in CI job, verify SSH key accessible to that user
- Check: `GIT_SSH_COMMAND` env var is set (not unset by before_script)
