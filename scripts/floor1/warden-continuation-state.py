"""Full native Warden transition checks; no fixture is an earned gameplay state."""
from pathlib import Path
import importlib.util,struct,sys
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=module('wc_state_base',ROOT/'scripts/floor1/continuous-opening-state.py')
route=module('wc_state_route',ROOT/'scripts/floor1/warden-continuation-route.py')
SECTIONS={n:m['section'] for n,m in route.native_maps().items()}
fields=base.fields;prior=base.prior;friendship=base.friendship
NAMES=('boss','boss-repeat','stairs-no','stairs-yes','checkpoint','save')
def snapshot(path):
    d=base.snapshot(path);assert d['saved_count']==2 and d['facing'] in (1,2,3,4)
    assert d['section']==SECTIONS[d['map'][1]],'exact source map section'
    assert struct.unpack_from('<H',d['vars'],0x54)[0]==d['counter'],'native counter/var identity'
    for f in (32,33,34,36,37,38,39,2135,2136,2137,2193):assert d['flags'][f//8]&(1<<(f%8))
    assert not(d['flags'][2194//8]&(1<<(2194%8)))
    return d
def same(a,b):
    assert set(a)==set(b)
    for key in a:
        if key not in ('context','owned'):assert a[key]==b[key],('full native state',key)
def anchor(d,number,position,counter,poison):
    assert d['map']==[35,number] and d['position']==list(position)
    assert d['section']==SECTIONS[number],'exact source map section'
    assert d['counter']==struct.unpack_from('<H',d['vars'],0x54)[0]==counter,'exact route counter'
    assert struct.unpack_from('<H',d['vars'],0x56)[0]==poison,'exact route poison counter'
    assert d['facing']==1,'source route south-facing stationary anchor'
def phase_anchor(name,d,before):
    if name in ('boss','boss-repeat'):anchor(d,3,(8,7),7,1 if name=='boss' and before else 0)
    elif name in ('stairs-no','stairs-yes'):
        if name=='stairs-yes' and not before:anchor(d,4,(4,4),14,3)
        else:anchor(d,3,(12,10),14,3)
    else:anchor(d,4,(8,6),20,1)
def continue_equivalence(expected,current,save):
    anchor(expected,1,(4,5),110,0);anchor(current,1,(4,5),110,0)
    same(expected,current)
    return disk_equivalence(save,current,([35,1],[4,5]))
def disk_equivalence(save,live,endpoint):
    decoded=fields.saved_party(save) # Native checksums for all fourteen sectors.
    raw=Path(save).read_bytes();assert len(raw) in (131072,131088)
    latest=max(struct.unpack_from('<I',raw,i*4096+0xffc)[0] for i in range(28)
               if struct.unpack_from('<I',raw,i*4096+0xff8)[0]==0x08012025)
    selected={}
    for i in range(28):
        sector=raw[i*4096:(i+1)*4096];sid,_,signature,count=struct.unpack_from('<HHII',sector,0xff4)
        if signature==0x08012025 and count==latest and sid<14:
            assert sid not in selected;selected[sid]=sector
    assert set(selected)==set(range(14))
    sb=b''.join(selected[i+1][:min(3968,0x3d88-i*3968)] for i in range(4))
    assert decoded['party']==live['party']==live['saved']
    assert decoded['count']==live['count']==live['saved_count']==struct.unpack_from('<I',sb,0x234)[0]==2
    assert decoded['friendship_counter']==live['counter']
    assert (decoded['map'],decoded['position'])==(live['map'],live['position'])==endpoint
    assert sb[0x1270:0x139c]==live['flags'] and sb[0x139c:0x159c]==live['vars']
    assert prior.resources.canonical(sb[0x490:0x988],selected[0][0xac:0xb0])==live['logical']
    return True
def validate(name,before,after):
    assert name in NAMES
    phase_anchor(name,before,True);phase_anchor(name,after,False)
    base.validate(name,before,after)
    if name=='stairs-yes':
        assert after['facing']==1 # Plain checkpoint floor defaults south.
    else:assert after['section']==before['section'] and after['facing']==before['facing']
    if name=='boss':
        assert (before['map'],before['position'])==([35,3],[8,7])
        members=[fields.decode(after['party'][100*i:100*(i+1)])['fields'] for i in range(2)]
        assert [m['experience'] for m in members]==[974,1284]
        assert [m['level'] for m in members]==[12,10]
        assert [m['PP'][1] for m in members][0]==37
        assert 0<=members[0]['PP'][0]<8 and members[1]['PP'][0]<=2
        assert 0<members[1]['PP'][1]<=37
    if name=='save':
        assert (after['map'],after['position'],after['facing'])==([35,4],[8,6],1)
def cold_equivalence(before,after,save):
    anchor(before,4,(8,6),20,1);anchor(after,4,(8,6),20,1)
    same(before,after)
    return disk_equivalence(save,after,([35,4],[8,6]))
if __name__=='__main__':
    mode=sys.argv[1];current=snapshot('current-state.bin')
    if mode=='continue':
        expected=snapshot('expected-input-state.bin')
        # Read-only native fourteen-sector decoding separately verifies the input
        # checkpoint's Quiet endpoint; no checkpoint-floor acceptance is reused.
        continue_equivalence(expected,current,'game.sav')
    elif mode=='cold':cold_equivalence(snapshot('expected-final-state.bin'),current,'game.sav')
    else:
        validate(mode,snapshot('before-state.bin'),current)
        if mode=='save':disk_equivalence('game.sav',current,([35,4],[8,6]))
    print('PASS full native Warden continuation '+mode)
