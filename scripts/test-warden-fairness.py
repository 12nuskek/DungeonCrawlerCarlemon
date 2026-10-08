#!/usr/bin/env python3
"""Focused exact-header scope/cadence tests and source damage envelopes; no emulator."""
from pathlib import Path
import subprocess,tempfile,json,importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[1]
BASE='ed519a05e34f47bf45fa150aa5e456b9e1028926'
PIN='c643f01c11ec68119b0347b107ee20115131debc'
spec=importlib.util.spec_from_file_location('audit',ROOT/'scripts/audit-f1-g01e-warden-threat.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
x=json.loads((ROOT/'docs/evidence/floor1/g01e/warden-threat-audit/analysis.json').read_text())
c,d=x['party'];w,h=x['enemies_source_derived']
def bounds(att,defn,power,atk=0,defense=0,crit=False,special=False,spread=False,stab=False):return a.damage(att,defn,power,atk,defense,crit,special,spread,stab)
off=[bounds(w,c,45,1,stab=True),bounds(w,c,45,0,stab=True)]
fort=[bounds(w,c,45,-1,1,stab=True),bounds(w,c,45,-1,3,stab=True),bounds(w,c,45,-1,3,stab=True),bounds(w,c,45,-2,3,stab=True)]
assert [b[1] for b in off]==[16,12] and [b[1] for b in fort]==[6,4,4,4]
assert sum(b[1] for b in off)<38 and sum(b[1] for b in fort)<38
# Worst ordinary offensive Warden clear t4 then helper cleanup t5/t6;
# fortify Warden t7 then helper cleanup t8/t9. Ignore beneficial level gains.
doff=[bounds(h,d,35,0,stab=True),bounds(h,d,35,-3,stab=True)]
dfort=[bounds(h,d,35,-1,stab=True),bounds(h,d,35,-3,stab=True),bounds(h,d,35,-6,stab=True)]
assert sum(b[1] for b in doff)==11 and sum(b[1] for b in dfort)==14
crit=bounds(h,d,35,-6,crit=True,stab=True);assert crit==[12,15]
wp=dict(w,level=10,max_hp=36,attack=19,defense=13,speed=14,special_attack=19,special_defense=13)
hp=dict(h,level=8,max_hp=28,attack=13,defense=8,speed=9,special_attack=13,special_defense=8)
prepared=[bounds(wp,c,45,1,stab=True),bounds(wp,c,45,0,stab=True)]
assert [b[1] for b in prepared]==[15,10]
prepared_strike=bounds(c,wp,40);assert prepared_strike==[9,11]
assert 4*prepared_strike[0]+2*bounds(d,wp,50,special=True,spread=True)[0]>=36
code=r"""
#include <stdint.h>
#include <assert.h>
#include <stdio.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef uint8_t bool8;
#include "crawler_warden.h"
int main(void) {
 unsigned f=BATTLE_TYPE_TRAINER|BATTLE_TYPE_DOUBLE|BATTLE_TYPE_IS_MASTER;
 for(unsigned t=0;t<65536;t++) {
  int member=t==858||t==859;
  assert(DccWardenEncounter(t,f)==member);
  assert(DccWardenSlam(t,f,SPECIES_LOUDRED,B_SIDE_OPPONENT,MOVE_DCC_SLAM)==member);
  assert(DccWardenHelper(t,f,SPECIES_WHISMUR,B_SIDE_OPPONENT)==member);
 }
 for(unsigned t=858;t<=859;t++) {
  assert(!DccWardenEncounter(t,0));
  assert(!DccWardenEncounter(t,f|BATTLE_TYPE_LINK));
  assert(!DccWardenEncounter(t,f|BATTLE_TYPE_FRONTIER));
  assert(!DccWardenSlam(t,f,SPECIES_LOUDRED,B_SIDE_PLAYER,MOVE_DCC_SLAM));
  assert(!DccWardenSlam(t,f,SPECIES_WHISMUR,B_SIDE_OPPONENT,MOVE_DCC_SLAM));
  assert(!DccWardenSlam(t,f,SPECIES_LOUDRED,B_SIDE_OPPONENT,MOVE_TACKLE));
  assert(!DccWardenHelper(t,f,SPECIES_WHISMUR,B_SIDE_PLAYER));
  assert(!DccWardenHelper(t,f,SPECIES_LOUDRED,B_SIDE_OPPONENT));
 }
 for(unsigned turn=0;turn<256;turn++) assert(DccWardenHelperAttacks(turn)==(turn%4==0));
 puts("PASS exact C guards: all65536 trainer identities; both members/player/wild/link/frontier/species/move exclusions;256 cadence turns");
}
"""
with tempfile.TemporaryDirectory() as temp:
 p=Path(temp);(p/'test.c').write_text(code)
 subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I',str(ROOT/'engine/include'),str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
# Stock crit body and shared move/party tables are preserved byte-for-byte.
old=subprocess.check_output(['git','show',PIN+':engine/src/battle_script_commands.c'],cwd=ROOT,text=True)
new=(ROOT/'engine/src/battle_script_commands.c').read_text()
def stock(s):
 start=s.index('static void Cmd_critcalc(void)\n{');end=s.index('static void Cmd_damagecalc(void)\n{',start)
 return s[s.index('    item = gBattleMons[gBattlerAttacker].item;',start):end]
assert stock(old)==stock(new)
for file in ['engine/src/data/battle_moves.h','engine/src/data/trainer_parties.h','engine/src/data/trainers.h','engine/src/crawler.c','engine/include/pokemon.h','engine/include/global.h']:
 assert (ROOT/file).read_bytes()==subprocess.check_output(['git','show',PIN+':'+file],cwd=ROOT)
print('PASS stock critical body/shared moves/parties/duo/save structs unchanged')
result={'method':'Pure exact C guards plus pinned source integer endpoints; no RNG/emulator/alternate trajectory',
 'offensive_slam_bounds':off,'fortify_slam_bounds':fort,'carl_ordinary_hp_floor_offensive':38-sum(b[1] for b in off),'carl_ordinary_hp_floor_fortify':38-sum(b[1] for b in fort),
 'helper_offensive_turns':[0,4],'helper_fortify_turns':[0,4,8],'helper_offensive_bounds':doff,'helper_fortify_bounds':dfort,'donut_ordinary_hp_floor_offensive':30-sum(b[1] for b in doff),'donut_ordinary_hp_floor_fortify':30-sum(b[1] for b in dfort),
 'warden_clear_turns_no_player_crit':{'offensive':[3,4],'fortify':[6,7]},'last_cleanup_turn_max':{'offensive':6,'fortify':9},'carl_strike_cost_max':7,'donut_spark_cost':2,'helper_critical_bounds_at_negative_stages':crit,
 'helper_crit_limitation':'Two maximum stock helper criticals may exhaust30HP; retained global mechanic, no universal RNG guarantee or searched trajectory',
 'prepared_offensive_slam_bounds':prepared,'prepared_ordinary_carl_hp_floor':38-sum(b[1] for b in prepared),'prepared_enemy_initial_hp':[36,28],'prepared_xp_gain_each':192,'prepared_money_gain':320,'warden_slam_critical_multiplier':1,'shared_slam_power':65,'authored_slam_power':45,'new_emulator_executions_at_envelope_gate':0}
(ROOT/'artifacts/floor1/warden-fairness/envelopes.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
