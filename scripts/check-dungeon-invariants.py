#!/usr/bin/env python3
"""Check the visual-only dungeon contract against recorded pre-change state."""
from pathlib import Path
from PIL import Image
import hashlib,json,struct,sys
root=Path(sys.argv[1]); baseline=json.loads(Path(sys.argv[2]).read_text()); engine=root/'engine'
geometry=json.loads((root/'scripts/contracts/n02-geometry.json').read_text())
changed_cells=0
for name,spec in geometry['rooms'].items():
 for change in spec['changes']:
  cell=baseline['maps'][name]['cells'][change['y']*16+change['x']]
  assert (cell['upper_bits'],cell['attribute'])==(change['before_upper'],change['before_attribute'])
  cell['upper_bits']=change['after_upper'];cell['attribute']=change['after_attribute'];changed_cells+=1
base=engine/'data/tilesets/secondary/dcc';im=Image.open(base/'tiles.png')
assert im.mode=='P' and im.getextrema()[1]<16 and im.width%8==im.height%8==0
assert (base/'tiles.png').read_bytes()[24]==4, 'atlas must be 4bpp'
num_tiles=im.width*im.height//64
assert num_tiles<=512 and not im.crop((0,0,8,8)).getbbox()
attrs=(base/'metatile_attributes.bin').read_bytes(); metatiles=(base/'metatiles.bin').read_bytes()
assert len(metatiles)%16==0 and len(metatiles)//16<=512
assert len(attrs)%2==0 and len(attrs)//2==len(metatiles)//16
layouts={x['name'].removesuffix('_Layout'):x for x in json.loads((engine/'data/layouts/layouts.json').read_text())['layouts']}
used=set(); cells=0
for name,old in baseline['maps'].items():
 layout=layouts[name];assert (layout['width'],layout['height'])==(old['width'],old['height'])
 current=json.loads((engine/'data/maps'/name/'map.json').read_text())
 # Only the visual identifier of an existing object may change in this increment.
 for obj in current['object_events']:obj.pop('graphics_id',None)
 assert current==old['event_contract'], (name,'event/warp/script contract changed')
 for filename,entries in [('map.bin',old['cells']),('border.bin',old['border_cells'])]:
  words=list(struct.iter_unpack('<H',(engine/'data/layouts'/name/filename).read_bytes()))
  assert len(words)==len(entries),(name,filename,'dimensions')
  for i,((word,),entry) in enumerate(zip(words,entries)):
   mid=word&1023;off=mid-512
   assert 0<=off<len(attrs)//2,(name,i,'invalid secondary metatile')
   assert word&~1023==entry['upper_bits'],(name,filename,i,'collision/elevation changed')
   assert struct.unpack_from('<H',attrs,off*2)[0]==entry['attribute'],(name,filename,i,'behavior/layer changed')
   used.add(mid);cells+=1
# Runtime-selectable pairs preserve exactly the same upper bits and behavior.
states=json.loads((root/'scripts/contracts/n03-presentation.json').read_text())
for state in states:
 for entry in state['entries']:
  assert entry['off']&~1023==entry['on']&~1023,(state['label'],'state changes collision')
  for key in ['off','on']:
   mid=entry[key]&1023;used.add(mid)
   assert struct.unpack_from('<H',attrs,(mid-512)*2)[0]==entry['attribute'],(state['label'],'state changes behavior')
for mid in used:
 for (tile,) in struct.iter_unpack('<H',metatiles[(mid-512)*16:(mid-511)*16]):
  assert 512<=tile&1023<512+num_tiles,(mid,'tile outside atlas')
  assert 6<=tile>>12<=12,(mid,'secondary palette outside banks6–12')
for name,digest in baseline['unchanged_obj_art'].items():
 p=engine/name;data=p.read_text().encode() if p.suffix=='.pal' else p.read_bytes()
 assert hashlib.sha256(data).hexdigest()==digest,(name,'approved art changed')
print(json.dumps({'checked_cells_and_border':cells,'metatiles':len(used),'secondary_tiles':num_tiles,'approved_art_files':len(baseline['unchanged_obj_art']),'event_contracts':len(baseline['maps']),'explicit_geometry_cells':changed_cells},indent=2))
