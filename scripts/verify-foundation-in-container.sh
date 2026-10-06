#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/boot
dpkg-query -W > artifacts/packages.tsv
bash scripts/setup-foundation.sh > artifacts/setup.log 2>&1
bash scripts/build-baseline.sh > artifacts/build-driver.log 2>&1
cc -std=gnu11 -Wall -Wextra -Werror scripts/boot-baseline.c -lmgba -o artifacts/boot-baseline
cd artifacts/boot
../boot-baseline ../../engine/pokeemerald.gba < ../../docs/evidence/f01/route.txt > boot.log 2> mgba.log
python3 - <<'PY'
from pathlib import Path
from PIL import Image
for path in Path('.').glob('*.ppm'):
    Image.open(path).save(path.with_suffix('.png'))
PY
