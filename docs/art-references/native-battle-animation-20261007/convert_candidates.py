#!/usr/bin/env python3
"""Source-constrained native pixel candidates. No engine / repository operations.
Python 3, Pillow, numpy, scipy. Run from any directory. Read-only input masters.
Authoring operations: alpha isolation, semantic color reduction, source-cluster
voting, binary silhouettes, one-pixel outline, isolated-cluster cleanup and
explicit native feature repairs listed in pixel_edits.json. Never invent poses.
"""
from pathlib import Path
from input_paths import source, baseline, REFS
import hashlib, json, shutil, struct
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy.ndimage import label, binary_erosion
R=Path(__file__).resolve().parent
S=R/'sources'; F=R/'frames'; V=R/'review'
missing_inputs=[str(p.relative_to(R)) for name in REFS['sources'] if not (p:=source(name)).is_file()]
if missing_inputs:
 raise SystemExit('Source regeneration unavailable in partial staging: missing '+', '.join(missing_inputs))
F.mkdir(exist_ok=True);V.mkdir(exist_ok=True)
# Tight bounds are measured connected alpha>=128 source components. Source feet
# / pelvis anchors are explicitly authored, never automatic per-frame fit-to-box.
DEF={
 'carl': {'scale':.115,'pivot':[27,61],'baseline':'carl-back.png','poses':[
 ['strike-anticipation','carl-keypose-master-v2.png',[95,49,442,509],[267,508]],
 ['strike-contact','carl-keypose-master-v2.png',[553,47,1055,506],[774,505]],
 ['strike-recovery','carl-keypose-master-v2.png',[1085,47,1447,508],[1265,507]],
 ['brace-set','carl-keypose-master-v2.png',[70,538,460,973],[264,972]],
 ['brace-hold','carl-keypose-master-v2.png',[581,561,936,972],[768,971]]]},
 'donut':{'scale':.112,'pivot':[42,61],'baseline':'donut-back.png','poses':[
 ['spark-anticipation','donut-keypose-master-v1.png',[30,186,431,606],[367,605]],
 ['spark-cast','donut-keypose-master-v1.png',[455,135,879,611],[777,610]],
 ['spark-recovery','donut-keypose-master-v1.png',[853,182,1222,612],[1178,611]],
 ['weaken-preparation','donut-keypose-correction-v2.png',[30,761,432,1160],[366,1159]],
 ['weaken-release','donut-keypose-correction-v2.png',[451,732,852,1162],[751,1161]],
 ['attention','donut-keypose-master-v1.png',[875,683,1229,1156],[1185,1155]]]},
 'warden':{'scale':.123,'pivot':[32,61],'baseline':'warden-front.png','poses':[
 ['idle','warden-keypose-master-v1.png',[22,273,396,593],[209,592]],
 ['windup','warden-keypose-master-v1.png',[417,258,785,593],[601,592]],
 ['hold','warden-keypose-master-v1.png',[812,169,1153,593],[982,592]],
 ['slam','warden-keypose-master-v1.png',[1203,337,1569,601],[1385,600]],
 ['recovery','warden-keypose-master-v1.png',[1589,295,1950,593],[1770,592]]]},
}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def palette(character):
 im=Image.open(baseline(DEF[character]['baseline']))
 return np.array(im.getpalette()[:48],dtype=np.int16).reshape(16,3)
def remap(rgb,pal):
 # Perceptual weighted squared RGB distance, opaque entries ONLY; no dithering.
 delta=rgb[:,:,None,:].astype(float)-pal[None,None,1:,:]
 weights=np.array([.30,.59,.11])
 return (np.sum(delta*delta*weights,axis=-1).argmin(axis=-1)+1).astype(np.uint8)
def author(ch,row):
 name,src,bounds,anchor=row; cfg=DEF[ch];sc=cfg['scale'];pivot=cfg['pivot'];pal=palette(ch)
 full=np.array(Image.open(source(src)).convert('RGBA')); l,t,r,b=bounds
 # Do NOT composite RGB hidden under alpha0: isolate actual visible component.
 crop=full[t:b,l:r].copy(); mask=crop[:,:,3]>=128
 labs,n=label(mask);sizes=np.bincount(labs.ravel());sizes[0]=0;mask=labs==sizes.argmax()
 indices=remap(crop[:,:,:3],pal);indices[~mask]=0
 out=np.zeros((64,64),dtype=np.uint8);coverage=np.zeros((64,64))
 # Each native pixel votes among palette source clusters; alpha-zero colors have
 # zero weight. Raster boundaries use coverage, not soft resampled alpha.
 for y in range(64):
  ya=max(t,int(np.floor(anchor[1]+(y-pivot[1]-.5)/sc)));yb=min(b,int(np.ceil(anchor[1]+(y-pivot[1]+.5)/sc)))
  if yb<=ya:continue
  for x in range(64):
   xa=max(l,int(np.floor(anchor[0]+(x-pivot[0]-.5)/sc)));xb=min(r,int(np.ceil(anchor[0]+(x-pivot[0]+.5)/sc)))
   if xb<=xa:continue
   block=indices[ya-t:yb-t,xa-l:xb-l];counts=np.bincount(block.ravel(),minlength=16)
   fraction=(block!=0).sum()/((yb-ya)*(xb-xa));coverage[y,x]=fraction
   if fraction>=.5:
    counts[0]=0;winner=int(counts.argmax())
    # Preserve tiny existing identity accents, not added effects: heart, jewel,
    # iris/collar, visor/core may occupy less than a cell's majority.
    accents={'carl':[14,15],'donut':[12,13,14],'warden':[13,14,15]}[ch]
    a=max(accents,key=lambda v:counts[v])
    if counts[a]/block.size>=.18:winner=a
    out[y,x]=winner
 # A deliberate single native pixel contour replaces uneven sub-pixel linework.
 occupied=out>0; rim=occupied & ~binary_erosion(occupied,structure=np.ones((3,3)),border_value=0)
 out[rim]=1
 # Clean single-color singleton dithery clusters. Preserve dark linework and
 # identity accents; no silhouette edits and no new anatomy.
 changes=[]
 accentset={1,14,15} if ch=='carl' else {1,11,12,13,14,15} if ch=='donut' else {1,12,13,14,15}
 old=out.copy()
 for y in range(1,63):
  for x in range(1,63):
   v=int(old[y,x])
   if not v or v in accentset:continue
   nb=old[y-1:y+2,x-1:x+2].copy();nb[1,1]=0
   if (nb==v).sum()==0:
    counts=np.bincount(nb.ravel(),minlength=16);counts[0]=0
    winner=int(counts.argmax())
    if counts[winner]>=5:out[y,x]=winner;changes.append([x,y,v,winner])
 return out,{'cleanup_singletons':changes,'source_bounds':bounds,'source_anchor':anchor,'source':src,'source_sha256':digest(source(src))}
