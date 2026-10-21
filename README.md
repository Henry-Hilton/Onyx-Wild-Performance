# Onyx Wild Performance kernel

[Releases](https://github.com/Henry-Hilton/Onyx-Wild-Performance/releases) ·
[Build workflow](https://github.com/Henry-Hilton/Onyx-Wild-Performance/actions/workflows/build-release.yml)

## Automated builds and releases

Every build produces two root variants: KernelSU and SukiSU Ultra. Both use the
same kernel base, performance settings, CRC bypass, ABI fixes, SUSFS, NoMount,
Baseband Guard and remaining shared features. KPM is enabled exclusively in
SukiSU. Use the matching root manager. Each variant has Auto Slot, Slot A and
Slot B ZIPs, for six flashable ZIPs per successful release. CI requires both
variants to pass before publishing and keeps their reports/source archives separate.
SukiSU and its KPM loader still require hardware testing; no KPM modules are bundled.

Every push to `main` and every manual workflow run builds the pinned sources,
checks features, validates module symbol CRCs and 15 structure layouts, and
packages the AnyKernel3 ZIP. Every successful build publishes a uniquely tagged
experimental prerelease containing the ZIP, complete modified source archive,
checksums, configuration, manifest and validation reports. Failed builds do not
publish releases. Release tags include the run ID and attempt number.

The workflow uses GitHub's built-in token, with write permission confined to
the release job. No personal access token or other secret is required.
`sources.lock.json`, `patches/` and `source-additions/` reconstruct the tested
source tree; `configs/` records the feature selection. CI consumes interface
metadata in `abi/`, so no ROM or proprietary module binaries are redistributed.
The baseline covers the available crDroid Android 17 build; newer firmware ABI
changes require updating the baseline and validating the new source.

For a Linux build with LLVM 21 and the listed dependencies, run
`bash scripts/ci_build.sh`. Set `ONYX_VARIANT=kernelsu` (default) or `sukisu`,
`ONYX_BUILD_ROOT` to a fresh directory and `JOBS`
to the desired parallelism. The workflow can be started using **Actions → Build
and release kernel → Run workflow**. Dependencies stay pinned so a passing build
does not silently absorb unreviewed upstream changes.

Target: Redmi Turbo 4 Pro / Poco F7 (`onyx`), Android 15 GKI generation,
Linux 6.6, 4 KiB pages. The intended targets are current HyperOS and AOSP ROMs.
Boot validation on a physical phone is required before claiming compatibility.
The user confirmed that v0.1.2 boots AxionOS 2.9 (Android 16 QPR2) without
issues observed so far. This is a user-reported result for that build; subsequent
upstream updates still require device validation.

The working source is the maintained crDroid onyx tree at
`10570812a4878b644e31b47c2f0bd052664cf86d`, initially Linux 6.6.142.
The Linux 6.6.143 update is ported with Android changes retained. Xiaomi's
`onyx-v-oss` source and the two user-tested deprecated kernels are research
references; the deprecated repositories are not used as the final base.

## Features

- KernelSU with current SUSFS kernel integration and all SUSFS configuration
  options exposed by WildKernels, including path, mount, kstat, map and uname
  support, open redirection, command-line/bootconfig support and Unicode fix.
- NoMount kernel support; Baseband Guard with its LSM selected.
- KernelSU preinit runner integrated through the SUSFS manual exec path before
  UID/su filtering. PID 1 runs it once before `selinux_setup`; original arguments
  are preserved and recoverable exec failures fall back to normal init. The
  upstream runner retains action deadlines and boot-loop protection. Use a
  matching current KernelSU manager/userspace to configure preinit modules.
- WireGuard, BBR and BBRv3, IPSet variants, connection marking, TTL/hop-limit
  targets, IPv6 NAT, FQ/FQ-CoDel/CAKE and CIFS with xattrs/POSIX extensions.
- BTF/eBPF/FUSE-BPF, TMPFS xattrs/ACLs, OverlayFS and NTSync.
- DroidSpaces kernel prerequisites: PID/user/IPC namespaces, SYSVIPC with
  task-structure ABI padding, POSIX message queues, devtmpfs and binary formats.
- WildKernels memory, scheduler, filesystem and wakeup tuning; O3,
  Cortex-X4 instruction scheduling and ThinLTO. Optional live maximum
  performance profile in `profiles/max-performance.sh`.

Root implementations are alternatives. This build selects KernelSU; it does
not combine KernelSU, KernelSU-Next and ReSukiSU into one kernel. Userspace
software (the matching KernelSU manager, SUSFS module, a mount metamodule,
DroidSpaces runtime and FUSE-BPF programs) must be installed separately.
Their availability in the kernel does not install or activate the applications.
The ptrace fix for kernels older than 5.16 does not apply to Linux 6.6.

## Build and verification

Build storage is under `/root/onyx-kernel-dev` in WSL Ubuntu. The source is
`/root/onyx-kernel-dev/kernel`; output is `/root/onyx-kernel-dev/out`.
Compilation uses the installed LLVM/Clang 21 tools through a private symlink
directory. Run `scripts/build.sh` inside WSL after source preparation.

`scripts/check_features.py` checks that core requested features survive
Kconfig dependency resolution. `scripts/audit_modules.py` compares kernel
exports and CRCs with 961 extracted modules from the locally available
`crDroidAndroid-17.0-20261003-onyx-v13.0-BETA.zip`.
`scripts/package.py` requires a real ARM64 Image header and successful module
checks before creating the AnyKernel3 ZIP. It validates ZIP integrity and
records component revisions and hashes.
The final symbol audit reports zero missing exports and zero CRC mismatches.
The BTF audit also matches 15 selected vendor-facing structures, including
task, network, memory, file, netlink, Bluetooth and IR layouts.

The source archive in `dist` includes the modified kernel and integrated
KernelSU, SUSFS, NoMount and Baseband Guard code. The original tree's dangling
links to a separate vendor device-tree repository are omitted; this GKI build
preserves the ROM's device trees. Extract it and run
`scripts/build_exported_source.sh /path/to/kernel /path/to/kernel.config /path/to/out`
on Linux with Clang/LLVM 21, pahole, flex, bison, bc, OpenSSL development headers
and the usual kernel build dependencies. The script supplies the recorded
KernelSU version when Git history is absent. Component patches are also saved.

The installer checks for onyx and replaces the current slot's boot kernel,
using slot properties, `/proc/bootconfig` or the kernel command line. Boot block
devices are resolved through named links, deeper recovery paths or sysfs
partition names. The `Slot-A` and `Slot-B` ZIPs provide an explicit slot when a
recovery exposes no active-slot metadata; choose only your confirmed active slot.
If available metadata disagrees with that selection, installation aborts.
retaining the installed ROM's ramdisk and device trees. It does not replace
vendor or system modules. Stock 250 Hz, CFI, KASAN exports and vendor-visible
debug interfaces are retained for module compatibility; KASAN is requested
off at runtime. Symbol CRC mismatches are accepted at runtime, matching
gki-clo's `check_version()` bypass, and a warning is logged. This also applies
to the `module_layout` CRC. CI still requires the supplied ABI baseline to match.
Missing symbols, other vermagic differences and other loader errors can still
prevent a module from loading. The configuration disables
GKI protected-export restrictions to permit the ROM's existing vendor modules.

## Validation limits

Compilation and a module symbol audit cannot prove boot compatibility,
correct runtime structure layouts or performance improvement. Neither
HyperOS nor AOSP has been device-tested with this build. New firmware can
change the module ABI even while continuing to use Linux 6.6.
The default target is current ROM releases, with compatibility taking priority.
A single ZIP cannot promise compatibility with every future firmware update;
new module interfaces must be checked before rebuilding for those releases.
The gki-clo CRC bypass is now included at the user's request. It cannot guarantee
boot on every ROM: incompatible layouts or function interfaces can still crash
after a module loads. Accepting a CRC mismatch does not prove compatibility.

Aggressive filesystem tuning includes a 30-second ext4 journal commit
interval instead of five seconds, which extends the window for losing recent
uncommitted writes after a sudden reset. O3 and the tuning patches are
experimental; speed gains require device benchmarks. Thermal protections
remain active. The optional maximum performance profile increases sustained
power consumption and heat and can be undone by rebooting.

## Upstream sources

- https://github.com/MiCode/Xiaomi_Kernel_OpenSource/tree/onyx-v-oss
- https://github.com/crdroidandroid/android_kernel_xiaomi_sm8735/tree/17.0
- https://github.com/WildKernels/GKI_KernelSU_SUSFS
- https://github.com/WildKernels/kernel_patches
- https://github.com/tiann/KernelSU
- https://gitlab.com/simonpunk/susfs4ksu
- https://github.com/maxsteeel/nomount
- https://github.com/vc-teahouse/Baseband-guard
- https://github.com/ravindu644/Droidspaces-OSS
- https://github.com/WildKernels/AnyKernel3
- https://github.com/gregkh/linux

Preserve upstream licenses and notices when redistributing source or binaries.
