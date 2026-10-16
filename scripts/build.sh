#!/usr/bin/env bash
set -euo pipefail
WORKSPACE=$(cd "$(dirname "$0")/.." && pwd)
ROOT=${ONYX_BUILD_ROOT:-/root/onyx-kernel-dev}
KERNEL="$ROOT/kernel"
OUT="$ROOT/out"
export PATH="$ROOT/toolchain/bin:$PATH"
export KBUILD_BUILD_USER=onyx KBUILD_BUILD_HOST=kernel-builder
JOBS=${JOBS:-8}
mkdir -p "$OUT" "$WORKSPACE/dist"
make -C "$KERNEL" O="$OUT" ARCH=arm64 LLVM=1 gki_defconfig
python3 "$WORKSPACE/scripts/configure_features.py" "$KERNEL" "$OUT"
make -C "$KERNEL" O="$OUT" ARCH=arm64 LLVM=1 olddefconfig
python3 "$WORKSPACE/scripts/check_features.py" "$OUT/.config"
make -C "$KERNEL" O="$OUT" ARCH=arm64 LLVM=1 headers_install
make -C "$KERNEL" O="$OUT" ARCH=arm64 LLVM=1 -j"$JOBS" \
  KCFLAGS="-O3 -mtune=cortex-x4" Image.gz modules
python3 "$WORKSPACE/scripts/audit_modules.py" --symvers "$OUT/vmlinux.symvers" \
  --output "$WORKSPACE/dist/crdroid-module-audit.json" > "$ROOT/module-audit-summary.log"
python3 "$WORKSPACE/scripts/audit_layouts.py" \
  /root/onyx-recovery-inputs/rom-images/original-kernel.btf "$OUT/vmlinux" \
  "$WORKSPACE/dist/structure-layout-audit.json" > "$ROOT/layout-audit-summary.log"
python3 "$WORKSPACE/scripts/package.py" "$ROOT" "$WORKSPACE"
