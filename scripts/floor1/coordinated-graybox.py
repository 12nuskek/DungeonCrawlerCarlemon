#!/usr/bin/env python3
"""Third layout: field and interiors exported only to a disposable snapshot."""
import argparse, collections, hashlib, json, struct
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[2]

def rectangle(r):
    x0,y0,x1,y1=r
    return {(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1)}

def terrain(m, opened):
    cells=set().union(*(rectangle(r) for r in m['rectangles'].values()))
    for r in m['blocked'].values(): cells-=rectangle(r)
    if not opened and 'closed_barrier' in m: cells-=rectangle(m['closed_barrier'])
    return cells

def cells(m, opened):
    return terrain(m,opened)-{tuple(o[:2]) for o in m['objects']}

def path(m, opened, start, end):
    start,end=tuple(start),tuple(end)
    # Crossing an untargeted warp would leave this map; it is never a shortcut.
    allowed=cells(m,opened)-{tuple(w['at']) for w in m['warps'] if tuple(w['at']) not in [start,end]}
    assert start in allowed and end in allowed,(m['name'],start,end)
    q=collections.deque([start]);parent={start:None}
    while q:
        at=q.popleft()
        if at==end:
            result=[]
            while at is not None: result.append(at);at=parent[at]
            return result[::-1]
        for dx,dy in [(0,-1),(1,0),(0,1),(-1,0)]:
            n=(at[0]+dx,at[1]+dy)
            if n in allowed and n not in parent:parent[n]=at;q.append(n)
    raise ValueError(f'Unreachable {m["name"]}: {start}→{end}')

def audit(spec, opened):
    results={}
    for key,m in spec['maps'].items():
        floor=cells(m,opened);w,h=m['width'],m['height']
        assert (w+15)*(h+14)<=spec['limits']['buffer_cells']
        assert len(m['objects'])+1<=spec['limits']['active_objects']
        assert len(m['objects'])<=spec['limits']['saved_templates']
        assert all(0<x<w-1 and 0<y<h-1 for x,y in floor)
        for label,r in m['widths'].items():
            sample=rectangle(r[:4]);assert len(sample)==r[4] and sample<=floor,(key,label,sample-floor)
            assert not sample&{tuple(v['at']) for v in m['warps']},(key,label,'warp in clear lane')
        start=tuple(m['anchors']['arrival']);q=collections.deque([start]);visited=set(q)
        while q:
            x,y=q.popleft()
            for n in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if n in floor and n not in visited:visited.add(n);q.append(n)
        assert visited==floor,(key,'disconnected filler')
        for anchor in m['anchors'].values():path(m,opened,start,anchor)
        results[key]={'reachable_cells':len(floor),'buffer_cells':(w+15)*(h+14),'objects_including_player':len(m['objects'])+1,'widths':m['widths']}
    f,q,b=[spec['maps'][k] for k in ['field','quiet','boss']]
    distance=lambda m,a,z:len(path(m,opened,m['anchors'][a],m['anchors'][z]))-1
    guide=distance(q,'arrival','guide');boss=distance(b,'arrival','warden')
    steps={'guard_each_leg':distance(f,'guard','quiet_door')+guide,'howler_each_leg':distance(f,'howler','quiet_door')+guide,'guide_to_warden':guide+distance(f,'quiet_door','warden_door')+boss,'far_to_junction':distance(f,'far_junction','junction')}
    steps['preboss_total']=steps['howler_each_leg']+steps['guide_to_warden']
    for key in ['guard_each_leg','howler_each_leg','guide_to_warden','preboss_total']:assert steps[key]==spec['expected_steps'][key],(key,steps)
    assert steps['far_to_junction']==spec['expected_steps']['far_to_junction_open' if opened else 'far_to_junction_closed']
    ceiling=json.loads((ROOT/spec['comparison_contract']).read_text())
    for key in ['guard','howler']:assert steps[key+'_each_leg']<=ceiling['roundtrips'][key]['steps_each_leg']
    assert steps['preboss_total']<=ceiling['preboss']['steps_total']
    return {'diagnostic':True,'attempt':3,'opened_loop':opened,'maps':results,'steps':steps,'final_T':None,'scope':'Static field+two interior paths; actor occupancy/untargeted warps excluded; no live migration, persistent loop state, battle or art acceptance.'}

