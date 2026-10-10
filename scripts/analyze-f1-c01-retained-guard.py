#!/usr/bin/env python3
"""Bounded, read-only retained C01 r2 analysis. Never starts an emulator/encoder.

Only allowlisted decoded fields leave this module. Inputs and their identities
remain private; source and processed findings may be reviewed publicly.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {0: 'Carl', 1: 'enemy1', 2: 'Donut', 3: 'enemy3'}
MOVES = {33: 'TACKLE', 355: 'STRIKE', 356: 'BRACE', 357: 'SPARK', 358: 'WEAKEN'}
PHASES = {5: 'trial', 8: 'guard'}
RATIOS = [(10, 40), (10, 35), (10, 30), (10, 25), (10, 20), (10, 15),
          (10, 10), (15, 10), (20, 10), (25, 10), (30, 10), (35, 10), (40, 10)]
FRAME_BYTES = 240 * 160 * 3


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def battle_mon(q):
    return dict(species=struct.unpack_from('<H', q)[0],
                stats=list(struct.unpack_from('<5H', q, 2)),
                moves=list(struct.unpack_from('<4H', q, 12)),
                stages=list(q[24:32]), ability=q[32], types=list(q[33:35]),
                PP=list(q[36:40]), HP=struct.unpack_from('<H', q, 40)[0],
                level=q[42], maxHP=struct.unpack_from('<H', q, 44)[0],
                held_item=struct.unpack_from('<H', q, 46)[0],
                status1=struct.unpack_from('<I', q, 76)[0])


def tackle_bounds(attacker, defender, critical):
    """Integer-order bounds, not Random(), seeds, roll enumeration or replay.

    Restricted to observed neutral Normal Tackle, no damaging abilities, status,
    held items, badges or screens. These actors have no Attack-raising move.
    The unobserved screen/badge assumptions are separately declared in findings.
    """
    assert defender['types'][0] in (0, 1)
    assert attacker['ability'] not in (37, 55, 62)  # Huge/Pure Power, Hustle/Guts below
    assert attacker['ability'] not in (74,) and defender['ability'] != 63
    assert not attacker['held_item'] and not defender['held_item']
    assert not attacker['status1'] and not defender['status1']
    a = attacker['stages'][1]
    d = defender['stages'][2]
    if critical:
        a, d = max(6, a), min(6, d)
    attack = attacker['stats'][0] * RATIOS[a][0] // RATIOS[a][1]
    defense = defender['stats'][1] * RATIOS[d][0] // RATIOS[d][1]
    base = max(1, attack * 35 * (2 * attacker['level'] // 5 + 2) // defense // 50) + 2
    base *= 2 if critical else 1
    if 0 in attacker['types']:
        base = base * 15 // 10  # Normal STAB, neutral matchup
    return [max(1, base * 85 // 100), base]


def risk(mons, phase, turn):
    result = {}
    foes = [b for b in (1, 3) if mons[b]['HP']]
    for b in (0, 2):
        # Authored GUARD uses BRACE turn0, then TACKLE on player-left Carl.
        # Its fallback/absent-Carl case is outside this first-incapacitation scope.
        reachable = [e for e in foes if not (phase == 'guard' and e == 1 and (turn == 0 or b == 2))]
        normal = [tackle_bounds(mons[e], mons[b], False)[1] for e in reachable]
        critical = [tackle_bounds(mons[e], mons[b], True)[1] for e in reachable]
        result[NAMES[b]] = dict(single_critical_max=max(critical, default=0),
                               all_critical_round_max=sum(critical),
                               one_critical_rest_normal_max=max(
                                   (sum(normal) - normal[i] + critical[i]
                                    for i in range(len(reachable))), default=0),
                               per_enemy={NAMES[e]: {'reachable_incoming_TACKLE': e in reachable,
                                                     'normal_matchup_bounds': tackle_bounds(mons[e], mons[b], False),
                                                     'critical_matchup_bounds': tackle_bounds(mons[e], mons[b], True)}
                                          for e in foes})
    return result


def export_capacity(frames):
    assert 0 < frames <= 100000
    chunk_frames, cap, overhead = 1000, 256 * 1024**2, 256 * 1024**2
    count = (frames + chunk_frames - 1) // chunk_frames
    return dict(frames=frames, RGB_bytes=frames * FRAME_BYTES,
                chunk_frames=chunk_frames, chunk_count=count,
                last_chunk_frames=frames - (count - 1) * chunk_frames,
                per_file_cap_bytes=cap, other_reserved_bytes=overhead,
                additional_export_reservation_bytes=count * cap + overhead,
                compression_ratio_assumed=False, codec_completion_guaranteed=False)


def analyze(retained):
    fields = module('retained_fields', ROOT / 'scripts/floor1/party-fields.py')
    orders = fields.orders()
    fields.orders = lambda: orders
    state = module('retained_state', ROOT / 'scripts/floor1/continuous-opening-state.py')
    manifest_raw = (retained / 'local-retention-manifest.json').read_bytes()
    prior_receipt = json.loads((ROOT / 'docs/evidence/floor1/c01/uninterrupted-unprepared-r2-20261010/local-retention-receipt.json').read_text())
    assert hashlib.sha256(manifest_raw).hexdigest() == prior_receipt['manifest_SHA256']
    manifest = json.loads(manifest_raw)

    def verified(relative, limit):
        path = retained / relative
        assert path.stat().st_size <= limit
        raw = path.read_bytes()
        entry = manifest['entries'][str(path)]
        assert len(raw) == entry['bytes'] and hashlib.sha256(raw).hexdigest() == entry['SHA256']
        return raw

    raw = verified('opening/complete-battle-trace-private.bin', 1040 * 100000)
    assert len(raw) % 1040 == 0
    samples, transient_slots = {}, 0
    for offset in range(0, len(raw), 1040):
        packet = raw[offset:offset + 1040]
        meta = struct.unpack_from('<16I', packet)
        assert meta[1] in PHASES and meta[8] in (0, 1) and meta[9] in (0, 1)
        mons = [battle_mon(packet[664 + i * 88:752 + i * 88]) for i in range(4)]
        party = []
        for i in range(2):
            decoded = fields.decode(packet[64 + i * 100:164 + i * 100])
            if not decoded['checksum_valid']:
                transient_slots += 1
                party.append(None)
            else:
                f = decoded['fields']
                party.append(dict(experience=f['experience'], level=f['level']))
        assert meta[0] not in samples
        samples[meta[0]] = dict(frame=meta[0], phase=PHASES[meta[1]], turn=meta[2],
                               move=meta[3], critical=meta[5], attacker=meta[6], target=meta[7],
                               result_flags=meta[12], native_damage=meta[13], outcome=meta[10],
                               mons=mons, party=party,
                               chosen=list(struct.unpack_from('<4H', packet, 1032)))
    log = verified('opening/runtime.log', 8 * 1024**2).decode()
    pattern = re.compile(r'TURN_METRIC absolute=(\d+) encounter=(\d+) turn=(\d+) actor=(\d+) menu=(\d+) selection=(\d+) key=(\d+) HP=([\d,]+) PP=([\d,]+) stages=([\d,]+)')
    metrics, boundaries, inputs = [], {}, {}
    for match in pattern.finditer(log):
        f, encounter, turn, actor, menu, selection, key = map(int, match.groups()[:7])
        s = samples[f]
        assert (encounter, s['phase']) in ((855, 'trial'), (856, 'guard'))
        assert turn == s['turn']
        hp, pp, stages = [list(map(int, v.split(','))) for v in match.groups()[7:]]
        assert hp == [m['HP'] for m in s['mons']]
        assert pp == s['mons'][0]['PP'][:2] + s['mons'][2]['PP'][:2]
        assert stages == [s['mons'][0]['stages'][2], s['mons'][1]['stages'][1], s['mons'][3]['stages'][1]]
        k = s['phase'], turn
        boundaries.setdefault(k, f)
        metrics.append(f)
        if actor in (0, 2) and menu and key:
            inputs.setdefault(k, []).append(dict(frame=f, actor=NAMES[actor], menu=menu,
                                                  selected=selection, key=key))
    events, active, last_party = [], {}, [None, None]
    previous = None
    for s in samples.values():
        if not previous or previous['phase'] != s['phase']:
            previous, last_party = s, s['party']
            continue
        common = dict(frame=s['frame'], phase=s['phase'], turn=s['turn'])
        for b in range(4):
            old, new = previous['mons'][b], s['mons'][b]
            for slot in range(2):
                if new['PP'][slot] == old['PP'][slot] - 1:
                    assert s['attacker'] == b and s['move'] == old['moves'][slot]
                    assert s['chosen'][b] == s['move']
                    event = dict(**common, kind='move', actor=NAMES[b], move=MOVES[s['move']],
                                 PP_before=old['PP'][slot], PP_after=new['PP'][slot],
                                 observed_initial_target=NAMES[s['target']],
                                 missed=bool(s['result_flags'] & 1))
                    events.append(event)
                    active[(s['phase'], s['turn'], b)] = event
            if new['HP'] < old['HP']:
                # Initialization/reuse is not an attack. Once pilot runs, all
                # damage must have a PP-decrement action in this native turn.
                if (s['phase'], s['turn']) not in boundaries:
                    continue
                action = active[(s['phase'], s['turn'], s['attacker'])]
                assert s['target'] == b and s['move'] in (33, 355, 357)
                event = dict(**common, kind='hit', actor=NAMES[s['attacker']], target=NAMES[b],
                             move=MOVES[s['move']], HP_before=old['HP'], HP_after=new['HP'],
                             HP_removed=old['HP'] - new['HP'], native_damage=s['native_damage'],
                             critical_multiplier=s['critical'], result_flags=s['result_flags'])
                assert event['HP_removed'] == min(old['HP'], event['native_damage'])
                if s['move'] == 33:
                    bound = tackle_bounds(s['mons'][s['attacker']], previous['mons'][b], s['critical'] == 2)
                    assert bound[0] <= s['native_damage'] <= bound[1]
                    event['source_damage_bounds'] = bound
                events.append(event)
                action.setdefault('observed_targets', []).append(NAMES[b])
            if new['stages'] != old['stages']:
                if s['move'] in (356, 358) and new['HP']:
                    events.append(dict(**common, kind='support', actor=NAMES[s['attacker']],
                                       target=NAMES[b], move=MOVES[s['move']],
                                       stages_before=old['stages'], stages_after=new['stages']))
                    active[(s['phase'], s['turn'], s['attacker'])].setdefault('observed_targets', []).append(NAMES[b])
            if b in (0, 2) and old['maxHP'] and new['maxHP'] > old['maxHP']:
                events.append(dict(**common, kind='level_HP_update', actor=NAMES[b],
                                   HP_before=old['HP'], HP_after=new['HP'],
                                   maxHP_before=old['maxHP'], maxHP_after=new['maxHP']))
        for i, p in enumerate(s['party']):
            if p is None:
                continue  # RAM reads can meet native decrypt/update/re-encrypt.
            if last_party[i] and p != last_party[i]:
                assert p['experience'] >= last_party[i]['experience']
                events.append(dict(**common, kind='XP_level', actor=('Carl', 'Donut')[i],
                                   before=last_party[i], after=p, checksum_valid=True))
            last_party[i] = p
        previous = s
    phases = {}
    for phase in ('trial', 'guard'):
        turns = sorted({e['turn'] for e in events if e['phase'] == phase and e['kind'] == 'move'})
        phase_samples = [s for s in samples.values() if s['phase'] == phase]
        table = []
        for turn in turns:
            start = boundaries[(phase, turn)]
            end = boundaries.get((phase, turn + 1), phase_samples[-1]['frame'] + 1) - 1
            a, z = samples[start], samples[end]
            turn_events = [e for e in events if e['phase'] == phase and e['turn'] == turn]
            for b in (0, 2):
                action = next(e for e in turn_events if e['kind'] == 'move' and e['actor'] == NAMES[b])
                assert any(i['actor'] == NAMES[b] and i['menu'] == 2 and i['key'] == 1
                           and MOVES[a['mons'][b]['moves'][i['selected']]] == action['move']
                           for i in inputs[(phase, turn)])
                if b == 0:
                    target = next(i for i in inputs[(phase, turn)]
                                  if i['actor'] == 'Carl' and i['menu'] == 3 and i['key'] == 1)
                    assert NAMES[target['selected']] == action['observed_initial_target']
            table.append(dict(turn=turn, first_metric_frame=start, last_sample_frame=end,
                              before={NAMES[b]: a['mons'][b] for b in range(4)},
                              after={NAMES[b]: z['mons'][b] for b in range(4)},
                              source_risk_before=risk(a['mons'], phase, turn), inputs=inputs[(phase, turn)],
                              available_inventory={'Potion': 2 if phase == 'trial' else 1,
                                                   'Scrap': 0 if phase == 'trial' else 2},
                              inventory_basis='accepted field endpoint plus no Bag actions in retained pilot',
                              events=turn_events))
        phases[phase] = table
    field_endpoints = []
    for i in range(8):
        relative = f'opening/phase-{i:02d}-state.bin'
        verified(relative, 3324)
        snap = state.snapshot(retained / relative)
        logical = snap['logical']
        quantities = {struct.unpack_from('<H', logical, 0xd0 + j*4)[0]:
                      struct.unpack_from('<H', logical, 0xd2 + j*4)[0] for j in range(30)}
        actors = []
        for j in range(2):
            f = fields.decode(snap['party'][j*100:(j+1)*100])['fields']
            actors.append(dict(actor=('Carl', 'Donut')[j], level=f['level'], XP=f['experience'],
                               HP=f['hp_maxhp_attack_defense_speed_spatk_spdef'][0],
                               maxHP=f['hp_maxhp_attack_defense_speed_spatk_spdef'][1], PP=f['PP'], status=f['status']))
        field_endpoints.append(dict(phase_index=i, actors=actors, Potion=quantities.get(13, 0),
                                    Scrap=quantities.get(378, 0), money=struct.unpack_from('<I', logical)[0]))
    cpu = struct.unpack('<24I', verified('opening/first-failure-CPU-context-private.bin', 96))
    assert cpu[0:4] == (31258, 90, 65535, 0) and cpu[20:22] == (1, 0)
    assert samples[31258]['mons'][0]['HP'] == 0 and samples[31258]['outcome'] == 0
    assert 'POTION_DEMONSTRATION necessary_survival_cost=0 demonstration_cost=1 actual_missingHP=4 native_capped_gain=4' in log
    return dict(analysis_base='56565c1ffdf24e025fe9d86d51e72fa9306149c4',
                runtime_helper='978cbf03907c38ef24fb4008bfed04e1c69daea5',
                game_source='4a92a9de70848b9d7275f9f255bb0d2f53232ab8',
                engine_tree='0fedd142f43f136ceee189c54101b095fc88f495',
                input_files_verified_against_existing_private_manifest=True,
                battle_packets=len(samples), TURN_METRIC_crosschecks=len(metrics),
                transient_checksum_invalid_actor_samples_excluded=transient_slots,
                CPU=dict(first_failure_frame=cpu[0], reason=cpu[1], GPRs_valid=16,
                         CPSR_valid=True, SPSR_valid=False, full_banked_context=False),
                phases=phases, field_endpoints=field_endpoints,
                terminal=dict(frame=31258, Carl_HP=0, Donut_HP=16, outcome=0,
                              resolved_defeat=False, gameplay_attempts_added=0),
                export_capacity=export_capacity(31258), future_100000_capacity=export_capacity(100000))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--retained', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    retained, output = args.retained.resolve(), args.output.resolve()
    assert retained not in output.parents and output != retained
    assert not output.exists(), 'separately named output; never overwrite retained results'
    result = analyze(retained)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ('battle_packets', 'TURN_METRIC_crosschecks',
                     'transient_checksum_invalid_actor_samples_excluded', 'terminal')}))


if __name__ == '__main__':
    main()
