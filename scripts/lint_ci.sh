#!/usr/bin/env bash
set -euo pipefail
ROOT=${TMPDIR:-/tmp}/onyx-actionlint
mkdir -p "$ROOT"
curl --fail --location --silent --show-error \
  https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz \
  -o "$ROOT/actionlint.tar.gz"
tar -xzf "$ROOT/actionlint.tar.gz" -C "$ROOT" actionlint
"$ROOT/actionlint" -shellcheck= .github/workflows/build-release.yml
bash -n scripts/ci_build.sh scripts/build_exported_source.sh anykernel/anykernel.sh
python3 -m compileall -q scripts
