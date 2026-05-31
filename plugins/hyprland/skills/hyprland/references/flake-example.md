# Complete flake.nix Example

Working `flake.nix` for NixOS + Hyprland (flake input) + integrated graphics + home-manager + Wails dev shell.

```nix
{
  description = "NixOS + Hyprland for Wails desktop dev";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    # Do NOT add inputs.nixpkgs.follows here -- breaks Hyprland cachix.
    hyprland.url = "github:hyprwm/Hyprland";
  };

  outputs = { self, nixpkgs, home-manager, hyprland, ... }@inputs:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    nixosConfigurations.wails-dev = nixpkgs.lib.nixosSystem {
      inherit system;
      specialArgs = { inherit inputs; };
      modules = [
        hyprland.nixosModules.default

        ({ pkgs, ... }: {
          boot.loader.systemd-boot.enable = true;
          boot.loader.efi.canTouchEfiVariables = true;
          networking.hostName = "wails-dev";
          networking.networkmanager.enable = true;

          programs.hyprland = {
            enable = true;
            xwayland.enable = true;
            package       = inputs.hyprland.packages.${system}.hyprland;
            portalPackage = inputs.hyprland.packages.${system}.xdg-desktop-portal-hyprland;
            withUWSM = true;
          };

          xdg.portal = {
            enable = true;
            extraPortals = [ pkgs.xdg-desktop-portal-gtk ];
          };

          # Integrated graphics (Intel example; swap for AMD as needed)
          hardware.graphics = {
            enable = true;
            enable32Bit = true;
            extraPackages = with pkgs; [
              intel-media-driver intel-vaapi-driver libvdpau-va-gl vpl-gpu-rt
              # rocmPackages.clr.icd  # AMD APU OpenCL
            ];
          };

          environment.sessionVariables = {
            LIBVA_DRIVER_NAME = "iHD";
            # Wails / webkit2gtk fixes
            WEBKIT_DISABLE_DMABUF_RENDERER = "1";
            WEBKIT_DISABLE_COMPOSITING_MODE = "1";
            GDK_BACKEND = "wayland,x11";
            QT_QPA_PLATFORM = "wayland;xcb";
            NIXOS_OZONE_WL = "1";
            _JAVA_AWT_WM_NONREPARENTING = "1";
            XDG_CURRENT_DESKTOP = "Hyprland";
            XDG_SESSION_TYPE = "wayland";
          };

          security.rtkit.enable = true;
          services.pipewire = {
            enable = true;
            alsa = { enable = true; support32Bit = true; };
            pulse.enable = true;
          };

          services.dbus.enable = true;
          security.polkit.enable = true;
          services.displayManager.sddm = { enable = true; wayland.enable = true; };

          environment.systemPackages = with pkgs; [
            hyprpaper hyprlock hypridle hyprcursor hyprpicker
            waybar rofi-wayland mako
            grim slurp swappy wl-clipboard cliphist
            brightnessctl playerctl pavucontrol pamixer networkmanagerapplet
            qt5.qtwayland qt6.qtwayland polkit_gnome
            noto-fonts noto-fonts-emoji
            go gcc pkg-config gtk3 webkitgtk_4_1 nodejs git kitty
          ];

          # Cachix (mandatory — Hyprland is C++ heavy)
          nix.settings = {
            experimental-features = [ "nix-command" "flakes" ];
            substituters = [ "https://cache.nixos.org" "https://hyprland.cachix.org" ];
            trusted-public-keys = [
              "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
              "hyprland.cachix.org-1:a7pgxzMz7+chwVL3/pzj6jIBMioiJM7ypFP8PwtkuGc="
            ];
          };

          users.users.kettle = {
            isNormalUser = true;
            extraGroups = [ "wheel" "networkmanager" "video" "render" "audio" "input" ];
          };
          system.stateVersion = "25.11";
        })

        home-manager.nixosModules.home-manager
        {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
          home-manager.extraSpecialArgs = { inherit inputs; };
          home-manager.users.kettle = { ... }: {
            imports = [ inputs.hyprland.homeManagerModules.default ];
            home.stateVersion = "25.11";
            wayland.windowManager.hyprland = {
              enable = true;
              package = null;        # use system Hyprland
              portalPackage = null;
              xwayland.enable = true;
              systemd.enable = true;
              # settings = ... (see references/home-manager.md)
            };
          };
        }
      ];
    };

    # Wails dev shell with webkit2gtk-4.1
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = with pkgs; [ go gcc pkg-config gtk3 webkitgtk_4_1 nodejs ];
      shellHook = ''
        export WEBKIT_DISABLE_DMABUF_RENDERER=1
        export WEBKIT_DISABLE_COMPOSITING_MODE=1
        export GDK_BACKEND=wayland,x11
        export CGO_ENABLED=1
        export PKG_CONFIG_PATH="${pkgs.webkitgtk_4_1.dev}/lib/pkgconfig:${pkgs.gtk3.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
        echo "Wails dev shell ready. Build with: wails build -tags webkit2_41"
      '';
    };
  };
}
```

## Apply & verify

```bash
nixos-rebuild switch --flake .#wails-dev
hyprctl version
echo $XDG_SESSION_TYPE                 # → wayland
echo $WEBKIT_DISABLE_DMABUF_RENDERER   # → 1
nix-shell -p libva-utils --run vainfo
nix develop && wails doctor
```
