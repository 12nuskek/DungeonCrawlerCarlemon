#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
: "${DCC_LEGACY_RUN:?Full acceptance requires the ordinary I01 save directory; see docs/testing.md}"
: "${DCC_CORNER_SAVE:?Full acceptance requires the ordinary N01 corner save; see docs/testing.md}"
for input in "$DCC_LEGACY_RUN/motion.sav" "$DCC_LEGACY_RUN/craft.sav" "$DCC_LEGACY_RUN/playtest.sav" "$DCC_CORNER_SAVE"; do
    test -s "$input" || { echo "Required legacy input missing or empty: $input" >&2; exit 2; }
done
git diff --quiet && git diff --cached --quiet || { echo 'Commit tracked changes first.' >&2; exit 2; }
revision=$(git rev-parse HEAD)
task=t01
if [[ "${DCC_MEMBERSHIP_PROBES:-0}" == 1 ]]; then task=a01; fi
mkdir -p "artifacts/floor1/$task"
evidence=$(mktemp -d "$repo/artifacts/floor1/$task/run-XXXXXX")
echo "Evidence: $evidence"
printf '%s\n' "$revision" > "$evidence/tested-commit.txt"
# Build only the captured commit: no ignored products or untracked source can leak in.
mkdir "$evidence/source"
git archive "$revision" | tar -x -C "$evidence/source"
repo="$evidence/source"
python3 "$repo/scripts/check-dungeon-invariants.py" "$repo" "$repo/scripts/contracts/n01-baseline.json" > "$evidence/invariants.json"
python3 "$repo/scripts/check-dungeon-connectivity.py" "$repo" > "$evidence/connectivity.json"
python3 "$repo/scripts/verify-opponent-art.py" "$repo" > "$evidence/native-art.json"
bash "$repo/scripts/setup-foundation.sh" > "$evidence/setup-toolchain.log" 2>&1
make -C "$repo/engine" -j"${JOBS:-2}" > "$evidence/build.log" 2>&1
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
sha256sum "$evidence/production.gba" > "$evidence/rom.sha256"
run_route setup "$repo/docs/evidence/s03/setup.route" 34 playtest.sav game.sym
run_route ui "$repo/docs/evidence/s03/ui.route" 16 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/trial-loss.sav"
run_route trial-defeat "$repo/docs/evidence/s03/trial-loss-defeat.route" 11 trial-loss.sav game.sym
run_route trial-retry "$repo/docs/evidence/s03/trial-loss-retry.route" 8 trial-loss.sav game.sym
run_route trial "$repo/docs/evidence/s03/trial.route" 61 playtest.sav game.sym
run_route rest "$repo/docs/evidence/s03/rest.route" 36 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/motion.sav"
run_route movement "$repo/docs/evidence/s03/movement.route" 9 motion.sav game.sym
run_route gates "$repo/scripts/routes/n03/gates.route" 30 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/both-pending.sav"
run_route both-pending "$repo/scripts/routes/n00b/both-pending.route" 8 both-pending.sav game.sym
cp "$evidence/playtest.sav" "$evidence/alternate.sav"
cp "$evidence/playtest.sav" "$evidence/guard-loss.sav"
run_route guard-defeat "$repo/docs/evidence/s03/guard-defeat.route" 12 guard-loss.sav game.sym
run_route guard-retry "$repo/docs/evidence/s03/guard-retry.route" 8 guard-loss.sav game.sym
run_route guard "$repo/docs/evidence/s03/guard.route" 13 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/howler-pending.sav"
run_route howler-pending "$repo/scripts/routes/n00b/howler-pending.route" 8 howler-pending.sav game.sym
run_route guard-rest "$repo/docs/evidence/s03/guard-rest.route" 12 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/howler-loss.sav"
run_route howler-defeat "$repo/docs/evidence/s03/howler-defeat.route" 12 howler-loss.sav game.sym
run_route howler-retry "$repo/docs/evidence/s03/howler-retry.route" 8 howler-loss.sav game.sym
run_route howler "$repo/docs/evidence/s03/howler.route" 13 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/boss-pending.sav"
run_route boss-pending "$repo/scripts/routes/n00b/boss-pending.route" 8 boss-pending.sav game.sym
run_route boss-rest "$repo/docs/evidence/s03/boss-rest.route" 14 playtest.sav game.sym
cp "$evidence/playtest.sav" "$evidence/boss-loss.sav"
cp "$evidence/playtest.sav" "$evidence/carl-down.sav"
cp "$evidence/playtest.sav" "$evidence/prepared.sav"
run_route boss-pattern "$repo/docs/evidence/s03/boss-pattern.route" 9 playtest.sav game.sym
run_route boss-defeat "$repo/scripts/routes/n03/boss-defeat.route" 20 boss-loss.sav game.sym
run_route boss-retry "$repo/scripts/routes/n03/boss-retry.route" 14 boss-loss.sav game.sym
run_route carl-down "$repo/docs/evidence/s03/carl-down-defeat.route" 13 carl-down.sav game.sym
run_route carl-down-retry "$repo/docs/evidence/s03/carl-down-retry.route" 8 carl-down.sav game.sym
run_route boss-unprepared "$repo/scripts/routes/n03/boss-unprepared.route" 27 playtest.sav game.sym
run_route stairs "$repo/scripts/routes/n03/stairs.route" 20 playtest.sav game.sym
run_route ending-reload "$repo/docs/evidence/s03/ending-reload.route" 25 playtest.sav game.sym
run_route preparation "$repo/docs/evidence/s03/preparation.route" 21 prepared.sav game.sym
cp "$evidence/prepared.sav" "$evidence/prepared-loss.sav"
run_route prepared-defeat "$repo/docs/evidence/s03/prepared-loss-defeat.route" 14 prepared-loss.sav game.sym
run_route prepared-retry "$repo/docs/evidence/s03/prepared-loss-retry.route" 8 prepared-loss.sav game.sym
run_route boss-prepared "$repo/scripts/routes/n03/boss-prepared.route" 33 prepared.sav game.sym
run_route prepared-ending "$repo/docs/evidence/s03/prepared-ending.route" 12 prepared.sav game.sym
run_route prepared-reload "$repo/scripts/routes/n03/prepared-reload.route" 12 prepared.sav game.sym
run_route quest-decline "$repo/docs/evidence/d01/decline.route" 13 quest.sav game.sym
run_route quest-accept-trap "$repo/scripts/routes/n03/quest-accept-trap.route" 17 quest.sav game.sym
run_route quest-tag-secret "$repo/scripts/routes/n03/quest-tag-secret.route" 18 quest.sav game.sym
run_route quest-complete-recover "$repo/docs/evidence/s03/quest-complete-recover.route" 22 quest.sav game.sym
run_route quest-reload-final "$repo/scripts/routes/n03/quest-reload-final.route" 20 quest.sav game.sym
run_route craft-materials "$repo/docs/evidence/d02/materials.route" 16 craft.sav game.sym
run_route craft-craft "$repo/docs/evidence/d02/craft.route" 13 craft.sav game.sym
run_route craft-blast-use "$repo/docs/evidence/d02/blast-use.route" 17 craft.sav game.sym
run_route craft-reload-recover "$repo/docs/evidence/d02/reload-recover.route" 13 craft.sav game.sym
run_route craft-reload-final "$repo/docs/evidence/d02/reload-final.route" 8 craft.sav game.sym
run_route collection-setup "$repo/docs/evidence/e01/new-game.route" 16 collection.sav game.sym
run_route collection-menus "$repo/docs/evidence/b03/menus.route" 14 collection.sav game.sym
run_route collection-guide "$repo/docs/evidence/s03/collection-guide.route" 10 collection.sav game.sym
run_route collection-battle "$repo/docs/evidence/s03/collection-battle.route" 10 collection.sav game.sym
run_route equipment-setup "$repo/docs/evidence/e01/new-game.route" 16 equipment.sav game.sym
run_route equipment-give "$repo/docs/evidence/r01/acquire-equip.route" 15 equipment.sav game.sym
run_route equipment-reload "$repo/docs/evidence/s03/equipment-reload.route" 5 equipment.sav game.sym
run_route continuous-prepared "$repo/scripts/routes/n02/continuous-prepared.route" 127 continuous.sav game.sym
run_route continuous-reload "$repo/docs/evidence/s03/continuous-reload.route" 10 continuous.sav game.sym
# Explicit diagnostic ROMs start from restored production source each time.
cp "$repo/engine/src/crawler.c" "$evidence/original-crawler.c"
cp "$repo/engine/src/battle_script_commands.c" "$evidence/original-battle-script-commands.c"
cp "$repo/engine/src/crawler_identity.c" "$evidence/original-crawler-identity.c"
cp "$repo/engine/data/maps/DCC_Entrance/scripts.inc" "$evidence/original-entrance-scripts.inc"
fixture() {
    local name=$1 script=$2
    cp "$evidence/original-crawler.c" "$repo/engine/src/crawler.c"
    cp "$evidence/original-battle-script-commands.c" "$repo/engine/src/battle_script_commands.c"
    cp "$evidence/original-crawler-identity.c" "$repo/engine/src/crawler_identity.c"
    cp "$evidence/original-entrance-scripts.inc" "$repo/engine/data/maps/DCC_Entrance/scripts.inc"
    python3 "$repo/scripts/$script" "$repo" "${3:-}"
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
run_route quest-fixture-capacity "$repo/scripts/routes/f1-t01/handin-capacity.route" 25 quest-fixture.sav quest-fixture.sym "$evidence/quest-fixture.gba"
run_route quest-fixture-reload "$repo/scripts/routes/f1-t01/handin-cold.route" 11 quest-fixture.sav quest-fixture.sym "$evidence/quest-fixture.gba"
fixture tag-fixture floor1/tag-capacity-fixture.py
run_route tag-fixture-full "$repo/scripts/routes/f1-t01/pickup-full.route" 14 tag-fixture.sav tag-fixture.sym "$evidence/tag-fixture.gba"
run_route tag-fixture-cold "$repo/scripts/routes/f1-t01/pickup-full-cold.route" 7 tag-fixture.sav tag-fixture.sym "$evidence/tag-fixture.gba"
fixture craft-fixture crafting-fixture.py
run_route craft-fixture-capacity "$repo/docs/evidence/d02/capacity.route" 33 craft-fixture.sav craft-fixture.sym "$evidence/craft-fixture.gba"
run_route craft-fixture-reload "$repo/docs/evidence/d02/capacity-reload.route" 11 craft-fixture.sav craft-fixture.sym "$evidence/craft-fixture.gba"
fixture exhaust-fixture exhaustion-fixture.py
run_route exhaust-fixture-setup "$repo/docs/evidence/s03/exhaust-setup.route" 20 exhaust-fixture.sav exhaust-fixture.sym "$evidence/exhaust-fixture.gba"
run_route exhaust-fixture-battle "$repo/docs/evidence/s03/exhaust-battle.route" 10 exhaust-fixture.sav exhaust-fixture.sym "$evidence/exhaust-fixture.gba"
run_route exhaust-fixture-recover "$repo/docs/evidence/s03/exhaust-recover.route" 13 exhaust-fixture.sav exhaust-fixture.sym "$evidence/exhaust-fixture.gba"
run_route exhaust-fixture-reload "$repo/docs/evidence/s03/exhaust-reload.route" 6 exhaust-fixture.sav exhaust-fixture.sym "$evidence/exhaust-fixture.gba"
run_route howler-first "$repo/scripts/routes/n00b/howler-first.route" 11 alternate.sav game.sym
run_route guard-pending "$repo/scripts/routes/n00b/guard-pending.route" 8 alternate.sav game.sym
if [[ -n "${DCC_LEGACY_RUN:-}" ]]; then
    cp "$DCC_LEGACY_RUN/motion.sav" "$evidence/legacy-landing.sav"
    cp "$DCC_LEGACY_RUN/craft.sav" "$evidence/legacy-workshop.sav"
    cp "$DCC_LEGACY_RUN/playtest.sav" "$evidence/legacy-ending.sav"
    sha256sum "$evidence"/legacy-*.sav > "$evidence/legacy-inputs.sha256"
    run_route legacy-landing "$repo/scripts/routes/n01/legacy-landing.route" 10 legacy-landing.sav game.sym
    run_route legacy-workshop "$repo/scripts/routes/n01/legacy-workshop.route" 11 legacy-workshop.sav game.sym
    run_route legacy-ending "$repo/scripts/routes/n01/legacy-ending.route" 20 legacy-ending.sav game.sym
fi
run_route rooms "$repo/docs/evidence/n01/before/input.route" 18 playtest.sav game.sym
run_route shape-probes "$repo/scripts/routes/n02/shape-probes.route" 47 playtest.sav game.sym
if [[ -n "${DCC_CORNER_SAVE:-}" ]]; then
    cp "$DCC_CORNER_SAVE" "$evidence/legacy-corner.sav"
    sha256sum "$evidence/legacy-corner.sav" > "$evidence/legacy-input.sha256"
    run_route legacy-corner "$repo/scripts/routes/n02/legacy-corner.route" 8 legacy-corner.sav game.sym
fi
run_route wire-setup "$repo/docs/evidence/d01/decline.route" 13 wire.sav game.sym
run_route wire-pair "$repo/scripts/routes/f1-t01/wire-pair.route" 23 wire.sav game.sym
run_route wire-cold "$repo/scripts/routes/f1-t01/wire-cold.route" 7 wire.sav game.sym
cp "$evidence/wire.sav" "$evidence/text.sav"
run_route text-state "$repo/scripts/routes/f1-t01/state-probe.route" 25 text.sav game.sym
run_route text-return-cold "$repo/scripts/routes/f1-t01/return-cold.route" 5 text.sav game.sym
run_route text-return-reentry "$repo/scripts/routes/f1-t01/return-reentry.route" 11 text.sav game.sym
cp "$evidence/quest.sav" "$evidence/text-complete.sav"
run_route text-complete "$repo/scripts/routes/f1-t01/completed-cold.route" 7 text-complete.sav game.sym
cp "$evidence/motion.sav" "$evidence/guide-after-trial.sav"
cp "$evidence/craft.sav" "$evidence/guide-before-trial.sav"
run_route guide-after-trial "$repo/scripts/routes/n05/after-trial.route" 6 guide-after-trial.sav game.sym
run_route guide-before-trial "$repo/scripts/routes/n05/before-trial.route" 6 guide-before-trial.sav game.sym
if [[ "${DCC_MEMBERSHIP_PROBES:-0}" == 1 ]]; then
    fixture membership-fixture floor1/membership-fixture.py
    run_route membership-fixture-policy "$repo/scripts/routes/f1-a01/membership.route" 3 membership-fixture.sav membership-fixture.sym "$evidence/membership-fixture.gba"
    fixture membership-extended-fixture floor1/membership-fixture.py extended
    run_route membership-extended-fixture-policy "$repo/scripts/routes/f1-a01/membership.route" 3 membership-extended-fixture.sav membership-extended-fixture.sym "$evidence/membership-extended-fixture.gba"
fi
python3 "$repo/scripts/render-walk.py" "$evidence/movement" "$evidence/walking.gif" > "$evidence/walking-render.log"
python3 - "$evidence" <<'PYIMG'
from pathlib import Path
from PIL import Image
import json,os,re,sys
root=Path(sys.argv[1]);results=[]
for path in root.glob('*/*.ppm'):
    if path.parent.name!='movement' or not path.name.startswith('walk-'):
        Image.open(path).save(path.with_suffix('.png'))
for log in sorted(root.glob('*/replay.log')):
    match=re.search(r'result=0 assertions=(\d+)\n$',log.read_text())
    assert match and not (log.parent/'errors.log').stat().st_size
    results.append({'route':log.parent.name,'assertions':int(match[1]),'fixture':'fixture' in log.parent.name})
(root/'validation-summary.json').write_text(json.dumps(results,indent=2)+'\n')
extended=os.environ.get('DCC_MEMBERSHIP_PROBES')=='1'
expected=(86,1399,226) if extended else (84,1393,220)
assert (len(results),sum(x['assertions'] for x in results),sum(x['assertions'] for x in results if x['fixture']))==expected, ('incomplete route coverage',expected)
# Continuous normal-input route: no mid-run boot/load or save-state injection.
route=(root/'source/scripts/routes/n02/continuous-prepared.route').read_text()
log=(root/'continuous-prepared/replay.log').read_text()
steps=[tuple(map(int,line.split()[1:3])) for line in route.splitlines() if line.startswith('step ')]
frames=int(re.findall(r'frame=(\d+) map',log)[-1])
pilots=[int(n) for n in re.findall(r'pilot completed policy=\w+ frames=(\d+)',log)]
assert frames==sum(n for n,k in steps)+sum(pilots)
timing={'normal_gba_hz':59.7275,'total_frames':frames,'total_seconds':frames/59.7275,
        'startup_frames':sum(n for n,k in steps[:9]),
        'fixed_zero_input_frames_including_startup':sum(n for n,k in steps if k==0),
        'scripted_button_frames':sum(n for n,k in steps if k!=0),
        'battle_pilot_frames':pilots,'mid_route_reboots':0,
        'interpretation':'Automated continuous prepared route with fixed waits; not fresh-player reading or decision time.'}
(root/'pacing.json').write_text(json.dumps(timing,indent=2)+'\n')

print('PASS',len(results),'sessions,',sum(x['assertions'] for x in results),'assertions; inspect actual images/motion before acceptance')
PYIMG
python3 "$repo/scripts/verify-opponent-frames.py" "$evidence" > "$evidence/opponent-pixels.json"
python3 "$repo/scripts/verify-environment-props.py" "$evidence" > "$evidence/prop-pixels.json"
python3 "$repo/scripts/verify-dungeon-presentation.py" "$evidence" > "$evidence/presentation-pixels.json"
test "$(git rev-parse HEAD)" = "$revision"
git diff --quiet && git diff --cached --quiet
echo "F1-$task full regression passed. Production and labeled fixture ROMs remain local; never commit ROMs/saves/executables. Pacing review is separate."
