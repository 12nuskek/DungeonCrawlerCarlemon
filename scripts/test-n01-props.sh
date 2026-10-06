#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir -p artifacts/n01-props
evidence=$(mktemp -d "$repo/artifacts/n01-props/run-XXXXXX")
echo "Evidence: $evidence"
printf '%s\n' "$revision" > "$evidence/tested-commit.txt"
# Build only the captured commit: no ignored products or untracked source can leak in.
mkdir "$evidence/source"
git archive "$revision" | tar -x -C "$evidence/source"
repo="$evidence/source"
python3 "$repo/scripts/check-dungeon-invariants.py" "$repo" "$repo/scripts/contracts/n01-baseline.json" > "$evidence/invariants.json"
python3 "$repo/scripts/verify-opponent-art.py" "$repo" > "$evidence/native-art.json"
bash "$repo/scripts/setup-foundation.sh" > "$evidence/setup-toolchain.log" 2>&1
make -C "$repo/engine" -j"${JOBS:-2}" > "$evidence/build.log" 2>&1
sha256sum "$repo/engine/pokeemerald.gba" > "$evidence/rom.sha256"
arm-none-eabi-nm -g --defined-only "$repo/engine/pokeemerald.elf" > "$evidence/game.sym"
python3 "$repo/scripts/battle-input-symbols.py" "$repo/engine" >> "$evidence/game.sym"
cc -std=gnu11 -Wall -Wextra -Werror ${DCC_TEST_CFLAGS:-} "$repo/scripts/playtest.c" ${DCC_TEST_LDFLAGS:-} -lmgba -o "$evidence/playtest"
run_route() {
    local name=$1 route=$2 assertions=$3 savefile=${4:-playtest.sav} symbols=${5:-game.sym} rom=${6:-"$evidence/production.gba"}
    mkdir "$evidence/$name"
    (cd "$evidence/$name"
     ../playtest "$rom" "../$savefile" "../$symbols" < "$route" > replay.log 2> errors.log
     grep -q "result=0 assertions=$assertions$" replay.log
     test ! -s errors.log)
}
cp "$repo/engine/pokeemerald.gba" "$evidence/production.gba"
run_route setup "$repo/docs/evidence/s03/setup.route" 34 playtest.sav game.sym
run_route ui "$repo/docs/evidence/s03/ui.route" 16 playtest.sav game.sym
run_route trial "$repo/docs/evidence/s03/trial.route" 61 playtest.sav game.sym
run_route rest "$repo/docs/evidence/s03/rest.route" 36 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/motion.sav"
run_route movement "$repo/docs/evidence/s03/movement.route" 9 motion.sav game.sym
run_route gates "$repo/docs/evidence/s03/gates.route" 23 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/both-pending.sav"
run_route both-pending "$repo/scripts/routes/n00b/both-pending.route" 8 both-pending.sav game.sym
cp "$evidence/playtest.sav" "$evidence/alternate.sav"
run_route guard "$repo/docs/evidence/s03/guard.route" 13 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/howler-pending.sav"
run_route howler-pending "$repo/scripts/routes/n00b/howler-pending.route" 8 howler-pending.sav game.sym
run_route guard-rest "$repo/docs/evidence/s03/guard-rest.route" 12 playtest.sav game.sym
run_route howler "$repo/docs/evidence/s03/howler.route" 13 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/boss-pending.sav"
run_route boss-pending "$repo/scripts/routes/n00b/boss-pending.route" 8 boss-pending.sav game.sym
run_route boss-rest "$repo/docs/evidence/s03/boss-rest.route" 14 playtest.sav game.sym
run_route boss-unprepared "$repo/docs/evidence/s03/boss-unprepared.route" 19 playtest.sav game.sym
run_route stairs "$repo/docs/evidence/s03/stairs.route" 14 playtest.sav game.sym
run_route ending-reload "$repo/docs/evidence/s03/ending-reload.route" 25 playtest.sav game.sym
run_route quest-decline "$repo/docs/evidence/d01/decline.route" 13 quest.sav game.sym
run_route quest-accept-trap "$repo/docs/evidence/d01/accept-trap.route" 16 quest.sav game.sym
run_route quest-tag-secret "$repo/docs/evidence/d01/tag-secret.route" 15 quest.sav game.sym
run_route quest-complete-recover "$repo/docs/evidence/s03/quest-complete-recover.route" 22 quest.sav game.sym
run_route quest-reload-final "$repo/docs/evidence/d01/reload-final.route" 18 quest.sav game.sym
run_route howler-first "$repo/scripts/routes/n00b/howler-first.route" 11 alternate.sav game.sym
run_route guard-pending "$repo/scripts/routes/n00b/guard-pending.route" 8 alternate.sav game.sym
run_route rooms "$repo/docs/evidence/n01/before/input.route" 18 playtest.sav game.sym
python3 "$repo/scripts/render-walk.py" "$evidence/movement" "$evidence/walking.gif" > "$evidence/walking-render.log"
python3 - "$evidence" <<'PYIMG'
from pathlib import Path
from PIL import Image
import json,re,sys
root=Path(sys.argv[1]);results=[]
for path in root.glob('*/*.ppm'):
    if path.parent.name!='movement' or not path.name.startswith('walk-'):
        Image.open(path).save(path.with_suffix('.png'))
for log in sorted(root.glob('*/replay.log')):
    match=re.search(r'result=0 assertions=(\d+)\n$',log.read_text())
    assert match and not (log.parent/'errors.log').stat().st_size
    results.append({'route':log.parent.name,'assertions':int(match[1]),'fixture':'fixture' in log.parent.name})
(root/'validation-summary.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS',len(results),'sessions,',sum(x['assertions'] for x in results),'assertions; inspect actual images/motion before acceptance')
PYIMG
python3 "$repo/scripts/verify-opponent-frames.py" "$evidence" > "$evidence/opponent-pixels.json"
python3 "$repo/scripts/verify-environment-props.py" "$evidence" > "$evidence/prop-pixels.json"
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "N01 props affected regression passed. Production and labeled fixture ROMs remain local; never commit ROMs/saves/executables. Pacing review is separate."
