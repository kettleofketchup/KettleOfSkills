# esxcli On-Host CLI Reference

Runs directly on ESXi hosts via SSH or ESXi Shell. Use for low-level host configuration, troubleshooting, and patching.

## Access

Enable SSH on the ESXi host (DCUI or vSphere Client), then: `ssh root@<esxi-host>`

Remote via govc: `govc host.esxcli -host esxi1 <namespace> <command>`

Remote via PowerCLI: `Get-EsxCli -VMHost <host>` returns a proxy object.

## Discovery

```bash
esxcli esxcli command list    # List ALL available commands
esxcli <namespace> --help     # Help for a namespace
```

## System

```bash
esxcli system version get                          # ESXi version and build
esxcli system hostname get                         # Hostname
esxcli system account list                         # Local users
esxcli system maintenanceMode set --enable yes     # Enter maintenance
esxcli system maintenanceMode set --enable no      # Exit maintenance
esxcli system shutdown reboot -d 60 -r "reason"    # Scheduled reboot
esxcli system shutdown poweroff -d 10 -r "reason"  # Power off
```

## Network

```bash
esxcli network nic list                # Physical NICs
esxcli network nic stats get -n vmnic0 # NIC statistics
esxcli network ip interface list       # Network interfaces
esxcli network ip interface ipv4 get   # IPv4 config
esxcli network ip connection list      # Active TCP connections
esxcli network ip dns server list      # DNS servers
esxcli network vswitch standard list   # Virtual switches
esxcli network vm list                 # VM network info
esxcli network firewall get            # Firewall status
esxcli network firewall ruleset list   # Firewall rules
esxcli network firewall ruleset set --enabled true --ruleset-id=nfsClient
```

## Storage

```bash
esxcli storage core device list        # All storage devices
esxcli storage vmfs extent list        # VMFS volumes
esxcli storage filesystem list         # All filesystems
esxcli storage nfs list                # NFS shares
esxcli storage nfs add --host=nfs.local --share=/exports/ds --volume-name=nfs1
esxcli storage core adapter rescan --all    # Rescan all adapters
esxcli storage core path list          # Storage paths (multipath)
```

## VM Process Management

```bash
esxcli vm process list                            # List running VMs (World IDs)
esxcli vm process kill --type soft --world-id 123 # Graceful stop (SIGTERM)
esxcli vm process kill --type hard --world-id 123 # Force stop (SIGKILL)
esxcli vm process kill --type force --world-id 123 # Last resort
```

Kill order: always try `soft` first, then `hard`, then `force`.

## Software / Patching

```bash
esxcli software vib list                           # Installed packages (VIBs)

# Profile-based update (required for ESXi 8.0 U2+)
esxcli software profile update -d /vmfs/volumes/ds1/depot.zip -p ESXi-8.0U3c-standard

# Dry run first
esxcli software profile update -d /vmfs/volumes/ds1/depot.zip -p ESXi-8.0U3c-standard --dry-run
```

Note: `esxcli software vib install/update` is deprecated in ESXi 8.0 U2+. Use `software profile update` instead.

## Hardware

```bash
esxcli hardware memory get     # Memory info
esxcli hardware cpu list       # CPU info
esxcli hardware pci list       # PCI devices
```

## vim-cmd (Companion Tool)

Not part of esxcli but commonly used alongside it on ESXi hosts:

```bash
vim-cmd vmsvc/getallvms                # List all registered VMs
vim-cmd vmsvc/power.getstate <vmid>    # Power state
vim-cmd vmsvc/power.on <vmid>          # Power on
vim-cmd vmsvc/power.off <vmid>         # Power off
vim-cmd vmsvc/power.shutdown <vmid>    # Guest shutdown
vim-cmd vmsvc/snapshot.create <vmid> "name" "desc" 0 0  # Create snapshot
vim-cmd vmsvc/snapshot.get <vmid>      # List snapshots
vim-cmd vmsvc/snapshot.revert <vmid> <snapid>  # Revert
vim-cmd vmsvc/snapshot.remove <vmid> <snapid>  # Remove
```
