# Hyprland Flake Input Setup

Use the upstream `hyprwm/Hyprland` flake for the latest Hyprland release. Always pair with cachix to avoid multi-hour local builds.

## Inputs

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # Hyprland flake — exposes nixosModules.default and homeManagerModules.default
    hyprland.url = "github:hyprwm/Hyprland";
    # ⚠ DO NOT add: inputs.hyprland.inputs.nixpkgs.follows = "nixpkgs";
    # Hyprland's pinned nixpkgs is required for cachix-built binaries.
    # Overriding forces a full local rebuild and breaks the binary cache.
  };
}
```

## NixOS module wiring

```nix
outputs = { self, nixpkgs, home-manager, hyprland, ... }@inputs: {
  nixosConfigurations.mymachine = nixpkgs.lib.nixosSystem {
    system = "x86_64-linux";
    specialArgs = { inherit inputs; };
    modules = [
      hyprland.nixosModules.default
      ({ pkgs, ... }: {
        programs.hyprland = {
          enable = true;
          xwayland.enable = true;
          package       = inputs.hyprland.packages.${pkgs.system}.hyprland;
          portalPackage = inputs.hyprland.packages.${pkgs.system}.xdg-desktop-portal-hyprland;
          withUWSM = true;
        };
      })
      ./configuration.nix
    ];
  };
};
```

## Cachix (mandatory for sane build times)

Hyprland is C++ heavy. Without cachix you compile from source — typically 20-60 min on a laptop iGPU.

```nix
# configuration.nix
nix.settings = {
  substituters = [
    "https://cache.nixos.org"
    "https://hyprland.cachix.org"
  ];
  trusted-public-keys = [
    "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
    "hyprland.cachix.org-1:a7pgxzMz7+chwVL3/pzj6jIBMioiJM7ypFP8PwtkuGc="
  ];
  experimental-features = [ "nix-command" "flakes" ];
};
```

## What the flake exposes

```nix
nixosModules.default        = import ./nix/module.nix inputs;
homeManagerModules.default  = import ./nix/hm-module.nix self;
packages.<system>.hyprland
packages.<system>.xdg-desktop-portal-hyprland
```

The flake's `nixosModules.default` ADDS extension options on top of nixpkgs:
- `programs.hyprland.plugins`
- `programs.hyprland.settings`
- `programs.hyprland.extraConfig`
- `programs.hyprland.topPrefixes`
- `programs.hyprland.bottomPrefixes`

It does NOT define `enable`/`xwayland` — those still come from nixpkgs.

## Verifying

```bash
nixos-rebuild switch --flake .#mymachine
hyprctl version  # should show the version from flake
```

If `hyprctl version` shows the nixpkgs version after rebuild, check that you imported `hyprland.nixosModules.default` AND set `programs.hyprland.package`.

## Source URLs

- Hyprland flake: https://github.com/hyprwm/Hyprland/blob/main/flake.nix
- Cachix setup discussion: https://discourse.nixos.org/t/how-to-setup-cachix-for-hyprland/57936
