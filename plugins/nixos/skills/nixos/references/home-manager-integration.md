# Home Manager: Flake & NixOS Integration

Split out of `home-manager.md`; see it for the preceding sections.

## Flake Integration

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager.url = "github:nix-community/home-manager";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, home-manager, ... }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    # Standalone home-manager
    homeConfigurations."username" = home-manager.lib.homeManagerConfiguration {
      inherit pkgs;
      modules = [ ./home.nix ];
      extraSpecialArgs = {
        # Pass extra args to home.nix
      };
    };
  };
}
```

## NixOS Module Integration

```nix
# In NixOS configuration.nix or flake module
{ inputs, ... }:
{
  imports = [ inputs.home-manager.nixosModules.home-manager ];

  home-manager = {
    useGlobalPkgs = true;      # Use system nixpkgs
    useUserPackages = true;    # Install to /etc/profiles
    users.myuser = import ./home.nix;

    # Pass extra args to home.nix
    extraSpecialArgs = {
      inherit inputs;
    };
  };
}
```

## Commands

```bash
# Build and activate (standalone)
home-manager switch

# Build only
home-manager build

# Show generations
home-manager generations

# Rollback
home-manager switch --rollback

# With flake
home-manager switch --flake .#username

# Via NixOS (when integrated)
sudo nixos-rebuild switch
```

## Environment Variables

```nix
{
  home.sessionVariables = {
    EDITOR = "nvim";
    VISUAL = "nvim";
    PATH = "$HOME/.local/bin:$PATH";
  };

  # For shells not managed by home-manager, source:
  # $HOME/.nix-profile/etc/profile.d/hm-session-vars.sh
}
```

## Activation Scripts

```nix
{
  home.activation = {
    myScript = lib.hm.dag.entryAfter [ "writeBoundary" ] ''
      $DRY_RUN_CMD mkdir -p $HOME/.local/share/myapp
    '';
  };
}
```

## Conditional Configuration

```nix
{ config, lib, pkgs, ... }:
{
  # Platform-specific
  home.packages = with pkgs; [
    git
  ] ++ lib.optionals stdenv.isLinux [
    inotify-tools
  ] ++ lib.optionals stdenv.isDarwin [
    darwin.apple_sdk.frameworks.Security
  ];

  # Host-specific (pass hostname via extraSpecialArgs)
  programs.git.userEmail = lib.mkIf (hostname == "work") "work@company.com";
}
```

## Troubleshooting

### File collision
Home-manager won't overwrite existing files. Back up and remove conflicting files.

### Changes not applying
Ensure shell is restarted or run `source ~/.nix-profile/etc/profile.d/hm-session-vars.sh`.

### Module not found
Check home-manager version matches nixpkgs branch (release-25.11 with nixos-25.11).
