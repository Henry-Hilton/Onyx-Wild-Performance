#!/usr/bin/env bash
set -euo pipefail
for tree in xiaomi konoha gki-clo; do
  root=/root/onyx-kernel-dev/$tree
  if [[ -f $root/Makefile ]]; then
    echo "=== $tree ==="
    git -C "$root" rev-parse HEAD
    head -n 6 "$root/Makefile"
    find "$root" -name AGENTS.md -print
    ls "$root/arch/arm64/configs/" | grep -E 'gki|konoha|capybara|vendor' || true
    git -C "$root" log -1 --format='%s'
  fi
done
