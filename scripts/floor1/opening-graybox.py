#!/usr/bin/env python3
"""Reproduce the D1 candidate and export ONLY to a disposable diagnostic snapshot."""
import argparse, collections, hashlib, json, struct
from pathlib import Path
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[2]

def rectangle(r):
    x0,y0,x1,y1=r
    return {(x,y) for y in range(y0,y1+1) for x in range(x0,x1+1)}

def geometry(spec, opened):
    cells=set().union(*(rectangle(r) for r in spec['rectangles'].values()))
    cells-=rectangle(spec['blocked_landmark'])
    if not opened: cells-=rectangle(spec['closed_loop_barrier'])
    # Every preview actor has physical occupancy, including scenery in a wall cell.
    return cells-{(v[0],v[1]) for v in spec['preview_objects']}

def path(cells, start, end):
    start,end=tuple(start),tuple(end); q=collections.deque([start]); parent={start:None}
    while q:
        p=q.popleft()
        if p==end:
            result=[]
            while p is not None: result.append(p);p=parent[p]
            return result[::-1]
        for dx,dy in [(0,-1),(1,0),(0,1),(-1,0)]:
            n=(p[0]+dx,p[1]+dy)
            if n in cells and n not in parent:parent[n]=p;q.append(n)
    raise ValueError(f'Unreachable {end} from {start}')

