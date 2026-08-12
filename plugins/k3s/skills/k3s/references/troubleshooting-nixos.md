# K3s Troubleshooting — Reset, Uninstall, NixOS

## Reset / Uninstall

```bash
# Full uninstall (server)
/usr/local/bin/k3s-uninstall.sh

# Full uninstall (agent)
/usr/local/bin/k3s-agent-uninstall.sh

# These scripts:
# - Stop service
# - Remove binary, scripts, data
# - Clean iptables/ipvs rules
# - Remove CNI config
```

## NixOS-Specific

On NixOS, K3s is managed via systemd + Nix config. Common patterns:

```bash
# Restart K3s (NixOS)
systemctl restart k3s

# Rebuild with changes
nixos-rebuild switch

# Check NixOS-generated K3s service
systemctl cat k3s
```

NixOS does not have `/usr/local/bin/k3s-uninstall.sh`. To uninstall, remove the K3s NixOS module from your configuration and run `nixos-rebuild switch`. Clean up state directories manually:

```bash
sudo rm -rf /var/lib/rancher/k3s
sudo rm -rf /etc/rancher/k3s
```
