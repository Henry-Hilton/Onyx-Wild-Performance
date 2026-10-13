#!/usr/bin/env bash
set -euo pipefail
ROOT=/root/onyx-kernel-dev
/root/onyx-kernel-dev/xiaomi/scripts/extract-ikconfig /root/onyx-recovery-inputs/rom-images/boot-unpacked/kernel > "$ROOT/crdroid-stock.config"
grep -E '^CONFIG_(LOCALVERSION|KASAN|CFI|MODVERSIONS|MODULE_SIG|HZ|ANDROID|LTO|DEBUG_INFO_BTF|ARM64_.*PAGES)' "$ROOT/crdroid-stock.config"
python3 /mnt/c/Users/Henry/Documents/ChatGPT/Android/scripts/audit_modules.py
