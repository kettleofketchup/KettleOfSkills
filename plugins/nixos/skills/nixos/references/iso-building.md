# NixOS ISO Building Reference

## ISO Configuration

```nix
# flake.nix
nixosConfigurations.iso = nixpkgs.lib.nixosSystem {
  system = "x86_64-linux";
  modules = [
    "${nixpkgs}/nixos/modules/installer/cd-dvd/installation-cd-minimal.nix"
    ./iso/configuration.nix
  ];
};
```

Build: `nix build .#nixosConfigurations.iso.config.system.build.isoImage`

## ISO Module

```nix
# iso/configuration.nix
{ config, lib, pkgs, ... }:
{
  isoImage.isoName = "myorg-installer.iso";
  isoImage.volumeID = "MYORG_INSTALL";

  environment.systemPackages = with pkgs; [
    gum glow yq-go     # TUI prompts, markdown display, YAML processing
    parted dosfstools e2fsprogs
  ];

  # Auto-run installer on boot
  systemd.services.auto-installer = {
    description = "Automated installer";
    after = [ "network.target" "getty@tty1.service" ];
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${./scripts/install.sh}";
      StandardInput = "tty";
      StandardOutput = "tty";
      TTYPath = "/dev/tty1";
    };
  };
}
```

## Closure Consistency

### Changes the closure (derivation hash)

Everything resolved at **build time**:

- Nix expressions, module options, `flake.lock` pins
- Files referenced as Nix paths: `${./scripts/install.sh}`, `${./config}`
- Package versions from nixpkgs
- `pkgs.writeText`, `pkgs.writeShellApplication` content
- `builtins.readFile` or string interpolation of paths

### Does NOT change the closure

Anything resolved at **runtime**:

- User input (stdin, TTY prompts via gum)
- Environment variables read by scripts
- Files written/read at runtime (`/etc/nixos/site-config.yaml`)
- Network responses, command-line arguments

### Rule: parameterize at runtime, not build time

```nix
# BAD - closure changes when hostname changes
environment.etc."install-config".text = ''
  hostname: ${myHostname}
'';

# GOOD - script prompts at runtime, closure stable
install-script = pkgs.writeShellApplication {
  name = "configure-host";
  runtimeInputs = [ pkgs.gum pkgs.yq-go ];
  text = builtins.readFile ./scripts/configure-host.sh;
};
```

### Verify closure stability

```bash
# Build twice — store path hash must match if no code changed
nix build .#nixosConfigurations.iso.config.system.build.isoImage
nix path-info --derivation .#nixosConfigurations.iso.config.system.build.isoImage
```

## Bundle Flake Source in ISO

Include the flake so the installed system can `nixos-rebuild`:

```nix
isoImage.contents = [
  { source = self; target = "/opt/flake"; }
];
```

## Reading YAML in NixOS Modules

Site config is runtime state — read it in activation scripts or systemd, not module evaluation:

```nix
# WRONG - evaluated at build time, breaks closure
config.networking.hostName = builtins.fromJSON
  (builtins.readFile /etc/nixos/site-config.yaml);

# RIGHT - activation script applies at runtime
system.activationScripts.apply-site-config = ''
  hostname=$(${pkgs.yq-go}/bin/yq '.hostname' /etc/nixos/site-config.yaml)
  hostnamectl set-hostname "$hostname"
'';

# RIGHT - systemd reads config at runtime
systemd.services.apply-network = {
  script = ''
    ip=$(${pkgs.yq-go}/bin/yq '.network.ip' /etc/nixos/site-config.yaml)
    # apply network config...
  '';
};
```

## ISO Variants Without Closure Duplication

Use module options with `mkDefault` for base config. Site values come from runtime:

```nix
{ lib, ... }:
{
  options.installer.configPath = lib.mkOption {
    type = lib.types.path;
    default = /etc/nixos/site-config.yaml;
    description = "Runtime config written by installer prompts";
  };
}
```

One ISO → many hosts. Differentiation happens at install time, not build time.
