#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir -p artifacts/s01
evidence=$(mktemp -d "$repo/artifacts/s01/run-XXXXXX")
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
run_route setup "$repo/docs/evidence/r02/setup-rewards.route" 32
run_route trial "$repo/docs/evidence/r02/victory-loot.route" 53
run_route rest "$repo/docs/evidence/r02/reload-reentry.route" 34
run_route gates "$repo/docs/evidence/s01/gates.route" 17
run_route guard "$repo/docs/evidence/s01/guard.route" 19
run_route guard-rest "$repo/docs/evidence/s01/guard-rest.route" 12
run_route howler "$repo/docs/evidence/s01/howler.route" 16
# Branch only ordinary saved flash from the same fresh-play route; no RAM writes.
cp "$evidence/playtest.sav" "$evidence/defeat.sav"
run_route boss-rest "$repo/docs/evidence/s01/boss-rest.route" 14
cp "$evidence/playtest.sav" "$evidence/prepared.sav"
run_route boss-pattern "$repo/docs/evidence/s01/boss-pattern.route" 9
run_route boss-unprepared "$repo/docs/evidence/s01/boss-unprepared.route" 25
run_route stairs "$repo/docs/evidence/s01/stairs.route" 10
run_route ending-reload "$repo/docs/evidence/s01/ending-reload.route" 15
run_route preparation "$repo/docs/evidence/s01/preparation.route" 21 prepared.sav
run_route boss-prepared "$repo/docs/evidence/s01/boss-prepared.route" 24 prepared.sav
run_route prepared-ending "$repo/docs/evidence/s01/prepared-ending.route" 12 prepared.sav
run_route prepared-reload "$repo/docs/evidence/s01/prepared-reload.route" 12 prepared.sav
run_route boss-defeat "$repo/docs/evidence/s01/boss-defeat.route" 21 defeat.sav
run_route defeat-reload "$repo/docs/evidence/s01/defeat-reload.route" 11 defeat.sav
python3 - "$evidence" <<'PYIMG'
from pathlib import Path
from PIL import Image
import sys
for path in Path(sys.argv[1]).glob('*/*.ppm'):
    Image.open(path).save(path.with_suffix('.png'))
PYIMG
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "S01 routes passed; visually review captures in $evidence. All routes use the production ROM; prepared/defeat branches copy normal manual saves. Never commit ROMs/saves/executables."
