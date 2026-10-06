#!/usr/bin/env python3
"""Verify exact indexed contracts; does not claim game/runtime validation."""
from pathlib import Path
from PIL import Image
import hashlib,json
import numpy as np
R=Path(__file__).resolve().parent
names=['scuttler','grub','guard','howler','warden']
shared=[int(v) for l in (R/'source/existing-shared.pal').read_text().splitlines()[3:19] for v in l.split()]
report={'status':'PASS','checks':[],'runtime':'NOT RUN','source_sha256':hashlib.sha256((R/'source/opponents-reference-v2.png').read_bytes()).hexdigest()}
assert report['source_sha256']=='000068d6bdae0a60e93836438920f4f3b847cee6aca8335733d3f05c7ac4a279'
for name in names:
    folder=R/'assets'/name
    lines=(folder/'normal.pal').read_text().splitlines();assert lines[:3]==['JASC-PAL','0100','16']
    pal=[int(v) for l in lines[3:] for v in l.split()];assert len(pal)==48 and all(v%8==0 for v in pal)
    assert (folder/'normal.pal').read_bytes()==(folder/'shiny.pal').read_bytes()
    specs={'front.png':(64,64),'back.png':(64,64),'anim_front.png':(64,128),'icon.png':(32,64)}
    if name!='grub':specs['overworld.png']=(32,32)
    for file,size in specs.items():
        path=folder/file;im=Image.open(path);b=path.read_bytes();pixels=np.asarray(im)
        assert im.mode=='P' and im.size==size
        assert b[24]==4 and b[25]==3, (file,'must encode PNG 4bpp indexed')
        assert im.info.get('transparency')==0 and int(pixels.max())<=15
        assert im.getpalette()[:48]==(shared if file in ['icon.png','overworld.png'] else pal)
        step=32 if file in ['icon.png','overworld.png'] else 64
        for y in range(0,size[1],step):
            frame=im.crop((0,y,size[0],y+step));box=frame.getbbox();assert box
            assert box[0]>0 and box[1]>0 and box[2]<size[0] and box[3]<step,(file,box)
        if file=='anim_front.png': assert np.array_equal(pixels[:64],pixels[64:])
        if file=='icon.png':assert np.array_equal(pixels[:32],pixels[32:])
        report['checks'].append({'path':str(path.relative_to(R)),'size':size,'mode':im.mode,'png_bit_depth':b[24],'opaque_colors':len(set(pixels.ravel()))-1,'sha256':hashlib.sha256(b).hexdigest()})
    assert (folder/'front.png').read_bytes()==(folder/'back.png').read_bytes()
    if name=='grub':assert not (folder/'overworld.png').exists(),'do not invent a field token'
for kind in ('battle','world'):
    one=Image.open(R/'previews'/f'{kind}-native-1x.png')
    six=Image.open(R/'previews'/f'{kind}-native-6x.png')
    assert six.size==(one.width*6,one.height*6)
    assert np.array_equal(np.asarray(one.resize(six.size,Image.Resampling.NEAREST)),np.asarray(six))
report['summary']='24 indexed PNGs pass: dimensions, packed frames, 4bpp, binary index0 transparency, battle RGB555 palettes, unchanged shared small-asset palette, native margins and exact 6x previews.'
(R/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['summary'])
