#!/usr/bin/env python3
"""Read-only opening4 trace/snapshot analysis. No emulator or replay entry point."""
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['Carl', 'Guard', 'Donut', 'Scuttler']
MOVES = {33: 'TACKLE', 355: 'STRIKE', 356: 'BRACE', 357: 'SPARK', 358: 'WEAKEN'}


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def analyze(retained):
    manifest_raw = (retained / 'private-retention-manifest.json').read_bytes()
    assert hashlib.sha256(manifest_raw).hexdigest() == 'bef0eb27e3f90ca500fe33d908b6b17c79de4a7168d3391dbd909c9da322fd30'
    manifest = json.loads(manifest_raw)
    checked = []

    def verified(relative):
        entry = manifest['entries'][relative]
        assert entry['bytes'] <= 16 * 1024**2
        raw = (retained / relative).read_bytes()
        assert len(raw) == entry['bytes']
        assert hashlib.sha256(raw).hexdigest() == entry['SHA256']
        checked.append(dict(file=relative, **entry))
        return raw

    helper = module('opening4_retained_helpers', ROOT / 'scripts/analyze-f1-c01-retained-guard.py')
    state = module('opening4_retained_state', ROOT / 'scripts/floor1/guard-choice-r2-state.py')
    orders = state.fields.orders()
    state.fields.orders = lambda: orders
    raw = verified('opening/complete-battle-trace-private.bin')
    log = verified('opening/runtime.log').decode()
    verified('STOP.json')
    for use in (1, 2):
        for name in ('field', 'bag', 'before', 'healed', 'return'):
            verified(f'opening/medicine-{use:02}-{name}-state.bin')
        verified(f'opening/medicine-{use:02}-order.bin')
    positions = state.audit(retained / 'opening')
    assert positions == [0, 0]
    samples, events, invalid = {}, [], []
    last = None
    assert len(raw) == 14295 * 1040
    for offset in range(0, len(raw), 1040):
        packet = raw[offset:offset + 1040]
        meta = struct.unpack_from('<16I', packet)
        mons = [helper.battle_mon(packet[664 + i * 88:752 + i * 88]) for i in range(4)]
        if meta[11] == 1:
            samples[meta[0]] = mons
            for i in range(2):
                if not state.fields.decode(packet[64 + i * 100:164 + i * 100])['checksum_valid']:
                    invalid.append(dict(frame=meta[0], actor=NAMES[2 * i]))
            if last and last[0][11] == 1:
                oldmeta, old = last
                for i in range(4):
                    delta = {k: [old[i][k], mons[i][k]] for k in ('HP', 'PP', 'stages', 'level', 'maxHP') if old[i][k] != mons[i][k]}
                    if delta:
                        events.append(dict(frame=meta[0], turn=meta[2], actor=NAMES[i], delta=delta,
                                           metadata=dict(move=MOVES.get(meta[3], str(meta[3])),
                                                         attacker=NAMES[meta[6]], target=NAMES[meta[7]],
                                                         critical_multiplier=meta[5], result_flags=meta[12],
                                                         damage=meta[13])))
        last = meta, mons
    choices = []
    for m in re.finditer(r'^GUARD_CHOICE absolute=(\d+) turn=(\d+) CarlHP=(\d+) DonutHP=(\d+) GuardAlive=(\d+) Potion=(\d+) choice=(\d+)$', log, re.M):
        frame, turn, chp, dhp, alive, potion, choice = map(int, m.groups())
        mons = samples[frame]
        assert [chp, dhp] == [mons[0]['HP'], mons[2]['HP']]
        assert alive == bool(mons[1]['HP'])
        choices.append(dict(frame=frame, turn=turn, HP=[x['HP'] for x in mons],
                            Carl_PP=mons[0]['PP'][:2], Donut_PP=mons[2]['PP'][:2],
                            Guard_defense_stage=mons[1]['stages'][2], Potion=potion, choice=choice))
    assert len(choices) == 5 and choices[-1]['frame'] == 27144 and choices[-1]['choice'] == 101
    metrics = 0
    pattern = r'^TURN_METRIC absolute=(\d+) encounter=856 turn=(\d+) actor=(\d+) menu=(\d+) selection=(\d+) key=(\d+) HP=([\d,]+) PP=([\d,]+) stages=([\d,]+)$'
    for match in re.finditer(pattern, log, re.M):
        frame = int(match[1])
        mm = samples[frame]
        assert list(map(int, match[7].split(','))) == [m['HP'] for m in mm]
        assert list(map(int, match[8].split(','))) == mm[0]['PP'][:2] + mm[2]['PP'][:2]
        assert list(map(int, match[9].split(','))) == [mm[0]['stages'][2], mm[1]['stages'][1], mm[3]['stages'][1]]
        metrics += 1
    assert metrics == 4785
    mons = samples[27144]
    assert [m['stats'][2] for m in mons] == [13, 15, 23, 12]
    assert [m['HP'] for m in mons] == [22, 3, 18, 18]
    guard_normal, guard_crit = [helper.tackle_bounds(mons[1], mons[0], c) for c in (False, True)]
    scut_normal, scut_crit = [helper.tackle_bounds(mons[3], mons[0], c) for c in (False, True)]
    assert [guard_normal, guard_crit, scut_normal, scut_crit] == [[5, 7], [12, 15], [5, 6], [10, 12]]
    terminal = state.snapshot(retained / 'opening/first-invalid-or-partial-medicine-state.bin')
    verified('opening/first-invalid-or-partial-medicine-state.bin')
    # Native flag layout SYSTEM_FLAGS=0x860; badge offsets7/9/B/D.
    assert '0x860' in (ROOT / 'engine/include/constants/flags.h').read_text()
    for flag in (0x867, 0x869, 0x86b, 0x86d):
        assert not terminal['flags'][flag // 8] & (1 << (flag % 8))
    assert all(m['held_item'] == 0 and m['status1'] == 0 for m in mons)
    assert all(m['stages'][6:] == [6, 6] for m in mons)
    carl = bytearray(state.fields.decode(terminal['party'][:100])['canonical'])
    assert struct.unpack_from('<I', carl, 36)[0] == 495
    carl[60] += 1  # source-earned Spinda Special Attack EV, arithmetic only
    stats = state.prior.level_stats(carl, 10)
    assert stats[0] == 36 and stats[2] == 17
    level10 = dict(mons[0], stats=stats[1:], level=10, maxHP=stats[0])
    assert helper.tackle_bounds(mons[3], level10, True) == [7, 9]
    # Native integer-order normal STRIKE at terminal +1 Guard Defense, no STAB.
    defense = mons[1]['stats'][1] * 15 // 10
    strike_max = mons[0]['stats'][0] * 40 * (2 * mons[0]['level'] // 5 + 2) // defense // 50 + 2
    assert [strike_max * 85 // 100, strike_max] == [5, 6]
    assert ((85 * 9 // 7) // 2) * 150 // 100 == 81
    assert max(15 + 6, 7 + 12) == 21
    closure_invalid = [x for x in invalid if 25419 <= x['frame'] <= 25502 or 26451 <= x['frame'] <= 26534]
    return dict(analysis_base='4cff72680be2256fd35531eb4ed2a643fb45da1e',
                input_files_verified=checked, battle_packets=14295, Guard_packets=len(samples),
                Guard_TURN_METRIC_crosschecks=metrics,
                choices=choices, observed_events=events, terminal_battle_mons=mons,
                medicine=dict(uses=2, complete_snapshot_and_acknowledgement_recheck='PASS',
                              inventory_positions=positions, checksum_invalid_guard_actor_samples=invalid,
                              checksum_invalid_ack_to_return_samples=closure_invalid,
                              instruction_path_coverage='not recorded per frame; specific gt_transition cuts remain offline-only'),
                source_bounds=dict(Guard_to_Carl_normal=guard_normal, Guard_to_Carl_critical=guard_crit,
                                   Scuttler_to_Carl_normal=scut_normal, Scuttler_to_Carl_critical=scut_crit,
                                   one_critical_plus_ordinary=21, simultaneous_critical=27,
                                   terminal_STRIKE_normal=[5, 6], Guard_KO_XP=81,
                                   Carl_XP_after_Guard_KO=576, Carl_level10_stats=stats,
                                   Scuttler_to_Carl_level10_critical=[7, 9],
                                   terminal_turn_Carl_minimum_HP=22-15+3-9),
                gameplay_processes_added=0, freeze_or_claim_added=False, Save_or_cold_added=False,
                changed_input_RNG_predicted=False)


if __name__ == '__main__':
    assert len(sys.argv) == 2
    print(json.dumps(analyze(Path(sys.argv[1])), indent=2, sort_keys=True))