def png(out,ch,path):
 im=Image.fromarray(out,'P');pal=palette(ch).flatten().tolist();im.putpalette(pal+[0]*(768-len(pal)))
 im.save(path,bits=4,transparency=0);return Image.open(path)
manifest={'status':'native_candidates_only','engine_changed':False,'emulator_verified':False,'method':'source palette-cluster voting + binary silhouette + native pixel cleanup','characters':{},'sources':[]}
all_edits=json.loads((R/'pixel_edits.json').read_text()) if (R/'pixel_edits.json').exists() else {}
for ch,cfg in DEF.items():
 dest=F/ch;dest.mkdir(exist_ok=True);rows=[];imgs=[]
 pal=palette(ch);(dest/'candidate.pal').write_text('JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,v)) for v in pal)+'\n')
 for row in cfg['poses']:
  arr,detail=author(ch,row);name=row[0]
  for x,y,v in all_edits.get(ch+'/'+name,[]):arr[y,x]=v
  p=dest/(name+'.png');im=png(arr,ch,p);imgs.append(im)
  bbox=im.getbbox();opaque=int((arr>0).sum()); top,lft=0,0
  assert im.size==(64,64) and im.mode=='P'; assert int(arr.max())<=15 and im.info.get('transparency')==0
  assert bbox and bbox[0]>=1 and bbox[2]<=63 and bbox[1]>=1 and bbox[3]<=62,(ch,name,bbox)
  assert bbox[3]==62,(ch,name,bbox)
  rowdata={'name':name,'path':str(p.relative_to(R)),'sha256':digest(p),'bbox':list(bbox),'opaque_pixels':opaque,'opaque_colors':len(np.unique(arr[arr>0])),'pivot':cfg['pivot'],'native_feature_edits':all_edits.get(ch+'/'+name,[]),**detail};rows.append(rowdata)
  if ch=='warden':
   assert not arr[:8].any();lift=np.zeros_like(arr);lift[:56]=arr[8:];q=dest/(name+'-runtime-lift8.png');png(lift,ch,q);rowdata['runtime_lift8_path']=str(q.relative_to(R));rowdata['runtime_lift8_sha256']=digest(q);rowdata['runtime_bbox']=[bbox[0],bbox[1]-8,bbox[2],bbox[3]-8]
 # Review cells show native 1x and 4x nearest-neighbor. Baseline stays unchanged.
 cw=286;sheet=Image.new('RGB',(cw*len(imgs),374),(38,43,52));d=ImageDraw.Draw(sheet)
 for i,(im,row) in enumerate(zip(imgs,rows)):
  x=i*cw;d.text((x+8,8),ch+' '+row['name'],fill=(240,240,235));d.text((x+8,26),'candidate, source baseline y61',fill=(170,184,196))
  rgba=im.convert('RGBA')
  for yy in range(64):
   for xx in range(64):
    col=(66,72,81) if ((xx//8+yy//8)%2) else (55,61,69)
    d.rectangle((x+12+xx*4,94+yy*4,x+15+xx*4,97+yy*4),fill=col)
  sheet.paste(rgba,(x+110,40),rgba);big=rgba.resize((256,256),Image.Resampling.NEAREST);sheet.paste(big,(x+12,94),big)
  d.line((x+12,94+62*4,x+267,94+62*4),fill=(90,145,151));d.text((x+8,355),'1x above / 4x below; local art preview',fill=(160,170,185))
 sheet.save(V/(ch+'-contact-sheet.png'))
 stack=Image.new('P',(64,len(imgs)*64),0);stack.putpalette(imgs[0].getpalette())
 for i,im in enumerate(imgs):stack.paste(im,(0,i*64))
 stack.save(dest/'candidate-pose-stack.png',bits=4,transparency=0)
 manifest['characters'][ch]={'palette':'existing approved per-character palette, unmodified','palette_rgb888':pal.tolist(),'scale':cfg['scale'],'pivot':cfg['pivot'],'frames':rows,'distinct_sha256_count':len(set(r['sha256'] for r in rows))}
for name,rel in sorted(REFS['sources'].items()):
 p=source(name);manifest['sources'].append({'path':rel,'sha256':digest(p),'dimensions':list(Image.open(p).size)})
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'PASS','frames':sum(len(c['frames']) for c in manifest['characters'].values()),'distinct':{c:m['distinct_sha256_count'] for c,m in manifest['characters'].items()},'emulator_verified':False}))
