"""Source/ELF-pinned passive trace points. No game preparation or execution."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('timeline_boundary',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)

def resolve(elf):
    elf=Path(elf);symbols=native.symbols.elf_symbols(elf);functions=native.symbols.functions(symbols)
    def function(identity):
        rows=[r for r in functions if identity in r['aliases']]
        assert len(rows)==1 and rows[0]['size'],identity
        r=rows[0];return {**r,'compiled_SHA256':hashlib.sha256(native.rom_bytes(elf,r['address'],r['size'])).hexdigest()}
    identities=['G:AgbMain','L:main.o:ReadKeys','L:main.o:CallCallbacks','L:main.o:WaitForVBlank',
                'L:main.o:VBlankIntr','G:ProcessSpriteCopyRequests','G:VBlankCB_Battle']
    f={i:function(i) for i in identities};boundary=native.resolve(elf)
    def offset(identity,n,opcode):
        r=f[identity];assert n+2<=r['size'];pc=r['address']+n
        assert struct.unpack('<H',native.rom_bytes(elf,pc,2))[0]==opcode,(identity,n)
        return (pc,pc,opcode,1)
    def exit_point(identity):
        r=f[identity]
        text=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(r['address']),
            '--stop-address='+hex(r['address']+r['size']),str(elf)],text=True)
        matches=[int(line.split(':')[0],16) for line in text.splitlines() if '\tbx\tr0' in line]
        assert len(matches)==1,identity
        return offset(identity,matches[0]-r['address'],0x4700)
    def data(name,size=None):
        rows=[r for r in symbols if r['name']==name and r['index']]
        assert len(rows)==1,name
        if size:assert rows[0]['size']==size,(name,rows[0]['size'])
        return rows[0]['value']
    main='G:AgbMain';call='L:main.o:CallCallbacks';wait='L:main.o:WaitForVBlank';vblank='L:main.o:VBlankIntr'
    points=[offset(main,0x86,struct.unpack('<H',native.rom_bytes(elf,0x0800042a,2))[0]),
        offset('L:main.o:ReadKeys',0,0xb500),exit_point('L:main.o:ReadKeys'),
        offset(call,0,0xb510),offset(call,0xe,0x6860),offset(call,0x18,0xbc10),exit_point(call),
        offset(wait,0,0xb500),offset(wait,0xc,0x8390),exit_point(wait),
        offset(vblank,0,0xb510),offset(vblank,0x92,0x8010),offset(vblank,0x9c,0x8381),exit_point(vblank),
        offset('G:ProcessSpriteCopyRequests',0,0xb5f0),exit_point('G:ProcessSpriteCopyRequests'),
        offset('G:VBlankCB_Battle',0,0xb500),exit_point('G:VBlankCB_Battle'),
        offset(main,boundary['caller_BL']-8-f[main]['address'],struct.unpack('<H',native.rom_bytes(elf,boundary['caller_BL']-8,2))[0]),
        offset(main,boundary['caller_BL']-4-f[main]['address'],struct.unpack('<H',native.rom_bytes(elf,boundary['caller_BL']-4,2))[0]),
        (data('IntrMain_Buffer',2048),data('IntrMain'),0xe3a03301,0)]
    assert points[0][0]==0x0800042a and points[7][0]==0x080008ac
    assert native.rom_bytes(elf,points[-1][1],4)==struct.pack('<I',points[-1][2])
    names=['ReadKeys-call','ReadKeys-entry','ReadKeys-exit','callback-dispatch','CB1-resume','CB2-resume',
           'callback-dispatch-exit','Wait-entry','Wait-clear','Wait-exit','VBlankIntr-entry','BIOS-flag-set',
           'main-flag-set','VBlankIntr-exit','copy-process-entry','copy-process-exit','battle-VBlank-entry',
           'battle-VBlank-exit','playtime-call','music-call','native-IRQ-dispatch']
    return {'ELF_SHA256':hashlib.sha256(elf.read_bytes()).hexdigest(),'functions':f,
        'data':{'Main':data('gMain'),'CopyCount':data('sSpriteCopyRequestCount',1),
                'CopyArmed':data('sShouldProcessSpriteCopyRequests',1),'Copies':data('sSpriteCopyRequests',768)},
        'points':[dict(index=i,name=name,pc=p[0],rom=p[1],opcode=p[2],mode=p[3]) for i,(name,p) in enumerate(zip(names,points))],
        'observation_scope':'Before/after original instructions and event drains only; video/IRQ observations are aggregate drain observations, not callback replacements; no missing historical state recovered.'}

def export(elf,output):
    record=resolve(elf);Path(output).write_text(json.dumps(record,indent=2)+'\n')
    rows=[f'{value:08x} A bv_tl{name}\n' for name,value in record['data'].items()]
    for p in record['points']:
        for name,key in [('PC','pc'),('ROM','rom'),('OP','opcode'),('MODE','mode')]:rows.append(f'{p[key]:08x} A bv_tl{name}{p["index"]}\n')
    return ''.join(rows)
