#!/usr/bin/env python3
"""Mechanical candidate conversion, never a claim of in-engine acceptance.
Generated reference -> isolated alpha crops -> fixed native bounds -> deterministic
coverage downsample -> nearest fixed palette with no dithering. Nothing is drawn
or retouched here. All coordinates, targets and policy choices are explicit.
"""
from pathlib import Path
import hashlib,json,math
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
SOURCE=R/'source/environment-props-reference.png'
P_SHARED=[(0,0,0),(25,29,39),(62,46,43),(115,72,51),(189,120,82),(244,183,132),(255,220,172),(241,232,202),(177,163,142),(191,53,67),(111,34,53),(231,182,65),(69,151,145),(35,80,91),(110,118,136),(190,204,211)]
P_ENV=[(0,0,0),(18,26,36),(30,43,53),(47,61,68),(65,79,82),(92,107,106),(129,145,135),(179,190,166),(39,75,78),(54,114,113),(82,164,148),(199,168,100),(143,94,65),(204,87,66),(223,211,174),(244,236,205)]
# Visual inspection showed generated column boundaries differ from a uniform grid.
xs=[0,400,750,1080,1449];ys=[0,282,541,803,1086]
names=['gate_closed','gate_open','stairs_up','stairs_down','workbench','warning_sign','cache_sealed','cache_open','trap_armed','trap_spent','secret_cracked','secret_breached','bedroll','storage_rack','wall_lantern','rubble']
# World props preserve one-cell event compatibility. Larger BG art is an optional
# candidate and requires new metatile placement, layering and collision review.
world_names=names[4:10]+names[12:]
env_sizes={'gate_closed':(32,32),'gate_open':(32,32),'stairs_up':(32,32),'stairs_down':(32,32),'workbench':(32,16),'warning_sign':(16,32),'cache_sealed':(16,16),'cache_open':(16,16),'trap_armed':(16,16),'trap_spent':(16,16),'secret_cracked':(16,32),'secret_breached':(16,32),'bedroll':(32,16),'storage_rack':(16,32),'wall_lantern':(16,32),'rubble':(16,16)}
source=Image.open(SOURCE).convert('RGBA');manifest={'status':'UNINTEGRATED_CANDIDATES','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_size':source.size,'base_commit':'bf27e2692025eb4291ffbf992a3b6412340d32cd','alpha_policy':'crop alpha >=128; BOX coverage downsample; keep output alpha >=128; output binary alpha at palette index0','resampling':'BOX; fixed-palette weighted RGB nearest match, no dither','assets':[]}
(R/'native/world_shared').mkdir(parents=True,exist_ok=True);(R/'native/background_env6').mkdir(parents=True,exist_ok=True);(R/'source/crops').mkdir(parents=True,exist_ok=True);(R/'previews').mkdir(exist_ok=True)
def native(crop,size,palette,wire=False):
 w,h=size; maxw,maxh=w-2,h-2
 scale=min(maxw/crop.width,maxh/crop.height)
 nw,nh=max(1,round(crop.width*scale)),max(1,round(crop.height*scale))
 if wire:nw,nh=14,8
 small=crop.resize((nw,nh),Image.Resampling.BOX)
 out=Image.new('P',size,0);out.putpalette(sum((list(c) for c in palette),[])+[0]*(768-48))
 ox,oy=(w-nw)//2,h-1-nh
 pixels=[]
 for r,g,b,a in small.getdata():
  if a<(48 if wire else 128):pixels.append(0)
  else:pixels.append(min(range(1,16),key=lambda i:2*(r-palette[i][0])**2+3*(g-palette[i][1])**2+(b-palette[i][2])**2))
 temp=Image.new('P',(nw,nh));temp.putdata(pixels);out.paste(temp,(ox,oy));out.info['transparency']=0
 return out
for i,name in enumerate(names):
 x,y=i%4,i//4;box=(xs[x],ys[y],xs[x+1],ys[y+1]);cell=source.crop(box)
 bounds=cell.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert bounds
 crop=cell.crop(bounds);crop.save(R/'source/crops'/f'{name}.png')
 for category,size,pal in [('background_env6',env_sizes[name],P_ENV)]+([('world_shared',(16,16),P_SHARED)] if name in world_names else []):
  out=native(crop,size,pal);path=R/'native'/category/f'{name}.png';out.save(path,bits=4,transparency=0)
  manifest['assets'].append({'name':name,'category':category,'path':str(path.relative_to(R)),'dimensions':size,'source_crop_bounds':[box[0]+bounds[0],box[1]+bounds[1],box[0]+bounds[2],box[1]+bounds[3]],'opaque_bounds':out.getbbox(),'palette':'existing shared.pal' if category=='world_shared' else 'existing dungeon palette bank6','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
# Narrow follow-on state sheet: no pressure-plate substitution for narrated wire.
state_path=R/'source/state-props-reference.png'
state=Image.open(state_path).convert('RGBA')
manifest['state_source_sha256']=hashlib.sha256(state_path.read_bytes()).hexdigest()
for i,name in enumerate(['quest_tag','wire_live','wire_spent','encounter_remains']):
 x,y=i%2,i//2; box=(x*state.width//2,y*state.height//2,(x+1)*state.width//2,(y+1)*state.height//2)
 cell=state.crop(box);bounds=cell.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert bounds
 crop=cell.crop(bounds);crop.save(R/'source/crops'/f'{name}.png')
 for category,size,pal in [('world_shared',(16,16),P_SHARED),('background_env6',(16,16),P_ENV)]:
  out=native(crop,size,pal,wire=name.startswith('wire_'));path=R/'native'/category/f'{name}.png';out.save(path,bits=4,transparency=0)
  manifest['assets'].append({'name':name,'category':category,'path':str(path.relative_to(R)),'dimensions':size,'native_adaptation':'Wire pair uses consistent 14x8 content bounds and alpha coverage threshold48 to retain thin cable; remaining assets preserve aspect ratio and threshold128.','source_file':str(state_path.relative_to(R)),'source_crop_bounds':[box[0]+bounds[0],box[1]+bounds[1],box[0]+bounds[2],box[1]+bounds[3]],'opaque_bounds':out.getbbox(),'palette':'existing shared.pal' if category=='world_shared' else 'existing dungeon palette bank6','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
for name,pal in [('world_shared',P_SHARED),('background_env6',P_ENV)]:
 (R/'native'/name/'palette.pal').write_text('JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,c)) for c in pal)+'\n')
 assets=[a for a in manifest['assets'] if a['category']==name]
 preview=Image.new('RGB',(4*160,math.ceil(len(assets)/4)*160),(37,42,46));d=ImageDraw.Draw(preview)
 for i,a in enumerate(assets):
  im=Image.open(R/a['path']).convert('RGBA');scale=4 if im.height>16 or im.width>16 else 6
  scaled=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
  ox=(i%4)*160+(160-scaled.width)//2;oy=(i//4)*160+8
  preview.paste(scaled,(ox,oy),scaled);d.text(((i%4)*160+8,(i//4)*160+141),a['name'],fill=(220,221,202))
 preview.save(R/'previews'/f'{name}-enlarged.png')
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Converted',len(manifest['assets']),'native-size candidates, not integrated or in-engine verified.')
