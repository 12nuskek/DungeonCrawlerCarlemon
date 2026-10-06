#!/usr/bin/env python3
"""Deterministic technical conversion of generated opponent references.

This does not edit the game repository. Output is NOT runtime-verified.
Dependencies: Python 3, Pillow, NumPy. No network, randomness or dithering.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source/opponents-reference-v2.png'
SOURCE_SHA='000068d6bdae0a60e93836438920f4f3b847cee6aca8335733d3f05c7ac4a279'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
source=Image.open(SOURCE).convert('RGBA')
# Bounds measured from the five independent alpha>=128 connected components.
# Do not use equal grid crops: Warden extends beyond its nominal cell.
SPECS={
 'scuttler':{'box':(41,93,528,459),'width':52,'role':'Trial melee foe and patrol melee partner','species':'ZIGZAGOON'},
 'grub':{'box':(592,132,985,442),'width':42,'role':'Trial melee foe','species':'WURMPLE'},
 'guard':{'box':(1056,36,1488,500),'height':50,'role':'Durable patrol, BRACE then TACKLE','species':'SPINDA'},
 'howler':{'box':(22,525,552,956),'width':56,'role':'WEAKEN patrol and Warden helper','species':'WHISMUR'},
 'warden':{'box':(560,476,1200,993),'width':60,'role':'Heavy WIND UP / SLAM gate boss','species':'LOUDRED'},
}
PALETTES={
 'scuttler':['000000','100818','281820','482030','703038','884030','a85030','d07838','e8a050','f8c070','786858','b8a880','e8d8a0','f8f0c8','b81828','f84028'],
 'grub':['000000','081820','102838','184858','206070','308088','48a8a0','70c8b8','98d8b8','c8f0d0','305850','688870','b8b088','f0e8b8','e09810','f8d848'],
 'guard':['000000','080810','102838','204050','286070','488088','384058','586878','808898','a0a8b8','c8d0d0','f8f0d8','881820','e83020','f8a818','f8d850'],
 'howler':['000000','180818','301028','481030','681840','982848','c83850','e85860','f89078','382038','a89870','d8c890','f8e8b8','b87818','e8b820','f8e858'],
 'warden':['000000','080810','102838','204050','286070','488088','384058','586878','808898','a0a8b8','c8d0d0','f8f0d8','881820','e83020','f8a818','f8d850'],
}
PALETTES={n:[tuple(int(c[i:i+2],16)//8*8 for i in (0,2,4)) for c in colors] for n,colors in PALETTES.items()}
SHARED=[tuple(map(int,l.split())) for l in (ROOT/'source/existing-shared.pal').read_text().splitlines()[3:19]]
SHARED555=[tuple(v//8*8 for v in c) for c in SHARED]

def save_indexed(data,palette,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    im=Image.fromarray(data,'P');im.putpalette([v for c in palette for v in c]+[0]*(768-48))
    im.save(path,transparency=0,bits=4)

def convert(name,size,palette):
    crop=source.crop(SPECS[name]['box']);rgba=np.array(crop)
    rgba[:,:,3]=np.where(rgba[:,:,3]>=128,255,0)
    reduced=np.asarray(Image.fromarray(rgba).resize(size,Image.Resampling.BOX))
    mask=reduced[:,:,3]>=128
    weights=np.array([0.8,1.0,0.65])
    colors=np.array(palette[1:],float)*weights
    rgb=reduced[:,:,:3].astype(float)*weights
    labels=(np.argmin(np.sum((rgb[:,:,None,:]-colors)**2,axis=-1),axis=-1)+1).astype(np.uint8)
    labels[~mask]=0
    # Preserve source accent-color coverage. These masks cannot add geometry.
    hsv=np.asarray(crop.convert('HSV'));h,s,v=hsv[:,:,0],hsv[:,:,1],hsv[:,:,2]
    visible=rgba[:,:,3]>0
    features=[]
    if name=='scuttler':
        region=np.zeros_like(visible);region[204:242,116:160]=True;region[198:242,189:241]=True
        features.append(('red eyes',((h<4)|(h>250))&(s>185)&(v>150)&visible&region,15,0.20))
    elif name in ('grub','howler'):
        features.append(('golden eyes',(h>=20)&(h<=47)&(s>150)&(v>155)&visible,15,0.20))
    else:
        features.append(('existing red visor/core',((h<9)|(h>246))&(s>150)&(v>120)&visible,13,0.20))
        features.append(('existing amber detail',(h>=18)&(h<=45)&(s>150)&(v>140)&visible,14,0.20))
    changes=[]
    for feature,m,target,coverage in features:
        cov=np.asarray(Image.fromarray(m.astype(np.uint8)*255).resize(size,Image.Resampling.BOX))
        choose=(cov>=round(coverage*255))&mask
        ys,xs=np.where(choose&(labels!=target))
        changes.append({'feature':feature,'changes':[[int(x),int(y),int(labels[y,x]),target] for y,x in zip(ys,xs)]})
        labels[choose]=target
    return labels,changes

manifest={'source_sha256':SOURCE_SHA,'source_reference':'source/opponents-reference-v2.png','repository_base':'d8f8ae62a3fba0dbe4c2c17fa2a4a1ce193bc530','provenance':'OpenAI built-in image generation, one density simplification revision, deterministic technical conversion with source color-mask preservation. No third-party tracing. Original tutorial adaptations, not book-canon identification.','assets':{},'runtime_status':'Not integrated, compiled or emulator-tested.'}
for name,spec in SPECS.items():
    l,t,r,b=spec['box'];w=spec.get('width');h=spec.get('height')
    if w is None:w=round((r-l)*h/(b-t))
    if h is None:h=round((b-t)*w/(r-l))
    data,changes=convert(name,(w,h),PALETTES[name])
    frame=np.zeros((64,64),np.uint8);left=(64-w)//2;top=62-h
    frame[top:top+h,left:left+w]=data
    folder=ROOT/'assets'/name
    save_indexed(frame,PALETTES[name],folder/'front.png')
    # Existing opponents have front==back. Preserve that supported static contract;
    # this back.png is explicitly not a newly drawn rear view.
    save_indexed(frame,PALETTES[name],folder/'back.png')
    save_indexed(np.vstack([frame,frame]),PALETTES[name],folder/'anim_front.png')
    pal='JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,c)) for c in PALETTES[name])+'\n'
    (folder/'normal.pal').write_text(pal);(folder/'shiny.pal').write_text(pal)
    manifest['assets'][name]={**spec,'occupied_size':[w,h],'offset':[left,top],'source_color_preservation':changes,'palette':PALETTES[name],'back':'same as front; preserves current non-playable opponent contract','animation':'two identical front frames; no authored motion'}
    # Icons and four existing stationary world tokens use the EXISTING shared
    # runtime palette. Never bind these remapped indices to a battle palette.
    sw=round(w*0.5);sh=round(h*0.5)
    small=Image.open(folder/'front.png').convert('RGBA').crop((left,top,left+w,top+h)).resize((sw,sh),Image.Resampling.BOX)
    smallpix=np.asarray(small);mask=smallpix[:,:,3]>=128
    rgb=smallpix[:,:,:3].astype(float)*np.array([0.8,1.0,0.65])
    cols=np.array(SHARED555[1:],float)*np.array([0.8,1.0,0.65])
    labels=(np.argmin(((rgb[:,:,None,:]-cols)**2).sum(axis=-1),axis=-1)+1).astype(np.uint8);labels[~mask]=0
    icon=np.zeros((32,32),np.uint8);ix=(32-sw)//2;iy=31-sh;icon[iy:iy+sh,ix:ix+sw]=labels
    save_indexed(np.vstack([icon,icon]),SHARED,folder/'icon.png')
    if name!='grub':save_indexed(icon,SHARED,folder/'overworld.png')
    manifest['assets'][name]['small_assets']={'occupied_size':[sw,sh],'offset':[ix,iy],'palette':'UNCHANGED existing-shared.pal, runtime RGB555 truncated','icon':'two static 32x32 frames','overworld':'one stationary 32x32 token' if name!='grub' else 'none; no mapped Grub token exists','note':'Source-derived format-conversion candidates; separate in-game world/palette review still required.'}

# Unlabelled native-pixel diagnostic strips; not game evidence.
pre=ROOT/'previews';pre.mkdir(exist_ok=True)
for kind,cell,size in [('battle',64,(344,80)),('world',32,(184,48))]:
    sheet=Image.new('RGB',size,(77,78,86))
    for i,name in enumerate(SPECS):
        p=ROOT/'assets'/name/('front.png' if kind=='battle' else 'icon.png')
        im=Image.open(p).convert('RGBA').crop((0,0,cell,cell));sheet.paste(im,(8+i*(cell+4),8),im)
    sheet.save(pre/f'{kind}-native-1x.png');sheet.resize((size[0]*6,size[1]*6),Image.Resampling.NEAREST).save(pre/f'{kind}-native-6x.png')
# Compose reference on a neutral background for honest alpha review.
ref=Image.new('RGBA',source.size,(77,78,86,255));ref.alpha_composite(source);ref.convert('RGB').save(pre/'reference-neutral.png')
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Converted 5 battle sets, 5 shared-palette icons and 4 stationary tokens. NOT runtime-verified.')
