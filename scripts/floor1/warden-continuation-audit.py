"""Read-only ladder/source/ELF checks and bounded offline cold fixtures."""
from pathlib import Path
import copy,hashlib,importlib.util,struct,subprocess

def ladder_proof(root,native,walks,elf,parser,boundary):
    import json
    layouts=json.loads((root/'engine/data/layouts/layouts.json').read_text())['layouts']
    attributes=(root/'engine/data/tilesets/secondary/dcc/metatile_attributes.bin').read_bytes()
    rows=parser.elf_symbols(elf);records=[];headers=[]
    def compiled(name,data):
        hits=[r for r in rows if r['name']==name and r['index']];assert len(hits)==1
        assert boundary.rom_bytes(elf,hits[0]['value'],len(data))==data,'actual compiled map/attribute bytes'
        return dict(symbol=name,address=hits[0]['value'],bytes=len(data),SHA256=hashlib.sha256(data).hexdigest())
    proofs=[compiled('gMetatileAttributes_Dcc',attributes)]
    groups=[r for r in rows if r['name']=='gMapGroups' and r['index']];assert len(groups)==1
    maps=struct.unpack('<I',boundary.rom_bytes(elf,groups[0]['value']+35*4,4))[0]
    for number,m in native.items():
        header=struct.unpack('<I',boundary.rom_bytes(elf,maps+number*4,4))[0]
        section=boundary.rom_bytes(elf,header+20,1)[0]
        assert section==m['section'],'exact actual ELF map section'
        headers.append(dict(map=number,header=header,section=section))
    for number in (0,1,3):
        m=native[number];layout=next(r for r in layouts if r['id']==m['layout'])
        assert layout['primary_tileset']=='gTileset_General' and layout['secondary_tileset']=='gTileset_Dcc'
        proofs.append(compiled(layout['name']+'_Blockdata',(root/'engine'/layout['blockdata_filepath']).read_bytes()))
    names={m['id']:n for n,m in native.items()}
    for step in (r for r in walks if r['kind']=='ladder'):
        source=native[step['map']];dest=native[step['destination'][0]]
        dep=next(w for w in source['warp_events'] if [w['x'],w['y']]==step['after'])
        assert names[dep['dest_map']]==step['destination'][0]
        arrive=dest['warp_events'][int(dep['dest_warp_id'])]
        assert [arrive['x'],arrive['y']]==step['destination'][1:]
        assert arrive['dest_map']==source['id']
        assert source['warp_events'][int(arrive['dest_warp_id'])]==dep,'reciprocal native destination'
        for number,m,w in ((step['map'],source,dep),(step['destination'][0],dest,arrive)):
            layout=next(r for r in layouts if r['id']==m['layout']);data=(root/'engine'/layout['blockdata_filepath']).read_bytes()
            word=struct.unpack_from('<H',data,2*(w['x']+layout['width']*w['y']))[0]
            tile=word&0x3ff;assert 512<=tile<1024
            attr=struct.unpack_from('<H',attributes,2*(tile-512))[0]
            assert word&0xc00==0 and word>>12==w['elevation']==3
            assert attr&255==0x61,'native MB_LADDER'
            records.append(dict(map=number,position=[w['x'],w['y']],word=word,attribute=attr,warp=w))
    assert len(records)==4
    avatar=(root/'engine/src/field_control_avatar.c').read_text()
    assert '&& MetatileBehavior_IsLadder(metatileBehavior) != TRUE' in avatar
    fieldmap=(root/'engine/src/fieldmap.c').read_text()
    assert 'secondaryTileset->metatileAttributes[metatile - NUM_METATILES_IN_PRIMARY]' in fieldmap
    assert 'if (metatileBehavior == MB_LADDER)' in (root/'engine/src/metatile_behavior.c').read_text()
    return dict(native_ladder_ends=records,actual_ELF_bytes=proofs,actual_ELF_map_sections=headers)

