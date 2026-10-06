#!/usr/bin/env python3
"""Validate native battle asset dimensions, indices, palette and reproducibility."""
from pathlib import Path
import hashlib,json,subprocess,sys
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parent
expected={'carl/front.png':(64,64),'carl/back.png':(64,64),'carl/anim_front.png':(64,128),'carl/trainer_back.png':(64,256),'donut/front.png':(64,64),'donut/back.png':(64,64),'donut/anim_front.png':(64,128)}
checks=[]
for rel,size in expected.items():
    path=R/'assets'/rel;im=Image.open(path);p=np.asarray(im)
    assert im.mode=='P',(rel,im.mode)
    assert im.size==size,(rel,im.size)
    assert im.info.get('transparency')==0,(rel,im.info)
    assert int(p.max())<16
    assert path.read_bytes()[24]==4,'PNG IHDR bit depth must be 4'
    assert path.read_bytes()[25]==3,'PNG color type must be indexed'
    rgba=np.asarray(im.convert('RGBA'))
    assert set(np.unique(rgba[:,:,3]).tolist())<={0,255},'binary alpha only'
    char=rel.split('/')[0]
    palfile=R/'assets'/char/'normal.pal'
    lines=palfile.read_text().splitlines();assert lines[:3]==['JASC-PAL','0100','16']
    colors=[tuple(map(int,line.split()))for line in lines[3:]]
    assert len(colors)==16
    assert all(all(0<=v<=248 and v%8==0 for v in c)for c in colors)
    assert im.getpalette()[:48]==[v for c in colors for v in c]
    assert palfile.read_bytes()==(palfile.parent/'shiny.pal').read_bytes()
    if rel.endswith('/front.png') or rel.endswith('/back.png'):
      ys,xs=np.where(p>0);assert 1<=int(xs.min())<=int(xs.max())<=62
      assert 1<=int(ys.min())<=int(ys.max())<=62
    if rel.endswith('/anim_front.png'):
      front=np.asarray(Image.open(path.parent/'front.png'))
      assert np.array_equal(p[:64],front) and np.array_equal(p[64:],front)
    if rel.endswith('/trainer_back.png'):
      back=np.asarray(Image.open(path.parent/'back.png'))
      assert all(np.array_equal(p[y:y+64],back)for y in range(0,256,64))
    checks.append({'path':str(path.relative_to(R)),'mode':'P','size':list(size),'bit_depth':4,'max_index':int(p.max()),'opaque_colors_used':len(set(p.ravel().tolist())-{0}),'binary_alpha':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
paths=sorted((R/'assets').rglob('*'))
before={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths if p.is_file()}
subprocess.run([sys.executable,str(R/'convert_native.py')],cwd=R,stdout=subprocess.DEVNULL,check=True)
after={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths if p.is_file()}
assert before==after,'regeneration changed asset bytes'
report={'status':'PASS','pngs':checks,'palette_files':4,'regeneration_sha256_identical':True,'visual_review':'1x and nearest-neighbor 6x asset review completed; actual emulator review pending','limitations':['Not compiled or emulator-tested','Front animation and trainer intro packs contain static duplicated frames','Icons and native overworld not included as approved assets']}
(R/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
