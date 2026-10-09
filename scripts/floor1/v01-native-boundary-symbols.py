"""Offline, exact-ELF AgbMain -> WaitForVBlank boundary authority.

This exports a proposed adapter contract; it never prepares or runs gameplay.
"""
from pathlib import Path
import hashlib,importlib.util,json,struct
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('verified_v01_functions',ROOT/'scripts/floor1/v01-battle-symbols.py')
symbols=importlib.util.module_from_spec(spec);spec.loader.exec_module(symbols)

def rom_bytes(elf,address,size):
    data=Path(elf).read_bytes();header=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    matches=[]
    for i in range(header[12]):
        section=struct.unpack_from('<10I',data,header[6]+i*header[11])
        if section[1]==1 and section[3]<=address and address+size<=section[3]+section[5]:
            matches.append(data[section[4]+address-section[3]:section[4]+address-section[3]+size])
    assert len(matches)==1,'Missing/ambiguous compiled bytes'
    return matches[0]

def thumb_bl(address,data):
    high,low=struct.unpack('<HH',data)
    if high&0xf800!=0xf000 or low&0xf800!=0xf800:return None
    offset=((high&0x7ff)<<12)|((low&0x7ff)<<1)
    if offset&0x400000:offset-=0x800000
    return (address+4+offset)&0xffffffff

def resolve(elf):
    rows=symbols.functions(symbols.elf_symbols(elf))
    identities=['G:AgbMain','L:main.o:WaitForVBlank','L:main.o:CallCallbacks',
                'G:PlayTimeCounter_Update','G:MapMusicMain','L:main.o:VBlankIntr',
                'G:VBlankCB_Battle','L:overworld.o:VBlankCB_Field']
    selected={}
    for identity in identities:
        matches=[r for r in rows if identity in r['aliases']]
        assert len(matches)==1 and matches[0]['size'],'Unresolved boundary identity: '+identity
        row=dict(matches[0]);row['compiled_SHA256']=hashlib.sha256(rom_bytes(elf,row['address'],row['size'])).hexdigest();selected[identity]=row
    main=selected['G:AgbMain'];wait=selected['L:main.o:WaitForVBlank'];code=rom_bytes(elf,main['address'],main['size'])
    calls=[main['address']+i for i in range(0,len(code)-3,2)
           if thumb_bl(main['address']+i,code[i:i+4])==wait['address']]
    assert len(calls)==1,'Missing/ambiguous direct AgbMain WaitForVBlank call'
    call=calls[0]
    for offset,identity in [(-8,'G:PlayTimeCounter_Update'),(-4,'G:MapMusicMain'),(0,'L:main.o:WaitForVBlank')]:
        assert thumb_bl(call+offset,rom_bytes(elf,call+offset,4))==selected[identity]['address'],'Native call order changed'
    assert rom_bytes(elf,wait['address'],2)==b'\x00\xb5','Expected native entry push {lr}'
    return {'ELF_SHA256':hashlib.sha256(Path(elf).read_bytes()).hexdigest(),
            'entry':wait['address'],'caller_BL':call,'caller_LR':(call+4)|1,
            'entry_opcode':0xb500,'call_sequence_bytes':rom_bytes(elf,call-8,12).hex(),
            'functions':selected,'scope':'Offline proposed native entry boundary only; no live validation'}

def write(elf,output):
    record=resolve(elf);Path(output).write_text(json.dumps(record,indent=2)+'\n');return record
