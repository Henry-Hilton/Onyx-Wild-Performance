#!/usr/bin/env bash
set -euo pipefail
ROOT=/root/onyx-kernel-dev
git -C "$ROOT/xiaomi" fetch --depth=1 https://github.com/gregkh/linux.git tag v6.6.56 tag v6.6.143
git -C "$ROOT/xiaomi" diff v6.6.56 v6.6.143 > "$ROOT/stable-56-to-143.patch"
wc -l "$ROOT/stable-56-to-143.patch"
