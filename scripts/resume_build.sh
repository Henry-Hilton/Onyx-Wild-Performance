#!/usr/bin/env bash
set -euo pipefail
WORKSPACE=$(cd "$(dirname "$0")/.." && pwd)
ROOT=${ONYX_BUILD_ROOT:-/root/onyx-kernel-dev}
export PATH="$ROOT/toolchain/bin:$PATH"
export KBUILD_BUILD_USER=onyx KBUILD_BUILD_HOST=kernel-builder
make -C "$ROOT/kernel" O="$ROOT/out" ARCH=arm64 LLVM=1 -j"${JOBS:-8}" \
  KCFLAGS="-O3 -mtune=cortex-x4" Image.gz modules
python3 "$WORKSPACE/scripts/audit_modules.py" --symvers "$ROOT/out/vmlinux.symvers" \
  --output "$WORKSPACE/dist/crdroid-module-audit.json" > "$ROOT/module-audit-summary.log"
python3 "$WORKSPACE/scripts/audit_layouts.py" \
  /root/onyx-recovery-inputs/rom-images/original-kernel.btf "$ROOT/out/vmlinux" \
  "$WORKSPACE/dist/structure-layout-audit.json" > "$ROOT/layout-audit-summary.log"
python3 "$WORKSPACE/scripts/package.py" "$ROOT" "$WORKSPACE"
