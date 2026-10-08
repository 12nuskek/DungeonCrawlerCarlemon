#!/usr/bin/env python3
"""Offline source/retained-trace audit. No emulator, RNG, save writes or policy search."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

GAME = 'c643f01c11ec68119b0347b107ee20115131debc'
ROM_SHA = 'b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a'
SAVE_SHA = '026c16feccd0a1741ff0c3ec077e7272fc6ee43bf0e4fa12ab8953c50523220a'
TRACE_SHA = '598e6f5e7f3675e3d65d7a775e56af61671a7e0827463925800e7d9900046ba2'
SYMBOLS_SHA = 'b5ce937aa5d54594fc01957905be8ea977c6fdf8c14505db4fadf88be38edc4e'
ROOT = Path(__file__).resolve().parents[1]
RATIOS = [(10, 40), (10, 35), (10, 30), (10, 25), (10, 20), (10, 15),
          (10, 10), (15, 10), (20, 10), (25, 10), (30, 10), (35, 10), (40, 10)]
STAT_NAMES = ['max_hp', 'attack', 'defense', 'speed', 'special_attack', 'special_defense']
SOURCES = ['engine/include/global.h', 'engine/include/pokemon.h', 'engine/include/data.h',
           'engine/include/save.h', 'engine/src/save.c', 'engine/src/crawler.c',
           'engine/src/pokemon.c', 'engine/src/battle_main.c',
           'engine/src/battle_controller_opponent.c', 'engine/src/battle_ai_script_commands.c',
           'engine/data/battle_ai_scripts.s', 'engine/src/battle_script_commands.c',
           'engine/data/battle_scripts_1.s', 'engine/src/data/battle_moves.h',
           'engine/src/data/trainer_parties.h', 'engine/src/data/trainers.h',
           'engine/src/data/pokemon/species_info.h', 'engine/data/maps/DCC_Boss/scripts.inc']


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pinned(path, expected):
    data = path.read_bytes()
    if digest(data) != expected:
        raise ValueError(f'Pinned input mismatch: {path.name}')
    return data


def stage(stat, value):
    num, den = RATIOS[value + 6]
    return stat * num // den


def damage(attacker, defender, power, atk_stage=0, def_stage=0,
           critical=False, special=False, spread=False, stab=False):
    """Pinned integer order for this status/item/weather-free neutral matchup.

    Min/max only: no Random(), seed, trajectory, emulator or alternate roll.
    Spread is the two-live-foe case; reduction precedes the final base +2.
    """
    attack = attacker['special_attack' if special else 'attack']
    defense = defender['special_defense' if special else 'defense']
    attack = stage(attack, max(0, atk_stage) if critical else atk_stage)
    defense = stage(defense, min(0, def_stage) if critical else def_stage)
    base = attack * power * (2 * attacker['level'] // 5 + 2) // defense // 50
    if spread:
        base //= 2
    base = (base if special else max(1, base)) + 2
    if critical:
        base *= 2
    if stab:
        base = base * 15 // 10
    return [max(1, base * 85 // 100), base]


def saved_stats(save):
    # Full-slot headers establish the newest complete record. Read only plaintext
    # party tail and flags. Never decrypt or print secure fields, OT IDs or keys.
    slots = []
    for slot in range(2):
        records = {}
        counters = set()
        for index in range(slot * 14, slot * 14 + 14):
            sector = save[index * 4096:(index + 1) * 4096]
            sid, checksum, signature, counter = struct.unpack_from('<HHII', sector, 4084)
            if signature != 0x8012025 or sid not in range(14) or sid in records:
                break
            records[sid] = (sector, checksum)
            counters.add(counter)
        if len(records) == 14 and len(counters) == 1:
            slots.append((counters.pop(), records))
    if not slots:
        raise ValueError('No complete ordinary save slot')
    _, records = max(slots, key=lambda record: record[0])
    chunks = []
    for sid in (1, 2):
        sector, checksum = records[sid]
        total = sum(struct.unpack('<992I', sector[:3968])) & 0xffffffff
        assert ((total >> 16) + total) & 65535 == checksum
        chunks.append(sector[:3968])
    block = b''.join(chunks)
    assert block[0x234] == 2
    result = []
    for index, name in enumerate(('Carl', 'Donut')):
        offset = 0x238 + index * 100
        hp, *stats = struct.unpack_from('<7H', block, offset + 0x56)
        mon = dict(zip(STAT_NAMES, stats))
        mon.update(name=name, level=block[offset + 0x54], hp=hp,
                   status=struct.unpack_from('<I', block, offset + 0x50)[0])
        result.append(mon)
    for flag in (0x867, 0x869, 0x86b, 0x86d):
        assert not block[0x1270 + flag // 8] & (1 << (flag % 8))
    assert result[0]['hp'] == result[0]['max_hp'] == 38
    assert result[1]['hp'] == result[1]['max_hp'] == 30
    assert [m['level'] for m in result] == [11, 10]
    assert [m['status'] for m in result] == [0, 0]
    return result


def enemy_stats(rom, symbols):
    def read(address, size):
        offset = address - 0x08000000
        assert 0 <= offset < offset + size <= len(rom)
        return rom[offset:offset + size]

    trainer = read(symbols['gTrainers'] + 858 * 40, 40)
    assert trainer[0] == 1 and trainer[24] == 1 and trainer[32] == 2
    assert trainer[16:24] == bytes(8) and struct.unpack_from('<I', trainer, 28)[0] == 0
    name_hash = 0
    result = []
    party = struct.unpack_from('<I', trainer, 36)[0]
    for index, (species, level, name) in enumerate(((371, 12, 'Warden'), (370, 9, 'Helper'))):
        # agbcc GBA ABI rounds the 14 used bytes to a 16-byte struct stride.
        member = read(party + index * 16, 16)
        assert struct.unpack_from('<H', member)[0] == 0
        assert member[2] == level and struct.unpack_from('<H', member, 4)[0] == species
        moves = list(struct.unpack_from('<4H', member, 6))
        assert moves == ([359, 360, 0, 0] if index == 0 else [33, 0, 0, 0])
        name_hash += sum(trainer[4:16].split(b'\xff')[0])
        name_hash += sum(read(symbols['gSpeciesNames'] + species * 11, 11).split(b'\xff')[0])
        nature = (128 + (name_hash << 8)) % 25  # CreateNPCTrainerParty cumulative hash
        nature_mods = struct.unpack('<5b', read(symbols['gNatureStatTable'] + nature * 5, 5))
        bases = read(symbols['gSpeciesInfo'] + species * 28, 6)
        values = [bases[0] * 2 * level // 100 + level + 10]
        for base, modification in zip(bases[1:], nature_mods):
            value = base * 2 * level // 100 + 5
            values.append(value * (110 if modification == 1 else 90 if modification == -1 else 100) // 100)
        mon = dict(zip(STAT_NAMES, values))
        mon.update(name=name, level=level, nature_index=nature, moves=moves, iv=0, ev=0)
        result.append(mon)
    assert [m['max_hp'] for m in result] == [42, 30]
    assert [m['speed'] for m in result] == [16, 10]
    return result


def reconstruct(trace, carl, donut, warden, helper):
    turn_pattern = re.compile(r'^pilot turn=(\d+) HP=(\d+),(\d+) foeHP=(\d+),(\d+) foeAtk=(\d+)')
    hit_pattern = re.compile(r'^HP transition frame=(\d+) battler=(\d+) from=(\d+) to=(\d+) attacker=(\d+) target=(\d+) move=(\d+) criticalMultiplier=(\d+) pendingDamage=(\d+)')
    # Inferred completed stage changes for the fixed fortify selections. Turn
    # snapshots can precede the last faint processing; hits retain exact order.
    warden_attack_at_slam = {1: -1, 3: -1, 5: -1, 7: -2}
    warden_attack_start = [0, 0, -1, -1, -1, 0, -1, -1]
    pp = [8, 40, 2, 40, 40, 40, 35]
    hit_rows, turn_rows = [], []
    turn = None
    for line in trace.splitlines():
        match = turn_pattern.match(line)
        if match:
            turn, chp, dhp, whp, hhp, wstage = map(int, match.groups())
            assert wstage - 6 == warden_attack_start[turn]
            turn_rows.append({'turn': turn, 'observed_hp': [chp, dhp, whp, hhp],
                              'observed_warden_attack_stage': wstage - 6,
                              'source_inferred_carl_defense_start': min(turn, 3),
                              'source_inferred_pp_start': list(pp), 'hits': []})
            # Pure support executions have no HP transition. Source ordering:
            # Donut first, Warden next, Carl next, Helper last.
            if turn in (0, 1, 2, 5, 6, 7):
                pp[3] -= 1
            if turn < 3:
                pp[1] -= 1
            if turn % 2 == 0:
                pp[4] -= 1
            continue
        match = hit_pattern.match(line)
        if not match:
            continue
        frame, battler, before, after, attacker, target, move, crit, amount = map(int, match.groups())
        assert target == battler and after == max(0, before - amount)
        if attacker == 1:
            assert move == 360 and turn in warden_attack_at_slam
            envelope = damage(warden, carl if target == 0 else donut, 65,
                              warden_attack_at_slam[turn], min(turn, 3) if target == 0 else 0,
                              crit == 2, stab=True)
            pp[5] -= 1
        elif attacker == 3:
            weaken_count = min(turn + 1, 3) + max(0, turn - 4)
            envelope = damage(helper, carl if target == 0 else donut, 35,
                              -weaken_count, min(turn + 1, 3) if target == 0 else 0,
                              crit == 2, stab=True)
            pp[6] -= 1
        elif attacker == 0:
            assert move == 355 and target == 1
            envelope = damage(carl, warden, 40, critical=crit == 2)
            pp[0] -= 1
        else:
            assert attacker == 2 and move == 357 and target in (1, 3)
            envelope = damage(donut, warden if target == 1 else helper, 50,
                              critical=crit == 2, special=True, spread=True)
            if target == 1:
                pp[2] -= 1  # spread costs one PP, not one per hit
        assert envelope[0] <= amount <= envelope[1], (turn, attacker, envelope, amount)
        row = {'frame': frame, 'turn': turn, 'attacker': attacker, 'target': target,
               'move': move, 'critical_multiplier': crit, 'observed_hp': [before, after],
               'observed_damage': amount, 'source_damage_bounds': envelope}
        hit_rows.append(row)
        turn_rows[-1]['hits'].append(row)
    assert len(turn_rows) == 8 and len(hit_rows) == 17
    assert 'policy=fortify frames=11674 outcome=2 incapacitation=5' in trace
    return turn_rows, pp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--symbols', type=Path, required=True)
    parser.add_argument('--trace', type=Path, required=True)
    args = parser.parse_args()
    for path in SOURCES:
        expected = subprocess.check_output(['git', 'show', f'{GAME}:{path}'], cwd=ROOT)
        assert (ROOT / path).read_bytes() == expected, path
    save = pinned(args.save, SAVE_SHA)
    rom = pinned(args.rom, ROM_SHA)
    trace = pinned(args.trace, TRACE_SHA).decode()
    symbol_text = pinned(args.symbols, SYMBOLS_SHA).decode()
    symbols = {parts[2]: int(parts[0], 16) for parts in
               (line.split() for line in symbol_text.splitlines()) if len(parts) == 3}
    carl, donut = saved_stats(save)
    warden, helper = enemy_stats(rom, symbols)
    turns, final_pp = reconstruct(trace, carl, donut, warden, helper)
    strike = damage(carl, warden, 40)
    spark = damage(donut, warden, 50, special=True, spread=True)
    # Strike-fast = existing offensive choices, including WEAKEN after two SPARKs.
    slam1 = damage(warden, carl, 65, atk_stage=1, stab=True)
    slam2 = damage(warden, carl, 65, stab=True)
    tackle = damage(helper, carl, 35, stab=True)
    assert 3 * strike[1] + 2 * spark[1] < warden['max_hp']
    assert slam1[0] + slam2[0] + tackle[0] >= carl['max_hp']
    table = {
        'carl_strike_warden': strike,
        'carl_strike_warden_critical': damage(carl, warden, 40, critical=True),
        'carl_strike_helper': damage(carl, helper, 40),
        'donut_spark_warden_two_foes': spark,
        'donut_spark_warden_two_foes_critical': damage(donut, warden, 50, special=True, spread=True, critical=True),
        'donut_spark_helper_two_foes': damage(donut, helper, 50, special=True, spread=True),
        'strike_fast_first_slam_normal': slam1,
        'strike_fast_first_slam_critical': damage(warden, carl, 65, atk_stage=1, critical=True, stab=True),
        'strike_fast_second_slam_normal': slam2,
        'strike_fast_second_slam_critical': damage(warden, carl, 65, critical=True, stab=True),
        'unweakened_helper_tackle_carl': tackle,
        'fortify_first_slam_normal': damage(warden, carl, 65, -1, 1, stab=True),
        'fortify_second_or_third_slam_normal': damage(warden, carl, 65, -1, 3, stab=True),
        'fortify_slam_critical_bypassing_support': damage(warden, carl, 65, -1, 3, critical=True, stab=True),
    }
    result = {
        'method': 'Offline plaintext save stats, pinned ROM metadata/source, retained trace, integer min/max arithmetic; no emulator/RNG/seed/trajectory/policy search',
        'game_source': GAME, 'rom_sha256': ROM_SHA, 'save_sha256': SAVE_SHA,
        'trace_sha256': TRACE_SHA, 'symbols_sha256': digest(args.symbols.read_bytes()),
        'sources_sha256': {path: digest((ROOT / path).read_bytes()) for path in SOURCES},
        'party': [carl, donut], 'enemies_source_derived': [warden, helper],
        'badge_1_3_5_7_unset': True, 'source_inferred_turn_order': ['Donut', 'Warden', 'Carl', 'Helper'],
        'pp_column_order': ['Carl STRIKE', 'Carl BRACE', 'Donut SPARK', 'Donut WEAKEN', 'WIND UP', 'SLAM', 'TACKLE'],
        'retained_turn_reconstruction': turns, 'source_inferred_pp_end': final_pp,
        'observed_hits_within_source_bounds': 17, 'damage_bounds': table,
        'strike_fast_noncritical_warden_cumulative_after_turns_0_1_2_3_4':
            [[(turn + 1) * strike[0] + min(turn + 1, 2) * spark[0],
              (turn + 1) * strike[1] + min(turn + 1, 2) * spark[1]] for turn in range(5)],
        'fortify_noncritical_warden_cumulative_after_turns_3_4_5_6_7':
            [[(turn + 1) * strike[0] + min(turn + 1, 2) * spark[0],
              (turn + 1) * strike[1] + min(turn + 1, 2) * spark[1]] for turn in range(5)],
        'warden_attempts_total_current_reconstructed_input': 1, 'warden_failures_total_current_reconstructed_input': 1,
        'new_emulator_executions': 0, 'second_response_proposed': False,
        'conclusion': 'Strike-fast is conditionally viable, but ordinary helper targeting or the first critical SLAM defeats its no-incapacity margin. Three support turns mitigate ordinary hits but lose tempo and critical protection. Parent design review, not another seeded attempt, is the supported next action.'
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
