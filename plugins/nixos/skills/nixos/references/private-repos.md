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

Continued in `private-repos-auth.md`.
