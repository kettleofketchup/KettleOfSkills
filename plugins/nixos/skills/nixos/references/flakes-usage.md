# Flakes: Module Arguments, Commands & Lockfiles

Split out of `flakes.md`; see it for the preceding sections.

## Passing Extra Arguments to Modules

```nix
outputs = { self, nixpkgs, ... }: {
  nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
    system = "x86_64-linux";
    specialArgs = {
      # Available in all modules as function arguments
      myCustomArg = "value";
      inherit self;
    };
    modules = [ ./configuration.nix ];
  };
};

# In configuration.nix
{ config, pkgs, myCustomArg, self, ... }:
{
  # Use myCustomArg and self here
}
```

## Commands

```bash
# Show flake outputs
nix flake show
nix flake show github:owner/repo

# Check flake validity
nix flake check

# Update all inputs
nix flake update

# Update specific input
nix flake lock --update-input nixpkgs

# Build outputs
nix build .#packageName
nix build .#nixosConfigurations.hostname.config.system.build.toplevel

# Enter devShell
nix develop
nix develop .#shellName

# Run apps
nix run .#appName

# Create new flake from template
nix flake init -t templates#name

# Show flake metadata
nix flake metadata

# Lock without building
nix flake lock
```

## flake.lock

The lock file pins exact revisions. Key fields:

```json
{
  "nodes": {
    "nixpkgs": {
      "locked": {
        "lastModified": 1234567890,
        "narHash": "sha256-...",
        "owner": "NixOS",
        "repo": "nixpkgs",
        "rev": "abc123...",
        "type": "github"
      }
    }
  }
}
```

## Private Repositories

See `references/private-repos.md` for comprehensive guide. Key points:

- `git+ssh://` input fetching runs as the **calling user** (not nix daemon)
- Developer machines: SSH works via `~/.ssh/` automatically
- CI runners: Need `GIT_SSH_COMMAND` with absolute paths to SSH config
- `--override-input path:` produces **different derivation hashes** than `git+ssh://` — avoid on CI

```nix
inputs = {
  # Private repo via SSH
  myflake.url = "git+ssh://git@gitlab.example.com/group/repo.git";
  myflake.inputs.nixpkgs.follows = "nixpkgs";

  # Private repo via HTTPS + access-token
  myflake.url = "git+https://gitlab.example.com/group/repo.git";
};
```

## Common Issues

### Input not found
Ensure flake has `git add flake.nix flake.lock` - untracked files ignored.

### Dirty tree warning
Commit or stage changes, or use `--impure` flag.

### Infinite recursion
Usually from accessing config values before they're defined. Use `lib.mkIf` for conditional config.

### Hash mismatch
Update hash with: `nix build 2>&1 | grep 'got:' | awk '{print $2}'`

### SSH "Permission denied" on CI
fetchGit runs as the CI job user, not root. Ensure `GIT_SSH_COMMAND` is set (not unset in before_script) and points to an SSH config with the deploy key. See `references/private-repos.md`.
