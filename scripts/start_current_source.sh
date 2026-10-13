#!/usr/bin/env bash
set -euo pipefail
ROOT=/root/onyx-kernel-dev
WORKSPACE=$(cd "$(dirname "$0")/.." && pwd)
test -f "$ROOT/crdroid/Makefile"
test ! -e "$ROOT/official-port-research"
test "$(realpath "$ROOT/kernel")" = /root/onyx-kernel-dev/kernel
mv "$ROOT/kernel" "$ROOT/official-port-research"
python3 "$WORKSPACE/scripts/prepare_kernel.py"
git -C "$ROOT/xiaomi" diff --full-index v6.6.142 v6.6.143 > "$ROOT/stable-142-to-143.patch"
git -C "$ROOT/kernel" apply --check "$ROOT/stable-142-to-143.patch"
git -C "$ROOT/kernel" apply "$ROOT/stable-142-to-143.patch"
head -n 6 "$ROOT/kernel/Makefile"
