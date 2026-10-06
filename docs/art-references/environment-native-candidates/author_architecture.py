#!/usr/bin/env python3
"""Original native pixel architecture, authored as deterministic geometry.
Standalone art preparation only; never imports or mutates the game repository.
This follows the repository's code-authored indexed-art method. No stock art.
"""
from pathlib import Path
import json,math,struct,hashlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
OUT=R/'native/architecture';OUT.mkdir(parents=True,exist_ok=True)
P=[(0,0,0),(18,26,36),(30,43,53),(47,61,68),(65,79,82),(92,107,106),(129,145,135),(179,190,166),(39,75,78),(54,114,113),(82,164,148),(199,168,100),(143,94,65),(204,87,66),(223,211,174),(244,236,205)]
# Optional BG-only palette choices. Exact 5-bit-friendly values; sprite/OBJ
# palettes are completely independent and MUST remain unchanged.
NEUTRAL=[(0,0,0),(16,24,24),(32,40,40),(48,56,56),(64,72,64),(88,96,80),(120,136,112),(168,184,144),(32,64,56),(48,88,72),(88,136,104),(184,152,80),(120,80,48),(184,80,48),(208,200,160),(232,224,184)]
WARM=[(0,0,0),(24,24,24),(40,40,40),(64,64,56),(80,80,64),(112,104,80),(144,136,104),(192,184,144),(40,64,56),(56,88,72),(104,144,104),(200,160,88),(136,88,48),(184,80,48),(224,208,168),(248,232,192)]
COLD=[(0,0,0),(16,24,32),(24,40,48),(40,56,64),(56,72,80),(80,104,104),(112,136,128),(160,184,152),(24,56,64),(40,88,88),(72,144,128),(184,144,72),(112,80,56),(176,80,56),(208,200,160),(232,224,184)]
DANGER=[(0,0,0),(24,24,24),(40,40,40),(56,56,56),(80,72,64),(104,88,72),(136,112,88),(176,160,120),(40,56,56),(56,80,72),(88,120,96),(192,144,72),(136,80,48),(192,80,48),(216,192,152),(240,224,184)]
A={};meta={}
def canvas(fill=0):
 im=Image.new('P',(16,16),fill);im.putpalette(sum((list(c) for c in P),[])+[0]*(768-48));im.info['transparency']=0;return im

def put(name,im,role,base):
 A[name]=im;meta[name]={'role':role,'suggested_existing_behavior':base,'size':[16,16]}

def floor():return canvas(3)
# Broad quiet 32x32 slab pattern, not one bright boxed square per step.
for ry in range(2):
 for rx in range(2):
  im=floor();d=ImageDraw.Draw(im)
  if rx:d.line((15,9,15,15),fill=2)
  if ry:d.line((0,15,7,15),fill=2)
  put(f'floor_slab_{rx}{ry}',im,'optional broken joint quadrant; place sparsely, never alternate across entire room','0x201')
for variant in ['plain','scuff','crack','dust','repair','drain','warm_pool','cold_pool']:
 im=floor();d=ImageDraw.Draw(im)
 if variant=='scuff':d.line((3,10,6,10),fill=4);d.line((6,9,8,9),fill=4)
 if variant=='crack':d.line([(3,0),(4,3),(7,5),(6,8),(9,11)],fill=2);d.line((6,8,3,10),fill=2)
 if variant=='dust':
  for x,y in [(1,3),(2,4),(4,3),(3,6),(6,2),(1,9)]:d.point((x,y),4)
 if variant=='repair':d.rectangle((3,4,12,12),fill=4);d.line((3,12,12,12),fill=2);d.line((12,4,12,12),fill=2);d.line((4,4,9,4),fill=5)
 if variant=='drain':
  d.rectangle((3,5,12,10),fill=2)
  for x in [4,7,10]:d.line((x,6,x,9),fill=5)
 if variant in ['warm_pool','cold_pool']:
  d.polygon([(1,0),(14,0),(12,7),(3,7)],fill=4)
 put('floor_'+variant,im,'walkable quiet floor/detail','0x201')