def cold_fixtures(root,out,model,saved,native_save,env):
    """Actual validator entry point on labelled inert bytes; no emulator/Save UI."""
    directory=out/'SYNTHETIC-OFFLINE-cold-validator';directory.mkdir();checks=0
    disk=native_save(saved);path=directory/'SYNTHETIC-NOT-GAMEPLAY-DISK.fixture';path.write_bytes(disk)
    cold=copy.deepcopy(saved);cold['context']^=0xA5A5A5A5
    cold['owned']=model.prior.resources.canonical(cold['logical'],struct.pack('<I',cold['context']))
    assert model.cold_equivalence(saved,cold,path);checks+=1
    def rejects(fn):
        nonlocal checks
        try:fn()
        except AssertionError:checks+=1;return
        raise AssertionError('offline cold corruption accepted')
    for sector in range(14):
        bad=bytearray(disk);bad[sector*4096]^=1;path.write_bytes(bad)
        rejects(lambda:model.cold_equivalence(saved,cold,path))
    path.write_bytes(disk)
    for key in ('party','saved','flags','vars','logical'):
        bad=copy.deepcopy(cold);data=bytearray(bad[key]);data[-1]^=1;bad[key]=bytes(data)
        rejects(lambda:model.cold_equivalence(saved,bad,path))
    for key in ('count','saved_count','counter','section','facing'):
        bad=copy.deepcopy(cold);bad[key]+=1
        rejects(lambda:model.cold_equivalence(saved,bad,path))
    for counter,poison,section in ((19,1,saved['section']),(21,1,saved['section']),
                                  (20,0,saved['section']),(20,2,saved['section']),(20,1,213)):
        a=copy.deepcopy(saved);b=copy.deepcopy(cold)
        for state in (a,b):
            state['counter']=counter;state['section']=section;v=bytearray(state['vars'])
            struct.pack_into('<H',v,0x54,counter);struct.pack_into('<H',v,0x56,poison);state['vars']=bytes(v)
        rejects(lambda:model.cold_equivalence(a,b,path))
    for key,value in (('saved_count',0x10002),('map',[35,3]),('position',[4,4])):
        bad=copy.deepcopy(saved);bad[key]=value;path.write_bytes(native_save(bad))
        rejects(lambda:model.cold_equivalence(saved,cold,path))
    for key in ('saved','flags','vars','logical'):
        bad=copy.deepcopy(saved);data=bytearray(bad[key]);data[-1]^=1;bad[key]=bytes(data)
        if key=='logical':bad['owned']=model.prior.resources.canonical(bad['logical'],struct.pack('<I',bad['context']))
        path.write_bytes(native_save(bad))
        rejects(lambda:model.cold_equivalence(saved,cold,path))
    path.write_bytes(disk)
    # CLI's fixed names exist only inside this labelled inert fixture directory.
    spec=importlib.util.spec_from_file_location('wc_fixture_pack',root/'scripts/floor1/continuous-opening-r2-offline.py')
    packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    (directory/'game.sav').write_bytes(disk)
    (directory/'expected-final-state.bin').write_bytes(packer.pack(saved))
    (directory/'current-state.bin').write_bytes(packer.pack(cold))
    command=['python3',str(root/'scripts/floor1/warden-continuation-state.py'),'cold']
    good=subprocess.run(command,cwd=directory,env=env,capture_output=True,text=True,timeout=20)
    (directory/'positive-validator.log').write_text(good.stdout+good.stderr);assert good.returncode==0;checks+=1
    bad=copy.deepcopy(cold);bad['section']=213
    (directory/'current-state.bin').write_bytes(packer.pack(bad))
    failed=subprocess.run(command,cwd=directory,env=env,capture_output=True,text=True,timeout=20)
    (directory/'negative-validator.log').write_text(failed.stdout+failed.stderr);assert failed.returncode!=0;checks+=1
    (directory/'current-state.bin').write_bytes(packer.pack(cold))
    return dict(checks=checks,actual_validator_CLI_positive=True,actual_validator_CLI_negative=True,
                encryption_context_changes_logically_exact=True,all14_native_sector_checksum_negatives=True,
                synthetic_only=True,emulator_processes=0,Save_UI_actions=0)
