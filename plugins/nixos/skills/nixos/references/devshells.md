# DevShells Reference

## mkShell Basics

```nix
# Basic development shell
pkgs.mkShell {
  packages = [ pkgs.git pkgs.nodejs pkgs.yarn ];
}

# With environment variables
pkgs.mkShell {
  packages = [ pkgs.python3 ];

  PYTHONPATH = "${pkgs.python3Packages.requests}/lib/python3.11/site-packages";
  MY_VAR = "value";
}

# With shell hook (runs on entry)
pkgs.mkShell {
  packages = [ pkgs.kubectl ];

  shellHook = ''
    echo "Kubernetes development environment"
    export KUBECONFIG=$HOME/.kube/config
    alias k=kubectl
  '';
}

# mkShellNoCC (no C compiler, lighter)
pkgs.mkShellNoCC {
  packages = [ pkgs.nodejs pkgs.yarn ];
}
```

## Flake DevShells

```nix
{
  outputs = { self, nixpkgs, ... }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    # Default shell (nix develop)
    devShells.${system}.default = pkgs.mkShell {
      packages = [ pkgs.git ];
    };

    # Named shells (nix develop .#name)
    devShells.${system} = {
      default = pkgs.mkShell { packages = [ pkgs.git ]; };
      python = pkgs.mkShell { packages = [ pkgs.python3 ]; };
      node = pkgs.mkShell { packages = [ pkgs.nodejs ]; };
    };
  };
}
```

## Shared DevShell Across Repos

```nix
# utils/nix/devshell.nix
{ pkgs }:

pkgs.mkShell {
  packages = with pkgs; [
    # Kubernetes
    kubectl
    kubernetes-helm
    kustomize
    k9s

    # Nix
    nil  # Nix LSP
    nixpkgs-fmt

    # Git
    git

    # Utilities
    jq
    yq-go
  ];

  shellHook = ''
    echo "Development environment loaded"
  '';
}

# Consuming repo's flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    utils.url = "git+ssh://gitlab.example.com/flakes/utils";
  };

  outputs = { self, nixpkgs, utils, ... }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    devShells.${system}.default = import "${utils}/nix/devshell.nix" { inherit pkgs; };
  };
}
```

## Build Inputs vs Packages

```nix
pkgs.mkShell {
  # Modern: use packages (clearer intent)
  packages = [ pkgs.git pkgs.nodejs ];

  # Legacy: buildInputs (still works)
  buildInputs = [ pkgs.openssl ];

  # Native build inputs (build-time only tools)
  nativeBuildInputs = [ pkgs.pkg-config ];
}
```

## inputsFrom (Inherit from Derivations)

```nix
# Get all dependencies from a package
pkgs.mkShell {
  inputsFrom = [ pkgs.mypackage ];

  # Add extra tools
  packages = [ pkgs.gdb ];
}
```

---

# Overlays

Continued in `overlays.md`.
