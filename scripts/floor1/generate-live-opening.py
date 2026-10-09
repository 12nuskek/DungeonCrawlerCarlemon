#!/usr/bin/env python3
"""Generate production D1 source from the frozen third-layout contract.

Legacy map/layout entries stay intact. Never imports diagnostic ROMs or saves.
"""
from pathlib import Path
import argparse, copy, importlib.util, json, struct

ROOT=Path(__file__).resolve().parents[2]
loader=importlib.util.spec_from_file_location('geometry',Path(__file__).with_name('relocation-graybox.py'))
g=importlib.util.module_from_spec(loader);loader.loader.exec_module(g)
nav_loader=importlib.util.spec_from_file_location('navigation',Path(__file__).with_name('live-navigation.py'))
nav=importlib.util.module_from_spec(nav_loader);nav_loader.loader.exec_module(nav)

def generate(root):
    engine=root/'engine';live_roots=nav.generate(engine);spec=json.loads((root/'scripts/contracts/f1-g01d-relocation.json').read_text())
    g.audit(spec,False);g.audit(spec,True)
    identity=spec['production_identity_proposal']['maps']
    groups_path=engine/'data/maps/map_groups.json';groups=json.loads(groups_path.read_text())
    group='gMapGroup_DccFloor1Opening'
    if group in groups['group_order']:
        assert groups['group_order'][-1]==group
        groups['group_order'].remove(group);del groups[group]
    assert len(groups['group_order'])==35
    groups['group_order'].append(group);groups[group]=[m['name'] for m in identity.values()]
    groups_path.write_text(json.dumps(groups,indent=2)+'\n')
    lp=engine/'data/layouts/layouts.json';layouts=json.loads(lp.read_text())
    names={m['name']+'_Layout' for m in identity.values()}
    layouts['layouts']=[m for m in layouts['layouts'] if m['name'] not in names]
    assert len(layouts['layouts'])==447
    old_layouts={m['name']:m for m in layouts['layouts']}
    models={old:json.loads((engine/'data/maps'/old/'map.json').read_text()) for old in spec['legacy_object_destinations']}
    objects={k:{} for k in identity}
    for old,destinations in spec['legacy_object_destinations'].items():
        assert len(destinations)==len(models[old]['object_events'])
        for obj,(key,role) in zip(models[old]['object_events'],destinations):
            pos=spec['object_roles'][key][role];obj=copy.deepcopy(obj)
            obj['x'],obj['y']=pos['actor_at']
            obj['script']=live_roots.get(obj['script'],obj['script']);objects[key][pos['production_local_id']]=obj
    for key,m in spec['maps'].items():
        for i,(x,y,gfx,description) in enumerate(m['objects'],1):
            if i not in objects[key]:
                obj=copy.deepcopy(models['DCC_Entrance']['object_events'][1]);obj.update(graphics_id=gfx,x=x,y=y,script=f'{identity[key]["name"]}_Marker{i}')
                objects[key][i]=obj
    extra_includes=[];loop_pairs=[]
    for key,m in spec['maps'].items():
        name=identity[key]['name'];w,h=m['width'],m['height'];tile=m['tile_ids']
        def words(opened):
            floor=g.g.terrain(m,opened);result=[]
            for y in range(h):
                for x in range(w):
                    if (x,y) in floor:word=0x3000|tile['floor']
                    elif (x,y+1) in floor:word=0x3c00|tile['north']
                    elif (x,y-1) in floor:word=0x3c00|tile['south']
                    elif (x+1,y) in floor:word=0x3c00|tile['west']
                    elif (x-1,y) in floor:word=0x3c00|tile['east']
                    else:word=0x3c00|tile['void']
                    result.append(word)
            for warp in m['warps']:
                old=old_layouts[warp['source_map']+'_Layout'];raw=(engine/old['blockdata_filepath']).read_bytes();x,y=warp['source_at']
                word=struct.unpack_from('<H',raw,2*(y*old['width']+x))[0];x,y=warp['at'];result[y*w+x]=word
            return result
        closed=words(False);opened=words(True)
        if key=='field':
            for y in range(13,22):loop_pairs.append((35,y,closed[y*w+35],opened[y*w+35]))
        if key=='boss':
            s=m['stairs_transition'];old=old_layouts[s['source_map']+'_Layout'];raw=(engine/old['blockdata_filepath']).read_bytes();x,y=s['source_at']
            word=struct.unpack_from('<H',raw,2*(y*old['width']+x))[0];x,y=s['at'];closed[y*w+x]=word
        d=engine/'data/layouts'/name;d.mkdir(exist_ok=True)
        (d/'map.bin').write_bytes(struct.pack('<'+'H'*len(closed),*closed));(d/'border.bin').write_bytes(struct.pack('<4H',*([0x3c00|tile['void']]*4)))
        layouts['layouts'].append(dict(id='LAYOUT_'+name.upper(),name=name+'_Layout',width=w,height=h,primary_tileset='gTileset_General',secondary_tileset='gTileset_Dcc',border_filepath=f'data/layouts/{name}/border.bin',blockdata_filepath=f'data/layouts/{name}/map.bin'))
        assert len(layouts['layouts'])==identity[key]['layout_id']
        old={'field':'DCC_Entrance','quiet':'DCC_Vestibule','workshop':'DCC_Service','boss':'DCC_Boss','checkpoint':'DCC_Exit'}[key]
        model=copy.deepcopy(models[old]);model.update(id='MAP_'+name.upper(),name=name,layout='LAYOUT_'+name.upper(),object_events=[v for i,v in sorted(objects[key].items())],warp_events=[],coord_events=[],bg_events=[])
        assert sorted(objects[key])==list(range(1,len(m['objects'])+1))
        for warp in m['warps']:
            dest=next(k for k,v in spec['maps'].items() if v['map_num']==warp['dest']);x,y=warp['at']
            model['warp_events'].append(dict(x=x,y=y,elevation=3,dest_map='MAP_'+identity[dest]['name'].upper(),dest_warp_id=str(warp['dest_warp'])))
        scripts=f'{name}_MapScripts::\n\tmap_script MAP_SCRIPT_ON_LOAD, {name}_Load\n'
        if key=='field':scripts+='\tmap_script MAP_SCRIPT_ON_FRAME_TABLE, DCC_Entrance_FrameTable\n'
        scripts+=f'\t.byte 0\n{name}_Load:\n\tspecial DccRestoreMapPresentation\n'
        if key=='field':
            scripts+='\tsetvar VAR_TEMP_0, 0\n\tgoto_if_unset FLAG_DCC_TRAP_SPENT, '+name+'_LoadDone\n\tsetvar VAR_TEMP_0, 1\n'+name+'_LoadDone:\n'
            # The entrance frame table uses a separate temporary variable so it
            # cannot suppress an unspent wire after a later map return.
            scripts=scripts.replace('DCC_Entrance_FrameTable',name+'_FrameTable')
        scripts+='\tend\n'
        if key=='field':
            scripts+=f'{name}_FrameTable:\n\tmap_script_2 VAR_TEMP_1, 0, {name}_Intro\n\t.2byte 0\n{name}_Intro:\n\tsetvar VAR_TEMP_1, 1\n\tgoto_if_set FLAG_DCC_INTRO_SEEN, {name}_IntroDone\n\tlockall\n\tmsgbox DCC_Entrance_Text_Intro, MSGBOX_DEFAULT\n\tsetflag FLAG_DCC_INTRO_SEEN\n\treleaseall\n{name}_IntroDone:\n\tend\n'
        for i,obj in sorted(objects[key].items()):
            if obj['script']==f'{name}_Marker{i}':
                description=m['objects'][i-1][3][:32]
                scripts+=f'{name}_Marker{i}::\n\tlock\n\tmsgbox {name}_MarkerText{i}, MSGBOX_DEFAULT\n\trelease\n\tend\n{name}_MarkerText{i}:\n\t.string "ROOM SIGN:\\n{description}$"\n'
        if key=='field':
            model['coord_events']=[dict(type='trigger',x=46,y=42,elevation=3,var='VAR_TEMP_0',var_value='0',script='DCC_Service_Trap')]
            model['bg_events']=[dict(type='sign',x=55,y=42,elevation=0,player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script='DCC_Service_Secret'),dict(type='sign',x=35,y=16,elevation=0,player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=name+'_Loop')]
            scripts+=f'{name}_Loop::\n\tlockall\n\tspecial DccTryOpenReturnLoop\n\tgoto_if_eq VAR_RESULT, FALSE, {name}_LoopLocked\n\tmsgbox {name}_LoopOpenText, MSGBOX_DEFAULT\n\treleaseall\n\tend\n{name}_LoopLocked:\n\tmsgbox {name}_LoopLockedText, MSGBOX_DEFAULT\n\treleaseall\n\tend\n{name}_LoopOpenText:\n\t.string "The return gate is open.\\nThis crossing works both ways.$"\n{name}_LoopLockedText:\n\t.string "The latch is on the far side.\\nFollow the southern route around.$"\n'
        if key=='boss':
            model['bg_events']=[dict(type='sign',x=12,y=11,elevation=0,player_facing_dir='BG_EVENT_PLAYER_FACING_ANY',script=name+'_Stairs')]
            scripts+=f'{name}_Stairs::\n\tlockall\n\tgoto_if_unset FLAG_DCC_BOSS_CLEARED, DCC_Boss_StairsLocked\n\tmsgbox {name}_StairsText, MSGBOX_YESNO\n\tgoto_if_eq VAR_RESULT, NO, DCC_Boss_StairsCancel\n\tsetflag FLAG_DCC_SLICE_COMPLETE\n\twarp MAP_DCC_F1D1CHECKPOINT, 4, 4\n\twaitstate\n\treleaseall\n\tend\n{name}_StairsText:\n\t.string "Go to the opening checkpoint?\\nYou can return from there.$"\n'
        if key=='checkpoint':
            for i,obj in enumerate(model['object_events']):obj['script']=name+('_Review' if i==0 else '_Donut')
            for role,text in [('Review','OPENING CHECKPOINT\\nSave here to keep your progress.\\pThe ladder returns to the warden.\\nThe rest of Floor 1 is in progress.'),('Donut','DONUT: Another room survived.\\nMy next request is still cushions.')]:
                scripts+=f'{name}_{role}::\n\tlock\n\tfaceplayer\n\tmsgbox {name}_{role}Text, MSGBOX_DEFAULT\n\trelease\n\tend\n{name}_{role}Text:\n\t.string "{text}$"\n'
        d=engine/'data/maps'/name;d.mkdir(exist_ok=True);(d/'map.json').write_text(json.dumps(model,indent=2)+'\n');(d/'scripts.inc').write_text(scripts)
        extra_includes.append(f'\t.include "data/maps/{name}/scripts.inc"')
    lp.write_text(json.dumps(layouts,indent=2)+'\n')
    p=engine/'data/event_scripts.s';s=p.read_text();s='\n'.join(line for line in s.splitlines() if not any(name in line for name in (m['name'] for m in identity.values())))
    s='\n'.join(line for line in s.splitlines() if 'data/scripts/dcc_live_navigation.inc' not in line)
    p.write_text(s.rstrip()+'\n\n'+'\n'.join(extra_includes)+'\n\t.include "data/scripts/dcc_live_navigation.inc"\n')
    p=engine/'src/data/dcc_opening.h'
    p.write_text('// Generated by scripts/floor1/generate-live-opening.py.\n'
        +'static const struct DccPresentationTile sDccLoopTiles[] = {\n'+''.join(f'    {{ MAP_DCC_F1D1FIELD, {x}, {y}, FLAG_DCC_D1_LOOP_OPEN, 0x{a:04X}, 0x{b:04X} }},\n' for x,y,a,b in loop_pairs)+'};\n'
        +'static const struct DccPresentationTile sDccLiveTiles[] = {\n'
        +'    { MAP_DCC_F1D1WARDEN, 12, 11, FLAG_DCC_BOSS_CLEARED, 0x3618, 0x362A },\n'
        +'    { MAP_DCC_F1D1FIELD, 46, 42, FLAG_DCC_TRAP_SPENT, 0x328F, 0x329C },\n'
        # Existing floor panel/scuff art: retain elevation3, walkability and MB_CAVE.
        +'    { MAP_DCC_F1D1FIELD, 55, 42, FLAG_DCC_SECRET_TAKEN, 0x3248, 0x3243 },\n};\n')
    (engine/'src/data/dcc_map_counts.h').write_text('// Generated full map-group bounds; not crawler membership.\n'
        +'static const u8 sDccMapCounts[] = {'+', '.join(str(len(groups[n])) for n in groups['group_order'])+'};\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();generate(a.root)
