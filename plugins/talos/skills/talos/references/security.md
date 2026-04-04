# Talos v1.12 Security Reference

## Certificate Management

**Auto-rotation:** Talos auto-rotates server certs for etcd, Kubernetes API, Talos API.
Kubelet requires restart at least once/year for cert rotation (any upgrade/reboot suffices).

**Client certs:** User-managed, 1-year TTL. kubeconfig regenerated on each download.

**Renew talosconfig (3 methods):**
```bash
# 1. From control plane (requires os:admin role)
talosctl -n CP1 config new talosconfig-reader --roles os:reader --crt-ttl 24h

# 2. From secrets bundle
talosctl gen config --with-secrets secrets.yaml --output-types talosconfig -o talosconfig <cluster> <endpoint>

# 3. Manual: extract CA from controlplane.yaml, generate key+CSR+cert, encode to talosconfig
```

**Verify cert status:** `talosctl get KubernetesDynamicCerts -o yaml`

## CA Rotation

CAs have 10-year lifespan. Rotate only on key compromise, credential revocation, or approaching expiry.

**Talos API CA rotation (no reboot, no disruption):**
```bash
talosctl -n <CP> rotate-ca --dry-run=false --talos=true --kubernetes=false
```
Phases: add new CA as accepted -> switch issuing CA -> refresh certs -> remove old CA.
Post: update `secrets.yaml`, merge new talosconfig via `talosctl config merge`.

**Kubernetes API CA rotation (may disrupt in-cluster comms):**
```bash
talosctl -n <CP> rotate-ca --dry-run=false --talos=false --kubernetes=true
```
Post: retrieve new kubeconfig via `talosctl kubeconfig`, restart pods to pick up new CA.

**Manual rotation:** Patch `.machine.acceptedCAs`/`.machine.ca` (Talos) or `.cluster.acceptedCAs`/`.cluster.ca` (K8s) through 7-step process mirroring automated flow.

## Certificate Authorities Hierarchy

**Built-in CAs:** Talos API CA, Kubernetes CA, etcd CA -- generated at cluster creation, stored in machine config. 10-year lifetime.

**Add custom trusted CAs:**
```yaml
apiVersion: v1alpha1
kind: TrustedRootsConfig
name: custom-ca
certificates: |
  -----BEGIN CERTIFICATE-----
  ...
  -----END CERTIFICATE-----
```
- Multiple documents supported, each with multiple certs
- Available in maintenance mode
- If STATE partition encrypted, CAs load only after unlock -- avoid circular dependency

## Security Checklist

1. **Protect secrets** -- encrypt secrets in machine config, restrict access to config files (contain cluster CA keys)
2. **Enable disk encryption** -- TPM-backed auto-unlock, SecureBoot+TPM for integrity verification
3. **Keep current** -- 3 minor releases/year + patches; `talosctl upgrade --nodes <ip>`
4. **Pod security** -- enable Pod Security Admission (baseline), network policies, restrict privileged/hostPath/hostNS
5. **Network/firewall** -- Talos ingress firewall for OS-layer; cloud security groups/VPC rules
6. **SecureBoot** -- enable when hardware supports, use TPM-backed key storage
7. **Limit API access** -- protect talosconfig, rotate certs on team changes, prefer short-lived credentials
8. **Backups** -- etcd snapshots, store off-cluster, test recovery regularly
9. **Monitor/audit** -- audit logs, network flows, cluster events; Prometheus+Grafana integration

## Image Verification (cosign)

**Signed images:** installer, talos, talosctl, imager, all system extensions at `ghcr.io/siderolabs/`

```bash
cosign verify \
  --certificate-identity-regexp '@siderolabs\.com$' \
  --certificate-oidc-issuer https://accounts.google.com \
  ghcr.io/siderolabs/installer:v1.12.4
```

Validates: cosign claims, transparency log (offline), CA verification.
Signer: Sidero Labs employees via `siderolabs.com` certificate authority flow.
Reproducible builds available for kernel, initramfs, talosctl, ISO, containers.

## SELinux

- Introduced Talos 1.10, experimental. Enabled by default, **permissive mode** by default.
- Protects OS from workloads including privileged pods.

| Mode | Kernel param | Behavior |
|------|-------------|----------|
| Permissive (default) | -- | Logs violations, blocks config access + debugger attach |
| Enforcing | `enforcing=1` | Prevents unauthorized access; tested with Flannel only |
| Disabled | `selinux=0` | Required if using AppArmor (mutually exclusive) |

```bash
talosctl --nodes <IP> get SecurityState          # check status
talosctl --nodes <IP> logs auditd > audit.log    # denial logs
```

Known: extensions lack enforcing support; many CNI/CSI incompatible with enforcing mode.

## Secure Boot

**Architecture:** UEFI firmware -> systemd-boot -> signed UKI (kernel+initramfs+cmdline) -> TPM PCR measurement -> disk decrypt.

**Generate signing keys:**
```bash
talosctl gen secureboot uki --common-name "SecureBoot Key"   # RSA 4096, signs UKI
talosctl gen secureboot pcr                                   # RSA 2048, signs TPM policy
talosctl gen secureboot database                              # db.auth, KEK.auth, PK.auth
```

**PCR binding:**
- PCR 7: SecureBoot state + enrolled keys (configurable, firmware updates may change it)
- PCR 11: UKI sections (.linux, .osrel, .cmdline, .initrd, .ucode, etc.) + boot phases
- Boot phases extending PCR 11: `enter-initrd` -> `leave-initrd` -> `enter-machined` -> `start-the-world`
- `start-the-world` fires AFTER disk decrypt -- workloads cannot access TPM-sealed keys

**TPM disk encryption patch:**
```yaml
machine:
  systemDiskEncryption:
    ephemeral:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
    state:
      provider: luks2
      keys:
        - slot: 0
          tpm: {}
```

**Install with pre-signed ISO:**
```bash
# Download SecureBoot ISO from Image Factory
# Boot on UEFI system in SecureBoot setup mode (auto-enrolls keys)
talosctl gen config <cluster> https://<endpoint>:6443 \
  --install-image=factory.talos.dev/installer-secureboot/<schematic>:<ver> \
  --install-disk=/dev/sda --config-patch @tpm-disk-encryption.yaml
talosctl -n <IP> apply-config --insecure -f controlplane.yaml
talosctl -n <IP> get securitystate
```

**Custom SecureBoot assets (imager):**
```bash
docker run --rm -t -v $PWD/_out:/secureboot:ro -v $PWD/_out:/out \
  ghcr.io/siderolabs/imager:<ver> secureboot-iso
docker run --rm -t -v $PWD/_out:/secureboot:ro -v $PWD/_out:/out \
  ghcr.io/siderolabs/imager:<ver> secureboot-installer
```

**Upgrades:** Rebuild UKI + installer with same signing keys. Without key preservation, nodes cannot boot or decrypt.

**Limitations:** No upgrade path from GRUB-based to UKI/SecureBoot (fresh install required). No BIOS support. Requires TPM 2.0 for disk encryption.
