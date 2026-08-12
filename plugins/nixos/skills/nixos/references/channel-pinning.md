# Channel pinning & nixpkgs upgrades

## Why pin (the failure mode)

`nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable"` (or any bare BRANCH ref) is
a FLOATING input. `nix flake update` — which release/version recipes often run
automatically — re-resolves the branch to its latest tip every time, silently
rolling the **kernel, iso-image module, systemd, everything**. Real incident:
unstable rolled kernel 6.18.31 → 6.18.33 between two release cuts and 6.18.33
kernel-panicked on bare metal (`VFS: Unable to mount root fs`). Nobody chose the
new kernel; the relock did.

For appliances / airgapped / anything where reproducibility matters: **pin an
immutable commit sha, not a branch.**

## Pinning correctly (sha, not branch)

```nix
# FLOATS — rolls on every `nix flake update`:
nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
# PINNED — immutable; `nix flake update` re-resolves to the SAME sha (no-op):
nixpkgs.url = "github:NixOS/nixpkgs/e8e446a361172fe838243958325845d0b845c5e5";
```

- The third path segment is overloaded: a **40-char hex sha** locks as
  `original.rev` (immutable); a name locks as `original.ref` (a moving branch).
- MUST be the FULL 40-char sha — the `github:` fetcher rejects short shas.
- A release TAG is NOT more immutable than a sha (tags can be re-pointed); the
  bare sha is the gold standard. Add a comment with the channel + kernel for
  humans.
- Every input with `inputs.nixpkgs.follows = "nixpkgs"` (disko, sops-nix,
  home-manager, your own sub-flakes…) inherits the pin transitively — one lever
  pins the whole closure's kernel. Verify a given input's follows took:
  `jq -r '.nodes.<input>.inputs.nixpkgs' flake.lock` should be `["nixpkgs"]`.

## Upgrading a pinned nixpkgs (the deliberate bump)

```bash
git ls-remote https://github.com/NixOS/nixpkgs nixos-26.05   # → new head sha
# edit flake.nix:nixpkgs.url to the new sha, THEN:
nix flake update nixpkgs                                     # re-locks ONLY nixpkgs
jq -r '.nodes.nixpkgs.locked.rev' flake.lock                 # confirm new sha
nix flake check                                              # eval gate (see below)
```

- **Editing flake.nix alone does nothing** — `flake.lock` still has the old rev
  until `nix flake update nixpkgs`. `nix flake check` against an un-relocked tree
  evaluates the OLD pin and proves nothing.
- Use `nix flake update <input>` (named) to bump one input. **Bare
  `nix flake update` rolls EVERY floating input** (disko, sops-nix, the git+ssh
  submodules, and any flake carrying its own nixpkgs like `determinate`).

## Reading the lock — use jq, NOT grep

`grep -A6 '"nixpkgs"' flake.lock` matches the FIRST node containing "nixpkgs"
(often `nixpkgs-23-11` / `nixpkgs-regression` / a transitive `nixpkgs_2`), NOT
the root input. It WILL give you the wrong rev. Always:

```bash
jq -r '.nodes.nixpkgs.locked.rev' flake.lock          # root nixpkgs rev
jq -r '.root as $r | .nodes[$r].inputs | keys[]' flake.lock   # actual root inputs
```

**Second-nixpkgs gotcha:** an input like `determinate` may carry its OWN nixpkgs
(`nixpkgs_3`, a flakehub weekly) that does NOT follow root. Before assuming "pin
root = pin kernel", PROVE the kernel comes from root:
`nix eval .#nixosConfigurations.<cfg>.config.boot.kernelPackages.kernel` and check
its store path. (In practice the kernel comes from the `nixpkgs.lib.nixosSystem`
input = root; a `determinate` module installs the daemon, not a kernel.) Do NOT
add a builder-root `determinate.inputs.nixpkgs.follows` if determinate is reached
via a SUBMODULE (`os.inputs.determinate`) — it won't parse, and Determinate
advises against the follows (FlakeHub-Cache misses).

## Default kernel per release (NixOS LTS pattern)

NixOS defaults to the latest LTS kernel; `boot.kernelPackages` unset = that
default. Pinning a channel pins the kernel SERIES — you cannot select a point
release by attribute (there is NO `linux_6_18_31`; `linux_6_18` is whatever the
tree vendored).

| Release | default kernel |
|---------|----------------|
| 25.05 / 25.11 | 6.12 LTS |
| 26.05 "Yarara" | 6.18 LTS |
| nixos-unstable (≈2026-05) | 6.18.x pre-LTS (rolls) |

Implication: newer GPUs (e.g. NVIDIA Blackwell, driver 595.x) need 6.18 → 25.11's
6.12 is a dead end for them; target 26.05. Verify what the fleet runs before
choosing: `ssh <node> 'uname -r; nixos-version; nvidia-smi --query-gpu=name,driver_version --format=csv,noheader'`.

## `nix flake check` is the upgrade go/no-go gate

It EVALUATES every config (incl. submodules via `follows`) and catches
removed/renamed options + dropped packages before any build. It is local-safe
(eval ≠ build; the never-build-locally rule is about `nix build`). Run where any
`git+ssh` inputs are reachable, else it fails at fetch (false negative). A FATAL
error = real incompat (must fix before cutting); a WARNING (e.g. version skew)
evaluates fine.

See `references/nixos-2605.md` for the 26.05-specific changes (systemd-initrd
default, ISO autoboot, ZFS/GCC15 warnings, migration checklist).
