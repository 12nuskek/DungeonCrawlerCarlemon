from pathlib import Path
import json,collections
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1];base=json.loads((root/'scripts/contracts/n01-baseline.json').read_text());spec=json.loads((root/'scripts/contracts/n02-geometry.json').read_text());report=[]
preserved=json.loads((root/'scripts/contracts/n02-preserved-paths.json').read_text())['rooms']
for name,m in base['maps'].items():
 cells=[dict(c) for c in m['cells']];js=json.loads((root/'engine/data/maps'/name/'map.json').read_text());objects={(o['x'],o['y']) for o in js['object_events']};warps={(w['x'],w['y']) for w in js['warp_events']}
 for c in spec['rooms'][name]['changes']:
  assert (c['x'],c['y']) not in objects|warps
  cells[c['y']*16+c['x']]['upper_bits']=c['after_upper']
 for x,y in preserved[name]:assert cells[y*16+x]['upper_bits']==0x3000,(name,x,y,'previously tested route blocked')
 walk={(i%16,i//16) for i,c in enumerate(cells) if c['upper_bits']==0x3000}-objects
 origin=(4,8) if name=='DCC_Entrance' else next(iter(warps))
 hazard={(8,6)} if name=='DCC_Service' else set();seen={origin};q=collections.deque([origin])
 while q:
  x,y=q.popleft()
  if (x,y) in warps and (x,y)!=origin:continue
  for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
   p=(x+dx,y+dy)
   if p in walk-hazard-seen:seen.add(p);q.append(p)
 assert warps<=seen,(name,'warp connectivity')
 for x,y in objects:assert any((x+dx,y+dy) in seen for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]),(name,x,y,'object approach')
 for c in spec['rooms'][name]['changes']:
  x,y=c['x'],c['y']
  if c['kind']=='open':assert (x,y) in seen,(name,x,y,'new alcove disconnected')
  else:
   assert any((x+dx,y+dy) in walk and m['cells'][(y+dy)*16+x+dx]['upper_bits']==0x3000 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<16 and 0<=y+dy<12),(name,x,y,'old-save escape')
 if name=='DCC_Service':assert {(7,6),(9,6),(12,3),(6,9),(13,9)}<=seen
 if name=='DCC_Boss':assert (12,5) in seen
 report.append({'map':name,'reachable_without_trap':len(seen),'all_object_approaches':True,'all_warps':True,'old_save_escape':True,'preserved_route_cells':len(preserved[name])})
print(json.dumps(report,indent=2))
