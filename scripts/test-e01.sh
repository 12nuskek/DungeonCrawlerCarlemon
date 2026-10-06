#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir -p artifacts/e01
evidence=$(mktemp -d "$repo/artifacts/e01/run-XXXXXX")
echo "Evidence: $evidence"
printf '%s\n' "$revision" > "$evidence/tested-commit.txt"
make -C engine -j"${JOBS:-2}" > "$evidence/build.log" 2>&1
sha256sum engine/pokeemerald.gba > "$evidence/rom.sha256"
arm-none-eabi-nm -g --defined-only engine/pokeemerald.elf > "$evidence/game.sym"
# Optional include/library flags support workspace-local dependency installs.
cc -std=gnu11 -Wall -Wextra -Werror ${CFLAGS:-} scripts/playtest.c ${LDFLAGS:-} -lmgba -o "$evidence/playtest"
cd "$evidence"
./playtest "$repo/engine/pokeemerald.gba" playtest.sav game.sym < "$repo/docs/evidence/e01/new-game.route" > new-game.log 2> new-game-errors.log
grep -q 'result=0 assertions=16' new-game.log
# A separate process boots from the actual flash save, never an emulator savestate.
./playtest "$repo/engine/pokeemerald.gba" playtest.sav game.sym < "$repo/docs/evidence/e01/reload.route" > reload.log 2> reload-errors.log
grep -q 'result=0 assertions=3' reload.log
python3 - <<'PY'
from pathlib import Path
from PIL import Image
for path in Path('.').glob('*.ppm'):
    Image.open(path).save(path.with_suffix('.png'))
PY
cd "$repo"
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "E01 route passed; visually review captures in $evidence. Do not commit its ROM, executable, symbols or save."
