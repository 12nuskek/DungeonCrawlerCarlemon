#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir -p artifacts/b01
evidence=$(mktemp -d "$repo/artifacts/b01/run-XXXXXX")
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
run_route defeat "$repo/docs/evidence/b01/defeat.route" 8
run_route victory "$repo/docs/evidence/b01/victory.route" 9
run_route reload "$repo/docs/evidence/b01/reload.route" 5
python3 - "$evidence" <<'PY'
from pathlib import Path
from PIL import Image
import sys
for path in Path(sys.argv[1]).glob('*/*.ppm'):
    Image.open(path).save(path.with_suffix('.png'))
PY
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "B01 routes passed; visually review captures in $evidence. No ROM/save/executable belongs in source commits."
