"""Private native snapshot validation for ONE current Guard-first execution.
Expected templates are comparison data only: never written to emulator/save.
"""
from pathlib import Path
import importlib.util,json,struct,sys
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
fields=module('gf_native_fields',ROOT/'scripts/floor1/party-fields.py')
resources=module('gf_native_resources',ROOT/'scripts/floor1/prepared-save-validation.py')
friendship=module('gf_native_friendship',ROOT/'scripts/floor1/native-friendship.py')
def snapshot(prefix):
    p=Path(prefix);s=json.loads(Path(str(p)+'-metadata.json').read_text())
    for kind in ('party','flags','owned','context'):s[kind]=Path(str(p)+'-'+kind+'.bin').read_bytes()
    assert len(s['party'])==600 and len(s['flags'])==300 and len(s['owned'])==1272 and len(s['context'])==4
    s['logical']=resources.canonical(s['owned'],s['context']);return s

def seed_snapshot(save,prefix):
    save=Path(save);decoded=fields.saved_party(save);raw=save.read_bytes();latest=max(struct.unpack_from('<I',raw,i*4096+0xffc)[0] for i in range(28) if struct.unpack_from('<I',raw,i*4096+0xff8)[0]==0x08012025)
    selected={}
    for i in range(28):
        sec=raw[4096*i:4096*(i+1)];sid,_,sig,count=struct.unpack_from('<HHII',sec,0xff4)
        if sig==0x08012025 and count==latest and sid<14:selected[sid]=sec
    sb=b''.join(selected[i+1][:min(3968,0x3d88-i*3968)] for i in range(4));sb2=selected[0]
    parts={'party':decoded['party'],'flags':sb[0x1270:0x1270+300],'owned':sb[0x490:0x988],'context':sb2[0xac:0xb0]}
    for k,v in parts.items():Path(str(prefix)+'-'+k+'.bin').write_bytes(v)
    meta={'count':decoded['count'],'saved_count':decoded['count'],'counter':decoded['friendship_counter'],'map':decoded['map'],'position':decoded['position'],'native_phase_valid':True,'absolute_frame':0,'section':None}
    Path(str(prefix)+'-metadata.json').write_text(json.dumps(meta,indent=2)+'\n');return decoded

def encode(canonical,original):
    # Complete native checksum/ciphertext derivation; no unlabelled field masks.
    c=bytearray(canonical);positions=fields.orders()[struct.unpack_from('<I',original)[0]%24]
    plain=bytearray(48)
    for i,j in enumerate(positions):plain[12*j:12*j+12]=c[32+12*i:44+12*i]
    struct.pack_into('<H',c,28,sum(struct.unpack('<24H',plain))&65535)
    key=struct.unpack_from('<I',original)[0]^struct.unpack_from('<I',original,4)[0]
    c[32:80]=b''.join(struct.pack('<I',x^key) for x in struct.unpack('<12I',plain));return bytes(c)

