# Private Git Repositories in Nix Flakes

## Architecture: Who Fetches What

Understanding which process fetches git repos is critical for debugging auth issues.

```
┌─────────────────────────────────────────────────────┐
│  nix build .#package                                │
│                                                     │
│  Phase 1: EVALUATION (client process)               │
│  ├── Runs as: THE CALLING USER (not root, not nix)  │
│  ├── Resolves flake inputs (flake.lock)             │
│  ├── builtins.fetchGit → calls git binary           │
│  ├── git uses SSH → reads $GIT_SSH_COMMAND or       │
│  │   ~/.ssh/config from the calling user            │
│  └── This is where git+ssh:// auth happens          │
│                                                     │
│  Phase 2: BUILD (nix daemon)                        │
│  ├── Runs as: nixbld users (sandboxed)              │
│  ├── Builds derivations                             │
│  ├── NO network access (sandbox)                    │
│  └── pkgs.fetchgit runs here (needs hash, no SSH)   │
└─────────────────────────────────────────────────────┘
```

**Key distinction:**
- `builtins.fetchGit` / flake input resolution = **evaluation-time**, client-side, calling user's credentials
- `pkgs.fetchgit` (from nixpkgs) = **build-time**, sandboxed, nixbld user, no SSH access

## Input URL Formats for Private Repos

```nix
inputs = {
  # SSH (recommended for private repos)
  myflake.url = "git+ssh://git@gitlab.example.com/group/repo.git";

  # HTTPS with token (alternative)
  myflake.url = "git+https://gitlab.example.com/group/repo.git";

  # With specific branch
  myflake.url = "git+ssh://git@gitlab.example.com/group/repo.git?ref=main";

  # With specific revision
  myflake.url = "git+ssh://git@gitlab.example.com/group/repo.git?rev=abc123";
};
```

## SSH Authentication Setup

### Developer Machine

SSH just works — the evaluator runs as your user with access to `~/.ssh/`:

```bash
# Standard SSH key setup
ssh-keygen -t ed25519 -C "dev@example.com"
# Add public key to GitLab/GitHub as deploy key

# Test
nix flake show git+ssh://git@gitlab.example.com/group/repo.git
```

### sudo nixos-rebuild

When using `sudo`, the evaluator runs as **root**. Two options:

**Option A: Use `--use-remote-sudo`** (preferred)
```bash
# Evaluates as YOUR user (SSH works), elevates only for activation
nixos-rebuild switch --use-remote-sudo --flake .#hostname
```

**Option B: Preserve SSH agent through sudo**
```nix
# configuration.nix
security.sudo.extraConfig = ''
  Defaults env_keep+=SSH_AUTH_SOCK
'';
```

**Option C: Deploy key in /root/.ssh/**
```bash
sudo cp ~/.ssh/id_ed25519 /root/.ssh/
sudo chmod 600 /root/.ssh/id_ed25519
```

### CI/CD Runner (GitLab, GitHub Actions, etc.)

The CI job process runs `nix build` as the runner user. SSH must work for **that user**.

#### NixOS GitLab Runner with SSH Deploy Key

```nix
# gitlab-runner/configuration.nix

# 1. Static user (DynamicUser breaks SSH key pre-provisioning)
users.users.gitlab-runner = {
  isSystemUser = true;
  group = "gitlab-runner";
  home = "/var/lib/gitlab-runner";
};
users.groups.gitlab-runner = {};

# 2. Decrypt SSH key from sops
sops.secrets.gitlab_runner_ssh_key = {
  sopsFile = ./secrets.yml;
  owner = "root";
};

# 3. Setup service: deploy SSH key + config before runner starts
systemd.services.gitlab-ssh-setup = {
  description = "Setup SSH keys for GitLab Runner";
  wantedBy = [ "multi-user.target" ];
  before = [ "gitlab-runner.service" ];
  after = [ "sops-install-secrets.service" ];
  serviceConfig = {
    Type = "oneshot";
    RemainAfterExit = true;
  };
  script = ''
    # gitlab-runner's SSH (for fetchGit during evaluation)
    mkdir -p /var/lib/gitlab-runner/.ssh
    install -m 600 /run/secrets/gitlab_runner_ssh_key \
      /var/lib/gitlab-runner/.ssh/deploy-key
    cat > /var/lib/gitlab-runner/.ssh/config << 'EOF'
    Host gitlab.example.com
      IdentityFile /var/lib/gitlab-runner/.ssh/deploy-key
      StrictHostKeyChecking accept-new
    EOF
    chmod 600 /var/lib/gitlab-runner/.ssh/config
    chown -R gitlab-runner:gitlab-runner /var/lib/gitlab-runner/.ssh
  '';
};

# 4. GIT_SSH_COMMAND on the runner service
# Critical for DynamicUser/namespace isolation — bypasses ~ resolution
systemd.services.gitlab-runner.environment = {
  GIT_SSH_COMMAND = "ssh -F /var/lib/gitlab-runner/.ssh/config -o UserKnownHostsFile=/var/lib/gitlab-runner/.ssh/known_hosts";
};
```

#### CI Template (before_script)

**Do NOT unset `GIT_SSH_COMMAND`** in CI templates. The evaluator (fetchGit) runs as the CI job user and needs it to find SSH credentials:

```yaml
# WRONG — breaks fetchGit SSH auth
.nix-base:
  before_script:
    - unset GIT_SSH_COMMAND  # DON'T DO THIS

# CORRECT — keep GIT_SSH_COMMAND from service environment
.nix-base:
  before_script:
    - export GIT_CONFIG_GLOBAL="$CI_PROJECT_DIR/.gitconfig"
    - truncate -s0 "$GIT_CONFIG_GLOBAL" 2>/dev/null || true
    # GIT_SSH_COMMAND inherited from service — do not unset
```

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
