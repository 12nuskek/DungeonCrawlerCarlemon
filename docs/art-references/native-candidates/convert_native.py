#!/usr/bin/env python3
"""Deterministic format conversion of approved generated art; no game changes.

Requires Python 3, Pillow, NumPy. Source SHA is checked before conversion.
Outputs are technical integration candidates, not emulator-validated final art.
"""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'carl-donut-proposed-replacement-reference-v2.png'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='4c713bb73c041af17a4daf9568087fc911f63daba617c184b68e0744b51619aa'
im=Image.open(SOURCE).convert('RGBA')
SPECS={
 'carl': {'front':(78,46,540,706),'back':(745,46,1206,725),'height':56},
 'donut':{'front':(108,725,627,1225),'back':(676,735,1157,1235),'height':44},
}
# RGB888 values snapped to multiples of 8, matching GBA RGB555 precision.
PALETTES={
 'carl': ['000000','201820','402820','704030','985830','b87048','d88858','f0a870','f8c890','f8dca8','585048','908870','c8bca0','f8f0d8','b82038','d84040'],
 'donut':['000000','201820','382830','504038','705040','985838','c07848','e8a868','f8d8a0','f8f0d0','a89878','e0b838','307870','48a090','f0d848','983838'],
}
PALETTES={k:[tuple(int(v[i:i+2],16)//8*8 for i in (0,2,4)) for v in vals] for k,vals in PALETTES.items()}

def perceptual_space(rgb):
    """Fast weighted RGB distance; palette mapping is deterministic, no dithering."""
    return np.asarray(rgb,dtype=np.float32)*np.array([0.8,1.0,0.65])

def palette_map(rgb,mask,palette):
    pixels=perceptual_space(rgb)[...,None,:]
    choices=perceptual_space(palette[1:])
    labels=np.argmin(((pixels-choices)**2).sum(axis=-1),axis=-1)+1
    return np.where(mask,labels,0).astype(np.uint8)

def convert_subject(box,height,palette,name,side,method='box'):
    crop=im.crop(box)
    a=np.asarray(crop.getchannel('A'))
    # Most opaque-looking source pixels are alpha 253. Never demand alpha==255.
    mask=(a>=128).astype(np.uint8)*255
    rgb=np.asarray(crop)[:,:,:3].copy()
    rgba=np.dstack([rgb,mask])
    width=round(crop.width*height/crop.height)
    # Area integration deliberately avoids point-sampling the irregular source grid.
    # It is a format-conversion sample, not final smooth output: output is hard-indexed.
    reduced=Image.fromarray(rgba,'RGBA').resize((width,height),Image.Resampling.BOX)
    pix=np.asarray(reduced)
    foreground=pix[:,:,3]>=128
    labels=palette_map(pix[:,:,:3],foreground,palette)
    # Preserve already-present tiny source color marks that mean-color reduction
    # otherwise washes out. This is source-mask coverage, not invented features.
    hsv=np.asarray(crop.convert('HSV'))
    hh,ss,vv=hsv[:,:,0],hsv[:,:,1],hsv[:,:,2]
    feature_changes=[]
    feature_masks=[]
    if name=='carl':
      red=(((hh<5)|(hh>244))&(ss>115)&(vv>120)&(a>=128))
      # Heart print lives on the existing shorts only; do not recolor reddish skin.
      red[:int(crop.height*0.50)]=False
      red[int(crop.height*0.71):]=False
      feature_masks.append(('existing red hearts',red,15,0.18))
    if name=='donut':
      teal=(hh>=105)&(hh<=143)&(ss>95)&(vv>80)&(a>=128)
      feature_masks.append(('existing teal collar jewel',teal,13,0.20))
      yellow=(hh>=25)&(hh<=55)&(ss>100)&(vv>100)&(a>=128)
      iris_region=np.zeros_like(yellow)
      if side=='front':iris_region[95:135,145:270]=True
      else:iris_region[95:145,370:445]=True
      yellow &= iris_region
      feature_masks.append(('existing amber iris',yellow,14,0.18))
      if side=='front':
        pupils=np.zeros_like(yellow)
        pupils[103:119,167:177]=True
        pupils[103:119,245:251]=True
        pupils &= np.max(rgb,axis=-1)<80
        feature_masks.append(('existing dark iris pupils',pupils,1,0.24))
    for label,source_mask,target,coverage in feature_masks:
      reduced_mask=np.asarray(Image.fromarray(source_mask.astype(np.uint8)*255).resize((width,height),Image.Resampling.BOX))
      selected=(reduced_mask>=round(255*coverage))&foreground
      ys,xs=np.where(selected&(labels!=target))
      feature_changes.append({'feature':label,'pixels':[[int(x),int(y),int(labels[y,x]),target] for x,y in zip(xs,ys)]})
      labels[selected]=target
    # Only isolated transparent pinholes completely surrounded by the same palette
    # index are repaired. No semantic contours/anatomy are invented.
    repairs=[]
    before=labels.copy()
    for y in range(1,height-1):
      for x in range(1,width-1):
        n=[int(before[y-1,x]),int(before[y+1,x]),int(before[y,x-1]),int(before[y,x+1])]
        if before[y,x]==0 and n[0]!=0 and len(set(n))==1:
          labels[y,x]=n[0];repairs.append([x,y,0,n[0]])
    frame=np.zeros((64,64),np.uint8)
    left=(64-width)//2;top=62-height
    frame[top:top+height,left:left+width]=labels
    return frame,{'source_box':box,'occupied_size':[width,height],'offset':[left,top],'pinhole_repairs':repairs,'source_color_preservation':feature_changes}

def save_indexed(data,palette,path):
    out=Image.fromarray(data,'P')
    flat=[v for c in palette for v in c]+[0]*(768-48)
    out.putpalette(flat);out.save(path,transparency=0,bits=4)

manifest={'provenance':'OpenAI image-generated reference, deterministic technical conversion; not emulator-validated','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'assets':{},'format':'indexed PNG, 4bpp, transparent index 0, RGB555-compatible palette values'}
for name,spec in SPECS.items():
  folder=ROOT/'assets'/name;folder.mkdir(parents=True,exist_ok=True)
  palette=PALETTES[name]
  for side in ('front','back'):
    data,info=convert_subject(spec[side],spec['height'],palette,name,side)
    path=folder/(side+'.png');save_indexed(data,palette,path)
    manifest['assets'][str(path.relative_to(ROOT))]=info
  # Preserve the existing engine's static duplicated-frame timing explicitly.
  front=np.asarray(Image.open(folder/'front.png'))
  back=np.asarray(Image.open(folder/'back.png'))
  save_indexed(np.vstack([front,front]),palette,folder/'anim_front.png')
  manifest['assets'][str((folder/'anim_front.png').relative_to(ROOT))]={'size':[64,128],'frames':2,'animation':'static duplicate of front.png; no movement authored'}
  if name=='carl':
    save_indexed(np.vstack([back]*4),palette,folder/'trainer_back.png')
    manifest['assets'][str((folder/'trainer_back.png').relative_to(ROOT))]={'size':[64,256],'frames':4,'animation':'static duplicate of back.png; existing intro timing retained'}
  pal='JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,c)) for c in palette)+'\n'
  (folder/'normal.pal').write_text(pal);(folder/'shiny.pal').write_text(pal)

# A plain diagnostic contact sheet, never game evidence. Exact native pixels first.
(ROOT/'previews').mkdir(parents=True,exist_ok=True)
native=Image.new('RGB',(272,80),(77,78,86))
for i,(name,side) in enumerate((('carl','front'),('carl','back'),('donut','front'),('donut','back'))):
  asset=Image.open(ROOT/'assets'/name/(side+'.png')).convert('RGBA')
  native.paste(asset,(4+i*67,8),asset)
native.save(ROOT/'previews/battle-native-1x.png')
native.resize((1632,480),Image.Resampling.NEAREST).save(ROOT/'previews/battle-native-6x.png')
manifest['note']='Battle fronts/backs plus explicitly duplicated static animation/trainer packs. Icons and overworld require separate review.'
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
