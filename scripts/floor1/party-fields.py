"""Offline native Emerald decoding. Inputs/decoded identities remain private."""
from pathlib import Path
import hashlib, re, struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'engine/src/pokemon.c'


def orders():
    text = SOURCE.read_text()
    rows = re.findall(r'SUBSTRUCT_CASE\(\s*(\d+),(\d+),(\d+),(\d+),(\d+)\)', text)
    result = {int(n): tuple(map(int, (a, b, c, d))) for n, a, b, c, d in rows}
    assert sorted(result) == list(range(24))
    assert all(sorted(v) == list(range(4)) for v in result.values())
    assert 'boxMon->secure.raw[i] ^= boxMon->personality;' in text
    assert 'boxMon->secure.raw[i] ^= boxMon->otId;' in text
    return result


def decode(raw):
    assert len(raw) == 100
    personality, owner = struct.unpack_from('<II', raw)
    plain = b''.join(struct.pack('<I', x ^ personality ^ owner)
                     for x in struct.unpack('<12I', raw[32:80]))
    positions = orders()[personality % 24]
    blocks = [plain[12*i:12*i+12] for i in positions]
    canonical = raw[:32] + b''.join(blocks) + raw[80:]
    stored = struct.unpack_from('<H', raw, 28)[0]
    computed = sum(struct.unpack('<24H', plain)) & 0xffff
    encrypted = b''.join(struct.pack('<I', x ^ personality ^ owner)
                         for x in struct.unpack('<12I', plain))
    assert encrypted == raw[32:80]
    growth, attacks, effort, misc = blocks
    fields = {
        'personality': personality, 'owner_id': owner,
        'nickname_bytes': raw[8:18].hex(), 'language': raw[18],
        'box_flags': raw[19], 'owner_name_bytes': raw[20:27].hex(),
        'markings': raw[27], 'checksum': stored, 'unknown': raw[30:32].hex(),
        'species': struct.unpack_from('<H', growth)[0],
        'held_item': struct.unpack_from('<H', growth, 2)[0],
        'experience': struct.unpack_from('<I', growth, 4)[0],
        'pp_bonuses': growth[8], 'friendship': growth[9],
        'growth_padding': growth[10:].hex(),
        'moves': list(struct.unpack('<4H', attacks[:8])), 'PP': list(attacks[8:]),
        'effort_contest': list(effort), 'origin_IV_ribbons': misc.hex(),
        'status': struct.unpack_from('<I', raw, 80)[0], 'level': raw[84],
        'mail': raw[85], 'hp_maxhp_attack_defense_speed_spatk_spdef': list(struct.unpack_from('<7H', raw, 86))
    }
    return {'fields': fields, 'canonical': canonical, 'raw': raw,
            'checksum_stored': stored, 'checksum_computed': computed,
            'checksum_valid': stored == computed, 'reencoding_exact': encrypted == raw[32:80],
            'bad_egg': bool(raw[19] & 1), 'egg': bool(raw[19] & 4),
            'friendship_raw_offset': 32 + 12*positions[0] + 9}


def saved_party(path):
    """Validate every latest native sector against pinned struct sizes/map."""
    raw = Path(path).read_bytes()
    sizes = [0xf2c] + [min(3968, 0x3d88 - i*3968) for i in range(4)] + [min(3968, 0x83d0-i*3968) for i in range(9)]
    sectors = []
    for i in range(28):
        s = raw[i*4096:(i+1)*4096]
        sid, checksum, signature, count = struct.unpack_from('<HHII', s, 0xff4)
        if signature == 0x08012025 and sid < 14:
            sectors.append((count, sid, checksum, s))
    latest = max(x[0] for x in sectors)
    selected = {sid: (checksum, s) for count, sid, checksum, s in sectors if count == latest}
    assert sorted(selected) == list(range(14))
    for sid, (stored, data) in selected.items():
        n = sizes[sid]
        total = sum(struct.unpack('<' + str(n//4) + 'I', data[:n])) & 0xffffffff
        assert stored == ((total & 0xffff) + (total >> 16)) & 0xffff, ('sector checksum', sid)
    sb = b''.join(selected[i][1][:sizes[i]] for i in range(1, 5))
    return {'party': sb[0x238:0x238+600], 'count': sb[0x234],
            'friendship_counter': struct.unpack_from('<H', sb, 0x13f0)[0],
            'map': list(sb[4:6]), 'position': list(struct.unpack_from('<hh', sb)),
            'save_SHA256': hashlib.sha256(raw).hexdigest(), 'latest_sector_checksums_valid': True}


def compare(before, after):
    """All bytes, including unlabelled/padding fields, participate in review."""
    assert len(before) == len(after) == 600
    members = []
    private = []
    for i, name in enumerate(('Carl', 'Donut')):
        a, b = decode(before[100*i:100*i+100]), decode(after[100*i:100*i+100])
        changed = [j for j, (x, y) in enumerate(zip(a['canonical'], b['canonical'])) if x != y]
        delta = b['fields']['friendship'] - a['fields']['friendship']
        only = set(changed) <= {28, 29, 41}
        valid = all(x['checksum_valid'] and x['reencoding_exact'] and not x['bad_egg'] and not x['egg'] for x in (a, b))
        raw_diffs = [j for j, (x, y) in enumerate(zip(a['raw'], b['raw'])) if x != y]
        encoded_only = set(raw_diffs) <= {28, 29, a['friendship_raw_offset']} and a['friendship_raw_offset'] == b['friendship_raw_offset']
        checksums_derived = ((b['checksum_stored'] - a['checksum_stored']) & 0xffff) == ((delta << 8) & 0xffff)
        changes = {k: {'before': v, 'after': b['fields'][k]} for k, v in a['fields'].items() if v != b['fields'][k]}
        safe = {k: v for k, v in changes.items() if k in ('friendship', 'checksum')}
        members.append({'member': name, 'changed_field_names': sorted(changes),
                        'safe_changed_fields': safe, 'checksums_valid_before_after': valid,
                        'reencoding_exact': a['reencoding_exact'] and b['reencoding_exact'],
                        'all_other_canonical_bytes_exact': only, 'derived_checksum_delta_exact': checksums_derived,
                        'only_derived_ciphertext_bytes_changed': encoded_only,
                        'raw_changed_offsets': raw_diffs, 'canonical_changed_offsets': changed,
                        'friendship_delta': delta})
        private.append({'member': name, 'before': a['fields'], 'after': b['fields'],
                        'all_decoded_field_differences': changes})
    return {'members': members, 'remaining400_party_bytes_exact': before[200:] == after[200:],
            'strict200_byte_equal': before[:200] == after[:200]}, private
