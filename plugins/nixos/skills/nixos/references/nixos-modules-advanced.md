# NixOS Modules: Arguments, Exports & Debugging

Split out of `nixos-modules.md`; see it for the preceding sections.

## Module Arguments

Standard arguments available to all modules:

```nix
{ config   # Full system configuration (after evaluation)
, lib      # Nixpkgs library functions
, pkgs     # Package set
, options  # All declared options
, modulesPath  # Path to nixpkgs/nixos/modules
, ...
}:
```

## Conditional Imports

```nix
{ config, lib, ... }:
{
  imports = [
    ./base.nix
  ] ++ lib.optionals config.services.myservice.enable [
    ./myservice-extra.nix
  ];
}
```

## Exporting Modules from Flakes

```nix
# flake.nix
{
  outputs = { self, nixpkgs, ... }: {
    # Single module
    nixosModules.default = import ./modules;

    # Multiple modules
    nixosModules = {
      k3s = import ./modules/k3s;
      airgap = import ./modules/airgap;
    };
  };
}

# Usage in another flake
{
  inputs.myflake.url = "...";

  outputs = { nixpkgs, myflake, ... }: {
    nixosConfigurations.host = nixpkgs.lib.nixosSystem {
      modules = [
        myflake.nixosModules.default
        myflake.nixosModules.k3s
      ];
    };
  };
}
```

## Common Service Patterns

```nix
{ config, lib, pkgs, ... }:
let
  cfg = config.services.myapp;
in {
  options.services.myapp = {
    enable = lib.mkEnableOption "myapp service";
    user = lib.mkOption {
      type = lib.types.str;
      default = "myapp";
    };
    dataDir = lib.mkOption {
      type = lib.types.path;
      default = "/var/lib/myapp";
    };
  };

  config = lib.mkIf cfg.enable {
    users.users.${cfg.user} = {
      isSystemUser = true;
      group = cfg.user;
      home = cfg.dataDir;
      createHome = true;
    };
    users.groups.${cfg.user} = {};

    systemd.services.myapp = {
      after = [ "network.target" ];
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        User = cfg.user;
        WorkingDirectory = cfg.dataDir;
        ExecStart = "${pkgs.myapp}/bin/myapp";
        Restart = "on-failure";
      };
    };
  };
}
```

## Debugging Modules

```nix
# In nix repl
:lf .
nixosConfigurations.hostname.config.services.myservice

# Show option definition locations
nixosConfigurations.hostname.options.services.myservice.port.definitionsWithLocations

# Evaluate with trace
config.myModule.port = builtins.trace "port value" 8080;
```
