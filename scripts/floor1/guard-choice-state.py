"""Complete native field, medicine audit, manual Save and independent cold model."""
from pathlib import Path
import importlib.util,json,re,struct,sys
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=module('gc_base_state',ROOT/'scripts/floor1/continuous-opening-state.py')
medicine=module('gc_medicine_model',ROOT/'scripts/floor1/guard-choice-model.py')
prior=base.prior;fields=base.fields;friendship=base.friendship
POKEMON_BYTES=base.POKEMON_BYTES;MAIL_OFFSET=base.MAIL_OFFSET;MAIL_NONE=base.MAIL_NONE;EMPTY_POKEMON=base.EMPTY_POKEMON
change_item=base.change_item
def snapshot(path):
    result=base.snapshot(path);assert result['map'] in ([35,0],[35,1])
    for flag in (47,48,2137,2138):assert not(result['flags'][flag//8]&(1<<(flag%8)))
    return result
NAMES=['boot','note','supply','guide-initial','trial','scrap','guide-posttrial','guard','guide-guard','save']
def snapshot_ui(path,positions):
    raw=Path(path).read_bytes();assert len(raw)==3324
    # Explicit source bijection restores identity only for party-menu comparison.
    native=medicine.to_field(raw[:600],positions)
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile() as f:
        f.write(native+raw[600:]);f.flush();return snapshot(f.name)
def same(before,after):
    for key in ('party','flags','logical','vars','saved','count','saved_count','counter','map','position','section','facing'):
        assert before[key]==after[key],('complete medicine state',key)
def audit(directory=Path('.')):
    log=(directory/'runtime.log').read_text();events=re.findall(r'MEDICINE_CONFIRM absolute=(\d+) turn=(\d+) owner=2 recipient=(\d+) UI=(\d+) position=(\d+) HP=(\d+) max=(\d+)',log)
    heals=re.findall(r'MEDICINE_HEAL absolute=(\d+) turn=(\d+) owner=2 recipient=(\d+) UI=(\d+) HP=(\d+)->(\d+) restored=(\d+) wasted=(\d+) Potion=(\d+)->(\d+) CarlSTRIKE=355 DonutItemPP=0',log)
    returns=re.findall(r'MEDICINE_RETURN absolute=(\d+) turn=(\d+) uses=(\d+) full_state_exact=1',log)
    assert len(events)==len(heals)==len(returns)<=2
    positions=[]
    for i,(event,heal,ret) in enumerate(zip(events,heals,returns),1):
        frame,turn,recipient,slot,position,hp,maxhp=map(int,event);afterframe,afterturn,afterrecipient,afterslot,oldhp,newhp,gain,waste,quantity,newquantity=map(int,heal)
        assert afterframe>frame and int(ret[0])>afterframe and (turn,recipient,slot,hp)==(afterturn,afterrecipient,afterslot,oldhp)
        assert int(ret[1])==turn and int(ret[2])==i and newhp==min(hp+20,maxhp) and gain==newhp-hp and waste==20-gain and newquantity==quantity-1
        order=medicine.order((directory/f'medicine-{i:02}-order.bin').read_bytes());assert order[slot]==recipient
        field=snapshot(directory/f'medicine-{i:02}-field-state.bin');bag=snapshot(directory/f'medicine-{i:02}-bag-state.bin')
        expected=dict(field,logical=medicine.compact(field['logical']));same(expected,bag)
        before=snapshot_ui(directory/f'medicine-{i:02}-before-state.bin',order);same(bag,before)
        after=snapshot_ui(directory/f'medicine-{i:02}-healed-state.bin',order)
        expected=dict(before,party=medicine.healed(before['party'],recipient),logical=medicine.remove(before['logical'],position=position));same(expected,after)
        same(after,snapshot(directory/f'medicine-{i:02}-return-state.bin'));positions.append(position)
    return positions
def validate(name,before,after,consumption_positions=None):
    assert name in NAMES
    if name=='guard':
        positions=audit() if consumption_positions is None else consumption_positions
        assert len(positions)<=2
        logical=before['logical']
        for pos in positions:logical=medicine.remove(medicine.compact(logical),position=pos)
        expected=dict(before,logical=logical)
        base.validate(name,expected,after)
    else:base.validate(name,before,after)
    if name in ('guide-guard','save'):
        assert after['map']==[35,1] and after['position']==[4,5]
        members=[fields.decode(after['party'][100*i:100*i+100])['fields'] for i in range(2)]
        assert [m['level'] for m in members]==[10,9] and [m['experience'] for m in members]==[627,937]
        assert all(m['status']==0 and m['hp_maxhp_attack_defense_speed_spatk_spdef'][0]==m['hp_maxhp_attack_defense_speed_spatk_spdef'][1] for m in members)
        assert [m['PP'][:2] for m in members]==[[8,40],[2,40]]
        assert struct.unpack_from('<I',after['logical'])[0]==3640
        assert sum(struct.unpack_from('<H',after['logical'],0xd2+4*i)[0] for i in range(30) if struct.unpack_from('<H',after['logical'],0xd0+4*i)[0]==378)==2
        for flag in (37,2135,2136):assert after['flags'][flag//8]&(1<<(flag%8))
        for flag in (40,41,42,43,44,45,46,47,48,49,2137,2138,2139):assert not(after['flags'][flag//8]&(1<<(flag%8)))
def disk_equivalence(save,live):
    # Same complete native fourteen-sector validator, with this contract's legal endpoint.
    code=(ROOT/'scripts/floor1/continuous-opening-state.py').read_text()
    import ast
    tree=ast.parse(code);node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='disk_equivalence')
    source=ast.unparse(node).replace('== [35, 4]','== [35, 1]').replace('== [8, 6]','== [4, 5]')
    namespace={'fields':fields,'Path':Path,'struct':struct,'prior':prior};exec(compile(source,'<same-native-disk-QuietLanding>','exec'),namespace)
    return namespace['disk_equivalence'](save,live)
def cold_equivalence(before,after,save):
    for key in ('party','count','counter','flags','vars','logical','saved','saved_count','map','position'):
        assert before[key]==after[key],('actual cold state',key)
    return disk_equivalence(save,after)
if __name__=='__main__':
    name=sys.argv[1];after=snapshot('current-state.bin')
    if name=='cold':cold_equivalence(snapshot('expected-final-state.bin'),after,'game.sav')
    else:validate(name,snapshot('before-state.bin'),after)
    print('PASS complete source-native Guard-choice transition '+name)
