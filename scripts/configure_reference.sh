#!/usr/bin/env bash
set -euo pipefail
ROOT=/root/onyx-kernel-dev
mkdir -p "$ROOT/toolchain/bin"
for tool in clang ld.lld llvm-ar llvm-nm llvm-objcopy llvm-objdump llvm-readelf llvm-strip; do
  if command -v "$tool-21" >/dev/null; then
    ln -sfn "$(command -v "$tool-21")" "$ROOT/toolchain/bin/$tool"
  fi
done
export PATH="$ROOT/toolchain/bin:$PATH"
for tree in xiaomi konoha gki-clo; do
  cfg=gki_defconfig
  [[ $tree == konoha ]] && cfg=konoha_defconfig
  [[ $tree == gki-clo ]] && cfg=capybara_defconfig
  if [[ $tree == xiaomi ]]; then
    # Published Xiaomi source omits these separately supplied vendor modules.
    # Their options are disabled in GKI; remove only unresolved source entries.
    sed -i '\|source "drivers/misc/hwid/Kconfig"|d' "$ROOT/$tree/drivers/misc/Kconfig"
    sed -i '\|source "drivers/power/supply/mca/Kconfig"|d' "$ROOT/$tree/drivers/power/supply/Kconfig"
  fi
  if [[ $tree == konoha ]]; then
    sed -i '\|source "drivers/kernelsu/Kconfig"|d' "$ROOT/$tree/drivers/Kconfig"
  fi
  make -s -C "$ROOT/$tree" O="$ROOT/config-$tree" ARCH=arm64 LLVM=1 "$cfg" > "$ROOT/config-$tree.log" 2>&1
done
python3 /mnt/c/Users/Henry/Documents/ChatGPT/Android/scripts/compare_configs.py
