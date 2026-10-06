"""Original S02 indexed pixel art. Run with Python3 + Pillow.

All geometry is authored here; no upstream images are traced or recoloured.
Internal species slots remain engine implementation details. Palette0 transparent.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import struct
R = Path(__file__).resolve().parents[2] / 'engine'
P = [(0,0,0),(25,29,39),(62,46,43),(115,72,51),(189,120,82),(244,183,132),
     (255,220,172),(241,232,202),(177,163,142),(191,53,67),(111,34,53),
     (231,182,65),(69,151,145),(35,80,91),(110,118,136),(190,204,211)]
def canvas(w,h):
 im=Image.new('P',(w,h),0); im.putpalette(sum((list(c) for c in P),[])+[0]*(768-48)); return im

def save(im,path):
 path=R/path;path.parent.mkdir(parents=True,exist_ok=True);im.save(path,transparency=0,bits=4)
def pal(path,colors=P):
 path=R/path;path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text('JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str,c)) for c in colors)+'\n')
def carl(back=False):
 im=canvas(64,64);d=ImageDraw.Draw(im)
 # Bare-footed, shorts and squared stance; asymmetric raised fighting arm.
 d.polygon([(20,33),(14,35),(10,48),(12,51),(18,49),(22,42),(23,50),(20,57),(28,59),(33,54),(37,59),(46,58),(43,50),(45,37),(40,31)],fill=1)
 d.polygon([(21,34),(15,37),(12,47),(15,49),(21,40),(24,48),(40,48),(43,36),(38,32)],fill=5)
 d.polygon([(24,34),(26,44),(38,45),(40,35),(34,31)],fill=6)
 d.line([(23,36),(24,43),(29,44)],fill=4,width=2);d.line([(38,36),(37,44)],fill=4)
 d.rectangle((23,47,41,53),fill=7);d.rectangle((30,51,34,55),fill=1)
 for x,y in [(25,48),(35,49),(39,51)]: d.polygon([(x,y),(x+1,y+1),(x+2,y),(x+2,y+2),(x+1,y+3),(x,y+2)],fill=9)
 d.rectangle((22,54,28,59),fill=5);d.rectangle((36,54,43,59),fill=5)
 d.rectangle((20,59,29,61),fill=4);d.rectangle((36,59,46,61),fill=4)
 d.polygon([(40,35),(45,34),(48,24),(53,24),(53,37),(47,44),(42,43)],fill=1)
 d.polygon([(42,36),(47,36),(49,26),(52,26),(51,36),(46,41),(43,41)],fill=5)
 d.rectangle((48,21,54,27),fill=1);d.rectangle((49,22,53,26),fill=6)
 d.ellipse((22,11,42,34),fill=1);d.ellipse((24,13,40,32),fill=5)
 d.polygon([(23,20),(23,12),(28,8),(37,9),(42,13),(41,22),(38,17),(28,16)],fill=2)
 d.line([(26,13),(32,11),(37,13)],fill=3,width=2)
 if back: d.polygon([(24,18),(39,17),(39,26),(35,30),(28,28),(24,24)],fill=2);d.line((27,20,37,21),fill=3,width=2)
 else:
  d.line((26,21,29,21),fill=1);d.line((34,21,37,21),fill=1)
  d.rectangle((30,23,32,25),fill=4);d.line((28,29,36,29),fill=2)
 return im

def donut(back=False):
 im=canvas(64,64);d=ImageDraw.Draw(im)
 d.arc((36,33,61,60),270,110,fill=1,width=8);d.arc((36,33,61,60),270,110,fill=8,width=5)
 d.polygon([(18,30),(13,35),(16,38),(11,43),(16,46),(13,50),(20,56),(18,59),(29,60),(33,57),(39,60),(48,58),(44,53),(48,47),(45,41),(48,36),(42,31)],fill=1)
 d.ellipse((16,29,46,57),fill=8);d.ellipse((21,31,41,56),fill=7)
 d.ellipse((17,54,29,60),fill=7);d.ellipse((34,54,46,60),fill=7)
 d.polygon([(16,23),(16,11),(26,17),(37,16),(47,10),(47,25),(51,29),(46,34),(40,39),(23,38),(14,30)],fill=1)
 d.polygon([(18,24),(18,15),(27,20),(37,19),(45,14),(45,25),(48,29),(42,34),(24,35),(17,29)],fill=8)
 d.polygon([(20,18),(20,23),(25,21)],fill=4);d.polygon([(42,18),(39,22),(43,23)],fill=4)
 if not back:
  d.ellipse((21,23,29,29),fill=7);d.ellipse((35,23,43,29),fill=7)
  d.rectangle((25,24,27,28),fill=12);d.rectangle((37,24,39,28),fill=12)
  d.point((26,25),1);d.point((38,25),1)
  d.polygon([(29,30),(34,30),(32,33)],fill=10)
  d.line((23,32,17,31),fill=7);d.line((40,32,47,31),fill=7)
 else: d.line((24,24,40,25),fill=3,width=2);d.line((27,28,38,29),fill=3)
 # Small gold collar, no later-book costume or class assumed.
 d.line((24,37,40,37),fill=11,width=2);d.rectangle((31,38,33,40),fill=12)
 return im

def enemy(kind):
 im=canvas(64,64);d=ImageDraw.Draw(im)
 if kind=='scuttler':
  for x in (17,26,36,45):d.line([(x,38),(x-8,46),(x-9,54)],fill=1,width=3)
  d.ellipse((15,27,51,49),fill=1);d.ellipse((17,29,49,46),fill=3)
  for x in (23,31,39):d.line((x,30,x-2,45),fill=4,width=2)
  d.polygon([(42,30),(54,34),(52,44),(43,45)],fill=5)
  d.rectangle((49,34,51,36),fill=9);d.line((52,39,59,42),fill=7,width=2)
 elif kind=='grub':
  for x,y in [(13,43),(22,40),(31,38),(40,36)]:
   d.ellipse((x,y,x+16,y+17),fill=1);d.ellipse((x+2,y+2,x+14,y+14),fill=12)
  d.ellipse((39,27,56,46),fill=1);d.ellipse((41,29,54,43),fill=13)
  d.rectangle((45,32,48,34),fill=11);d.line((46,39,53,39),fill=7)
 elif kind=='guard':
  for x in (12,45):d.polygon([(x,35),(x-5,52),(x+3,58),(x+7,42)],fill=1)
  d.ellipse((16,15,50,56),fill=1);d.ellipse((19,18,47,53),fill=14)
  d.polygon([(20,27),(32,18),(45,28),(42,43),(32,51),(22,43)],fill=13)
  d.polygon([(24,29),(32,23),(41,29),(38,41),(32,46),(26,40)],fill=12)
  d.rectangle((25,33,39,35),fill=11);d.rectangle((22,12,43,22),fill=1)
  d.rectangle((25,15,40,19),fill=14);d.rectangle((27,17,37,18),fill=9)
 elif kind=='howler':
  d.polygon([(22,31),(8,24),(3,44),(18,40),(25,47),(22,58),(31,55),(42,58),(40,43),(58,42),(55,23),(42,29)],fill=1)
  d.polygon([(20,32),(10,29),(7,40),(20,37),(26,42),(30,53),(37,53),(39,35),(52,28),(54,38),(41,37)],fill=10)
  d.ellipse((21,13,45,43),fill=1);d.ellipse((23,15,43,41),fill=9)
  d.ellipse((26,24,40,39),fill=1);d.ellipse((29,27,37,36),fill=10)
  d.rectangle((26,19,29,21),fill=11);d.rectangle((37,19,40,21),fill=11)
 else:
  d.polygon([(18,23),(10,27),(5,48),(13,52),(20,42),(22,53),(18,61),(30,61),(33,52),(36,61),(50,61),(45,51),(47,40),(54,48),(61,43),(54,23),(44,19)],fill=1)
  d.polygon([(19,25),(13,29),(8,44),(13,47),(21,35),(23,49),(43,49),(44,29),(40,23)],fill=14)
  d.polygon([(45,24),(52,27),(57,41),(54,43),(45,34)],fill=8)
  d.rectangle((23,52,29,59),fill=13);d.rectangle((37,52,45,59),fill=13)
  d.polygon([(23,27),(41,27),(39,44),(26,44)],fill=13)
  d.rectangle((27,30,37,38),fill=1);d.rectangle((29,32,35,36),fill=9)
  d.rectangle((24,10,43,24),fill=1);d.rectangle((27,12,40,21),fill=14)
  d.rectangle((28,16,39,18),fill=11);d.rectangle((24,7,29,11),fill=13)
  for x,y in [(17,30),(43,27),(27,41),(39,41)]:d.rectangle((x,y,x+2,y+2),fill=7)
 return im

names={'machop':('carl',carl()),'meowth':('donut',donut()),'zigzagoon':('scuttler',enemy('scuttler')),'wurmple':('grub',enemy('grub')),'spinda':('guard',enemy('guard')),'whismur':('howler',enemy('howler')),'loudred':('warden',enemy('warden'))}
for species,(name,front) in names.items():
 path=Path('graphics/dcc')/name
 back=carl(True) if name=='carl' else donut(True) if name=='donut' else front
 save(front,path/'front.png');save(back,path/'back.png')
 anim=canvas(64,128);anim.paste(front,(0,0));anim.paste(front,(0,64));save(anim,path/'anim_front.png')
 icon=canvas(32,64);small=front.resize((32,32),Image.Resampling.NEAREST);icon.paste(small,(0,0));icon.paste(small,(0,32));save(icon,path/'icon.png')
 pal(path/'normal.pal');pal(path/'shiny.pal')
# Player battle-intro four-frame pose strip, original pixels, same engine contract.
trainer=canvas(64,256)
for y in range(0,256,64):trainer.paste(carl(True),(0,y))
save(trainer,Path('graphics/dcc/carl/trainer_back.png'))
pal(Path('graphics/dcc/shared.pal'))

# Independent dungeon secondary tileset. Preserve each used cave behavior exactly.
colors=[(0,0,0),(18,26,36),(30,43,53),(47,61,68),(65,79,82),(92,107,106),(129,145,135),(179,190,166),(39,75,78),(54,114,113),(82,164,148),(199,168,100),(143,94,65),(204,87,66),(223,211,174),(244,236,205)]
tiles=[]
def tile(kind):
 im=canvas(16,16);d=ImageDraw.Draw(im);d.rectangle((0,0,15,15),fill=2)
 if kind in ('floor','crack','rug','stripe','debris'):
  d.rectangle((1,1,14,14),fill=3);d.line((1,1,14,1),fill=4);d.line((1,1,1,14),fill=4);d.point((12,12),4)
  if kind=='crack':d.line([(1,3),(6,6),(5,10),(11,14)],fill=13,width=2);d.line((1,15,15,1),fill=11)
  if kind=='rug':d.rectangle((0,0,15,15),fill=8);d.line((0,3,15,3),fill=9);d.line((0,12,15,12),fill=9);d.rectangle((6,6,9,9),fill=11)
  if kind=='stripe':d.rectangle((6,0,9,15),fill=11);d.line((6,0,6,15),fill=12)
  if kind=='debris':d.line((3,5,8,6),fill=7,width=2);d.line((8,11,12,9),fill=12,width=2)
 elif kind=='stairs':
  d.rectangle((1,0,14,15),fill=1)
  for y in (2,6,10,14):d.rectangle((3,y,12,y+1),fill=6);d.line((3,y+2,12,y+2),fill=3)
  d.line((1,0,1,15),fill=11);d.line((14,0,14,15),fill=11)
 else:
  d.rectangle((0,0,15,15),fill=2)
  for y in (0,8):
   d.line((0,y,15,y),fill=5);d.line((0,y+1,15,y+1),fill=3);d.line(((4 if y else 11),y,(4 if y else 11),y+7),fill=1)
  if kind=='wallbase':d.rectangle((0,10,15,12),fill=1);d.line((0,13,15,13),fill=6);d.line((0,15,15,15),fill=1)
  if kind=='lamp':d.rectangle((5,3,10,11),fill=1);d.rectangle((6,4,9,9),fill=10);d.line((5,12,10,12),fill=11)
 return im
kinds=['floor','stairs','wall','wallbase','crack','rug','stripe','debris','lamp']
# Blank tile index0 ensures transparent overlay; each metatile contributes four tiles.
atlas=canvas(128,24);metatiles=bytearray((0x1A0)*16)
attrs=bytearray((0x1A0)*2)
old=(R/'data/tilesets/secondary/cave/metatile_attributes.bin').read_bytes()
attrs[:len(old)]=old
ids={0x201:0,0x205:1,0x210:3,0x211:2,0x212:3,0x219:3,0x39e:4,0x220:5,0x221:6,0x222:7,0x223:8}
for k,kind in enumerate(kinds):
 t=tile(kind)
 for q in range(4):
  n=1+k*4+q;atlas.paste(t.crop(((q%2)*8,(q//2)*8,(q%2+1)*8,(q//2+1)*8)),((n%16)*8,(n//16)*8))
for mid,k in ids.items():
 entries=[(512+1+k*4+q)|(6<<12) for q in range(4)]+[512|(6<<12)]*4
 struct.pack_into('<8H',metatiles,(mid-512)*16,*entries)
 if mid in (0x220,0x221,0x222):attrs[(mid-512)*2:(mid-512+1)*2]=old[2:4]
 if mid==0x223:attrs[(mid-512)*2:(mid-512+1)*2]=old[(0x19)*2:(0x1A)*2]
base=Path('data/tilesets/secondary/dcc');save(atlas,base/'tiles.png')
(R/base/'metatiles.bin').write_bytes(metatiles);(R/base/'metatile_attributes.bin').write_bytes(attrs)
for i in range(16):pal(base/'palettes'/f'{i:02}.pal',colors)
print('Generated original seven crawler/enemy sprite sets and dungeon tiles.')
# Original inventory silhouettes, same24x24 engine icon bounds.
for name in ['wrap','scrap','tag','charge','medicine']:
 im=canvas(24,24);d=ImageDraw.Draw(im)
 if name=='wrap':
  d.polygon([(3,8),(15,3),(21,8),(10,14),(11,21),(5,20)],fill=1)
  d.polygon([(5,8),(15,5),(18,8),(8,13),(9,19),(6,18)],fill=7)
  d.line((6,9,14,7),fill=8);d.line((7,15,9,15),fill=8)
 elif name=='scrap':
  d.polygon([(3,7),(13,3),(17,9),(10,14),(6,13)],fill=1);d.polygon([(5,8),(12,5),(15,9),(9,12)],fill=14)
  d.polygon([(11,15),(18,9),(22,15),(18,21),(8,20)],fill=1);d.line((11,18,19,14),fill=8,width=3)
 elif name=='tag':
  d.rectangle((6,3,18,21),fill=1);d.rectangle((7,4,17,20),fill=11);d.rectangle((10,5,14,7),fill=1)
  d.line((9,11,15,11),fill=3);d.line((9,14,15,14),fill=3);d.rectangle((10,17,13,18),fill=9)
 elif name=='charge':
  d.rectangle((4,7,19,20),fill=1);d.rectangle((6,8,17,18),fill=9);d.rectangle((9,7,12,20),fill=8)
  d.line([(12,7),(12,3),(18,3),(20,5)],fill=11,width=2);d.point((21,5),7)
 else:
  d.rectangle((9,2,15,6),fill=1);d.rectangle((7,6,17,21),fill=1);d.rectangle((8,7,16,20),fill=12)
  d.rectangle((8,11,16,17),fill=7);d.rectangle((11,12,13,16),fill=9);d.rectangle((9,13,15,15),fill=9)
 save(im,Path('graphics/dcc/items')/(name+'.png'))
# Crate replaces a visual prop, retaining its original event footprint.
im=canvas(16,16);d=ImageDraw.Draw(im);d.rectangle((0,3,15,15),fill=1);d.rectangle((1,4,14,14),fill=3)
d.rectangle((1,2,14,5),fill=8);d.line((2,7,13,7),fill=4);d.rectangle((6,5,9,15),fill=14);d.rectangle((7,8,8,10),fill=11)
save(im,Path('graphics/dcc/crate.png'))
# Donut's standing exploration frames share Carl's already loaded palette.
cp=[tuple(map(int,l.split())) for l in (R/'graphics/object_events/palettes/carl.pal').read_text().splitlines()[3:]]
mini=donut().resize((16,16),Image.Resampling.NEAREST)
lookup=[0]+[min(range(1,16),key=lambda j:sum((P[i][k]-cp[j][k])**2 for k in range(3))) for i in range(1,16)]
mini=mini.point(lookup+[0]*240);mini.putpalette(sum((list(c) for c in cp),[])+[0]*(768-48))
world=Image.new('P',(48,16));world.putpalette(mini.getpalette())
for x in (0,16,32):world.paste(mini,(x,0))
save(world,Path('graphics/dcc/donut/overworld.png'))
# Visible encounter tokens and original stationary crawler NPCs.
for name in ['scuttler','guard','howler','warden']:
 front=next(im for _,(n,im) in names.items() if n==name)
 save(front.resize((32,32),Image.Resampling.NEAREST),Path('graphics/dcc')/name/'overworld.png')
for name,skin,shirt,hair in [('guide',5,13,14),('mara',4,9,1),('lev',5,12,2)]:
 im=canvas(16,32);d=ImageDraw.Draw(im)
 d.rectangle((4,21,11,29),fill=1);d.rectangle((5,22,7,27),fill=13);d.rectangle((9,22,11,27),fill=13)
 d.rectangle((3,28,7,30),fill=2);d.rectangle((9,28,13,30),fill=2)
 d.rectangle((2,13,13,23),fill=1);d.rectangle((3,14,12,22),fill=shirt);d.rectangle((2,17,3,23),fill=skin);d.rectangle((12,17,13,23),fill=skin)
 d.rectangle((4,12,11,16),fill=skin);d.rectangle((4,4,11,12),fill=1);d.rectangle((5,5,10,12),fill=skin)
 d.rectangle((4,3,11,6),fill=hair);d.point((5,8),1);d.point((10,8),1);d.line((7,11,9,11),fill=2)
 if name=='guide':d.rectangle((5,10,10,13),fill=14);d.rectangle((8,16,9,21),fill=11)
 if name=='mara':d.rectangle((3,6,4,13),fill=hair);d.line((5,18,10,18),fill=11)
 if name=='lev':d.rectangle((3,2,12,4),fill=11);d.rectangle((5,1,10,3),fill=11);d.rectangle((7,16,9,23),fill=13)
 save(im,Path('graphics/dcc')/name/'overworld.png')
# Authored5x7 lettering; title uses the existing timing/input flow.
FONT={
'A':['01110','10001','10001','11111','10001','10001','10001'],
'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],
'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],
'G':['01111','10000','10000','10111','10001','10001','01111'],
'I':['11111','00100','00100','00100','00100','00100','11111'],
'K':['10001','10010','10100','11000','10100','10010','10001'],
'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],
'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],
'P':['11110','10001','10001','11110','10000','10000','10000'],
'R':['11110','10001','10001','11110','10100','10010','10001'],
'U':['10001','10001','10001','10001','10001','10001','01110'],
'W':['10001','10001','10001','10101','10101','11011','10001'],
'1':['00100','01100','00100','00100','00100','00100','01110']}
def letters(im,text,y,size,color,shift=0):
 d=ImageDraw.Draw(im);x=(im.width-(len(text)*6-1)*size)//2+shift
 for ch in text:
  for yy,row in enumerate(FONT.get(ch,['00000']*7)):
   for xx,b in enumerate(row):
    if b=='1':d.rectangle((x+xx*size,y+yy*size,x+(xx+1)*size-1,y+(yy+1)*size-1),fill=color)
  x+=6*size
logo=canvas(256,64);letters(logo,'DUNGEON CRAWLER',7,2,7,-37);letters(logo,'CARLEMON',29,3,11,-37)
save(logo,Path('graphics/dcc/title/logo.png'))
# Affine background uses byte tile IDs and the same256-tile budget as upstream.
(R/'graphics/dcc/title/logo.bin').write_bytes(bytes(range(256))+bytes(768))
version=canvas(128,32);letters(version,'BOOK 1 OPENING',10,1,7);save(version,Path('graphics/dcc/title/version.png'))
portal=canvas(128,128);d=ImageDraw.Draw(portal)
d.rectangle((0,0,127,127),fill=1)
d.rounded_rectangle((34,10,94,116),radius=25,fill=14);d.rounded_rectangle((39,15,89,119),radius=23,fill=2)
d.rectangle((39,45,89,119),fill=2)
for y in range(75,121,9):d.rectangle((40,y,88,y+2),fill=8)
d.rectangle((21,46,26,65),fill=11);d.rectangle((102,46,107,65),fill=11)
save(portal,Path('graphics/dcc/title/portal.png'))
# Standard text tilemap, centered architectural background; unused tiles blank0.
bg=bytearray(2048)
for y in range(16):
 for x in range(16):struct.pack_into('<H',bg,((y+8)*32+x+7)*2,y*16+x)
(R/'graphics/dcc/title/portal.bin').write_bytes(bg)
save(canvas(128,56),Path('graphics/dcc/title/mist.png'));save(canvas(64,64),Path('graphics/dcc/title/shine.png'))
# Palette16 repeated to fill the title loader's fixed240-color read safely.
p=R/'graphics/dcc/title/background.pal';p.write_text('JASC-PAL\n0100\n256\n'+'\n'.join(' '.join(map(str,c)) for c in P*16)+'\n')
# Original dungeon battle arena,512 tiles within the existing character block.
arena=canvas(256,128);d=ImageDraw.Draw(arena);d.rectangle((0,0,255,127),fill=3)
for y in range(0,48,12):
 d.line((0,y,255,y),fill=5)
 for x in range((y//12%2)*16,256,32):d.line((x,y,x,y+11),fill=1)
d.rectangle((0,47,255,50),fill=1);d.line((0,51,255,51),fill=8)
for y in range(58,128,14):
 d.line((0,y,255,y),fill=2)
 for x in range((y//14%2)*20,256,40):d.line((x,y,x+10,y+13),fill=2)
for x in (20,218):d.rectangle((x,16,x+7,33),fill=1);d.rectangle((x+2,18,x+5,28),fill=12)
d.ellipse((120,45,231,78),fill=8);d.ellipse((126,48,225,74),fill=3)
d.ellipse((10,83,132,116),fill=8);d.ellipse((16,86,126,112),fill=3)
save(arena,Path('graphics/dcc/battle/arena.png'))
bm=bytearray(4096)
for block in range(2):
 for y in range(32):
  for x in range(32):struct.pack_into('<H',bm,block*2048+(y*32+x)*2,((y%16)*32+x)|(2<<12))
(R/'graphics/dcc/battle/map.bin').write_bytes(bm)
(R/'graphics/dcc/battle/palette.pal').write_text('JASC-PAL\n0100\n48\n'+'\n'.join(' '.join(map(str,c)) for c in colors*3)+'\n')
