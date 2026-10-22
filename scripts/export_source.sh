#!/usr/bin/env bash
set -euo pipefail
WORKSPACE=$(cd "$(dirname "$0")/.." && pwd)
ROOT=${ONYX_BUILD_ROOT:-/root/onyx-kernel-dev}
mkdir -p "$WORKSPACE/dist/source-patches"
mkdir -p "$ROOT/source-notices"
for component in kernelsu susfs nomount bbg; do
  cp "$ROOT/$component/LICENSE" "$ROOT/source-notices/$component-LICENSE"
done
cp "$WORKSPACE/README.md" "$ROOT/source-notices/README.md"
cp "$WORKSPACE/scripts/build_exported_source.sh" "$ROOT/source-notices/build_exported_source.sh"
cp "$WORKSPACE/scripts/patch_kpm.py" "$ROOT/source-notices/patch_kpm.py"
cp "$WORKSPACE/sources.lock.json" "$ROOT/source-notices/sources.lock.json"
for component in kernel kernelsu nomount bbg; do
  git -C "$ROOT/$component" diff --binary > "$WORKSPACE/dist/source-patches/$component.patch"
done
# Follow the three integrated dependency links so this archive can be extracted
# and built outside the original WSL directory. Omit Git metadata and build output.
tar --dereference --exclude='.git' --exclude='.github' \
  --exclude='kernel/arch/arm64/boot/dts/vendor' \
  --exclude='kernel/Documentation/devicetree/bindings' \
  --exclude='kernel/scripts/dtc/include-prefixes/arm64/vendor' \
  -czf "$WORKSPACE/dist/Onyx-Wild-Performance-source.tar.gz" \
  -C "$ROOT" kernel source-notices
(cd "$WORKSPACE/dist" && sha256sum Onyx-Wild-Performance-source.tar.gz \
  > Onyx-Wild-Performance-source.tar.gz.sha256)