def export(spec, engine, opened, out):
    assert (engine.parent/'.dcc-diagnostic-snapshot').is_file(),'Disposable committed snapshot required'
    groups=engine/'data/maps/map_groups.json';g=json.loads(groups.read_text());assert len(g['group_order'])==35
    g['group_order'].append('gMapGroup_TravelPreview');g['gMapGroup_TravelPreview']=[v['name'] for v in spec['maps'].values()];groups.write_text(json.dumps(g,indent=2)+'\n')
    lp=engine/'data/layouts/layouts.json';layouts=json.loads(lp.read_text());identities=[]
    originals={v['name']:v for v in layouts['layouts']}
    for key,m in spec['maps'].items():
        name=m['name'];mid='MAP_'+name.upper();lid='LAYOUT_'+name.upper();w,h=m['width'],m['height'];floor=terrain(m,opened);tile=m['tile_ids'];words=[]
        for y in range(h):
            for x in range(w):
                if (x,y) in floor:word=0x3000|tile['floor']
                elif (x,y+1) in floor:word=0x3c00|tile['north']
                elif (x,y-1) in floor:word=0x3c00|tile['south']
                elif (x+1,y) in floor:word=0x3c00|tile['west']
                elif (x-1,y) in floor:word=0x3c00|tile['east']
                else:word=0x3c00|tile['void']
                words.append(word)
        for warp in m['warps']:
            original=originals[warp['source_map']+'_Layout'];data=(engine/original['blockdata_filepath']).read_bytes();x,y=warp['source_at'];word=struct.unpack_from('<H',data,2*(y*original['width']+x))[0]
            assert word&0xfc00==0x3000,'Existing walkable warp upper bits required'
            x,y=warp['at'];words[y*w+x]=word
        d=engine/'data/layouts'/name;d.mkdir();block=struct.pack('<'+str(w*h)+'H',*words);(d/'map.bin').write_bytes(block);(d/'border.bin').write_bytes(struct.pack('<4H',*([0x3c00|tile['void']]*4)))
        layouts['layouts'].append({'id':lid,'name':name+'_Layout','width':w,'height':h,'primary_tileset':'gTileset_General','secondary_tileset':'gTileset_Dcc','border_filepath':f'data/layouts/{name}/border.bin','blockdata_filepath':f'data/layouts/{name}/map.bin'})
        model=json.loads((engine/'data/maps/DCC_Entrance/map.json').read_text());model.update(id=mid,name=name,layout=lid,object_events=[],warp_events=[],coord_events=[],bg_events=[])
        scripts=name+'_MapScripts::\n\t.byte 0\n'
        for i,(x,y,gfx,text) in enumerate(m['objects']):
            model['object_events'].append({'graphics_id':gfx,'x':x,'y':y,'elevation':3,'movement_type':'MOVEMENT_TYPE_FACE_DOWN','movement_range_x':0,'movement_range_y':0,'trainer_type':'TRAINER_TYPE_NONE','trainer_sight_or_berry_tree_id':'0','script':f'{name}_Object{i}','flag':'0'})
            heal='\tspecial HealPlayerParty\n' if key=='quiet' and i==0 else ''
            scripts+=f'{name}_Object{i}::\n\tlock\n\tfaceplayer\n{heal}\tmsgbox {name}_Text{i}, MSGBOX_DEFAULT\n\trelease\n\tend\n{name}_Text{i}:\n\t.string "Travel preview only.\\n{text[:32]}$"\n'
        for warp in m['warps']:
            dest=next(v for v in spec['maps'].values() if v['map_num']==warp['dest']);x,y=warp['at'];model['warp_events'].append({'x':x,'y':y,'elevation':3,'dest_map':'MAP_'+dest['name'].upper(),'dest_warp_id':str(warp['dest_warp'])})
        d=engine/'data/maps'/name;d.mkdir();(d/'map.json').write_text(json.dumps(model,indent=2)+'\n');(d/'scripts.inc').write_text(scripts)
        events=engine/'data/event_scripts.s';events.write_text(events.read_text()+f'\n\t.include "data/maps/{name}/scripts.inc"\n')
        identities.append({'key':key,'map_group':35,'map_num':m['map_num'],'layout_id':len(layouts['layouts']),'blockdata_sha256':hashlib.sha256(block).hexdigest(),'diagnostic_nonmember':True})
    lp.write_text(json.dumps(layouts,indent=2)+'\n')
    p=engine/'src/new_game.c';s=p.read_text();old='SetWarpDestination(MAP_GROUP(MAP_DCC_ENTRANCE), MAP_NUM(MAP_DCC_ENTRANCE), WARP_ID_NONE, 4, 8);';assert s.count(old)==1;x,y=spec['maps']['field']['anchors']['arrival'];p.write_text(s.replace(old,f'SetWarpDestination(MAP_GROUP(MAP_DCC_TRAVELFIELD), MAP_NUM(MAP_DCC_TRAVELFIELD), WARP_ID_NONE, {x}, {y});'))
    (out/'map-identities.json').write_text(json.dumps(identities,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--engine',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--opened',action='store_true');a=p.parse_args()
    spec=json.loads((ROOT/'scripts/contracts/f1-g01b-coordinated.json').read_text());result=audit(spec,a.opened);a.out.mkdir(parents=True,exist_ok=True);(a.out/'geometry.json').write_text(json.dumps(result,indent=2)+'\n')
    for key,m in spec['maps'].items():
        im=Image.new('RGB',(m['width']*12,m['height']*12),(17,20,27));d=ImageDraw.Draw(im)
        for x,y in cells(m,a.opened):d.rectangle((x*12,y*12,x*12+10,y*12+10),fill=(79,100,104))
        for n,(x,y) in m['anchors'].items():d.ellipse((x*12+2,y*12+2,x*12+8,y*12+8),fill=(244,197,79));d.text((x*12+3,y*12+10),n,fill=(255,238,203))
        im.save(a.out/(key+'-diagram.png'))
    if a.engine:export(spec,a.engine,a.opened,a.out)
    print(json.dumps(result))
if __name__=='__main__':main()
