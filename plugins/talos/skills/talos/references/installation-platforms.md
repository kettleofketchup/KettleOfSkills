# Talos v1.12 Installation Platforms Reference

## Bare Metal - ISO

- Download `metal-<arch>.iso` or `metal-<arch>-secureboot.iso` from GitHub releases or Image Factory
- Supports BIOS+UEFI (amd64), UEFI-only (arm64), SecureBoot (UEFI only)
- Talos does NOT install to disk until machine config applied -- boots into maintenance mode
- If prior install exists on disk, system prefers disk; adjust boot order or remove ISO
- Kernel params reference: `talos.platform=metal`, `slab_nomerge`, `pti=on`

## Bare Metal - PXE/iPXE

- Download `vmlinuz` + `initramfs` from releases page
- Required kernel params: `talos.platform=metal slab_nomerge pti=on`
- Config delivery: `talos.config=https://metadata.service/talos/config?mac=${mac}`
- Boots maintenance mode without config; disk install takes precedence if boot order favors disk
- PXE via Image Factory: `https://pxe.factory.talos.dev/pxe/<schematic-id>/<version>/metal-<arch>`
- Matchbox supported for PXE provisioning

## Proxmox

**VM settings:**
- BIOS: OVMF (UEFI), Machine: q35, CPU: host
- Control plane: 2+ cores, 4GB+ RAM; Workers: 4+ cores, 8GB+ RAM (min 2GB)
- Disable memory ballooning (no hotplug support)
- Disk controller: VirtIO SCSI (NOT "VirtIO SCSI Single" -- causes bootstrap hang)
- Disk format: raw (perf) or qcow2 (snapshots); cache: write-through or none
- EFI disk: 4MB; enable TRIM+SSD emulation for SSDs
- Network: virtio model, bridge vmbr0

**Install steps:**
```bash
talosctl gen config talos-proxmox-cluster https://$CP_IP:6443 --output-dir _out
talosctl apply-config --insecure --nodes $CP_IP --file _out/controlplane.yaml
# verify disk: talosctl get disks --insecure --nodes $CP_IP
# default /dev/sda, virtual disks may be /dev/vda
talosctl bootstrap
```

- QEMU guest agent: use Image Factory with `siderolabs/qemu-guest-agent` extension
- Vanilla ISO: `https://factory.talos.dev/image/376567988ad370138ad8b2698212367b8edcb69b5fd68c80be1f2ec7d603b4ba/v1.12.4/metal-amd64.iso`

## KVM/libvirt

- Prereqs: `/dev/kvm`, QEMU, virsh, 16GB RAM min
- Create NAT network: `virsh net-define my-talos-net.xml && virsh net-start my-talos-net`
- CP node: 2 vCPUs, 2048MB RAM, 40GB qcow2, virtio
- Worker: 2 vCPUs, 4086MB RAM, 40GB qcow2, virtio
```bash
virsh domifaddr <vm>                                    # get IP
talosctl get disks --nodes $CP_IP --insecure            # find disk
talosctl gen config my-cluster https://$CP_IP:6443 --install-disk /dev/vda
talosctl apply-config --insecure --nodes $CP_IP --file controlplane.yaml
talosctl -n $CP_IP bootstrap
```

## VMware

- Requires ESXi 6.7U2+ (vmx-15), `govc` CLI
- Pre-select VIP for control plane endpoint
```bash
talosctl gen config vmware-test https://<VIP>:<port> --config-patch-control-plane @cp.patch.yaml
```
- Deploy OVA via `govc library.create` + `govc library.deploy`
- Inject config: `govc vm.change -e "guestinfo.talos.config=<base64>"`
- Size: `govc vm.change -c <cpus> -m <memory>`; expand ephemeral disk to 10GB+
- CP: 2 CPU/4GB min; Workers: 4 CPU/8GB
- Post-deploy: bootstrap, kubeconfig, talos-vmtoolsd daemonset

## Docker (Local Dev/Testing)

```bash
talosctl cluster create                                 # basic cluster
talosctl cluster create --name c2 --cidr 10.6.0.0/24   # multiple clusters
talosctl cluster destroy [--name c2]
talosctl config nodes 10.5.0.2 10.5.0.3                # set endpoints
```
- Docker 18.03+; macOS: `sudo ln -s "$HOME/.docker/run/docker.sock" /var/run/docker.sock`
- No `upgrade`/`reset` API; no VIP on macOS
- Auto-populates `~/.talos/config` + `~/.kube/config`; ports mapped randomly
- Flannel may need: `sudo modprobe br_netfilter`
- Startup ~1 min; context switching: `talosctl --context c2`, `kubectl --context admin@c2`

## Boot Assets & Imager

**Image Factory** (recommended): `https://factory.talos.dev`
- Generates ISO, PXE, disk images, installer containers on-demand via schematics
- Schematic = YAML defining extra kernel args, system extensions, overlays
```bash
# upload schematic, get ID
curl -X POST --data-binary @schematic.yaml https://factory.talos.dev/schematics
```
- URLs: `factory.talos.dev/image/<id>/<ver>/metal-amd64.iso`
- PXE: `pxe.factory.talos.dev/pxe/<id>/<ver>/metal-amd64`
- Installer: `factory.talos.dev/installer/<id>:<ver>`
- Vanilla schematic ID: `376567988ad370138ad8b2698212367b8edcb69b5fd68c80be1f2ec7d603b4ba`

**Imager container** (advanced/custom):
```bash
docker run --rm -t -v "$PWD/_out:/out" -v /dev:/dev --privileged \
  ghcr.io/siderolabs/imager:<ver> <image-kind> [flags]
```
- Image kinds: `iso`, `secureboot-iso`, `metal`, `secureboot-metal`, `aws`, `gcp`, `azure`, `installer`
- Flags: `--arch`, `--extra-kernel-arg`, `--system-extension-image`, `--overlay-image`, `--meta`
- Remove default kernel arg with `-` prefix: `--extra-kernel-arg=-console`
- Resolve extension refs: `crane export ghcr.io/siderolabs/extensions:<ver> | tar x -O image-digests | grep <name>`
- Resolve overlays: `crane export ghcr.io/siderolabs/overlays:<ver> | tar x -O overlays.yaml`
- Registry auth: `GITHUB_TOKEN` env or mount `~/.docker/config.json`

**Upgrade with custom schematic:**
```bash
talosctl upgrade --image factory.talos.dev/metal-installer/<schematic-id>:<new-ver>
```

**Find current schematic:** `talosctl get extensions`

## Air-Gapped Installation

- Challenges: NTP access, container images, Image Factory, Discovery Service
- Registry mirrors: redirect all pulls to internal pre-populated registry
- PTP interface for time sync in virtual envs (no NTP needed)
- Self-hosted Image Factory + Discovery Service available (requires Sidero Labs license)
- Partial connectivity: use pull-through cache + HTTP proxy
- Custom DNS/NTP config required in machine config
