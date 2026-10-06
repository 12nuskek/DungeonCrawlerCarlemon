#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir -p artifacts/b03
evidence=$(mktemp -d "$repo/artifacts/b03/run-XXXXXX")
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
    local name=$1 route=$2 assertions=$3
    mkdir "$evidence/$name"
    (cd "$evidence/$name"
     ../playtest "$repo/engine/pokeemerald.gba" ../playtest.sav ../game.sym < "$route" > replay.log 2> errors.log
     grep -q "result=0 assertions=$assertions$" replay.log
     test ! -s errors.log)
}
run_route setup "$repo/docs/evidence/e01/new-game.route" 16
# Loss never saves: the subsequent cold boot still starts at the pre-trial save.
run_route menus "$repo/docs/evidence/b03/menus.route" 14
run_route guide-before-trial "$repo/docs/evidence/b02/guide-before-trial.route" 10
run_route support-defeat "$repo/docs/evidence/b02/support-defeat.route" 19
run_route depletion-victory "$repo/docs/evidence/b02/depletion-victory.route" 28
run_route reload "$repo/docs/evidence/b02/reload.route" 10
# Explicit GBA-side fixture, patched only in the isolated source after production runs.
cp "$evidence/rom.sha256" "$evidence/production-rom.sha256"
python3 "$repo/scripts/collection-fixture.py" "$repo"
# Record separate identity, full build log and symbols for this scripted fixture.
make -C "$repo/engine" -j"${JOBS:-2}" > "$evidence/fixture-build.log" 2>&1
sha256sum "$repo/engine/pokeemerald.gba" > "$evidence/fixture-rom.sha256"
arm-none-eabi-nm -g --defined-only "$repo/engine/pokeemerald.elf" > "$evidence/fixture.sym"
mkdir "$evidence/fixture"
(cd "$evidence/fixture"
 ../playtest "$repo/engine/pokeemerald.gba" fixture.sav ../fixture.sym < "$repo/docs/evidence/b03/policy.route" > replay.log 2>errors.log
 grep -q 'result=0 assertions=3$' replay.log
 test ! -s errors.log)
python3 - "$evidence" <<'PY'
from pathlib import Path
from PIL import Image
import sys
for path in Path(sys.argv[1]).glob('*/*.ppm'):
    Image.open(path).save(path.with_suffix('.png'))
PY
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "B03 routes passed; visually review captures in $evidence. No ROM/save/executable belongs in source commits."
