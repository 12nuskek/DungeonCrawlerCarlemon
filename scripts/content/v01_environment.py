"""Append verified native art to the accepted atlas; preserve all gameplay bindings."""
from pathlib import Path
from PIL import Image
import hashlib, json, struct, subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = '54526744eb7ed961007ffe6100f976a1e7448e8b'
SOURCE = ROOT / 'docs/art-references/environment-native-candidates/native/architecture'
TILESET = 'engine/data/tilesets/secondary/dcc'

def original(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)

def export():
    import io
    atlas = Image.open(io.BytesIO(original(TILESET + '/tiles.png')))
    palette = atlas.getpalette()
    tiles = [atlas.crop((x,y,x+8,y+8)).tobytes()
             for y in range(0,atlas.height,8) for x in range(0,atlas.width,8)]
    old_tiles = len(tiles)
    index = {tile:i for i,tile in reversed(list(enumerate(tiles)))}
    mids = bytearray(original(TILESET + '/metatiles.bin'))
    attributes = bytearray(original(TILESET + '/metatile_attributes.bin'))
    old_mids = len(mids)//16
    cache, sources, changes = {}, {}, []
    spec = json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
    maps = {}
    for key, name in [('field','DCC_F1D1Field'),('quiet','DCC_F1D1Quiet'),('workshop','DCC_F1D1Workshop')]:
        path = 'engine/data/layouts/' + name + '/map.bin'
        maps[key] = {'path':path, 'before':original(path), 'words':bytearray(original(path)),
                     'width':spec['maps'][key]['width'], 'height':spec['maps'][key]['height']}
    def native(name, bank, attr):
        key = (name,bank,attr)
        if key in cache:return cache[key]
        path = SOURCE/(name+'.png');im = Image.open(path)
        assert im.mode=='P' and im.size==(16,16) and max(im.tobytes())<16
        sources[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        entries=[]
        for y in (0,8):
            for x in (0,8):
                data=im.crop((x,y,x+8,y+8)).tobytes()
                if data not in index:index[data]=len(tiles);tiles.append(data)
                entries.append((512+index[data])|(bank<<12))
        mid=512+len(mids)//16
        mids.extend(struct.pack('<8H',*(entries+[512|(bank<<12)]*4)))
        attributes.extend(struct.pack('<H',attr));cache[key]=mid
        return mid
    reserved={k:{tuple(w['at']) for w in spec['maps'][k]['warps']}
              |{tuple(o[:2]) for o in spec['maps'][k]['objects']} for k in maps}
    reserved['field'].update([(35,y) for y in range(13,22)])
    reserved['field'].update([(46,42),(55,42),(50,42)])
    def put(key,x,y,name,bank,walkable=True):
        m=maps[key];assert 0<=x<m['width'] and 0<=y<m['height']
        if (x,y) in reserved[key]:return
        offset=2*(y*m['width']+x);word=struct.unpack_from('<H',m['before'],offset)[0]
        if bool(word&0xc00)==walkable:return
        old_mid=word&0x3ff;attr=struct.unpack_from('<H',original(TILESET+'/metatile_attributes.bin'),2*(old_mid-512))[0]
        new=(word&0xfc00)|native(name,bank,attr)
        struct.pack_into('<H',m['words'],offset,new)
        changes.append({'map':key,'x':x,'y':y,'before':word,'after':new,'asset':name,'bank':bank,'attribute':attr})
    # Broad junction retains exact passable contour and pillar/actor cells.
    for y in range(20,26):
        for x in range(26,35):put('field',x,y,f'floor_slab_{x%2}{y%2}',6)
    for x,y in [(28,24),(29,25),(33,24),(34,23)]:put('field',x,y,'floor_scuff',6)
    for x,y in [(29,26),(33,26),(30,23)]:put('field',x,y,'floor_crack',6)
    # Visible native lights/lintel cue existing doors without moving their warps.
    put('field',37,25,'door_lintel',7,False)
    for x in (34,39):put('field',x,25,'wall_lamp_lit',7,False)
    for x,y in [(36,27),(38,27),(37,28)]:put('field',x,y,'floor_warm_pool',7)
    for x in (40,44):put('field',x,40,'wall_lamp_lit',8,False)
    for x,y in [(41,41),(43,41),(42,42)]:put('field',x,y,'floor_repair',8)
    for x,y in [(44,42),(47,42),(48,42),(49,42),(51,42)]:put('field',x,y,'conduit_horizontal',8)
    # Quiet Landing: native warm mat around the existing guide, sparse repairs.
    for y in range(5,9):
        for x in range(3,6):
            name='mat_middle'
            if y==5:name='mat_top' if x==4 else 'mat_corner_nw' if x==3 else 'mat_corner_ne'
            elif y==8:name='mat_bottom' if x==4 else 'mat_corner_sw' if x==3 else 'mat_corner_se'
            elif x==3:name='mat_left'
            elif x==5:name='mat_right'
            put('quiet',x,y,name,7)
    for x in (4,11):put('quiet',x,1,'wall_lamp_lit',7,False)
    for x,y in [(7,5),(8,6),(9,9),(11,9)]:put('quiet',x,y,'floor_repair',7)
    # Workshop uses the already verified cold bank; no palette changes anywhere.
    for y in range(2,12):
        for x in range(2,15):put('workshop',x,y,f'floor_slab_{x%2}{y%2}',8)
    for x,y in [(5,9),(7,9),(11,9),(13,9)]:put('workshop',x,y,'floor_repair',8)
    for x,y in [(8,7),(9,7),(10,7)]:put('workshop',x,y,'conduit_horizontal',8)
    for x in (4,10):put('workshop',x,1,'wall_lamp_lit',8,False)
    assert len(tiles)<=512 and len(mids)//16<=512
    packed=Image.new('P',(128,((len(tiles)+15)//16)*8));packed.putpalette(palette)
    for i,tile in enumerate(tiles):packed.paste(Image.frombytes('P',(8,8),tile),(i%16*8,i//16*8))
    packed.save(ROOT/TILESET/'tiles.png',bits=4,transparency=0)
    (ROOT/TILESET/'metatiles.bin').write_bytes(mids)
    (ROOT/TILESET/'metatile_attributes.bin').write_bytes(attributes)
    assert bytes(mids[:old_mids*16])==original(TILESET+'/metatiles.bin')
    assert bytes(attributes[:old_mids*2])==original(TILESET+'/metatile_attributes.bin')
    for key,m in maps.items():
        for offset in range(0,len(m['words']),2):
            before=struct.unpack_from('<H',m['before'],offset)[0];after=struct.unpack_from('<H',m['words'],offset)[0]
            assert before&0xfc00==after&0xfc00
            old_attr=struct.unpack_from('<H',attributes,2*((before&0x3ff)-512))[0]
            new_attr=struct.unpack_from('<H',attributes,2*((after&0x3ff)-512))[0]
            assert old_attr==new_attr
        (ROOT/m['path']).write_bytes(m['words'])
    report={'base':BASE,'native_sources':sources,'old_tiles':old_tiles,'new_unique_tiles':len(tiles),
            'allocated_tiles':packed.width*packed.height//64,'old_metatiles':old_mids,'new_metatiles':len(mids)//16,
            'old_tile_pixels_preserved':True,'old_metatile_prefix_preserved':True,
            'all_map_collision_elevation_and_attributes_identical':True,'palettes_unchanged':True,
            'warps_actors_and_dynamic_state_cells_excluded':True,'changes':changes}
    target=ROOT/'scripts/contracts/f1-v01-environment-assets.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print('Verified native export:',len(changes),'placements;',len(tiles),'tiles;',len(mids)//16,'metatiles')

if __name__=='__main__':export()
