#!/usr/bin/env python3
"""Compare every opaque native pixel to actual RGB555-expanded emulator output."""
from pathlib import Path
from PIL import Image
import numpy as np,json,sys
run=Path(sys.argv[1]);root=run/'source';assets=root/'docs/art-references/opponent-native-candidates/assets'
def match(frame, native):
 im=Image.open(native);box=im.getbbox();im=im.crop(box);idx=np.asarray(im);pal=np.asarray(im.getpalette(),dtype=np.uint8).reshape(-1,3);v=pal>>3;pal=(v<<3)|(v>>2);rgb=pal[idx];mask=idx!=0
 ys,xs=np.nonzero(mask);h,w=idx.shape;f=np.asarray(Image.open(frame).convert('RGB'));fh,fw=f.shape[:2]
 # Filter candidate translations by one opaque anchor, then compare every pixel.
 ay,ax=ys[len(ys)//2],xs[len(xs)//2];poss=np.argwhere(np.all(f==rgb[ay,ax],axis=2));best=None
 for fy,fx in poss:
  y=int(fy)-int(ay);x=int(fx)-int(ax)
  if x<0 or y<0 or x+w>fw or y+h>fh:continue
  block=f[y:y+h,x:x+w]
  if np.array_equal(block[mask],rgb[mask]):return {'canvas_x':x-box[0],'canvas_y':y-box[1],'opaque_pixels':int(mask.sum()),'exact_rgb555_pixels':True}
 return None
results=[]
for name,route in [('scuttler','trial'),('grub','trial'),('guard','guard'),('howler','howler'),('warden','boss-unprepared')]:
 frame=run/route/'carl-menu.ppm';found=match(frame,assets/name/'front.png');assert found,(name,'battle mismatch');results.append({'name':name,'view':'battle','frame':str(frame.relative_to(run)),**found})
for name in ['scuttler','guard','howler','warden']:
 found=None
 for route in ['setup','ui','gates','guard','guard-rest','howler','boss-rest','boss-unprepared']:
  for frame in sorted((run/route).glob('*.ppm')):
   found=match(frame,assets/name/'overworld.png')
   if found:break
  if found:break
 assert found,(name,'map mismatch')
 results.append({'name':name,'view':'field','frame':str(frame.relative_to(run)),**found})
print(json.dumps(results,indent=2))
