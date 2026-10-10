"""Separate full-state continuation/new-Save validator. No historical operands change."""
from pathlib import Path
import importlib.util,struct,sys,hashlib
if not __debug__:raise RuntimeError('checks must remain enabled')
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=module('howler_native_state',ROOT/'scripts/floor1/continuous-opening-state.py')
old=module('howler_old_cold2',ROOT/'scripts/floor1/cold2-continue-state.py')
medicine=module('howler_medicine_model',ROOT/'scripts/floor1/guard-choice-model.py')
fields=base.fields;prior=base.prior;friendship=base.friendship
IMMUTABLE=Path('/workspace/scratch/c01-conserve-medicine-opening5-r1-20261010/opening')
NAMES=['howler','howler-repeat','guide-howler','save']
FORBIDDEN=(35,40,41,42,43,44,45,46,47,48,49,2138,2139)
KEYS=('party','flags','logical','vars','saved','count','saved_count','counter','map','position','section','facing')
def snapshot(path):
    d=base.snapshot(path);assert d['map'] in ([35,0],[35,1])
    assert d['facing'] in (1,2,3,4)
    assert d['saved_count']==2
    for f in FORBIDDEN:assert not(d['flags'][f//8]&(1<<(f%8)))
    for f in (37,2135,2136,2193):assert d['flags'][f//8]&(1<<(f%8))
    assert not(d['flags'][2194//8]&(1<<(2194%8)))
    return d
def same(a,b):
    assert set(a)==set(b)
    for key in a:
        if key not in ('owned','context'):assert a[key]==b[key],('complete decoded state',key)
def continue_equivalence(current,save):
    before,_=old.original(save,IMMUTABLE/'phase-09-state.bin')
    return old.compare(before,current)
def validate(name,before,after,positions=()):
    assert name in NAMES and len(positions)<=1
    if name=='howler':
        logical=before['logical']
        for pos in positions:logical=medicine.remove(medicine.compact(logical),position=pos)
        base.validate(name,dict(before,logical=logical),after)
        assert before['map']==[35,0] and before['position']==[51,27]
        pp=[fields.decode(after['party'][100*i:100*(i+1)])['fields']['PP'] for i in range(2)]
        assert 1<=pp[0][0]<=7 and pp[0][1:]==[40,0,0]
        assert pp[1][0] in ((0,1) if positions else (0,)) and 35<=pp[1][1]<=40 and pp[1][2:]==[0,0]
    else:base.validate(name,before,after)
    assert after['section']==before['section'] and after['facing']==before['facing']
    if name in ('guide-howler','save'):
        assert (after['map'],after['position'],after['section'],after['facing'])==([35,1],[4,5],214,1)
        assert after['counter']==112
        members=[fields.decode(after['party'][100*i:100*(i+1)])['fields'] for i in range(2)]
        assert [m['level'] for m in members]==[11,10]
        assert [m['experience'] for m in members]==[748,1058]
        assert [m['friendship'] for m in members]==[87,81]
        assert [m['hp_maxhp_attack_defense_speed_spatk_spdef'][0] for m in members]==[38,30]
        assert all(m['status']==0 for m in members)
        assert [m['PP'] for m in members]==[[8,40,0,0],[2,40,0,0]]
        assert struct.unpack_from('<I',after['logical'])[0]==4000
        def qty(item):return sum(struct.unpack_from('<H',after['logical'],0xd2+4*i)[0] for i in range(30) if struct.unpack_from('<H',after['logical'],0xd0+4*i)[0]==item)
        assert qty(378)==2 and qty(13) in (0,1)
        assert after['flags'][2137//8]&(1<<(2137%8))
def disk_equivalence(save,live):
    # Same unmodified complete fourteen-sector checks, legal Quiet endpoint.
    return old.base.disk_equivalence(save,live)
def cold_equivalence(before,after,save):
    assert before['flags'][2193//8]&(1<<(2193%8)), 'new Save already contains TV_WATCH'
    assert not(before['flags'][2194//8]&(1<<(2194%8)))
    same(before,after) # Idempotent TV_WATCH: no flag allowance or mask.
    return disk_equivalence(save,before)
if __name__=='__main__':
    mode=sys.argv[1];current=snapshot('current-state.bin')
    operands={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ('game.sav','current-state.bin')}
    if mode=='continue':continue_equivalence(current,'game.sav')
    elif mode=='cold':cold_equivalence(snapshot('expected-final-state.bin'),current,'game.sav')
    else:
        positions=()
        if mode=='howler':
            # The unchanged native UI/full-state/acknowledgement audits are
            # rebound to this validator; no historical Guard phase is executed.
            audit=module('howler_native_audit',ROOT/'scripts/floor1/conserve-medicine-state.py')
            audit.base.base.snapshot=snapshot
            positions=audit.audit();assert len(positions)<=1
        validate(mode,snapshot('before-state.bin'),current,positions)
        if mode=='save':disk_equivalence('game.sav',current)
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in operands.items())
    print('PASS separate complete Howler continuation state '+mode)
