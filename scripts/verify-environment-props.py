#!/usr/bin/env python3
"""Verify integrated prop pixels against accepted native masters in real frames."""
from pathlib import Path
from PIL import Image
import numpy as np,json,sys
run=Path(sys.argv[1]); assets=run/'source/docs/art-references/environment-native-candidates/native/world_shared'
def match(frame, native, origin=None):
 im=Image.open(native);box=im.getbbox();im=im.crop(box);idx=np.asarray(im);pal=np.asarray(im.getpalette(),dtype=np.uint8).reshape(-1,3);v=pal>>3;pal=(v<<3)|(v>>2);rgb=pal[idx];mask=idx!=0
 ys,xs=np.nonzero(mask);h,w=idx.shape;f=np.asarray(Image.open(frame).convert('RGB'));fh,fw=f.shape[:2]
 if origin is not None:
  x,y=origin[0]+box[0],origin[1]+box[1]
  if x<0 or y<0 or x+w>fw or y+h>fh:return None
  if np.array_equal(f[y:y+h,x:x+w][mask],rgb[mask]):return {'canvas_x':origin[0],'canvas_y':origin[1],'opaque_pixels':int(mask.sum()),'exact_rgb555_pixels':True}
  return None
 # Filter candidate translations by one opaque anchor, then compare every pixel.
 ay,ax=ys[len(ys)//2],xs[len(xs)//2];poss=np.argwhere(np.all(f==rgb[ay,ax],axis=2));best=None
 for fy,fx in poss:
  y=int(fy)-int(ay);x=int(fx)-int(ax)
  if x<0 or y<0 or x+w>fw or y+h>fh:continue
  block=f[y:y+h,x:x+w]
  if np.array_equal(block[mask],rgb[mask]):return {'canvas_x':x-box[0],'canvas_y':y-box[1],'opaque_pixels':int(mask.sum()),'exact_rgb555_pixels':True}
 return None
results=[]
for name,room in [('rubble','entrance'),('warning_sign','service'),('quest_tag','service'),('workbench','service'),('cache_sealed','service'),('storage_rack','landing')]:
    frame=run/'rooms'/(room+'-center.ppm')
    found=match(frame,assets/(name+'.png'))
    assert found,(name,'native prop not visible in actual frame')
    results.append({'name':name,'frame':str(frame.relative_to(run)),**found})
for name in ['legacy-landing','legacy-workshop']:
    frame=run/name/'native-props.ppm'
    if frame.exists():
        found=match(frame,assets/'storage_rack.png')
        assert found,(name,'old generic prop identity not refreshed')
        results.append({'name':'storage_rack','frame':str(frame.relative_to(run)),**found})
# Match each resolved object at its known camera-relative position, not just any
# occurrence of a shared marker. Include cancellation, capacity failure and cold load.
if (run/'source/scripts/contracts/n03-presentation.json').exists():
 cases=[
  ('encounter_remains','rooms/landing-center.ppm',(128,40)),
  ('encounter_remains','rooms/gauntlet-center.ppm',(64,56)),
  ('encounter_remains','rooms/gauntlet-center.ppm',(144,56)),
  ('encounter_remains','rooms/boss-center.ppm',(112,40)),
  ('cache_sealed','craft-blast-use/blast-cancel.ppm',(112,88)),
  ('cache_sealed','craft-fixture-capacity/cache-full.ppm',(112,88)),
  ('cache_open','craft-blast-use/blasted.ppm',(112,88)),
  ('cache_open','craft-reload-recover/reloaded.ppm',(192,104)),
  ('cache_open','rooms/entrance-center.ppm',(144,88)),
  ('cache_open','equipment-give/wrap-found.ppm',(112,88)),
 ]
 for name,path,origin in cases:
  frame=run/path;found=match(frame,assets/(name+'.png'),origin)
  assert found,(name,path,origin,'persistent object presentation mismatch')
  results.append({'name':name,'frame':path,'fixture':'fixture' in path,**found})
print(json.dumps(results,indent=2))
