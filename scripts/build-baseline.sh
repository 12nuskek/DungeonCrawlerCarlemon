#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
mkdir -p "$repo/artifacts"
make -C "$repo/engine" -j"${JOBS:-2}" 2>&1 | tee "$repo/artifacts/build.log"
make -C "$repo/engine" compare 2>&1 | tee "$repo/artifacts/compare.log"
sha256sum "$repo/engine/pokeemerald.gba" | tee "$repo/artifacts/rom.sha256"
