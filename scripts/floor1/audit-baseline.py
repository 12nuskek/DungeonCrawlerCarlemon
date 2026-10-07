#!/usr/bin/env python3
"""Read the immutable delivered source; never edit game data or saves."""
from pathlib import Path
import subprocess,json,struct,hashlib,re
root=Path(__file__).resolve().parents[2];base='3f1c851cce076b51cf4eb174925d9a2e41777a1f'
def read(p):return subprocess.check_output(['git','show',base+':'+p],cwd=root)
def data(p):return json.loads(read(p))
groups=data('engine/data/maps/map_groups.json');layouts={x['id']:x for x in data('engine/data/layouts/layouts.json')['layouts']}
maps=[]
for gi,g in enumerate(groups['group_order']):
 for ni,name in enumerate(groups[g]):
  if not name.startswith('DCC_'):continue
  path='engine/data/maps/'+name+'/map.json';m=data(path);l=layouts[m['layout']];raw=read('engine/'+l['blockdata_filepath']);cells=list(struct.unpack('<'+'H'*(len(raw)//2),raw));w,h=l['width'],l['height']
  assert len(cells)==w*h
  maps.append({'name':name,'group':gi,'number':ni,'map_header':m,'layout':l,'layout_id_one_based':list(layouts).index(m['layout'])+1,'map_words':cells,'map_sha256':hashlib.sha256(raw).hexdigest(),'object_local_ids':[{'local_id':i+1,**o} for i,o in enumerate(m['object_events'])],'padded_cells':(w+15)*(h+14),'legal_static_floor_candidates':[[i%w,i//w] for i,v in enumerate(cells) if (v&0xC00)==0],'new_destination':'PENDING reviewed D1 geometry; no migration implemented'})
flags=read('engine/include/constants/flags.h').decode();defs=[]
for n,v in re.findall(r'^#define\s+(\w+)\s+(0x[0-9A-Fa-f]+|\d+)\b',flags,re.M):
 if 0x20<=int(v,0)<=0x30:defs.append({'name':n,'value':int(v,0)})
report={'source_commit':base,'gameplay_tested':'eaf073d434a9347dfc2ed921f5f44d163563964b','maps':maps,'flag_numeric_aliases':defs,'engine_limits':{'map_buffer_u16_cells':10240,'map_buffer_bytes':20480,'padding_w':15,'padding_h':14,'active_objects_including_player':16,'saved_object_templates':64,'primary_tiles':512,'secondary_tiles':512,'bg_palette_banks':13},'envelope_buffer_checks':[{'width':w,'height':h,'padded_cells':(w+15)*(h+14),'remaining_cells':10240-(w+15)*(h+14)} for w,h in [(64,48),(72,48),(64,56),(56,48),(72,56)]],'entry_points':{'new_game':'engine/src/new_game.c:130; Entrance group34 number0 (4,8)','script_warp':'engine/data/maps/DCC_Boss/scripts.inc:50; Exit (4,6)','continue':'SaveBlock1 location/pos/mapLayoutId, mapView, objectEvents/templates; current refresh does not relocate','battle_return':'battle_setup.c CB2_EndTrainerBattle; local position, current narrow trainer range','menu_return':'current player position; no dedicated DCC relocation','debug_test_spawns':'existing ordinary routes and explicitly labeled capacity fixture initialisers; enumerate/remap through reviewed anchors before geometry changes'},'classification_hazards':['Use full (group,number) identity, not mapNum alone, in DccPresentationTile and resolved-object lookup.','Replace group-only palette/map cache/template guards with explicit supported crawler maps; test stock nonmembers.','Replace closed numeric trainer range with explicit crawler encounters before adding new encounters; test local recovery and stock nonmembers.'],'migration_required':['Map location, mapLayoutId, player position/facing','Saved and live object/template IDs and positions','Warp destinations and return anchors','Every legacy map/state; no reward/party/inventory changes','Explicit unused save discriminator after numeric alias audit','Idempotent second save and cold reload; no full-floor completion from old slice flag']}
print(json.dumps(report,indent=2))