put('void',canvas(1),'opaque dark cutaway; collision remains blocked','0x211')
# Three shallow bands establish wall thickness and top-left light.
def cap():
 im=canvas(1);d=ImageDraw.Draw(im);d.rectangle((0,2,15,10),fill=5);d.line((0,2,15,2),fill=7);d.line((0,3,15,3),fill=6);d.line((0,10,15,10),fill=3);d.rectangle((0,11,15,14),fill=2);d.line((0,15,15,15),fill=1);return im
for variant in ['plain','join','chip','damp']:
 im=cap();d=ImageDraw.Draw(im)
 if variant=='join':d.line((10,4,10,9),fill=3);d.line((11,4,11,9),fill=6)
 if variant=='chip':d.line([(5,2),(5,4),(7,4),(7,2)],fill=3);d.point((8,3),6)
 if variant=='damp':d.line((3,8,6,8),fill=8);d.line((6,9,9,9),fill=8)
 put('wall_top_'+variant,im,'north cutaway cap with opaque void outside','0x211')
 put('wall_bottom_'+variant,im.transpose(Image.Transpose.FLIP_TOP_BOTTOM),'south cutaway cap with opaque void outside','0x211')
def face(phase=0):
 im=canvas(4);d=ImageDraw.Draw(im)
 d.line((0,0,15,0),fill=2);d.line((0,1,15,1),fill=5)
 d.line((0,8,15,8),fill=2);d.line((0,9,15,9),fill=5)
 d.line((4 if phase else 12,2,4 if phase else 12,7),fill=3)
 d.line((12 if phase else 4,10,12 if phase else 4,13),fill=3)
 d.rectangle((0,14,15,15),fill=1)
 return im
for variant in ['a','b','damp','chip','repair','foot']:
 im=face(variant=='b');d=ImageDraw.Draw(im)
 if variant=='damp':d.line([(2,3),(2,6),(3,7),(3,11)],fill=8);d.point((4,12),8)
 if variant=='chip':d.line([(6,1),(7,4),(6,6)],fill=2);d.line((9,10,11,10),fill=6)
 if variant=='repair':d.rectangle((5,3,11,6),fill=5);d.line((5,6,11,6),fill=3)
 if variant=='foot':d.line((0,12,15,12),fill=5);d.rectangle((0,13,15,15),fill=1)
 put('wall_face_'+variant,im,'north wall frontal face, full blocking tile','0x219')
for side in ['left','right']:
 im=canvas(1);d=ImageDraw.Draw(im)
 if side=='left':
  d.rectangle((7,0,15,15),fill=5);d.line((7,0,7,15),fill=7);d.line((8,0,8,15),fill=6);d.rectangle((13,0,15,15),fill=2);d.line((9,8,12,8),fill=3)
 else:
  d.rectangle((0,0,8,15),fill=4);d.line((0,0,0,15),fill=2);d.line((1,0,1,15),fill=3);d.line((8,0,8,15),fill=6);d.line((3,8,7,8),fill=3)
 put('wall_side_'+side,im,'vertical cutaway return with thickness','0x211')
# Corner modules meet top/side silhouettes, filling void only outside room.
for orientation in ['nw','ne','sw','se']:
 im=cap();d=ImageDraw.Draw(im)
 isleft=orientation.endswith('w');isnorth=orientation.startswith('n')
 if isleft:
  d.rectangle((0,0,6,15),fill=1);d.rectangle((7,2,15,10),fill=5);d.line((7,2,15,2),fill=7);d.line((7,2,7,15),fill=7);d.rectangle((8,11,12,15),fill=5);d.rectangle((13,11,15,15),fill=2)
 else:
  d.rectangle((9,0,15,15),fill=1);d.rectangle((0,2,8,10),fill=4);d.line((0,2,8,2),fill=6);d.line((8,2,8,15),fill=6);d.rectangle((2,11,7,15),fill=4);d.rectangle((0,11,1,15),fill=2)
 if not isnorth:im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
 put('corner_outer_'+orientation,im,'outer cutaway corner; choose collision by architectural position','0x211')
for orientation in ['nw','ne','sw','se']:
 im=floor();d=ImageDraw.Draw(im)
 top=orientation.startswith('n');left=orientation.endswith('w')
 yy=(0,4) if top else (11,15);xx=(0,4) if left else (11,15)
 d.rectangle((0,yy[0],15,yy[1]),fill=2);d.rectangle((xx[0],0,xx[1],15),fill=2)
 d.line((0,yy[1] if top else yy[0],15,yy[1] if top else yy[0]),fill=4)
 put('corner_inner_'+orientation,im,'walkable floor contact shadow for reentrant corner','0x201')
