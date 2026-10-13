#!/usr/bin/env bash
set -euo pipefail
# Usage: build_exported_source.sh /path/to/extracted/kernel /path/to/kernel.config /path/to/out
KERNEL=$(realpath "$1")
CONFIG=$(realpath "$2")
mkdir -p "$3"
OUT=$(realpath "$3")
cp "$CONFIG" "$OUT/.config"
export KBUILD_BUILD_USER=onyx KBUILD_BUILD_HOST=kernel-builder
make -C "$KERNEL" O="$OUT" ARCH=arm64 LLVM="${LLVM:--21}" \
  KSU_GIT_VERSION=2680 KSU_GIT_VERSION_VALID=1 olddefconfig
make -C "$KERNEL" O="$OUT" ARCH=arm64 LLVM="${LLVM:--21}" -j"${JOBS:-8}" \
  KSU_GIT_VERSION=2680 KSU_GIT_VERSION_VALID=1 \
  KCFLAGS="-O3 -mtune=cortex-x4" Image.gz modules
