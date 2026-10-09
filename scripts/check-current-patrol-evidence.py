#!/usr/bin/env python3
"""Read-only current-candidate patrol acceptance; bounded output, no emulator."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, struct
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--original-save',type=Path,required=True);p.add_argument('--runner-commit',required=True);a=p.parse_args()
r=a.run.resolve();s=json.loads((r/'summary.json').read_text())
assert s['runner']==a.runner_commit
assert s['compiled']=='c643f01c11ec68119b0347b107ee20115131debc'
assert s['rom']=='b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a'
assert [x['assertions'] for x in s['sessions']]==[63,18]
assert all(x['exit']==0 and x['errors_bytes']==0 for x in s['sessions'])
assert s['sessions'][0]['historical_timestamps_equal'] and s['sessions'][0]['current_prefix_actions']==59 and s['sessions'][0]['historical_normalized_prefix_equal']
logs=[(r/x['route']/'replay.log').read_text() for x in s['sessions']]
assert all(not (r/x['route']/'errors.log').stat().st_size for x in s['sessions'])
for verdict in ['PASS Bag selection ready fade=0 expected_task=1 frame=24745','PASS actual Potion context acknowledged frame=24757',
    'PASS actual Carl recipient acknowledged frame=24829','PASS Potion healed20HP Carl=3->23 inventory=1->0 PP unchanged',
    'PASS Potion battle return HP=23 quantity=0 PP=4,40,0,38']:
    assert logs[0].count(verdict)==1
assert logs[0].index('PASS flag 2137 1')<logs[0].index('PASS flag 2136 1')
assert all('PASS repeat encounter no battle' in log and 'PASS unchanged XP level equipment' in log for log in logs)
# Stock shared trainer XP: floor(floor(yield*level/7)/2)*150//100, both crawlers alive.
def xp(yield_,level):return (yield_*level//7//2)*150//100
howler=xp(68,9)+xp(60,9);guard=xp(85,9)+xp(60,8)
assert (howler,guard)==(121,132)
def growth(log):
    return [tuple(map(int,m)) for m in re.findall(r'growth level/xp/item=(\d+)/(\d+)/(\d+),(\d+)/(\d+)/(\d+)',log)]
initial=growth(logs[0])[0]
after_howler=growth(logs[0][:logs[0].index('PASS flag 2137 1')])[-1]
final=growth(logs[0])[-1]
assert all(after_howler[i]-initial[i]==howler for i in [1,4])
assert all(final[i]-after_howler[i]==guard for i in [1,4])
assert growth(logs[1])[0]==final==growth(logs[1])[-1]
# Decode privately in host memory; output no key, raw save block or inventory dump.
spec=importlib.util.spec_from_file_location('save_reader',ROOT/'scripts/floor1/save-boundary-input.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def rewards(path):
    raw=path.read_bytes();sb1,sb2=m.blocks(raw);key=struct.unpack_from('<I',sb2,0xac)[0]
    inv=m.inventory(sb1[0x490:0x848],key);items={}
    for at in range(0x560-0x490,len(inv),4):
        iid,n=struct.unpack_from('<HH',inv,at)
        if iid:items[iid]=items.get(iid,0)+n
    return struct.unpack_from('<I',inv)[0],items
assert hashlib.sha256(a.original_save.read_bytes()).hexdigest()=='ea719ffb76f510eabac88cbd345c87d7e21ce009dde0bfca9418ca0a1d3babc8'
before,before_items=rewards(a.original_save);after,after_items=rewards(r/'ordinary-copy.sav')
# Both double-battle payouts:4*last enemy level*2*default class value5, multiplier1.
expected_money=4*9*2*5+4*8*2*5
assert expected_money==680 and after-before==expected_money
assert before_items=={13:1,378:2} and after_items=={378:2}
assert (r/'cold-copy.sav').read_bytes()==(r/'ordinary-copy.sav').read_bytes()
print(json.dumps(dict(host_readiness_checks=29,runtime_assertions=81,current_prefix_actions=59,
    heal_hp=20,potions_consumed=1,action_pp_unchanged=True,howler_then_guard_won=True,
    xp_each_howler=howler,xp_each_guard=guard,level_xp_equipment_same_after_repeat_and_cold=True,
    total_money_reward=expected_money,other_inventory_preserved=True,manual_save_cold_verified=True,
    original_and_cold_unchanged=True,current_candidate_patrol='verified_scoped',first_clear_full_finalT_V01='pending'),indent=2))
