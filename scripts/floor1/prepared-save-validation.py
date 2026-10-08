"""Offline complete normal Save validation; raw/contexts remain private."""
from pathlib import Path
import importlib.util,struct
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fields=module('prepared_save_fields',ROOT/'scripts/floor1/party-fields.py')
def canonical(raw,context):
    key=struct.unpack('<I',context)[0];out=bytearray(raw)
    struct.pack_into('<I',out,0,struct.unpack_from('<I',raw)[0]^key)
    struct.pack_into('<H',out,4,struct.unpack_from('<H',raw,4)[0]^(key&65535))
    for base,count in [(0x560,30),(0x5d8,30),(0x650,16),(0x690,64),(0x790,46)]:
        for i in range(count):
            q=base-0x490+4*i+2;struct.pack_into('<H',out,q,struct.unpack_from('<H',raw,q)[0]^(key&65535))
    return bytes(out)
def validate(save,final):
    final=Path(final);decoded=fields.saved_party(save);raw=Path(save).read_bytes();selected={}
    latest=max(struct.unpack_from('<I',raw,4096*i+0xffc)[0] for i in range(28)
               if struct.unpack_from('<I',raw,4096*i+0xff8)[0]==0x08012025)
    for i in range(28):
        sector=raw[4096*i:4096*(i+1)];sid,_,signature,count=struct.unpack_from('<HHII',sector,0xff4)
        if signature==0x08012025 and count==latest and sid<14:selected[sid]=sector
    sizes=[min(3968,0x3d88-i*3968) for i in range(4)]
    sb=b''.join(selected[i+1][:sizes[i]] for i in range(4));sb2=selected[0]
    assert decoded['party']==(final/'final-party.bin').read_bytes() and decoded['count']==2
    for i in range(2):assert fields.decode(decoded['party'][100*i:100*(i+1)])['checksum_valid']
    assert sb[0x1270:0x1270+300]==(final/'final-flags.bin').read_bytes()
    import json
    meta=json.loads((final/'final-metadata.json').read_text());assert decoded['friendship_counter']==meta['counter']
    assert canonical(sb[0x490:0x988],sb2[0xac:0xb0])==canonical((final/'final-owned.bin').read_bytes(),(final/'final-context.bin').read_bytes())
    assert decoded['map']==[35,4] and decoded['position']==[8,6]
    return {'latest_native_sector_checksums_valid':True,'exact600_party_and_count':True,
        'exact_counter_flags_all_logical_resources':True,'map':[35,4],'position':[8,6]}
