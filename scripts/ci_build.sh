#!/usr/bin/env bash
set -euo pipefail
WORKSPACE=$(cd "$(dirname "$0")/.." && pwd)
ROOT=${ONYX_BUILD_ROOT:-"$WORKSPACE/.build"}
python3 "$WORKSPACE/scripts/prepare_ci_sources.py" "$ROOT"
mkdir -p "$ROOT/out" "$WORKSPACE/dist"
cp "$WORKSPACE/configs/kernel.config" "$ROOT/out/.config"
cp "$WORKSPACE/configs/requested-features.json" "$ROOT/out/requested-features.json"
export KBUILD_BUILD_USER=onyx KBUILD_BUILD_HOST=kernel-builder
make -C "$ROOT/kernel" O="$ROOT/out" ARCH=arm64 LLVM=-21 \
  KSU_GIT_VERSION=2680 KSU_GIT_VERSION_VALID=1 olddefconfig
python3 "$WORKSPACE/scripts/check_features.py" "$ROOT/out/.config"
make -C "$ROOT/kernel" O="$ROOT/out" ARCH=arm64 LLVM=-21 -j"${JOBS:-2}" \
  KSU_GIT_VERSION=2680 KSU_GIT_VERSION_VALID=1 KCFLAGS="-O3 -mtune=cortex-x4" Image.gz modules
python3 "$WORKSPACE/scripts/audit_modules.py" --baseline "$WORKSPACE/abi/modules.json" \
  --symvers "$ROOT/out/vmlinux.symvers" --output "$WORKSPACE/dist/crdroid-module-audit.json"
python3 "$WORKSPACE/scripts/audit_layouts.py" "$WORKSPACE/abi/layouts.json" "$ROOT/out/vmlinux" \
  "$WORKSPACE/dist/structure-layout-audit.json"
python3 "$WORKSPACE/scripts/package_ci.py" "$ROOT" "$WORKSPACE"
