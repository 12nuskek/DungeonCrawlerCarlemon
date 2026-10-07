#!/usr/bin/env python3
"""Validate native art inputs/output only. Does not compile or emulate a game."""
from pathlib import Path
from input_paths import source, baseline
import json,hashlib,struct
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
M=json.loads((R/'manifest.json').read_text());checks=0;frames=0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PENDING=json.loads((R/'pending-source.json').read_text());missing_sources=[]
def source_hash(name):
 p=source(name)
 if p.is_file():return sha(p)
 assert str(p.relative_to(R))==PENDING['path']
 return PENDING['sha256'] # Declared provenance only, not byte-verified source.
for row in M['sources']:
 p=R/row['path']
 if not p.is_file():
  assert row['path']==PENDING['path'] and row['sha256']==PENDING['sha256'];missing_sources.append(row['path']);continue
 assert sha(p)==row['sha256'];assert list(Image.open(p).size)==row['dimensions'];checks+=2
for ch,data in M['characters'].items():
 base=Image.open(baseline({'carl':'carl-back.png','donut':'donut-back.png','warden':'warden-front.png'}[ch]));pal=base.getpalette()[:48]
 assert data['palette_rgb888']==np.array(pal).reshape(16,3).tolist();checks+=1
 seen=[]
 for row in data['frames']:
  p=R/row['path'];b=p.read_bytes();im=Image.open(p);a=np.array(im);rgba=np.array(im.convert('RGBA'))
  assert sha(p)==row['sha256'];checks+=1
  assert im.mode=='P' and im.size==(64,64);checks+=1
  assert b[24]==4 and b[25]==3;checks+=1 # PNG IHDR: 4-bit indexed, not 8-bit RGBA
  assert im.info.get('transparency')==0 and set(np.unique(rgba[:,:,3]))=={0,255};checks+=1
  assert a.max()<=15 and len(np.unique(a[a>0]))<=15;checks+=1
  assert im.getpalette()[:48]==pal and all(v%8==0 for v in pal);checks+=1
  assert list(im.getbbox())==row['bbox'];checks+=1
  x0,y0,x1,y1=row['bbox'];assert x0>=1 and x1<=63 and y0>=1 and y1==62;checks+=1
  assert row['pivot']==data['pivot'] and row['source_sha256']==source_hash(row['source']);checks+=1
  assert not a[0].any() and not a[-1].any() and not a[:,0].any() and not a[:,-1].any();checks+=1
  # Ensure arbitrary hidden source RGB never escapes index0 in output.
  assert np.all(rgba[a==0,:3]==0);checks+=1
  if ch=='warden':
   q=R/row['runtime_lift8_path'];li=Image.open(q);la=np.array(li)
   assert sha(q)==row['runtime_lift8_sha256'];checks+=1
   assert not a[:8].any() and np.array_equal(la[:56],a[8:]) and not la[56:].any();checks+=1
   assert list(li.getbbox())==row['runtime_bbox'] and row['runtime_bbox'][3]==54;checks+=1
   assert li.info.get('transparency')==0 and li.getpalette()[:48]==pal;checks+=1
  seen.append(row['sha256']);frames+=1
 assert len(set(seen))==data['distinct_sha256_count']==len(data['frames']);checks+=1
 stack=Image.open(R/'frames'/ch/'candidate-pose-stack.png');sa=np.array(stack)
 assert stack.size==(64,64*len(data['frames'])) and stack.info.get('transparency')==0;checks+=1
 for i,row in enumerate(data['frames']):assert np.array_equal(sa[i*64:(i+1)*64],np.array(Image.open(R/row['path'])));checks+=1
T=json.loads((R/'timing-proposal.json').read_text())
for sequence in T['sequences'].values():
 for row in sequence:
  assert row['frames']>0 and any(f['name']==row['pose'] for f in M['characters'][row['character']]['frames']);checks+=1
out={'status':'PASS_NATIVE_ASSETS_PARTIAL_SOURCE','checks':checks,'source_rebuild_verified':False,'missing_sources':missing_sources,'unique_native_source_pose_frames':frames,'warden_lift8_variants':5,'native_png_dimensions':[64,64],'palette_limit':'index0 transparent + at most15 opaque RGB555 colors','game_build_run':False,'emulator_verified':False,'animation_integration_verified':False}
(R/'verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
