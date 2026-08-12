# NixOS 26.05 "Yarara" — migration notes

Released 2026-05-30. Default kernel **Linux 6.18 LTS** (was 6.12 in 25.x), GCC 15,
GNOME 50, dbus→dbus-broker default. EOL ~2026-12-31 + (7-month stable cycle).
Source: nixos.org/manual release-notes rl-2605, announcement blog.

## systemd stage-1 initrd is now the DEFAULT

`boot.initrd.systemd.enable` now defaults true; the scripted initrd is deprecated
and **removed in 26.11**. Stay on systemd-initrd.

- If a config ALREADY set `boot.initrd.systemd.enable = true`, the default flip is
  a **no-op** — closure unchanged.
- Behavioral facts of the systemd-initrd path (matter for custom/ISO boot):
  - Root/ISO is mounted **by filesystem label** (`/dev/disk/by-label/…`), kernelparam
    `root=fstab` (root comes from generated mount units, not a `root=` device). So
    stage-1 MUST have the storage/USB controller modules to enumerate the media —
    this is the real dependency, not the toggle.
  - Live-ISO squashfs mounts at `/sysroot/iso/nix-store.squashfs`.
  - **LUKS footgun:** `fileSystems."/".device` must be `/dev/mapper/<name>` matching
    `boot.initrd.luks.devices.<name>` or systemd-initrd times out at the passphrase
    prompt. If it hangs, add `"x-systemd.device-timeout=infinity"` to root options.
    `cryptsetup-askpass` is gone; recovery = `systemctl default`. (disko normally
    emits the right device automatically — verify on a fresh install.)

## ISO autoboot (no GRUB menu) still works

`iso-image.nix` emits `set timeout=${timeout}` with **no `set default`** → GRUB
boots entry 0 immediately when `boot.loader.timeout = 0`. 26.05 did NOT add an
always-on menu entry; memtest is gated on `boot.loader.grub.memtest86.enable`.
To guarantee autoboot on a live ISO:

```nix
boot.loader.timeout = lib.mkForce 0;              # iso-image defaults it to 10 (mkDefault)
boot.loader.grub.memtest86.enable = lib.mkForce false;
```

Verify (don't trust): `nix eval .#nixosConfigurations.<iso>.config.boot.loader.timeout`
→ must be `0`. NOTE: this eval proves the override APPLIES, not that the menu is
gone — only a real boot proves autoboot (a stray keypress during the countdown,
or a firmware boot-picker, can still drop to a menu independent of nixpkgs).

## Warnings that are usually NOISE

- **`boot.zfs.forceImportRoot` default-true warning** — fires on any config with
  `stateVersion < 26.11` REGARDLESS of ZFS use. If the stack has no ZFS (ext4/LUKS
  + Ceph etc.), it never actually imports → ignore. Only act (`= false`) if ZFS is
  actually used.
- **nixvim "version 26.11 vs nixpkgs 26.05" skew** — nixvim's default branch tracks
  unstable. On 25.11 this was a FATAL `makeVimPackageInfo` eval error; on 26.05 it's
  a non-fatal WARNING (good signal 26.05 is the closer target). Fix: pin nixvim to
  its `nixos-26.05` branch in the consuming flake (`url = "github:nix-community/nixvim/nixos-26.05"`),
  relock. Only affects configs that actually import the nvim module.

## Eval-break audit (moving unstable→26.05 or 25.11→26.05)

`nix flake check` catches these. Removed/renamed options to grep for in a real
config: `services.openssh.banner`→`settings.Banner`; `systemd.coredump/sleep.extraConfig`→`.settings`;
`profiles/hardened` + `linux_hardened`/`linux-rt` removed; `reiserfs`/`ecryptfs`
removed; `fileSystems.<n>.fsType` no longer defaulted; `services.kubernetes.addons.dns.coredns`→`corednsImage`
(irrelevant if running K3s, which ships its own CoreDNS). 17.5k packages removed
in 26.05 — package-by-name refs may break.

## What's NOT affected by the nixpkgs bump

- **vLLM / CUDA** when container-based (helm-deployed `vllm/vllm-openai` image
  carries its own CUDA) — only the HOST nvidia kernel driver matters, not nixpkgs
  CUDA libs. Verify: is vllm in `nix/images.list` (container) or a nix derivation?
- **NVIDIA driver**: `boot.kernelPackages.nvidiaPackages.beta` resolves to a
  version from the pinned nixpkgs — verify it builds against 6.18 and matches the
  fleet (`nix eval .#nixosConfigurations.<cfg>.config.hardware.nvidia.package.version`).
  A future unstable roll could move `beta` to a non-building driver — keep pinned.

## Hard gate regardless of clean eval

`nix flake check` passing ≠ a booting kernel on real hardware. The original panic
was a kernel/initrd issue invisible to eval. ALWAYS finish with a CI ISO build +
bare-metal boot on the target board before trusting a kernel/channel change.
See `references/channel-pinning.md` for the pinning mechanics.
