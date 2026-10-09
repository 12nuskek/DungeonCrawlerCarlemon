#!/usr/bin/env python3
"""Read-only live-area/width/build inventory. Never launches or edits the game."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GAME = '5084a1814904f1a43fd999fddf770b221bb53653'
EARLIER = '99243073ebead4ecd4fa9e4f4362d9e0d70c86df'
ROM = '23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167'
ELF = 'cafc512d915d01ff1b598b1a7050261f5990bc50fc0faed533b0ec6d7309336b'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flood(allowed, start):
    assert start in allowed
    q = collections.deque([start]); seen = {start}
    while q:
        x, y = q.popleft()
        for at in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)):
            if at in allowed and at not in seen:
                seen.add(at); q.append(at)
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--build', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    subprocess.run(['git', 'diff', '--quiet', GAME, '--', 'engine'], cwd=ROOT, check=True)
    spec = json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
    layouts = {m['id']: m for m in json.loads((ROOT/'engine/data/layouts/layouts.json').read_text())['layouts']}
    presentation = (ROOT/'engine/src/data/dcc_opening.h').read_text()
    entries = re.findall(r'\{ MAP_(DCC_F1D1\w+), (\d+), (\d+), (FLAG_\w+), (0x\w+), (0x\w+) \}', presentation)
    assert len(entries) == 12
    attrs = (ROOT/'engine/data/tilesets/secondary/dcc/metatile_attributes.bin').read_bytes()
    states = []
    for opened in (False, True):
        maps = {}
        for key, contract in spec['maps'].items():
            name = spec['production_identity_proposal']['maps'][key]['name']
            model_path = ROOT/'engine/data/maps'/name/'map.json'
            model = json.loads(model_path.read_text())
            old = json.loads(git('show', EARLIER+':'+str(model_path.relative_to(ROOT))))
            # Binding/text changes do not imply a geometry or actor-position change.
            for obj in old['object_events'] + model['object_events']:
                obj.pop('script')
            assert old == {k: v for k, v in model.items()}
            assert model['connections'] is None
            layout = layouts[model['layout']]
            w, h = layout['width'], layout['height']
            assert (w, h) == (contract['width'], contract['height'])
            map_path = ROOT/'engine'/layout['blockdata_filepath']
            subprocess.run(['git', 'diff', '--quiet', EARLIER, GAME, '--', str(map_path.relative_to(ROOT)),
                            str((ROOT/'engine'/layout['border_filepath']).relative_to(ROOT))], cwd=ROOT, check=True)
            raw = map_path.read_bytes(); assert len(raw) == w*h*2
            words = list(struct.unpack('<'+'H'*(w*h), raw))
            for map_id, x, y, flag, closed, resolved in entries:
                if map_id == name.upper():
                    # Non-loop presentation has identical collision/elevation/behavior.
                    a, b = int(closed, 16), int(resolved, 16)
                    if flag != 'FLAG_DCC_D1_LOOP_OPEN':
                        assert (a & 0xfc00) == (b & 0xfc00)
                        assert attrs[2*((a & 1023)-512)] == attrs[2*((b & 1023)-512)]
                    words[int(y)*w+int(x)] = b if opened else a
            actors = {(o['x'], o['y']) for o in model['object_events']}
            assert len(actors) == len(model['object_events'])
            assert actors == {tuple(o[:2]) for o in contract['objects']}
            assert all(o['flag'] == '0' and o['movement_type'] == 'MOVEMENT_TYPE_FACE_DOWN'
                       for o in model['object_events'])
            terrain = set()
            for y in range(h):
                for x in range(w):
                    word = words[y*w+x]
                    if word & 0xc00: continue
                    assert word >> 12 == 3
                    metatile = word & 1023; assert metatile >= 512
                    # MB_CAVE and MB_LADDER: no directional/water/ledge restrictions.
                    behavior = struct.unpack_from('<H', attrs, 2*(metatile-512))[0] & 255
                    assert behavior in (8, 0x61), (name, x, y, behavior)
                    terrain.add((x,y))
            clear = terrain - actors
            reachable = flood(clear, tuple(contract['anchors']['arrival']))
            assert reachable == clear
            widths = {}
            for label, (x0,y0,x1,y1,width) in contract['widths'].items():
                cells = {(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1)}
                assert cells <= reachable and len(cells) == width
                assert not cells & {(v['x'],v['y']) for v in model['warp_events']}
                widths[label] = dict(clear_cells=width, at=[x0,y0,x1,y1])
            for at in contract['anchors'].values(): assert tuple(at) in reachable
            for x,y in actors: assert any(n in reachable for n in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
            maps[key] = dict(name=name, dimensions=[w,h], source_words=w*h,
                             collision_valid=len(terrain), occupied_walkable=len(terrain & actors),
                             reachable=len(reachable), excluded_objects=len(actors), widths=widths,
                             buffer_cells=(w+15)*(h+14), buffer_bytes=2*(w+15)*(h+14),
                             map_SHA256=sha(map_path))
        states.append(dict(loop_open=opened, maps=maps, unique_cells=sum(m['reachable'] for m in maps.values())))
    assert [s['unique_cells'] for s in states] == [1440,1449]
    rom = args.build/'pokeemerald.gba'; elf = args.build/'pokeemerald.elf'
    assert sha(rom) == ROM and sha(elf) == ELF
    sections = subprocess.check_output(['readelf','-SW',str(elf)], text=True)
    sizes = {}
    for name in ('ewram','iwram','.pseudo.save_block_1','.pseudo.save_block_2'):
        sizes[name] = int(re.search(r'\]\s+'+re.escape(name)+r'\s+\w+\s+\w+\s+\w+\s+(\w+)', sections)[1],16)
    assert sizes == {'ewram':249704,'iwram':30892,'.pseudo.save_block_1':15752,'.pseudo.save_block_2':3884}
    result = dict(source=GAME, reviewed_base='1663abb05000374b03d0c0db3c78a974c87b3852',
                  method='Native map words and source-defined presentation; fixed collision actors/props excluded once; all legal gates open; flood from each arrival; no map-edge buffers or player subtraction; no emulator',
                  states=states, final_live_T=1449, ten_T=14490, floor_band=[11592,17388],
                  unchanged_from_provisional_open=1449, delta=0,
                  budgets=dict(ROM_SHA256=ROM,ELF_SHA256=ELF,rom_file_bytes=rom.stat().st_size,
                               sections=sizes,ewram_static_remaining=262144-sizes['ewram'],
                               iwram_static_remaining=32768-sizes['iwram'],
                               note='Re-read existing approved ELF; no new compile; linked allocation is not runtime heap/stack/VRAM peak'))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'geometry-budget.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS source-only inventory: live T=1449 (982+115+116+118+118); closed1440; all25 authored clear-width probes; unchanged geometry/actors; exact5084 ROM/ELF; EWRAM249704/IWRAM30892; no emulator')


if __name__ == '__main__':
    main()