def export(spec, engine, opened, out):
    assert (engine.parent/'.dcc-diagnostic-snapshot').is_file(), 'Explicit disposable-snapshot marker required; never export to live engine'
    floor=geometry(spec,opened); w,h=spec['width'],spec['height']
    # Reuse already-reviewed bank6 native art; no new palette/tile allocation.
    words=[]
    for y in range(h):
        for x in range(w):
            if (x,y) in floor:word=0x3000|571
            elif (x,y+1) in floor:word=0x3c00|563
            elif (x,y-1) in floor:word=0x3c00|587
            elif (x+1,y) in floor:word=0x3c00|583
            elif (x-1,y) in floor:word=0x3c00|575
            else:word=0x3c00|556
            words.append(word)
    name='DCC_OpeningPreview'; directory=engine/'data/layouts'/name;directory.mkdir(parents=True)
    (directory/'map.bin').write_bytes(struct.pack('<'+str(w*h)+'H',*words))
    (directory/'border.bin').write_bytes(struct.pack('<4H',*([0x3c00|556]*4)))
    layouts=engine/'data/layouts/layouts.json';v=json.loads(layouts.read_text())
    assert not any(i['id']=='LAYOUT_DCC_OPENING_PREVIEW' for i in v['layouts'])
    v['layouts'].append({'id':'LAYOUT_DCC_OPENING_PREVIEW','name':name+'_Layout','width':w,'height':h,'primary_tileset':'gTileset_General','secondary_tileset':'gTileset_Dcc','border_filepath':f'data/layouts/{name}/border.bin','blockdata_filepath':f'data/layouts/{name}/map.bin'})
    layouts.write_text(json.dumps(v,indent=2)+'\n')
    groups=engine/'data/maps/map_groups.json';v=json.loads(groups.read_text());assert len(v['group_order'])==35
    v['group_order'].append('gMapGroup_OpeningPreview');v['gMapGroup_OpeningPreview']=[name];groups.write_text(json.dumps(v,indent=2)+'\n')
    m=json.loads((engine/'data/maps/DCC_Entrance/map.json').read_text())
    m.update(id='MAP_DCC_OPENING_PREVIEW',name=name,layout='LAYOUT_DCC_OPENING_PREVIEW',object_events=[],warp_events=[])
    scripts=name+'_MapScripts::\n\t.byte 0\n'
    for i,(x,y,gfx,text) in enumerate(spec['preview_objects']):
        obj={'graphics_id':gfx,'x':x,'y':y,'elevation':3,'movement_type':'MOVEMENT_TYPE_FACE_DOWN','movement_range_x':0,'movement_range_y':0,'trainer_type':'TRAINER_TYPE_NONE','trainer_sight_or_berry_tree_id':'0','script':f'{name}_Object{i}','flag':'0'}
        m['object_events'].append(obj)
        scripts+=f'{name}_Object{i}::\n\tlock\n\tmsgbox {name}_Text{i}, MSGBOX_DEFAULT\n\trelease\n\tend\n{name}_Text{i}:\n\t.string "Geometry preview only.\\nNo live encounter or door.\\p{text[:32]}$"\n'
    directory=engine/'data/maps'/name;directory.mkdir();(directory/'map.json').write_text(json.dumps(m,indent=2)+'\n');(directory/'scripts.inc').write_text(scripts)
    events=engine/'data/event_scripts.s';events.write_text(events.read_text()+f'\n\t.include "data/maps/{name}/scripts.inc"\n')
    newgame=engine/'src/new_game.c';old='SetWarpDestination(MAP_GROUP(MAP_DCC_ENTRANCE), MAP_NUM(MAP_DCC_ENTRANCE), WARP_ID_NONE, 4, 8);';s=newgame.read_text();assert s.count(old)==1
    x,y=spec['anchors']['arrival'];newgame.write_text(s.replace(old,f'SetWarpDestination(MAP_GROUP(MAP_DCC_OPENING_PREVIEW), MAP_NUM(MAP_DCC_OPENING_PREVIEW), WARP_ID_NONE, {x}, {y});'))
    # Preview is deliberately nonmember; stock cache path is exercised on save/cold.
    (out/'map-identity.json').write_text(json.dumps({'map_group':35,'map_num':0,'layout_id':len(json.loads(layouts.read_text())['layouts']),'diagnostic':True,'opened_loop':opened,'blockdata_sha256':hashlib.sha256((engine/f'data/layouts/{name}/map.bin').read_bytes()).hexdigest()},indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--engine',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--opened',action='store_true');a=p.parse_args()
    spec=json.loads((ROOT/'scripts/contracts/f1-g01-opening.json').read_text());floor=geometry(spec,a.opened);w,h=spec['width'],spec['height'];a.out.mkdir(parents=True,exist_ok=True)
    assert (w+15)*(h+14)<=spec['limits']['buffer_cells']
    assert len(spec['preview_objects'])+1<=spec['limits']['active_objects']
    assert all(0<x<w-1 and 0<y<h-1 for x,y in floor)
    for name,(x0,y0,x1,y1,width) in spec['width_samples'].items():
        cells=rectangle([x0,y0,x1,y1]);assert len(cells)==width and cells<=floor,(name,cells-floor)
    reach=set(path(floor,spec['anchors']['arrival'],pos)[-1] for pos in spec['anchors'].values());assert len(reach)==len(spec['anchors'])
    q=collections.deque([tuple(spec['anchors']['arrival'])]);visited=set(q)
    while q:
        x,y=q.popleft()
        for n in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
            if n in floor and n not in visited:visited.add(n);q.append(n)
    assert visited==floor, 'No disconnected walkable filler'
    anchors=spec['anchors'];distances={name:len(path(floor,anchors['arrival'],pos))-1 for name,pos in anchors.items()}
    back=len(path(floor,anchors['far_junction'],anchors['quiet_door']))-1
    result={'diagnostic':True,'final_T':None,'reachable_preview_field_cells':len(floor),'buffer_cells':(w+15)*(h+14),'objects_including_player':len(spec['preview_objects'])+1,'all_anchors_reachable':True,'width_samples':spec['width_samples'],'arrival_distances':distances,'far_to_quiet_door_steps':back,'loop_opened':a.opened,'limits':'Preview widths include actor occupancy. No interior/migration or final state/recovery/T acceptance.'}
    (a.out/'geometry.json').write_text(json.dumps(result,indent=2)+'\n')
    im=Image.new('RGB',(w*12,h*12),(17,20,27));draw=ImageDraw.Draw(im)
    for x,y in floor:draw.rectangle((x*12,y*12,x*12+10,y*12+10),fill=(79,100,104))
    for name,(x,y) in anchors.items():draw.ellipse((x*12+2,y*12+2,x*12+8,y*12+8),fill=(244,197,79));draw.text((x*12+3,y*12+10),name,fill=(255,238,203))
    im.save(a.out/'geometry-diagram.png')
    if a.engine:export(spec,a.engine,a.opened,a.out)
    print(json.dumps(result))
if __name__=='__main__':main()