def level_stats(c,level):
    species=struct.unpack_from('<H',c,32)[0];base={66:[70,80,50,35,35,35],52:[40,45,35,90,40,40]}[species]
    iv=struct.unpack_from('<I',c,72)[0];ev=c[56:62];nature=struct.unpack_from('<I',c)[0]%25
    result=[]
    for i,b in enumerate(base):
        value=((2*b+((iv>>(5*i))&31)+ev[i]//4)*level)//100+(level+10 if i==0 else 5)
        if i and nature//5!=nature%5:
            if i-1==nature//5:value=value*110//100
            if i-1==nature%5:value=value*90//100
        result.append(value)
    return result

def validate(stage,before,after,seed):
    assert after['native_phase_valid'] and after['count']==after['saved_count']==2 and 0<=after['counter']<128,'native phase/count/counter'
    assert after['map'][0]==35 and after['map'][1] in (0,1,3),'declared domain'
    for i in range(2):
        d=fields.decode(after['party'][100*i:100*(i+1)]);assert d['checksum_valid'] and d['reencoding_exact'] and not d['bad_egg'] and not d['egg'],'native party integrity'
    if stage=='boot':
        for k in ('party','flags','logical','counter','map','position'):assert after[k]==seed[k],('exact native boot',k)
        return
    assert after['counter']==before['counter'],'no walking during declared battle/recovery'
    assert after['party'][200:]==before['party'][200:],'all remaining400 exact'
    expectedflags=bytearray(before['flags']);logical=bytearray(before['logical'])
    if stage in ('guard-win','howler-win'):
        who=stage.split('-')[0];flag=2136 if who=='guard' else 2137
        assert before['map']==after['map']==[35,0] and before['position']==after['position']==([37,31] if who=='guard' else [51,27]),'battle local return'
        assert bool(before['flags'][2135//8]&(1<<(2135%8))),'trial gating'
        assert not(before['flags'][flag//8]&(1<<(flag%8))),'award once'
        assert bool(before['flags'][2136//8]&(1<<(2136%8)))==(who=='howler'),'Guard flag precedes Howler'
        assert not(before['flags'][2137//8]&(1<<(2137%8))),'Howler pending'
        expectedflags[flag//8]|=1<<(flag%8)
        gain=320 if who=='guard' else 360;struct.pack_into('<I',logical,0,struct.unpack_from('<I',logical)[0]+gain)
        for i in range(2):
            old=before['party'][100*i:100*(i+1)];new=after['party'][100*i:100*(i+1)]
            c=bytearray(fields.decode(old)['canonical']);n=fields.decode(new)['canonical']
            levels=(10,9) if who=='guard' else (11,10);xps=(627,937) if who=='guard' else (748,1058)
            struct.pack_into('<I',c,36,xps[i]);evdelta=(0,0,0,1,1,0) if who=='guard' else (1,0,0,1,0,0)
            # Native STAT order HP/Atk/Def/Speed/SpAtk/SpDef, no Pokerus/held item.
            assert c[68]==0 and struct.unpack_from('<H',c,34)[0]==0,'source EV multipliers'
            for j,v in enumerate(evdelta):c[56+j]+=v
            changes=levels[i]-c[84]
            c[41]=friendship.level_ups(c[41],levels=changes,met_location=c[69],section=after['section'],
                ball=(struct.unpack_from('<H',c,70)[0]>>11)&15,held_item=struct.unpack_from('<H',c,34)[0],pokerus=c[68])
            c[84]=levels[i]
            stats=level_stats(c,levels[i]);struct.pack_into('<6H',c,88,*stats)
            # HP and action expenditure are combat outputs; validate their legal
            # native ranges. Every other byte is derived exactly, not masked.
            hp=struct.unpack_from('<H',n,86)[0];assert 0<hp<=stats[0],'victory without incapacity'
            assert struct.unpack_from('<I',n,80)[0]==0,'no unresolved status'
            struct.pack_into('<H',c,86,hp)
            assert all(0<=n[52+j]<=c[52+j] for j in range(4)) and n[54:56]==c[54:56]==bytes(2),'legal PP expenditure'
            c[52:56]=n[52:56]
            assert encode(c,old)==new,('complete battle transition',i)
    else:
        assert stage in ('guide-guard','guide-howler','guide-preboss'),'frozen checkpoint name'
        assert before['map']==after['map']==[35,1] and before['position']==after['position']==[4,5],'guide locality'
        for i in range(2):
            old=before['party'][100*i:100*(i+1)];new=after['party'][100*i:100*(i+1)];c=bytearray(fields.decode(old)['canonical'])
            c[52:56]=bytes((8 if i==0 else 2,40,0,0));struct.pack_into('<I',c,80,0);c[86:88]=c[88:90]
            assert encode(c,old)==new,('exact full guide restoration',i)
    assert after['flags']==bytes(expectedflags),'all300 flags: optional/preparation/boss/checkpoint exact'
    assert after['logical']==bytes(logical),'all1272 logical owned bytes: once-only money/bags/PC exact'

def main():
    stage=sys.argv[1];after=snapshot('current');seed=snapshot('expected');before=seed if stage=='boot' else snapshot('before')
    validate(stage,before,after,seed)
    print('PASS native milestone',stage,'complete party/count/counter/flags/logical resources; identities private',flush=True)
if __name__=='__main__':main()
