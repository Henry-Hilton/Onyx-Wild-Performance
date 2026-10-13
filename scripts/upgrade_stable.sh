#!/usr/bin/env bash
set -euo pipefail
ROOT=/root/onyx-kernel-dev
cd "$ROOT/kernel"
git config user.name 'Onyx Kernel Development'
git config user.email 'onyx-kernel@localhost'
git add -A
git commit -m 'onyx: integrate WildKernels features before stable refresh'
git apply --3way "$ROOT/stable-56-to-143.patch" > "$ROOT/stable-merge.log" 2>&1 || {
  git diff --name-only --diff-filter=U > "$ROOT/stable-conflicts.txt"
  echo 'Stable update needs conflict resolution:'
  cat "$ROOT/stable-conflicts.txt"
  tail -n 10 "$ROOT/stable-merge.log"
  exit 1
}
git commit -m 'UPSTREAM: update official onyx kernel to Linux 6.6.143'
