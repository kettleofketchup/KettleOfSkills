# Talos v1.12 Security: Secure Boot & TPM Reference

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
