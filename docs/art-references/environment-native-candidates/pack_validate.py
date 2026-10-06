#!/usr/bin/env python3
"""Validate art candidates and pack reversible deduplicated 8x8 BG tiles.
No metatile IDs, game behavior, collision, event, palette-slot or script bindings
are changed here. The atlas is a staging aid, not a repository-ready replacement.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,math,struct,subprocess,sys
R=Path(__file__).resolve().parent
from collections import Counter
manifest=json.loads((R/'manifest.json').read_text());arch=json.loads((R/'architecture-manifest.json').read_text())
files=sorted((R/'native').glob('*/*.png'))
checks=[]
def check(ok,description):
 assert ok,description;checks.append(description)
for p in files:
 im=Image.open(p)
 check(im.mode=='P',f'{p.relative_to(R)} indexed P')
 check(im.width%8==0 and im.height%8==0,f'{p.relative_to(R)} 8px-aligned')
 check(im.getextrema()[1]<16,f'{p.relative_to(R)} indices below16')
 check(im.info.get('transparency')==0,f'{p.relative_to(R)} index0 transparent')
 check(set(im.convert('RGBA').getchannel('A').getdata())<={0,255},f'{p.relative_to(R)} binary alpha')
 palfile=p.parent/'palette.pal'
 palette=[tuple(map(int,line.split())) for line in palfile.read_text().splitlines()[3:19]]
 check(im.getpalette()[:48]==sum((list(c) for c in palette),[]),f'{p.relative_to(R)} embedded palette matches target')
 if p.parent.name=='world_shared':
  check(im.size==(16,16),f'{p.relative_to(R)} unchanged one-cell native footprint')
  b=im.getbbox();check(b and b[0]>=1 and b[1]>=1 and b[2]<=15 and b[3]<=15,f'{p.relative_to(R)} opaque margin')
for n in arch['tiles']:
 check(Image.open(R/'native/architecture'/f'{n}.png').size==(16,16),f'{n} exact metatile bounds')
for p in sorted((R/'native/architecture').glob('floor_*.png')):
 check(0 not in Image.open(p).getdata(),f'{p.name} fully opaque floor; no transparency-checker ambiguity')
# Floor assembly uses one body index and sparse broken seams, not alternating fills.
for p in sorted((R/'native/architecture').glob('floor_slab_*.png')):
 counts=Counter(Image.open(p).getdata());check(counts[3]>=241,f'{p.name} at least94percent quiet floor body')
# Useful seam checks. These test intended compatible edges, not a claim that any
# arbitrary named tiles can adjoin in every orientation.
def a(n):return Image.open(R/'native/architecture'/f'{n}.png')
check(list(a('wall_top_plain').crop((0,0,1,16)).getdata())==list(a('wall_top_plain').crop((15,0,16,16)).getdata()),'wall cap repeats seamlessly horizontally')
check(list(a('wall_face_a').crop((15,0,16,16)).getdata())==list(a('wall_face_b').crop((0,0,1,16)).getdata()),'staggered wall faces have coherent joins')
mat=Image.new('P',(48,32))
for y,row in enumerate([['mat_corner_nw','mat_top','mat_corner_ne'],['mat_corner_sw','mat_bottom','mat_corner_se']]):
 for x,n in enumerate(row):mat.paste(a(n),(x*16,y*16))
check(all(mat.getpixel((x,2))==11 for x in range(2,46)),'mat upper trim continuous across three cells')
check(all(mat.getpixel((x,29))==11 for x in range(2,46)),'mat lower trim continuous across three cells')
check(all(mat.getpixel((x,y))==8 for x in [15,16,31,32] for y in [15,16]),'mat has no internal seams')
# Reject accidental pressure-plate integration: kept only as a reference alternative.
bgfiles=sorted((R/'native/architecture').glob('*.png'))+sorted(p for p in (R/'native/background_env6').glob('*.png') if not p.name.startswith('trap_'))
unique=[bytes(64)];lookup={unique[0]:0};assetdata=[]
for p in bgfiles:
 im=Image.open(p);groups=[]
 for my in range(im.height//16):
  for mx in range(im.width//16):
   ids=[]
   for q in range(4):
    xx=mx*16+(q%2)*8;yy=my*16+(q//2)*8;raw=bytes(im.crop((xx,yy,xx+8,yy+8)).getdata())
    if raw not in lookup:lookup[raw]=len(unique);unique.append(raw)
    ids.append(lookup[raw])
   groups.append({'x':mx,'y':my,'local_tile_ids_tl_tr_bl_br':ids,'suggested_bg_entries':[(512+i)|(6<<12) for i in ids]})
 assetdata.append({'source':str(p.relative_to(R)),'size':list(im.size),'metatile_chunks':groups})
check(len(unique)<=512,'combined deduplicated BG tile count fits secondary512-tile budget')
w=128;h=math.ceil(len(unique)/16)*8;atlas=Image.new('P',(w,h));atlas.putpalette(a('floor_plain').getpalette())
raw4=bytearray()
for i,tile in enumerate(unique):
 t=Image.frombytes('P',(8,8),tile);atlas.paste(t,((i%16)*8,(i//16)*8))
 raw4.extend(tile[j]|(tile[j+1]<<4) for j in range(0,64,2))
atlas.save(R/'native/background-tiles-8x8.png',transparency=0,bits=4)
(R/'native/background-tiles.4bpp').write_bytes(raw4)
pack={'status':'UNINTEGRATED_STAGING_AID','palette_bank':6,'global_tile_base':512,'unique_tiles':len(unique),'allocated_tiles':w*h//64,'remaining_tiles':512-len(unique),'raw4bpp_bytes':len(raw4),'atlas_size':[w,h],'empty_overlay_local_tile':0,'warning':'Do not replace existing atlas without remapping every used metatile and regenerating/validating behavior and layer mappings. Props with transparency need floor underlay; no collision/event/script bindings are supplied.','excluded_pressure_plate_sources':['trap_armed','trap_spent'],'assets':assetdata}
(R/'tile-pack.json').write_text(json.dumps(pack,indent=2)+'\n')
# Verify reconstructibility from actual PNG packed atlas.
for item in assetdata:
 original=Image.open(R/item['source']);reconstructed=Image.new('P',original.size)
 for g in item['metatile_chunks']:
  for q,tid in enumerate(g['local_tile_ids_tl_tr_bl_br']):
   tile=atlas.crop(((tid%16)*8,(tid//16)*8,(tid%16+1)*8,(tid//16+1)*8))
   reconstructed.paste(tile,(g['x']*16+(q%2)*8,g['y']*16+(q//2)*8))
 check(bytes(original.getdata())==bytes(reconstructed.getdata()),f'{item["source"]} lossless atlas reconstruction')
check(all((raw4[j//2]>>(4*(j%2)))&15==unique[j//64][j%64] for j in range(len(unique)*64)),'raw GBA 4bpp nibble packing round-trips')
report={'status':'PASS','scope':'Static native-asset and mechanical-reproduction checks only. No in-engine integration, collision or emulator evidence.','native_image_count':len(files),'world_16x16_candidates':len(list((R/'native/world_shared').glob('*.png'))),'architecture_16x16_candidates':arch['count'],'background_prop_candidates':len(list((R/'native/background_env6').glob('*.png'))),'checks_passed':len(checks),'checks':checks,'bg_pack':{k:pack[k] for k in ['unique_tiles','allocated_tiles','remaining_tiles','raw4bpp_bytes','atlas_size']}}
(R/'validation-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
