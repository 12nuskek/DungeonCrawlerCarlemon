#!/usr/bin/env python3
"""Check format/budget/behavior contracts of authored S02 assets."""
from pathlib import Path
import struct
from PIL import Image
root = Path(__file__).resolve().parents[1] / 'engine'
count = 0
for p in (root/'graphics/dcc').rglob('*.png'):
    im = Image.open(p)
    assert im.mode == 'P', (p, 'must be indexed')
    assert im.getextrema()[1] < 16, (p, '4bpp palette overflow')
    assert im.width % 8 == im.height % 8 == 0, (p, 'tile alignment')
    count += 1
for name in ['carl','donut','scuttler','grub','guard','howler','warden']:
    for file,size in [('front.png',(64,64)),('back.png',(64,64)),('anim_front.png',(64,128)),('icon.png',(32,64))]:
        assert Image.open(root/'graphics/dcc'/name/file).size == size
arena = Image.open(root/'graphics/dcc/battle/arena.png')
assert arena.width * arena.height // 2 <= 0x4000, 'battle character-block budget'
logo = Image.open(root/'graphics/dcc/title/logo.png')
assert logo.width * logo.height // 64 <= 256, 'affine byte tile-index budget'
assert logo.crop((0,0,8,8)).getbbox() is None, 'blank affine map tile0 must stay transparent'
assert len((root/'graphics/dcc/title/logo.bin').read_bytes()) == 1024
cave = (root/'data/tilesets/secondary/cave/metatile_attributes.bin').read_bytes()
dcc = (root/'data/tilesets/secondary/dcc/metatile_attributes.bin').read_bytes()
metatiles = (root/'data/tilesets/secondary/dcc/metatiles.bin').read_bytes()
variants = {0x220:0x201,0x221:0x201,0x222:0x201,0x223:0x219}
used = set()
for p in (root/'data/layouts').glob('DCC_*/*.bin'):
    for (value,) in struct.iter_unpack('<H',p.read_bytes()):
        mid = value & 1023
        offset = (mid-512)*2
        original = (variants.get(mid,mid)-512)*2
        assert dcc[offset:offset+2] == cave[original:original+2], (p,mid,'behavior changed')
        for (tile,) in struct.iter_unpack('<H',metatiles[(mid-512)*16:(mid-511)*16]):
            assert 512 <= tile & 1023 < 550, (mid,'tile index outside atlas')
            assert tile >> 12 == 6, (mid,'unexpected palette bank')
        used.add(mid)
print(f'PASS {count} indexed asset images; seven sprite contracts; tile/palette budgets; {len(used)} used metatile behaviors')
# Independent protagonist palettes must agree across packed sprite consumers.
for name, size, path in [
    ('carl', (144,32), root/'graphics/object_events/pics/people/carl/walking.png'),
    ('donut', (48,16), root/'graphics/dcc/donut/overworld.png'),
]:
    atlas = Image.open(path)
    palette = Image.open(root/'graphics/dcc'/name/'front.png').getpalette()[:48]
    assert atlas.mode == 'P' and atlas.size == size
    assert atlas.getpalette()[:48] == palette
    assert atlas.info.get('transparency') == 0
    assert atlas.getextrema()[1] < 16
    for x in range(0, atlas.width, 16):
        frame = atlas.crop((x,0,x+16,atlas.height))
        box = frame.getbbox()
        assert box and box[1] > 0 and box[3] < atlas.height, (name,x,'clipped frame')
    for file in ['front.png','back.png','anim_front.png','icon.png']:
        assert Image.open(root/'graphics/dcc'/name/file).getpalette()[:48] == palette
print('PASS protagonist overworld packing, margins and independent palette coherence')
