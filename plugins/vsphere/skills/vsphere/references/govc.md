# govc CLI Reference

Go-based vSphere CLI built on [govmomi](https://github.com/vmware/govmomi). Single static binary, cross-platform.

## Installation

```bash
nix shell nixpkgs#govc                    # Nix
brew install govc                          # Homebrew
# Binary download
curl -L -o - "https://github.com/vmware/govmomi/releases/latest/download/govc_$(uname -s)_$(uname -m).tar.gz" \
  | tar -C /usr/local/bin -xvzf - govc
```

## Environment Variables

### Connection

| Variable | Purpose | Example |
|----------|---------|---------|
| `GOVC_URL` | ESXi/vCenter URL | `https://vcenter.example.com/sdk` |
| `GOVC_USERNAME` | Username | `administrator@vsphere.local` |
| `GOVC_PASSWORD` | Password | `secret` |
| `GOVC_INSECURE` | Skip TLS verification | `true` |
| `GOVC_TLS_CA_CERTS` | Custom CA cert path | `/path/to/ca.crt` |

### Defaults

| Variable | Purpose |
|----------|---------|
| `GOVC_DATACENTER` | Default datacenter |
| `GOVC_DATASTORE` | Default datastore |
| `GOVC_NETWORK` | Default network |
| `GOVC_RESOURCE_POOL` | Default resource pool |
| `GOVC_HOST` | Default ESXi host |
| `GOVC_FOLDER` | Default inventory folder |
| `GOVC_GUEST_LOGIN` | Guest credentials (`user:password`) |

## Inventory Navigation

Paths mirror the vSphere hierarchy: `/<Datacenter>/<folder-type>/<object>`

```bash
govc ls /                              # Root (all datacenters)
govc ls /DC1/                          # Datacenter contents
govc ls /DC1/vm/                       # All VMs
govc ls /DC1/host/                     # Hosts/clusters
govc ls /DC1/datastore/                # Datastores
govc ls /DC1/network/                  # Networks
govc tree /DC1/vm                      # Tree view
```

### Find objects by type

```bash
govc find / -type m                    # VMs (m=VirtualMachine)
govc find / -type h                    # Hosts (h=HostSystem)
govc find / -type s                    # Datastores (s=Datastore)
govc find / -type c                    # Clusters (c=ClusterComputeResource)
govc find / -type p                    # Resource pools
govc find / -type n                    # Networks
govc find / -type f                    # Folders
govc find /DC1/vm -type m -runtime.powerState poweredOn   # Running VMs
govc find /DC1/vm -type m -name "web*"                    # Name pattern
```

Type aliases: `a`=VirtualApp, `c`=Cluster, `d`=Datacenter, `f`=Folder, `g`=DVPortgroup, `h`=Host, `m`=VM, `n`=Network, `o`=OpaqueNetwork, `p`=ResourcePool, `r`=ComputeResource, `s`=Datastore, `w`=DVSwitch

## VM Operations

```bash
govc vm.create -m 4096 -c 2 -disk 40GB -net "VM Network" -on=false my-vm
govc vm.create -m 8192 -c 4 -disk 100GB -ds datastore1 -net "VM Network" \
  -net.adapter vmxnet3 -pool /DC1/host/Cluster1/Resources -g ubuntu64Guest -on=false my-vm
govc vm.info my-vm
govc vm.info -json my-vm | jq
govc vm.ip -wait 5m my-vm
govc vm.power -on my-vm
govc vm.power -off my-vm
govc vm.power -s my-vm                # Graceful shutdown (VMware Tools)
govc vm.power -r my-vm
govc vm.power -suspend my-vm
govc vm.clone -vm template-vm -on=false new-vm
govc vm.clone -vm template-vm -link new-vm
govc vm.clone -vm template-vm -snapshot snap-name new-vm
govc vm.change -vm my-vm -m 16384
govc vm.change -vm my-vm -c 8
govc vm.change -vm my-vm -e "guestinfo.userdata=$(cat ud.yaml)"
govc vm.upgrade -vm my-vm
govc vm.disk.create -vm my-vm -size 50G -name my-vm/disk2
govc vm.disk.change -vm my-vm -disk.name "disk-1000-0" -size 100G
govc vm.network.add -vm my-vm -net "VLAN100" -net.adapter vmxnet3
govc vm.network.change -vm my-vm -net "VLAN200" ethernet-0
govc vm.markastemplate my-vm
govc vm.markasvm -host esxi1 my-template
govc vm.power -off my-vm && govc vm.destroy my-vm
govc vm.console my-vm
```

## Snapshots

```bash
govc snapshot.create -vm my-vm "before-upgrade"
govc snapshot.create -vm my-vm -m=false "no-memory"   # Without memory
govc snapshot.tree -vm my-vm                           # List (tree)
govc snapshot.tree -vm my-vm -D -i                     # With dates and IDs
govc snapshot.revert -vm my-vm "before-upgrade"
govc snapshot.revert -vm my-vm                         # Revert to current
govc snapshot.remove -vm my-vm "before-upgrade"
govc snapshot.remove -vm my-vm '*'                     # Remove all
```

## Datastore Operations

```bash
govc datastore.ls                                      # List root
govc datastore.ls -ds datastore1 -l -R                 # Recursive long listing
govc datastore.mkdir -p isos                            # Create directory
govc datastore.upload local.iso isos/remote.iso         # Upload
govc datastore.download remote.iso local.iso            # Download
govc datastore.rm old-file.iso                          # Delete
govc datastore.disk.create -size 10G my-vm/disk1.vmdk   # Create VMDK
```

## OVA/OVF Deployment

```bash
govc import.spec app.ova > spec.json
govc import.ova -options=spec.json -name my-app app.ova
govc library.create my-library
govc library.import my-library ./my.ova
govc library.deploy /my-library/my.ova deployed-vm
```

## ISO / CD-ROM

```bash
govc datastore.upload ./installer.iso isos/installer.iso
govc device.cdrom.add -vm my-vm
govc device.cdrom.insert -vm my-vm -device cdrom-3000 isos/installer.iso
govc device.cdrom.eject -vm my-vm -device cdrom-3000
govc vm.create -iso isos/installer.iso -iso-datastore ds1 -on=false my-vm
```

See `references/govc-advanced.md` for host operations, guest operations, scripting patterns, and command group index.
