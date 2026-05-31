# Complete flake.nix Example

Working `flake.nix` for NixOS + Sway + integrated graphics + home-manager + Wails dev shell.

```nix
{
  description = "NixOS + Sway for Wails desktop dev";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    home-manager = {
      url = "github:nix-community/home-manager/release-25.11";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, home-manager, ... }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; config.allowUnfree = true; };
  in {
    nixosConfigurations.laptop = nixpkgs.lib.nixosSystem {
      inherit system;
      modules = [
        ({ config, pkgs, lib, ... }: {
          imports = [ ./hardware-configuration.nix ];

          boot.loader.systemd-boot.enable = true;
          boot.loader.efi.canTouchEfiVariables = true;
          boot.kernelPackages = pkgs.linuxPackages_latest;
          boot.initrd.kernelModules = [ "i915" ];   # or "amdgpu"

          networking.hostName = "laptop";
          networking.networkmanager.enable = true;

          # Integrated graphics: Intel example (swap for AMD as needed)
          hardware.graphics = {
            enable = true;
            enable32Bit = true;
            extraPackages = with pkgs; [
              intel-media-driver vpl-gpu-rt libvdpau-va-gl
              intel-compute-runtime vulkan-loader
            ];
            extraPackages32 = with pkgs.pkgsi686Linux; [ intel-media-driver libvdpau-va-gl ];
          };

          environment.sessionVariables = {
            LIBVA_DRIVER_NAME = "iHD";
            VDPAU_DRIVER      = "va_gl";
            NIXOS_OZONE_WL    = "1";
            MOZ_ENABLE_WAYLAND = "1";
            WEBKIT_DISABLE_DMABUF_RENDERER = "1";
          };

          services.xserver.videoDrivers = [ "modesetting" ];

          # PipeWire (required for screen-sharing portals)
          security.rtkit.enable = true;
          services.pipewire = {
            enable = true;
            alsa = { enable = true; support32Bit = true; };
            pulse.enable = true;
            wireplumber.enable = true;
          };

          # Sway compositor — auto-wires xdg.portal, polkit, dbus, pam.swaylock
          programs.sway = {
            enable = true;
            wrapperFeatures.gtk = true;     # CRITICAL for Wails
            xwayland.enable = true;
            extraSessionCommands = ''
              export SDL_VIDEODRIVER=wayland
              export QT_QPA_PLATFORM=wayland-egl
              export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
              export _JAVA_AWT_WM_NONREPARENTING=1
              export GDK_BACKEND="wayland,x11"
              export XDG_CURRENT_DESKTOP=sway
              export WEBKIT_DISABLE_DMABUF_RENDERER=1
            '';
            extraPackages = with pkgs; [
              waybar wofi mako slurp swappy wl-clipboard cliphist
              swaylock-effects swayidle brightnessctl playerctl
              pavucontrol pamixer xdg-utils libnotify
              qt5.qtwayland qt6.qtwayland polkit_gnome
              networkmanagerapplet
            ];
          };

          # NOTE: xdg.portal.* is auto-set by programs.sway. Don't duplicate.

          # Polkit GUI agent
          systemd.user.services.polkit-gnome-authentication-agent-1 = {
            description = "polkit-gnome-authentication-agent-1";
            wantedBy = [ "graphical-session.target" ];
            after    = [ "graphical-session.target" ];
            serviceConfig = {
              Type      = "simple";
              ExecStart = "${pkgs.polkit_gnome}/libexec/polkit-gnome-authentication-agent-1";
              Restart   = "on-failure";
            };
          };

          # Display manager: greetd + tuigreet
          services.greetd = {
            enable = true;
            settings.default_session = {
              command = "${pkgs.greetd.tuigreet}/bin/tuigreet --time --cmd sway";
              user = "greeter";
            };
          };

          fonts.packages = with pkgs; [
            noto-fonts noto-fonts-emoji nerd-fonts.jetbrains-mono
          ];

          users.users.dev = {
            isNormalUser = true;
            extraGroups  = [ "wheel" "networkmanager" "video" "render" "audio" "input" ];
          };

          environment.systemPackages = with pkgs; [
            git curl vim go nodejs_20 pkg-config wails
            gtk3 webkitgtk_4_1 glib cairo pango libsoup_3
          ];

          system.stateVersion = "25.11";
        })

        home-manager.nixosModules.home-manager
        {
          home-manager.useGlobalPkgs   = true;
          home-manager.useUserPackages = true;
          home-manager.users.dev = import ./home.nix;
        }
      ];
    };

    # Wails dev shell
    devShells.${system}.default = pkgs.mkShell {
      name = "wails-dev";
      nativeBuildInputs = with pkgs; [ go nodejs_20 pkg-config wails ];
      buildInputs = with pkgs; [
        gtk3 webkitgtk_4_1 glib cairo pango gdk-pixbuf libsoup_3
      ];
      shellHook = ''
        export CGO_ENABLED=1
        export PKG_CONFIG_PATH="${pkgs.webkitgtk_4_1.dev}/lib/pkgconfig:${pkgs.gtk3.dev}/lib/pkgconfig:$PKG_CONFIG_PATH"
        export WEBKIT_DISABLE_DMABUF_RENDERER=1
        export GDK_BACKEND="wayland,x11"
        echo "Build with: wails build -tags webkit2_41"
      '';
    };
  };
}
```

## Apply & verify

```bash
nixos-rebuild switch --flake .#laptop
swaymsg -t get_version
echo $XDG_SESSION_TYPE   # → wayland
nix develop && wails doctor
```
