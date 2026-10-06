#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir -p artifacts/d02
evidence=$(mktemp -d "$repo/artifacts/d02/run-XXXXXX")
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
run_route materials "$repo/docs/evidence/d02/materials.route" 16
run_route craft "$repo/docs/evidence/d02/craft.route" 13
run_route blast-use "$repo/docs/evidence/d02/blast-use.route" 17
run_route reload-recover "$repo/docs/evidence/d02/reload-recover.route" 13
run_route reload-final "$repo/docs/evidence/d02/reload-final.route" 8
# Explicit fixture: full bag, Scrap98/Charge99/SuperPotion99; workshop achievement unlocked.
python3 "$repo/scripts/crafting-fixture.py" "$repo"
make -C "$repo/engine" -j"${JOBS:-2}" > "$evidence/fixture-build.log" 2>&1
sha256sum "$repo/engine/pokeemerald.gba" > "$evidence/fixture-rom.sha256"
arm-none-eabi-nm -g --defined-only "$repo/engine/pokeemerald.elf" > "$evidence/fixture.sym"
run_route capacity "$repo/docs/evidence/d02/capacity.route" 33 fixture.sav fixture.sym
run_route capacity-reload "$repo/docs/evidence/d02/capacity-reload.route" 11 fixture.sav fixture.sym
python3 - "$evidence" <<'PYIMG'
from pathlib import Path
from PIL import Image
import sys
for path in Path(sys.argv[1]).glob('*/*.ppm'):
    Image.open(path).save(path.with_suffix('.png'))
PYIMG
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "D02 routes passed; visually review captures in $evidence. Local production.gba is separate from the fixture. Never commit ROMs/saves/executables."
