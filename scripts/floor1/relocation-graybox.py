#!/usr/bin/env python3
"""Five-map disposable contract; accepted patrol geometry is immutable."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[2]
loader = importlib.util.spec_from_file_location('coordinated', ROOT / 'scripts/floor1/coordinated-graybox.py')
g = importlib.util.module_from_spec(loader); loader.loader.exec_module(g)

path = g.path
cells = g.cells

def audit(spec, opened):
    old = json.loads((ROOT / spec['comparison_source']).read_text())
    # No new material field/guide/arena layout attempt: same collision geometry,
    # accepted main anchors, clear width probes and frozen travel measurements.
    for key in ('field', 'quiet', 'boss'):
        for name in ('width', 'height', 'rectangles', 'widths'):
            assert spec['maps'][key][name] == old['maps'][key][name], (key, name)
        for label, at in old['maps'][key]['anchors'].items():
            assert spec['maps'][key]['anchors'][label] == at, (key, label)
        for label, rect in old['maps'][key]['blocked'].items():
            assert spec['maps'][key]['blocked'][label] == rect, (key, label)
    assert spec['maps']['field']['closed_barrier'] == old['maps']['field']['closed_barrier']
    result = g.audit(spec, opened)
    assert len(spec['maps']) == 5 and [m['map_num'] for m in spec['maps'].values()] == list(range(5))
    for key, m in spec['maps'].items():
        for warp in m['warps']:
            dest = next(v for v in spec['maps'].values() if v['map_num'] == warp['dest'])
            assert 0 <= warp['dest_warp'] < len(dest['warps'])
        assert len({tuple(o[:2]) for o in m['objects']}) == len(m['objects']), (key, 'duplicate actor')
    for rule in spec['legacy_position_rules']:
        m = spec['maps'][rule['new']]; at = tuple(m['anchors'][rule['fallback_anchor']])
        assert at in g.cells(m, opened) and at not in {tuple(w['at']) for w in m['warps']}
    assert list(spec['legacy_object_counts'].values()) == [4,5,6,3,1,2]
    for name,count in spec['legacy_object_counts'].items():
        assert len(spec['legacy_object_destinations'][name]) == count
        for key,role in spec['legacy_object_destinations'][name]:
            item=spec['object_roles'][key][role];m=spec['maps'][key]
            assert item['actor_at']==m['objects'][item['diagnostic_object_index']][:2]
            x,y=item['actor_at']
            assert any((x+dx,y+dy) in g.cells(m,opened) for dx,dy in [(0,-1),(1,0),(0,1),(-1,0)]),(name,role,'inaccessible actor')
    for key,roles in spec['object_roles'].items():
        assert len({r['production_local_id'] for r in roles.values()})==len(roles)
    stairs = spec['maps']['boss']['stairs_transition']
    assert tuple(stairs['at']) not in g.cells(spec['maps']['boss'], opened)
    assert sum(abs(a-b) for a,b in zip(stairs['at'], stairs['approach'])) == 1
    result.update(candidate_unique_cells=sum(m['reachable_cells'] for m in result['maps'].values()),
                  final_T=None, scope='Complete five-map diagnostic occupancy/anchors; unchanged accepted travel geometry. Candidate cells only, not final live T, migration, persistence or battle acceptance.')
    return result

def export(spec, engine, opened, out):
    g.export(spec, engine, opened, out)
    boss = spec['maps']['boss']; stairs = boss['stairs_transition']
    dest = next(m for m in spec['maps'].values() if m['map_num'] == stairs['dest'])
    p = engine / 'data/maps' / boss['name'] / 'map.json'; model = json.loads(p.read_text())
    label = boss['name'] + '_DiagnosticStairs'
    model['bg_events'].append({'type': 'sign', 'x': stairs['at'][0], 'y': stairs['at'][1],
                              'elevation': 0, 'player_facing_dir': 'BG_EVENT_PLAYER_FACING_ANY', 'script': label})
    p.write_text(json.dumps(model, indent=2) + '\n')
    p = engine / 'data/maps' / boss['name'] / 'scripts.inc'
    x,y = stairs['dest_pos']
    p.write_text(p.read_text() + f'\n{label}::\n\tlockall\n\twarp MAP_{dest["name"].upper()}, {x}, {y}\n\twaitstate\n\treleaseall\n\tend\n')
    layouts = json.loads((engine / 'data/layouts/layouts.json').read_text())['layouts']
    old = next(l for l in layouts if l['name'] == stairs['source_map'] + '_Layout')
    raw = (engine / old['blockdata_filepath']).read_bytes(); x,y = stairs['source_at']
    word = struct.unpack_from('<H', raw, 2*(y*old['width']+x))[0]
    assert word & 0xC00, 'Native stairs must be blocking and interacted with from adjacent cell'
    p = engine / 'data/layouts' / boss['name'] / 'map.bin'; raw = bytearray(p.read_bytes());x,y = stairs['at']
    struct.pack_into('<H', raw, 2*(y*boss['width']+x), word);p.write_bytes(raw)
    ids = json.loads((out / 'map-identities.json').read_text())
    for row in ids:
        if row['key'] == 'boss': row['blockdata_sha256'] = hashlib.sha256(raw).hexdigest()
    (out / 'map-identities.json').write_text(json.dumps(ids, indent=2) + '\n')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--engine',type=Path);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--opened',action='store_true');args=parser.parse_args()
    spec=json.loads((ROOT / 'scripts/contracts/f1-g01d-relocation.json').read_text());result=audit(spec,args.opened)
    args.out.mkdir(parents=True,exist_ok=True);(args.out/'geometry.json').write_text(json.dumps(result,indent=2)+'\n')
    for key,m in spec['maps'].items():
        im=Image.new('RGB',(m['width']*12,m['height']*12),(17,20,27));d=ImageDraw.Draw(im)
        for x,y in g.cells(m,args.opened):d.rectangle((x*12,y*12,x*12+10,y*12+10),fill=(79,100,104))
        for n,(x,y) in m['anchors'].items():d.ellipse((x*12+2,y*12+2,x*12+8,y*12+8),fill=(244,197,79));d.text((x*12+3,y*12+10),n,fill=(255,238,203))
        im.save(args.out/(key+'-diagram.png'))
    if args.engine:export(spec,args.engine,args.opened,args.out)
    print(json.dumps(result))
if __name__=='__main__':main()
