#!/usr/bin/env python3
"""Source-bound damage and storage checks; no gameplay, media export or private input."""
import copy
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('analysis', ROOT / 'scripts/analyze-f1-c01-retained-guard.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

pokemon = (ROOT / 'engine/src/pokemon.c').read_text()
ratios = pokemon.split('const u8 gStatStageRatios', 1)[1].split('};', 1)[0]
assert a.RATIOS == [tuple(map(int, p)) for p in re.findall(r'\{(\d+), (\d+)\}', ratios)]
assert 'return damage + 2;' in pokemon
assert 'if (attacker->statStages[STAT_ATK] > DEFAULT_STAT_STAGE)' in pokemon
assert 'if (defender->statStages[STAT_DEF] < DEFAULT_STAT_STAGE)' in pokemon
commands = (ROOT / 'engine/src/battle_script_commands.c').read_text()
assert 'u16 randPercent = 100 - (rand % 16);' in commands
assert 'gBattleMoveDamage = gBattleMoveDamage * gCritMultiplier * gBattleScripting.dmgMultiplier;' in commands
assert 'gBattleMoveDamage = gBattleMoveDamage * 15;' in commands
assert '#define MOVE_RESULT_MISSED             (1 << 0)' in (ROOT / 'engine/include/constants/battle.h').read_text()

def mon(attack, defense, level, types):
    return dict(stats=[attack, defense, 0, 0, 0], level=level, types=types,
                stages=[6]*8, ability=0, held_item=0, status1=0)

guard, scuttler = mon(15, 15, 9, [0, 0]), mon(9, 11, 8, [0, 0])
carl, donut = mon(23, 15, 9, [1, 1]), mon(14, 13, 9, [0, 0])
assert a.tackle_bounds(guard, carl, False) == [5, 7]
assert a.tackle_bounds(guard, carl, True) == [12, 15]
assert a.tackle_bounds(scuttler, carl, True) == [10, 12]
assert a.tackle_bounds(guard, donut, True) == [15, 18]
assert a.tackle_bounds(scuttler, donut, True) == [10, 12]
weakened, braced = copy.deepcopy(guard), copy.deepcopy(carl)
weakened['stages'][1], braced['stages'][2] = 5, 7
assert a.tackle_bounds(weakened, carl, False) == [5, 6]
assert a.tackle_bounds(guard, braced, False) == [5, 6]
assert a.tackle_bounds(weakened, braced, True) == [12, 15]
carl10 = mon(25, 17, 10, [1, 1])
scuttler['stages'][1] = 2
assert a.tackle_bounds(scuttler, carl10, False) == [3, 4]
assert a.tackle_bounds(scuttler, carl10, True) == [7, 9]
# Trial Wurmple Tackle has no Normal STAB; retain this negative instead of
# treating all Tackle users as the Guard's Normal species.
wurmple = mon(12, 9, 8, [6, 6])
assert a.tackle_bounds(wurmple, mon(20, 14, 8, [1, 1]), False) == [4, 5]

opponent = (ROOT / 'engine/src/battle_controller_opponent.c').read_text()
assert 'pattern = turn == 0 ? 1 : 0;' in opponent
assert 'gBattlerTarget = GetBattlerAtPosition(B_POSITION_PLAYER_LEFT);' in opponent
for m, hp in zip((carl, guard, donut, scuttler), (33, 29, 28, 24)):
    m['HP'] = hp
r0 = a.risk([carl, guard, donut, scuttler], 'guard', 0)
r1 = a.risk([carl, guard, donut, scuttler], 'guard', 1)
assert r0['Carl']['all_critical_round_max'] == r0['Donut']['all_critical_round_max'] == 12
assert r1['Carl']['all_critical_round_max'] == 27 and r1['Donut']['all_critical_round_max'] == 12
assert not r1['Donut']['per_enemy']['enemy1']['reachable_incoming_TACKLE']

for frames in (1, 999, 1000, 1001, 31258, 100000):
    p = a.export_capacity(frames)
    ranges = [(i*1000+1, min(frames, (i+1)*1000)) for i in range(p['chunk_count'])]
    assert ranges[0][0] == 1 and ranges[-1][1] == frames
    assert sum(end-start+1 for start,end in ranges) == frames
    assert all(ranges[i][1]+1 == ranges[i+1][0] for i in range(len(ranges)-1))
    assert p['RGB_bytes'] == frames*115200
    assert p['additional_export_reservation_bytes'] == (len(ranges)+1)*268435456
assert a.export_capacity(31258)['additional_export_reservation_bytes'] == 8858370048
assert a.export_capacity(100000)['additional_export_reservation_bytes'] == 27111981056
print('PASS source ratios/critical bypass/STAB/miss flag/Guard move-target pattern/observed damage bounds and six export range/capacity geometries; zero emulators/encoders')
