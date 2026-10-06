"""Authoritative game export from accepted native PNG masters.

The reference package is partial: its original main sheet and optional packed
output are absent. This exporter needs only the staged accepted PNG masters.
It does not claim source-sheet reproduction or recreate/publish omitted files.
"""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs/art-references/environment-native-candidates/native'
PROPS = ['rubble', 'warning_sign', 'workbench', 'quest_tag', 'cache_sealed', 'storage_rack', 'cache_open', 'encounter_remains']

def export_props():
    target = ROOT / 'engine/graphics/dcc/environment'
    target.mkdir(parents=True, exist_ok=True)
    for name in PROPS:
        shutil.copyfile(SOURCE / 'world_shared' / (name+'.png'), target / (name+'.png'))


def export_rooms():
    """Compose native masters with declared geometry and existing-flag state pairs."""
    from PIL import Image
    import json, struct
    engine = ROOT/'engine'
    contract=json.loads((ROOT/'scripts/contracts/n01-baseline.json').read_text())
    geometry=json.loads((ROOT/'scripts/contracts/n02-geometry.json').read_text())
    for name,spec in geometry['rooms'].items():
        for change in spec['changes']:
            cell=contract['maps'][name]['cells'][change['y']*16+change['x']]
            assert (cell['upper_bits'],cell['attribute'])==(change['before_upper'],change['before_attribute'])
            cell['upper_bits']=change['after_upper'];cell['attribute']=change['after_attribute']
    architecture=SOURCE/'architecture'; backgrounds=SOURCE/'background_env6'
    native_palette=Image.open(architecture/'floor_plain.png').getpalette()
    def load(name):return Image.open(architecture/(name+'.png')).copy()
    tiles=[bytes(64)]; tile_ids={tiles[0]:0}; metatiles=[]; attributes=[]; mids={}; manifest={}
    state_rows=[]; state_manifest=[]
    state_dir=engine/'graphics/dcc/presentation';state_dir.mkdir(parents=True,exist_ok=True)
    def subtile(image):
        data=image.tobytes()
        if data not in tile_ids:tile_ids[data]=len(tiles);tiles.append(data)
        return 512+tile_ids[data]
    def metatile(image,bank,attribute):
        key=(image.tobytes(),bank,attribute)
        if key not in mids:
            mids[key]=512+len(metatiles)
            base=[subtile(image.crop((x,y,x+8,y+8)))|(bank<<12) for y in (0,8) for x in (0,8)]
            metatiles.append(base+[512|(bank<<12)]*4);attributes.append(attribute)
        return mids[key]
    banks={'DCC_Entrance':6,'DCC_Vestibule':7,'DCC_Service':8,'DCC_Corridor':6,'DCC_Boss':9,'DCC_Exit':7}
    for name,old in contract['maps'].items():
        room=Image.new('P',(256,192));room.putpalette(native_palette)
        states=[]
        floor={(i%16,i//16) for i,c in enumerate(old['cells']) if c['upper_bits']==0x3000 or c['attribute']==0x61}
        def put(x,y,kind):
            if not (0<=x<16 and 0<=y<12):return
            if kind.startswith(('floor_','mat_','conduit_','threshold_')) and (x,y) not in floor:return
            if kind.startswith(('wall_','corner_outer')) and (x,y) in floor:return
            room.paste(load(kind),(x*16,y*16))
        def prop(kind,px,py,target=None):
            im=Image.open(backgrounds/(kind+'.png'))
            # Use index mask, not palette luminance, to preserve every nonzero source pixel.
            mask=Image.frombytes('L',im.size,bytes(255 if v else 0 for v in im.tobytes()))
            (room if target is None else target).paste(im,(px,py),mask)
        def state_prop(label,flag,x,y,width,height,off,on,px=None,py=None):
            px=x*16 if px is None else px;py=y*16 if py is None else py
            before=room.copy();after=room.copy()
            prop(off,px,py,before);prop(on,px,py,after)
            if label=='wire':
                # Original pixel spark/highlight, not a pressure plate. Native wire
                # silhouette stays intact; bright marks distinguish the live state.
                for xx,yy in [(2,5),(3,4),(4,5),(3,6),(11,8),(12,7),(13,8),(12,9)]:
                    before.putpixel((px+xx,py+yy),15 if xx in (3,12) else 14)
            room.paste(before)
            states.append((label,flag,x,y,width,height,before,after))
        for y in range(12):
            for x in range(16):put(x,y,'floor_plain' if (x,y) in floor else 'void')
        # Follow actual floor contours; two rows of north wall and thin side/rear cutaways.
        for x,y in sorted(floor):
            if (x-1,y) not in floor:put(x-1,y,'wall_side_left')
            if (x+1,y) not in floor:put(x+1,y,'wall_side_right')
            if (x,y+1) not in floor:put(x,y+1,'wall_bottom_plain')
        for x,y in sorted(floor):
            if (x,y-1) not in floor:
                put(x,y-1,'wall_face_a' if x%2 else 'wall_face_b')
                if (x,y-2) not in floor:put(x,y-2,'wall_top_join' if x%5==0 else 'wall_top_plain')
                if (x-1,y) not in floor:
                    put(x-1,y-1,'wall_side_left');put(x-1,y-2,'corner_outer_nw')
                if (x+1,y) not in floor:
                    put(x+1,y-1,'wall_side_right');put(x+1,y-2,'corner_outer_ne')
            if (x,y+1) not in floor:
                if (x-1,y) not in floor:put(x-1,y+1,'corner_outer_sw')
                if (x+1,y) not in floor:put(x+1,y+1,'corner_outer_se')
        for change in geometry['rooms'][name]['changes']:
            x,y=change['x'],change['y']
            if change['kind']=='block' and all((x+dx,y+dy) in floor for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]):
                put(x,y,'wall_top_join')
        # Room-specific arrangements use sparse details rather than a global tile grid.
        if name=='DCC_Entrance':
            for x,y in [(6,6),(8,7),(7,8)]:put(x,y,'floor_crack')
            for x,y in [(6,7),(8,6),(6,8)]:put(x,y,'floor_dust')
            for x,y in [(4,7),(5,8),(10,8)]:put(x,y,'floor_scuff')
            for x in (6,7,8):put(x,2,'wall_face_chip');put(x,1,'wall_top_chip')
            put(4,2,'wall_lamp_lit');put(11,2,'wall_lamp_unlit')
            put(10,9,'floor_repair')
        elif name=='DCC_Vestibule':
            for y in range(7,10):
                for x in range(3,6):
                    kind='mat_middle'
                    if y==7:kind='mat_top' if x==4 else 'mat_corner_nw' if x==3 else 'mat_corner_ne'
                    elif y==9:kind='mat_bottom' if x==4 else 'mat_corner_sw' if x==3 else 'mat_corner_se'
                    elif x==3:kind='mat_left'
                    elif x==5:kind='mat_right'
                    put(x,y,kind)
            prop('bedroll',3*16,6*16)
            put(4,2,'wall_lamp_lit');put(10,2,'wall_lamp_unlit')
            prop('storage_rack',3*16,2*16)
            for x,y in [(8,5),(10,5),(8,7),(10,7)]:put(x,y,'floor_repair')
            put(9,7,'floor_scuff');put(7,5,'floor_warm_pool')
        elif name=='DCC_Service':
            for x in (5,6,7,8):put(x,2,'wall_face_damp')
            put(5,1,'wall_top_damp');put(10,2,'wall_lamp_lit')
            for y in (3,4,5,7,8):put(8,y,'conduit_vertical')
            # The existing hazard coordinate remains the wire, never a pressure plate.
            put(8,6,'conduit_broken')
            state_prop('wire','FLAG_DCC_TRAP_SPENT',8,6,1,1,'wire_live','wire_spent')
            for x,y in [(7,8),(8,8),(9,8),(10,8),(11,8),(12,8),(13,8)]:put(x,y,'conduit_horizontal')
            put(7,7,'floor_drain');put(10,6,'floor_drain')
            put(6,8,'floor_repair');put(13,8,'floor_repair')
            state_prop('secret','FLAG_DCC_SECRET_TAKEN',12,1,1,2,'secret_cracked','secret_breached')
        elif name=='DCC_Corridor':
            for x,y in [(4,5),(6,5),(4,7),(6,7)]:put(x,y,'floor_repair')
            for x,y in [(9,5),(11,5),(9,7),(11,7)]:put(x,y,'floor_drain')
            put(5,2,'wall_lamp_unlit');put(10,2,'wall_lamp_lit')
            prop('storage_rack',4*16,2*16)
            for x in (8,9,10,11):put(x,2,'wall_face_damp')
            for x,y in [(3,4),(8,4),(11,4),(8,8)]:put(x,y,'floor_scuff')
        elif name=='DCC_Boss':
            for x in (6,10):
                put(x,2,'wall_face_repair');put(x,1,'wall_top_join')
                put(x,5,'threshold_v');put(x,6,'threshold_v')
            for x in (7,8,9):put(x,7,'threshold_h')
            put(8,2,'wall_lamp_lit');put(4,2,'wall_lamp_unlit')
            for x in (9,10,11,12,13):put(x,8,'conduit_horizontal')
            put(13,7,'conduit_vertical');put(13,6,'conduit_vertical')
            before=room.copy();put(13,6,'conduit_broken');after=room.copy();room=before.copy()
            states.append(('supply-line','FLAG_DCC_CACHE_BLASTED',13,6,1,1,before,after))
            put(8,6,'floor_repair')
        elif name=='DCC_Exit':
            put(8,1,'wall_lamp_lit')
            for x in (6,7,8,9,10):put(x,3,'floor_warm_pool')
            for x,y in [(5,7),(6,7),(5,8),(6,8)]:put(x,y,'floor_scuff')
            prop('bedroll',4*16,8*16)
            for x in (7,8,9):put(x,9,'threshold_h')
        # Native 32px stair assemblies are centered on existing one-cell warp anchors.
        warp_positions={'DCC_Entrance':[(12,4,'stairs_down')],
          'DCC_Vestibule':[(12,4,'stairs_up'),(2,4,'stairs_down')],
          'DCC_Service':[(2,4,'stairs_up'),(2,9,'stairs_down')],
          'DCC_Corridor':[(2,4,'stairs_up'),(12,4,'stairs_down')],
          'DCC_Boss':[(2,4,'stairs_up'),(12,4,'gate_open')],
          'DCC_Exit':[(2,4,'stairs_up')]}
        for x,y,kind in warp_positions[name]:
            if kind=='gate_open':
                state_prop('gate','FLAG_DCC_BOSS_CLEARED',x-1,y-1,3,2,'gate_closed','gate_open',x*16-8,y*16-16)
            else:prop(kind,x*16-8,y*16-16)
        words=[];bank=banks[name];mapping=[]
        for i,cell in enumerate(old['cells']):
            x=i%16;y=i//16;mid=metatile(room.crop((x*16,y*16,x*16+16,y*16+16)),bank,cell['attribute'])
            words.append(cell['upper_bits']|mid);mapping.append(mid)
        target=engine/'data/layouts'/name
        (target/'map.bin').write_bytes(struct.pack('<192H',*words))
        border=[c['upper_bits']|metatile(load('void'),bank,c['attribute']) for c in old['border_cells']]
        (target/'border.bin').write_bytes(struct.pack('<4H',*border))
        manifest[name]={'palette_bank':bank,'metatiles':mapping,'warps_unchanged':True}
        for label,flag,x,y,width,height,before,after in states:
            entries=[]
            for yy in range(y,y+height):
                for xx in range(x,x+width):
                    cell=old['cells'][yy*16+xx];box=(xx*16,yy*16,(xx+1)*16,(yy+1)*16)
                    off=cell['upper_bits']|metatile(before.crop(box),bank,cell['attribute'])
                    on=cell['upper_bits']|metatile(after.crop(box),bank,cell['attribute'])
                    assert off==words[yy*16+xx],(name,label,xx,yy,'overlapping state composition')
                    state_rows.append((name,xx,yy,flag,off,on))
                    entries.append({'x':xx,'y':yy,'off':off,'on':on,'attribute':cell['attribute']})
            for suffix,im in [('off',before),('on',after)]:
                im.crop((x*16,y*16,(x+width)*16,(y+height)*16)).save(state_dir/f'{label}-{suffix}.png',bits=4,transparency=0)
            state_manifest.append({'label':label,'map':name,'flag':flag,'palette_bank':bank,'x':x,'y':y,'width':width,'height':height,'entries':entries})
    assert len(tiles)<=512 and len(metatiles)<=512,(len(tiles),len(metatiles))
    atlas=Image.new('P',(128,((len(tiles)+15)//16)*8));atlas.putpalette(native_palette)
    for i,data in enumerate(tiles):atlas.paste(Image.frombytes('P',(8,8),data),(i%16*8,i//16*8))
    base=engine/'data/tilesets/secondary/dcc';atlas.save(base/'tiles.png',bits=4,transparency=0)
    (base/'metatiles.bin').write_bytes(b''.join(struct.pack('<8H',*m) for m in metatiles))
    (base/'metatile_attributes.bin').write_bytes(struct.pack('<'+'H'*len(attributes),*attributes))
    for bank,name in [(6,'06-neutral'),(7,'07-warm'),(8,'08-cold'),(9,'09-gate')]:
        # Engine secondary palette filename is the global bank number.
        shutil.copyfile(SOURCE/'optional_bg_palettes'/(name+'.pal'),base/'palettes'/f'{bank:02}.pal')
    (ROOT/'scripts/contracts/n01-composition.json').write_text(json.dumps({'tiles':len(tiles),'metatiles':len(metatiles),'rooms':manifest},indent=2)+'\n')
    (ROOT/'scripts/contracts/n03-presentation.json').write_text(json.dumps(state_manifest,indent=2)+'\n')
    header='// Generated by scripts/content/environment_art.py; existing flags only.\nstatic const struct DccPresentationTile sDccPresentationTiles[] = {\n'
    for name,x,y,flag,off,on in state_rows:
        header+=f'    {{ MAP_NUM(MAP_{name.upper()}), {x}, {y}, {flag}, 0x{off:04X}, 0x{on:04X} }},\n'
    (engine/'src/data/dcc_presentation.h').write_text(header+'};\n')
    print('Native room composition:',len(tiles),'tiles;',len(metatiles),'metatiles; six authored maps with declared geometry')

if __name__ == '__main__':
    export_props()
    export_rooms()