for side in ['left','right']:
 im=floor();d=ImageDraw.Draw(im);x0=0 if side=='left' else 10
 d.rectangle((x0,0,x0+5,15),fill=2);d.rectangle((x0+1,0,x0+4,14),fill=5);d.line((x0+1,0,x0+1,14),fill=7)
 for y in [4,10]:d.line((x0+2,y,x0+4,y),fill=3)
 put('door_jamb_'+side,im,'framing overlay flattened on floor; review collision separately','0x201')
im=cap();d=ImageDraw.Draw(im);d.rectangle((0,6,15,12),fill=5);d.line((0,6,15,6),fill=7);d.rectangle((0,13,15,15),fill=1);put('door_lintel',im,'door head/threshold framing','0x211')
for axis in ['h','v']:
 im=floor();d=ImageDraw.Draw(im)
 if axis=='h':d.rectangle((0,6,15,10),fill=5);d.line((0,6,15,6),fill=7);d.line((0,11,15,11),fill=2)
 else:d.rectangle((6,0,10,15),fill=5);d.line((6,0,6,15),fill=7);d.line((11,0,11,15),fill=2)
 put('threshold_'+axis,im,'walkable threshold; does not itself warp','0x201')
for state in ['lit','unlit']:
 im=face();d=ImageDraw.Draw(im);d.rectangle((6,2,9,12),fill=1);d.rectangle((5,3,10,10),fill=2);d.rectangle((6,4,9,8),fill=11 if state=='lit' else 3)
 if state=='lit':d.rectangle((7,5,8,7),fill=15)
 d.line((5,11,10,11),fill=12);put('wall_lamp_'+state,im,'fixed wall lamp; restrained, no glow tile spam','0x219')
for variant in ['horizontal','vertical','broken']:
 im=floor();d=ImageDraw.Draw(im)
 if variant=='vertical':d.line((8,0,8,15),fill=2);d.line((9,0,9,15),fill=8);d.rectangle((7,7,10,8),fill=5)
 elif variant=='horizontal':d.line((0,8,15,8),fill=2);d.line((0,9,15,9),fill=8);d.rectangle((7,7,8,10),fill=5)
 else:d.line((0,8,5,8),fill=8);d.line((9,10,15,10),fill=2);d.point((6,9),11)
 put('conduit_'+variant,im,'walkable service cable, visual causal connection only','0x201')
for edge in ['middle','top','bottom','left','right','corner_nw','corner_ne','corner_sw','corner_se']:
 im=canvas(8);d=ImageDraw.Draw(im)
 if edge in ['top','corner_nw','corner_ne']:d.line((0,0,15,0),fill=3)
 if edge in ['bottom','corner_sw','corner_se']:d.line((0,15,15,15),fill=3)
 if edge in ['left','corner_nw','corner_sw']:d.line((0,0,0,15),fill=3)
 if edge in ['right','corner_ne','corner_se']:d.line((15,0,15,15),fill=3)
 if edge in ['top','corner_nw','corner_ne']:d.line((2 if edge=='corner_nw' else 0,2,13 if edge=='corner_ne' else 15,2),fill=11)
 if edge in ['bottom','corner_sw','corner_se']:d.line((2 if edge=='corner_sw' else 0,13,13 if edge=='corner_se' else 15,13),fill=11)
 if edge in ['left','corner_nw','corner_sw']:d.line((2,2 if edge=='corner_nw' else 0,2,13 if edge=='corner_sw' else 15),fill=11)
 if edge in ['right','corner_ne','corner_se']:d.line((13,2 if edge=='corner_ne' else 0,13,13 if edge=='corner_se' else 15),fill=11)
 # No repeated bright dots through middle; the old rug resembled hazard tape.
 if edge=='middle':d.line((3,11,7,11),fill=9)
 put('mat_'+edge,im,'walkable worn mat; use only for the small recovery nook','0x201')
