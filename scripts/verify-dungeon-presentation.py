#!/usr/bin/env python3
"""Match actual background pixels at known world/camera coordinates."""
from pathlib import Path
from PIL import Image
import numpy as np,json,sys
run=Path(sys.argv[1]);root=run/'source'
states={x['label']:x for x in json.loads((root/'scripts/contracts/n03-presentation.json').read_text())}
def check(label,state,path,player):
 spec=states[label];template=Image.open(root/'engine/graphics/dcc/presentation'/f'{label}-{state}.png');idx=np.asarray(template)
 pal=np.asarray([list(map(int,l.split())) for l in (root/f"engine/data/tilesets/secondary/dcc/palettes/{spec['palette_bank']:02}.pal").read_text().splitlines()[3:]],dtype=np.uint8);v=pal>>3;pal=(v<<3)|(v>>2);rgb=pal[idx];mask=idx!=0
 x=112+(spec['x']-player[0])*16;y=72+(spec['y']-player[1])*16
 actual=np.asarray(Image.open(run/path).convert('RGB'));h,w=idx.shape
 assert 0<=x and 0<=y and x+w<=240 and y+h<=160,(label,'frame clipping',x,y,w,h)
 block=actual[y:y+h,x:x+w];diff=int(np.count_nonzero(np.any(block!=rgb,axis=2)&mask))
 assert diff==0,(label,state,path,'mismatched opaque BG pixels',diff,'position',x,y)
 return {'label':label,'state':state,'frame':path,'world_origin':[spec['x'],spec['y']],'player':player,'screen_origin':[x,y],'exact_rgb555_pixels':int(mask.sum())}
cases=[('gate','off','gates/boss-locked.ppm',[8,5]),('gate','on','boss-unprepared/boss-saved.ppm',[8,5]),('supply-line','off','boss-unprepared/reloaded.ppm',[8,5]),('supply-line','on','boss-prepared/reloaded.ppm',[8,5]),('wire','off','quest-accept-trap/warning.ppm',[7,6]),('wire','on','quest-tag-secret/tag-saved.ppm',[11,3]),('secret','off','quest-decline/tag-reserved.ppm',[11,3]),('secret','on','quest-tag-secret/tag-saved.ppm',[11,3])]
cases += [('wire','off','wire-pair/wire-live-clear.ppm',[7,6]),('wire','on','wire-pair/wire-spent-clear.ppm',[7,6]),('wire','on','wire-cold/wire-cold-clear.ppm',[7,6])]
results=[]
for case in cases:
 if not (run/case[2]).exists():
  if '--partial' in sys.argv:continue
  raise AssertionError(case[2]+' absent')
 results.append(check(*case))
print(json.dumps(results,indent=2))
