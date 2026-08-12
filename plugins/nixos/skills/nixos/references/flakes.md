# Nix Flakes Reference

## Flake Structure

```nix
{
  description = "A flake description";

  inputs = {
    # Input declarations
  };

  outputs = { self, nixpkgs, ... }@inputs: {
    # Output declarations
  };
}
```

## Input Types

```nix
inputs = {
  # GitHub
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  # GitLab (self-hosted)
  myflake.url = "git+ssh://gitlab.example.com/group/repo";
  myflake.url = "git+https://gitlab.example.com/group/repo";

  # Git with ref/rev
  myflake.url = "git+ssh://host/repo?ref=main";
  myflake.url = "git+ssh://host/repo?rev=abc123";

  # Local path (for development)
  myflake.url = "path:./subdir";

  # Tarball
  myflake.url = "https://example.com/archive.tar.gz";

  # Pin inputs to same nixpkgs (critical for consistency)
  other-flake.url = "git+ssh://host/other";
  other-flake.inputs.nixpkgs.follows = "nixpkgs";

  # Flake without flake.nix
  non-flake.url = "github:owner/repo";
  non-flake.flake = false;
};
```

## Standard Outputs

```nix
outputs = { self, nixpkgs, ... }:
let
  system = "x86_64-linux";
  pkgs = import nixpkgs { inherit system; };
in {
  # NixOS configurations
  nixosConfigurations.hostname = nixpkgs.lib.nixosSystem {
    inherit system;
    modules = [ ./configuration.nix ];
  };

  # Reusable NixOS modules
  nixosModules.default = import ./modules;
  nixosModules.myservice = import ./modules/myservice.nix;

  # Packages
  packages.${system}.default = pkgs.hello;
  packages.${system}.mypackage = pkgs.callPackage ./pkg.nix {};

  # Development shells
  devShells.${system}.default = pkgs.mkShell {
    packages = [ pkgs.git pkgs.nodejs ];
  };

  # Overlays
  overlays.default = final: prev: {
    mypackage = prev.callPackage ./pkg.nix {};
  };

  # Apps (runnable with nix run)
  apps.${system}.default = {
    type = "app";
    program = "${self.packages.${system}.default}/bin/hello";
  };

  # Formatter (nix fmt)
  formatter.${system} = pkgs.nixpkgs-fmt;

  # Templates
  templates.default = {
    path = ./template;
    description = "A basic template";
  };

  # Checks (nix flake check)
  checks.${system}.test = pkgs.runCommand "test" {} "touch $out";
};
```

## Multi-System Support

```nix
outputs = { self, nixpkgs, ... }:
let
  systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
  forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f {
    pkgs = import nixpkgs { inherit system; };
    inherit system;
  });
in {
  packages = forAllSystems ({ pkgs, system }: {
    default = pkgs.hello;
  });

  devShells = forAllSystems ({ pkgs, system }: {
    default = pkgs.mkShell { packages = [ pkgs.git ]; };
  });
};
```

## Multi-Repo Composition Pattern

```nix
# builder/flake.nix - Composes multiple flakes
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    # Pin all to same nixpkgs
    os.url = "git+ssh://gitlab.example.com/flakes/os";
    os.inputs.nixpkgs.follows = "nixpkgs";

    k3s.url = "git+ssh://gitlab.example.com/flakes/k3s";
    k3s.inputs.nixpkgs.follows = "nixpkgs";

    services.url = "git+ssh://gitlab.example.com/flakes/services";
    services.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, os, k3s, services, ... }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        os.nixosModules.default
        k3s.nixosModules.k3s
        ./host-config.nix
      ];
    };
  };
}
```

Continued in `flakes-usage.md`.