for name,im in A.items():im.save(OUT/(name+'.png'),transparency=0,bits=4)
(OUT/'palette.pal').write_text('JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,c)) for c in P)+'\n')
(R/'native/optional_bg_palettes').mkdir(exist_ok=True)
for name,palette in [('06-neutral',NEUTRAL),('07-warm',WARM),('08-cold',COLD),('09-gate',DANGER)]:
 (R/'native/optional_bg_palettes'/f'{name}.pal').write_text('JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,c)) for c in palette)+'\n')
preview=Image.new('RGB',(8*112,math.ceil(len(A)/8)*104),(24,29,33));d=ImageDraw.Draw(preview)
for i,(name,im) in enumerate(A.items()):
 q=im.convert('RGBA').resize((64,64),Image.Resampling.NEAREST);x=i%8*112;y=i//8*104
 preview.paste(q,(x+24,y+2),q)
 lines=name.replace('corner_','crn_').replace('horizontal','horiz').replace('vertical','vert').split('_')
 d.text((x+3,y+70),'_'.join(lines[:2]),fill=(212,218,200));d.text((x+3,y+83),'_'.join(lines[2:]),fill=(212,218,200))
preview.save(R/'previews/architecture-enlarged.png')
# Native composition diagram, NOT an emulator screenshot or a collision map.
room=Image.new('P',(256,192),1);room.putpalette(A['void'].getpalette())
def stamp(name,x,y):room.paste(A[name],(x*16,y*16))
for y in range(12):
 for x in range(16):stamp('void',x,y)
for y in range(3,10):
 for x in range(2,14):stamp('floor_plain',x,y)
for n,x,y in [('floor_slab_01',3,4),('floor_slab_11',4,4),('floor_slab_01',8,5),('floor_slab_10',10,6),('floor_slab_01',12,8)]:stamp(n,x,y)
for x in range(2,14):stamp('wall_top_join' if x%3==0 else 'wall_top_plain',x,1);stamp('wall_face_b' if x%2 else 'wall_face_a',x,2);stamp('wall_bottom_plain',x,10)
for y in range(2,10):stamp('wall_side_left',1,y);stamp('wall_side_right',14,y)
for name,x,y in [('corner_outer_nw',1,1),('corner_outer_ne',14,1),('corner_outer_sw',1,10),('corner_outer_se',14,10),('wall_lamp_lit',4,2),('wall_face_damp',11,2),('floor_crack',3,8),('floor_scuff',8,7),('floor_drain',10,8),('wall_top_chip',12,1),('floor_warm_pool',4,3)]:stamp(name,x,y)
for y in range(7,9):
 for x in range(3,6):
  e=('top' if y==7 else 'bottom')
  if x==3:e='corner_nw' if y==7 else 'corner_sw'
  elif x==5:e='corner_ne' if y==7 else 'corner_se'
  stamp('mat_'+e,x,y)
def bgprop(name,x,y):
 p=Image.open(R/'native/background_env6'/f'{name}.png');mask=Image.frombytes('L',p.size,bytes(0 if i==0 else 255 for i in p.getdata()));room.paste(p,(x*16,y*16),mask)
bgprop('workbench',8,8);bgprop('stairs_up',11,3);bgprop('wall_lantern',7,1);bgprop('bedroll',3,7);bgprop('rubble',12,8)
room.info['transparency']=0;room.save(R/'previews/architecture-room-native-diagram.png',transparency=0,bits=4)
room.convert('RGB').resize((1024,768),Image.Resampling.NEAREST).save(R/'previews/architecture-room-enlarged-diagram.png')
neutral=room.copy();neutral.putpalette(sum((list(c) for c in NEUTRAL),[])+[0]*(768-48));neutral.convert('RGB').resize((1024,768),Image.Resampling.NEAREST).save(R/'previews/architecture-room-neutral-enlarged-diagram.png')
(R/'architecture-manifest.json').write_text(json.dumps({'status':'UNINTEGRATED_NATIVE_CANDIDATES','authorship':'Original deterministic pixel geometry authored for this task; no third-party source; follows existing slice_art.py native asset method.','palette':'Existing environment palette bank6; optional BG-only palette variants separate.','count':len(A),'tiles':meta},indent=2)+'\n')
print('Authored',len(A),'native 16x16 architecture candidates. Diagram is not emulator evidence.')
