# Home Manager Reference

## Basic Configuration

```nix
# ~/.config/home-manager/home.nix
{ config, pkgs, ... }:
{
  home.username = "user";
  home.homeDirectory = "/home/user";

  # Keep at version when first installed
  home.stateVersion = "25.11";

  # Let home-manager manage itself
  programs.home-manager.enable = true;
}
```

## Packages

```nix
{
  # User packages
  home.packages = with pkgs; [
    htop
    ripgrep
    fd
    jq
  ];
}
```

## Program Configuration

```nix
{
  # Git
  programs.git = {
    enable = true;
    userName = "Your Name";
    userEmail = "your@email.com";
    extraConfig = {
      init.defaultBranch = "main";
      pull.rebase = true;
    };
    aliases = {
      co = "checkout";
      st = "status";
    };
  };

  # Neovim
  programs.neovim = {
    enable = true;
    defaultEditor = true;
    viAlias = true;
    vimAlias = true;
    plugins = with pkgs.vimPlugins; [
      vim-nix
      telescope-nvim
    ];
    extraConfig = ''
      set number
      set relativenumber
    '';
  };

  # Zsh
  programs.zsh = {
    enable = true;
    enableCompletion = true;
    autosuggestion.enable = true;
    syntaxHighlighting.enable = true;
    shellAliases = {
      ll = "ls -la";
      update = "sudo nixos-rebuild switch";
    };
    initExtra = ''
      # Custom init
    '';
  };

  # Bash
  programs.bash = {
    enable = true;
    shellAliases = { ll = "ls -la"; };
    bashrcExtra = ''
      # Custom bashrc
    '';
  };

  # Starship prompt
  programs.starship = {
    enable = true;
    settings = {
      add_newline = false;
      character.success_symbol = "[>](bold green)";
    };
  };

  # Direnv
  programs.direnv = {
    enable = true;
    nix-direnv.enable = true;
  };
}
```

## Dotfiles Management

```nix
{
  # Copy file to home
  home.file.".config/app/config.toml".source = ./dotfiles/app-config.toml;

  # Inline content
  home.file.".config/app/settings.json".text = ''
    {
      "theme": "dark",
      "fontSize": 14
    }
  '';

  # Symlink (for frequently edited files)
  home.file.".config/app/user.conf" = {
    source = ./dotfiles/user.conf;
    # Note: source files must be tracked by git for flakes
  };

  # Recursive directory
  home.file.".config/nvim" = {
    source = ./dotfiles/nvim;
    recursive = true;
  };
}
```

## XDG Configuration

```nix
{
  xdg = {
    enable = true;
    configFile = {
      "app/config.toml".source = ./config.toml;
    };
    dataFile = {
      "app/data".source = ./data;
    };
  };
}
```

## Services (Linux)

```nix
{
  services.gpg-agent = {
    enable = true;
    enableSshSupport = true;
    defaultCacheTtl = 1800;
  };

  services.syncthing.enable = true;
}
```

Continued in `home-manager-integration.md`.
