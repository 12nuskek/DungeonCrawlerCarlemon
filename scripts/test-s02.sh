#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir -p artifacts/s02
evidence=$(mktemp -d "$repo/artifacts/s02/run-XXXXXX")
echo "Evidence: $evidence"
printf '%s\n' "$revision" > "$evidence/tested-commit.txt"
# Build only the captured commit: no ignored products or untracked source can leak in.
mkdir "$evidence/source"
git archive "$revision" | tar -x -C "$evidence/source"
repo="$evidence/source"
bash "$repo/scripts/setup-foundation.sh" > "$evidence/setup-toolchain.log" 2>&1
make -C "$repo/engine" -j"${JOBS:-2}" > "$evidence/build.log" 2>&1
sha256sum "$repo/engine/pokeemerald.gba" > "$evidence/rom.sha256"
arm-none-eabi-nm -g --defined-only "$repo/engine/pokeemerald.elf" > "$evidence/game.sym"
cc -std=gnu11 -Wall -Wextra -Werror ${DCC_TEST_CFLAGS:-} "$repo/scripts/playtest.c" ${DCC_TEST_LDFLAGS:-} -lmgba -o "$evidence/playtest"
run_route() {
    local name=$1 route=$2 assertions=$3 savefile=${4:-playtest.sav} symbols=${5:-game.sym}
    mkdir "$evidence/$name"
    (cd "$evidence/$name"
     ../playtest "$repo/engine/pokeemerald.gba" "../$savefile" "../$symbols" < "$route" > replay.log 2> errors.log
     grep -q "result=0 assertions=$assertions$" replay.log
     test ! -s errors.log)
}
cp "$repo/engine/pokeemerald.gba" "$evidence/production.gba"
python3 "$repo/scripts/check-slice-art.py" > "$evidence/asset-check.log"
run_route title "$repo/docs/evidence/s02/title.route" 1 title.sav
run_route setup "$repo/docs/evidence/s02/setup.route" 32
run_route ui "$repo/docs/evidence/s02/ui.route" 13
run_route trial "$repo/docs/evidence/s02/trial.route" 31
run_route rest "$repo/docs/evidence/s02/rest.route" 34
run_route gates "$repo/docs/evidence/s01/gates.route" 17
python3 - "$evidence" <<'PYIMG'
from pathlib import Path
from PIL import Image
import sys
for path in Path(sys.argv[1]).glob('*/*.ppm'):
    Image.open(path).save(path.with_suffix('.png'))
PYIMG
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "S02 routes passed; visually review captures in $evidence. All routes use the production ROM; no fixtures. S03 full progression regression remains separate. Never commit ROMs/saves/executables."
