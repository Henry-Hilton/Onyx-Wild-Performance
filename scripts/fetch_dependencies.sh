#!/usr/bin/env bash
set -euo pipefail
cd /root/onyx-kernel-dev
clone() {
  local name=$1 url=$2 branch=$3
  if [[ ! -d $name ]]; then
    git clone --depth 1 --single-branch -b "$branch" "$url" "$name"
  fi
}
clone patches https://github.com/WildKernels/kernel_patches.git main
clone susfs https://gitlab.com/simonpunk/susfs4ksu.git gki-android15-6.6
clone kernelsu https://github.com/tiann/KernelSU.git main
clone nomount https://github.com/maxsteeel/nomount.git dev
clone bbg https://github.com/vc-teahouse/Baseband-guard.git main
clone droidspaces https://github.com/ravindu644/Droidspaces-OSS.git main
clone anykernel https://github.com/WildKernels/AnyKernel3.git gki-2.0
