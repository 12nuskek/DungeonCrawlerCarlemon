#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
mkdir -p artifacts/s03
evidence=$(mktemp -d "$repo/artifacts/s03/run-XXXXXX")
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
cp "$evidence/playtest.sav" "$evidence/trial-loss.sav"
run_route trial-defeat "$repo/docs/evidence/s03/trial-loss-defeat.route" 11 trial-loss.sav game.sym
run_route trial-retry "$repo/docs/evidence/s03/trial-loss-retry.route" 8 trial-loss.sav game.sym
run_route trial "$repo/docs/evidence/s03/trial.route" 61 playtest.sav game.sym
run_route rest "$repo/docs/evidence/s03/rest.route" 36 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/motion.sav"
run_route movement "$repo/docs/evidence/s03/movement.route" 9 motion.sav game.sym
run_route gates "$repo/docs/evidence/s03/gates.route" 23 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/guard-loss.sav"
run_route guard-defeat "$repo/docs/evidence/s03/guard-defeat.route" 12 guard-loss.sav game.sym
run_route guard-retry "$repo/docs/evidence/s03/guard-retry.route" 8 guard-loss.sav game.sym
run_route guard "$repo/docs/evidence/s03/guard.route" 13 playtest.sav game.sym
run_route guard-rest "$repo/docs/evidence/s03/guard-rest.route" 12 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/howler-loss.sav"
run_route howler-defeat "$repo/docs/evidence/s03/howler-defeat.route" 12 howler-loss.sav game.sym
run_route howler-retry "$repo/docs/evidence/s03/howler-retry.route" 8 howler-loss.sav game.sym
run_route howler "$repo/docs/evidence/s03/howler.route" 13 playtest.sav game.sym
run_route boss-rest "$repo/docs/evidence/s03/boss-rest.route" 14 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/boss-loss.sav"
cp "$evidence/playtest.sav" "$evidence/carl-down.sav"
cp "$evidence/playtest.sav" "$evidence/prepared.sav"
run_route boss-pattern "$repo/docs/evidence/s03/boss-pattern.route" 9 playtest.sav game.sym
run_route boss-defeat "$repo/docs/evidence/s03/boss-loss-defeat.route" 13 boss-loss.sav game.sym
run_route boss-retry "$repo/docs/evidence/s03/boss-loss-retry.route" 8 boss-loss.sav game.sym
run_route carl-down "$repo/docs/evidence/s03/carl-down-defeat.route" 13 carl-down.sav game.sym
run_route carl-down-retry "$repo/docs/evidence/s03/carl-down-retry.route" 8 carl-down.sav game.sym
run_route boss-unprepared "$repo/docs/evidence/s03/boss-unprepared.route" 19 playtest.sav game.sym
run_route stairs "$repo/docs/evidence/s03/stairs.route" 14 playtest.sav game.sym
run_route ending-reload "$repo/docs/evidence/s03/ending-reload.route" 25 playtest.sav game.sym
run_route preparation "$repo/docs/evidence/s03/preparation.route" 21 prepared.sav game.sym
cp "$evidence/prepared.sav" "$evidence/prepared-loss.sav"
run_route prepared-defeat "$repo/docs/evidence/s03/prepared-loss-defeat.route" 14 prepared-loss.sav game.sym
run_route prepared-retry "$repo/docs/evidence/s03/prepared-loss-retry.route" 8 prepared-loss.sav game.sym
run_route boss-prepared "$repo/docs/evidence/s03/boss-prepared.route" 20 prepared.sav game.sym
run_route prepared-ending "$repo/docs/evidence/s03/prepared-ending.route" 12 prepared.sav game.sym
run_route prepared-reload "$repo/docs/evidence/s03/prepared-reload.route" 12 prepared.sav game.sym
run_route quest-decline "$repo/docs/evidence/d01/decline.route" 13 quest.sav game.sym
run_route quest-accept-trap "$repo/docs/evidence/d01/accept-trap.route" 16 quest.sav game.sym
run_route quest-tag-secret "$repo/docs/evidence/d01/tag-secret.route" 15 quest.sav game.sym
run_route quest-complete-recover "$repo/docs/evidence/d01/complete-recover.route" 22 quest.sav game.sym
run_route quest-reload-final "$repo/docs/evidence/d01/reload-final.route" 18 quest.sav game.sym
run_route craft-materials "$repo/docs/evidence/d02/materials.route" 16 craft.sav game.sym
run_route craft-craft "$repo/docs/evidence/d02/craft.route" 13 craft.sav game.sym
run_route craft-blast-use "$repo/docs/evidence/d02/blast-use.route" 17 craft.sav game.sym
run_route craft-reload-recover "$repo/docs/evidence/d02/reload-recover.route" 13 craft.sav game.sym
run_route craft-reload-final "$repo/docs/evidence/d02/reload-final.route" 8 craft.sav game.sym
run_route collection-setup "$repo/docs/evidence/e01/new-game.route" 16 collection.sav game.sym
run_route collection-menus "$repo/docs/evidence/b03/menus.route" 14 collection.sav game.sym
run_route collection-guide "$repo/docs/evidence/b02/guide-before-trial.route" 10 collection.sav game.sym
run_route collection-battle "$repo/docs/evidence/b03/battle-menu.route" 10 collection.sav game.sym
run_route equipment-setup "$repo/docs/evidence/e01/new-game.route" 16 equipment.sav game.sym
run_route equipment-give "$repo/docs/evidence/r01/acquire-equip.route" 15 equipment.sav game.sym
run_route equipment-reload "$repo/docs/evidence/s03/equipment-reload.route" 5 equipment.sav game.sym
# Explicit diagnostic ROMs start from restored production source each time.
cp "$repo/engine/src/crawler.c" "$evidence/original-crawler.c"
cp "$repo/engine/src/battle_script_commands.c" "$evidence/original-battle-script-commands.c"
fixture() {
    local name=$1 script=$2
    cp "$evidence/original-crawler.c" "$repo/engine/src/crawler.c"
    cp "$evidence/original-battle-script-commands.c" "$repo/engine/src/battle_script_commands.c"
    python3 "$repo/scripts/$script" "$repo"
    make -C "$repo/engine" -j"${JOBS:-2}" > "$evidence/$name-build.log" 2>&1
    cp "$repo/engine/pokeemerald.gba" "$evidence/$name.gba"
    sha256sum "$evidence/$name.gba" > "$evidence/$name-rom.sha256"
    arm-none-eabi-nm -g --defined-only "$repo/engine/pokeemerald.elf" > "$evidence/$name.sym"
    python3 "$repo/scripts/battle-input-symbols.py" "$repo/engine" >> "$evidence/$name.sym"
}
fixture collection-fixture collection-fixture.py
run_route collection-fixture-policy "$repo/docs/evidence/b03/policy.route" 3 collection-fixture.sav collection-fixture.sym "$evidence/collection-fixture.gba"
fixture equipment-fixture equipment-fixture.py
run_route equipment-fixture-setup "$repo/docs/evidence/r01/fixture-setup.route" 19 equipment-fixture.sav equipment-fixture.sym "$evidence/equipment-fixture.gba"
run_route equipment-fixture-capacity "$repo/docs/evidence/r01/capacity.route" 11 equipment-fixture.sav equipment-fixture.sym "$evidence/equipment-fixture.gba"
fixture reward-fixture reward-fixture.py
run_route reward-fixture-capacity "$repo/docs/evidence/r02/capacity.route" 28 reward-fixture.sav reward-fixture.sym "$evidence/reward-fixture.gba"
run_route reward-fixture-reload "$repo/docs/evidence/r02/capacity-reload.route" 9 reward-fixture.sav reward-fixture.sym "$evidence/reward-fixture.gba"
fixture quest-fixture quest-fixture.py
run_route quest-fixture-capacity "$repo/docs/evidence/d01/capacity.route" 21 quest-fixture.sav quest-fixture.sym "$evidence/quest-fixture.gba"
run_route quest-fixture-reload "$repo/docs/evidence/d01/capacity-reload.route" 9 quest-fixture.sav quest-fixture.sym "$evidence/quest-fixture.gba"
fixture craft-fixture crafting-fixture.py
run_route craft-fixture-capacity "$repo/docs/evidence/d02/capacity.route" 33 craft-fixture.sav craft-fixture.sym "$evidence/craft-fixture.gba"
run_route craft-fixture-reload "$repo/docs/evidence/d02/capacity-reload.route" 11 craft-fixture.sav craft-fixture.sym "$evidence/craft-fixture.gba"
fixture exhaust-fixture exhaustion-fixture.py
run_route exhaust-fixture-setup "$repo/docs/evidence/s03/exhaust-setup.route" 20 exhaust-fixture.sav exhaust-fixture.sym "$evidence/exhaust-fixture.gba"
run_route exhaust-fixture-battle "$repo/docs/evidence/s03/exhaust-battle.route" 10 exhaust-fixture.sav exhaust-fixture.sym "$evidence/exhaust-fixture.gba"
run_route exhaust-fixture-recover "$repo/docs/evidence/s03/exhaust-recover.route" 13 exhaust-fixture.sav exhaust-fixture.sym "$evidence/exhaust-fixture.gba"
run_route exhaust-fixture-reload "$repo/docs/evidence/s03/exhaust-reload.route" 6 exhaust-fixture.sav exhaust-fixture.sym "$evidence/exhaust-fixture.gba"
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
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "S03 routes passed. Production and labeled fixture ROMs remain local; never commit ROMs/saves/executables. Pacing review is separate."
