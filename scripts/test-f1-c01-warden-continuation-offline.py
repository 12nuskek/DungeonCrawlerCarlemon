#!/usr/bin/env python3
"""One bounded offline preparation. Never invokes the compiled observer.

All Save/build paths and pins are supplied by a private reviewed input receipt.
A failure writes a terminal receipt; the output directory is never reused.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,os,re,struct,subprocess,traceback
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def write(path,data):Path(path).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def pack(d):return d['party']+d['flags']+d['owned']+d['vars']+d['saved']+struct.pack('<10I',d['context'],d['counter'],d['count'],d['saved_count'],*d['map'],d['section'],*d['position'],d['facing'])
def run(config,out):
    assert __debug__ and not out.exists();out.mkdir()
    receipt=dict(PASS=False,scope='OFFLINE ONLY',emulator_processes=0,runtime_claims=0,runtime_authority=False)
    try:
        for path,pin in config['files'].items():assert sha(path)==pin,('reviewed input identity',path)
        # Inputs copied under a separate ordinary name; hashes stay immutable.
        original=Path(config['patrol_save']);input_state=Path(config['patrol_state'])
        copied=out/'patrol-input-verified-copy.sav';copied.write_bytes(original.read_bytes())
        assert sha(copied)==config['files'][str(original)]
        route=module('wc_offline_route',ROOT/'scripts/floor1/warden-continuation-route.py')
        model=module('wc_offline_state',ROOT/'scripts/floor1/warden-continuation-state.py')
        admission=module('wc_offline_admission',ROOT/'scripts/floor1/warden-continuation-admission.py')
        host=module('wc_offline_host',ROOT/'scripts/floor1/warden-continuation-host.py')
        initial=model.snapshot(input_state);model.disk_equivalence(copied,initial,([35,1],[4,5]))
        assert initial['counter']==110 and struct.unpack_from('<H',initial['vars'],0x56)[0]==0
        party=[model.fields.decode(initial['party'][100*i:100*(i+1)])['fields'] for i in range(2)]
        assert [p['experience'] for p in party]==[748,1058] and [p['level'] for p in party]==[11,10]
        assert [p['PP'] for p in party]==[[8,40,0,0],[2,40,0,0]]
        assert [p['hp_maxhp_attack_defense_speed_spatk_spdef'][0] for p in party]==[38,30]
        assert all(p['status']==0 for p in party)
        for f in (46,47,48,49,2138,2139):assert not(initial['flags'][f//8]&(1<<(f%8)))
        proposal=route.routes();budgets={n:route.budget(proposal[n]) for n in ('continuation','cold')}
        storage=admission.storage(budgets['continuation']['total'],budgets['cold']['total'])
        assert admission.capacity(storage['reservation_bytes'],storage['reservation_bytes'])
        try:admission.capacity(storage['reservation_bytes']-1,storage['reservation_bytes'])
        except RuntimeError:pass
        else:raise AssertionError('capacity accepted one byte short')
        for action in ('prepare','freeze','claim','execute','save','cold'):
            try:admission.runtime_action(action)
            except RuntimeError:pass
            else:raise AssertionError('runtime action opened')
        for n in ('continuation','cold'):(out/(n+'.route')).write_text(proposal[n])
        names=[s[12:] for s in proposal['continuation'].splitlines() if s.startswith('phase begin ')]
        assert names==host.NAMES and proposal['continuation'].count('pilot ')==1
        assert 'pilot fortify 30000\n' in proposal['continuation'] and 'guide' not in proposal['continuation']
        before=route.counters(proposal['walks'][:proposal['approach_walks']])
        after=route.counters(proposal['walks'][proposal['approach_walks']:],before['counter'],0)
        assert before==dict(counter=7,poison=1,walking_friendship_events=[19],physical_steps=27,step_script_updates=25)
        assert after==dict(counter=20,poison=1,walking_friendship_events=[],physical_steps=13,step_script_updates=13)
        # Separate native source review: route departure/arrival coordinates,
        # ordinary step order, script warp, boss selection, support and rewards.
        avatar=(ROOT/'engine/src/field_control_avatar.c').read_text()
        a=avatar.index('static bool8 TryStartStepBasedScript(struct MapPosition *position');b=avatar.index('\n}',a)
        block=avatar[a:b];assert block.index('TryStartWarpEventScript')<block.index('TryStartStepCountScript')
        assert 'IncrementGameStat(GAME_STAT_STEPS);' in avatar and '(*ptr) %= 128;' in avatar
        maps={'quiet':'DCC_F1D1Quiet','field':'DCC_F1D1Field','boss':'DCC_F1D1Warden','checkpoint':'DCC_F1D1Checkpoint'}
        native={k:json.loads((ROOT/f'engine/data/maps/{n}/map.json').read_text()) for k,n in maps.items()}
        assert any((w['x'],w['y'],w['dest_map'])==(4,3,'MAP_DCC_F1D1FIELD') for w in native['quiet']['warp_events'])
        assert any((w['x'],w['y'],w['dest_map'])==(45,17,'MAP_DCC_F1D1WARDEN') for w in native['field']['warp_events'])
        nav=(ROOT/'engine/data/scripts/dcc_live_navigation.inc').read_text()
        block=nav[nav.index('DCC_Live_Boss_Encounter::'):nav.index('DCC_Live_Boss_Prepared:')]
        assert 'goto_if_set FLAG_DCC_CACHE_BLASTED' in block and 'trainerbattle_double TRAINER_DCC_BOSS,' in block
        stairs=(ROOT/'engine/data/maps/DCC_F1D1Warden/scripts.inc').read_text()
        assert 'setflag FLAG_DCC_SLICE_COMPLETE\n\twarp MAP_DCC_F1D1CHECKPOINT, 4, 4' in stairs
        assert 'goto_if_eq VAR_RESULT, NO, DCC_Boss_StairsCancel' in stairs
        sections=json.loads((ROOT/'engine/src/data/region_map/region_map_sections.json').read_text())
        rows=sections['map_sections'];section={r['id']:i for i,r in enumerate(rows)}
        boss_section=section[native['boss']['region_map_section']];checkpoint_section=section[native['checkpoint']['region_map_section']]
        field_section=section[native['field']['region_map_section']]
        rewards=module('wc_rewards_source',ROOT/'scripts/floor1/continuous-opening-r2-offline.py').source_rewards()['boss']
        assert rewards==dict(XP=226,EV=[3,0,0,0,0,0],money=360)
        code,base=host.generate(git);(out/'observer.c').write_text(code)
        binder=module('wc_actual_elf',ROOT/'scripts/test-f1-c01-uninterrupted-r2.py')
        assert str(binder.ENGINE/'pokeemerald.elf') in config['files']
        elf_proof=binder.binding_table(code,out)
        assert code.index('return 101;')<code.index('mCoreFind')
        assert 'if(i!=3||' in code and 'if(co.attempts!=0)' in code
        assert 'i==3?30000u:36000u' in code and code.count('->runFrame(')==1
        # Compile only. The entry point is never invoked, even as a smoke test.
        tool=Path(config['tool_root']);env=dict(os.environ,LD_LIBRARY_PATH=str(tool/'usr/lib/x86_64-linux-gnu'))
        command=['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(tool/'usr/include'),str(out/'observer.c'),'-L'+str(tool/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(out/'observer')]
        with (out/'compile.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,env=env)
        # Independent executable policy check uses the exact original move
        # selection block on a tiny read-only bus, not a copied Howler policy.
        original=(ROOT/'scripts/playtest.c').read_text();a=original.index('                            unsigned desired=0;');b=original.index('                            unsigned cursor=',a)
        policy=original[a:b]
        test='''#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t bool8;typedef uint16_t u16;typedef uint32_t u32;
#include "crawler_warden.h"
struct bus{unsigned (*busRead8)(void*,unsigned);unsigned (*busRead16)(void*,unsigned);};
static unsigned pp;static unsigned read8(void*p,unsigned a){(void)p;(void)a;return pp;}
static unsigned read16(void*p,unsigned a){(void)p;(void)a;return 30;}
static unsigned select_move(unsigned turn,unsigned b,unsigned available){
 struct bus bus={read8,read16};struct bus *core=&bus;unsigned mons=0,party=0,chp=38,dhp=30;const char *policy="fortify";(void)chp;(void)dhp;pp=available;
'''+policy+''' return desired;}
int main(void){unsigned checks=0;
 for(unsigned t=0;t<40;t++)for(unsigned pp=0;pp<=2;pp++)for(unsigned actor=0;actor<=2;actor+=2){
  unsigned want=t<3?1:(actor==2&&pp==0);assert(select_move(t,actor,pp)==want);checks++;
 }
 for(unsigned t=0;t<40;t++){assert(DccWardenHelperAttacks(t)==(t%4==0));checks++;}
 assert(DccWardenSlam(858,BATTLE_TYPE_TRAINER|BATTLE_TYPE_DOUBLE,SPECIES_LOUDRED,B_SIDE_OPPONENT,MOVE_DCC_SLAM));
 assert(!DccWardenSlam(857,BATTLE_TYPE_TRAINER|BATTLE_TYPE_DOUBLE,SPECIES_LOUDRED,B_SIDE_OPPONENT,MOVE_DCC_SLAM));
 assert(!DccWardenSlam(858,BATTLE_TYPE_TRAINER|BATTLE_TYPE_DOUBLE,SPECIES_LOUDRED,B_SIDE_PLAYER,MOVE_DCC_SLAM));
 assert(!DccWardenSlam(858,BATTLE_TYPE_TRAINER|BATTLE_TYPE_DOUBLE,SPECIES_LOUDRED,B_SIDE_OPPONENT,MOVE_TACKLE));
 printf("PASS exact original fortify/native Warden support checks=%u guards=4\\n",checks);return 0;}
'''
        (out/'inert-policy.c').write_text(test)
        with (out/'policy-compile.log').open('w') as log:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'engine/include'),str(out/'inert-policy.c'),'-o',str(out/'inert-policy')],stdout=log,stderr=subprocess.STDOUT,check=True)
        with (out/'policy-check.log').open('w') as log:subprocess.run([str(out/'inert-policy')],cwd=out,stdout=log,stderr=subprocess.STDOUT,check=True)
        # Exact generated production readers on a synthetic memory bus. No core
        # initialization, ROM load, Save load, reset, game execution or injection.
        common=(ROOT/'scripts/floor1/continuous-opening-inert.c').read_text()
        common=common.replace('"OBSERVER"','"'+str(out/'observer.c')+'"').replace('int main(int argc,char**argv)','int historical_inert_main(int argc,char**argv)')
        common=common.replace('co.attempts=3','co.attempts=0')
        inert='#define main closed_observer_main\n'+common.replace('/* Offline mock','/* Offline mock',1)
        point='#include <assert.h>';inert=inert.replace(point,'#undef main\n'+point,1)
        inert+='\nint main(int argc,char**argv){\n'
        inert+=' if(argc==1){mustStop(87,2);mustStop(89,5);mustStop(89,6);mustStop(89,7);mustStop(90,8);mustStop(87,10);mustStop(87,11);puts("PASS Warden native terminal cases=7");return 0;}\n'
        inert+=' return historical_inert_main(argc,argv);}\n'
        (out/'inert.c').write_text(inert)
        compile_inert=command.copy();compile_inert[compile_inert.index(str(out/'observer.c'))]=str(out/'inert.c');compile_inert[-1]=str(out/'inert')
        with (out/'inert-compile.log').open('w') as log:subprocess.run(compile_inert,stdout=log,stderr=subprocess.STDOUT,check=True,env=env)
        (out/'fixture.bin').write_bytes(input_state.read_bytes())
        def native_check(before,after,kind):
            (out/'synthetic-before.bin').write_bytes(pack(before));(out/'synthetic-after.bin').write_bytes(pack(after))
            p=subprocess.run([str(out/'inert'),'--transition',str(out/'synthetic-before.bin'),str(out/'synthetic-after.bin'),str(kind)],cwd=out,env=env,capture_output=True,text=True)
            return p.returncode
        with (out/'native-terminal.log').open('w') as log:subprocess.run([str(out/'inert')],cwd=out,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        checks=0;chains=[]
        # Four legitimate walking outcomes are alternatives for verification,
        # not predictions, policies, RNG probes or selectable runtime operands.
        for mask in range(4):
            state=copy.deepcopy(initial);state.update(map=[35,3],position=[8,7],section=boss_section,facing=1,counter=7)
            variables=bytearray(state['vars']);struct.pack_into('<H',variables,0,0);struct.pack_into('<H',variables,2,0);struct.pack_into('<H',variables,0x54,7);struct.pack_into('<H',variables,0x56,1);state['vars']=bytes(variables)
            members=bytearray(state['party'])
            for i in range(2):
                raw=state['party'][100*i:100*(i+1)];c=bytearray(model.fields.decode(raw)['canonical'])
                if mask&(1<<i):c[41]=model.friendship.target(c[41],event='WALKING',met_location=c[69],section=field_section,ball=(struct.unpack_from('<H',c,70)[0]>>11)&15)
                members[100*i:100*(i+1)]=model.prior.encode(c,raw)
            state['party']=bytes(members);won=copy.deepcopy(state);members=bytearray(state['party'])
            for i in range(2):
                raw=state['party'][100*i:100*(i+1)];c=bytearray(model.fields.decode(raw)['canonical']);struct.pack_into('<I',c,36,[974,1284][i]);c[56]+=3
                old_level=c[84];c[84]=[12,10][i];c[41]=model.friendship.level_ups(c[41],levels=c[84]-old_level,met_location=c[69],section=boss_section,ball=(struct.unpack_from('<H',c,70)[0]>>11)&15,held_item=0,pokerus=c[68])
                stats=model.prior.level_stats(c,c[84]);struct.pack_into('<6H',c,88,*stats)
                struct.pack_into('<H',c,86,[15,20][i]);c[52:56]=bytes(([3,37,0,0] if i==0 else [0,34,0,0]));members[100*i:100*(i+1)]=model.prior.encode(c,raw)
            won['party']=bytes(members);flags=bytearray(won['flags'])
            for f in (47,2138):flags[f//8]|=1<<(f%8)
            won['flags']=bytes(flags);logical=bytearray(won['logical']);struct.pack_into('<I',logical,0,4360);won['logical']=bytes(logical)
            won['owned']=model.prior.resources.canonical(won['logical'],struct.pack('<I',won['context']))
            variables=bytearray(won['vars']);struct.pack_into('<H',variables,0x56,0);won['vars']=bytes(variables)
            model.validate('boss',state,won);assert native_check(state,won,10)==0;checks+=2
            for region,key in [('party','party'),('flags','flags'),('resources','logical'),('vars','vars'),('saved','saved')]:
                bad=copy.deepcopy(won);b=bytearray(bad[key]);b[-1]^=1;bad[key]=bytes(b)
                try:model.validate('boss',state,bad)
                except AssertionError:checks+=1
                else:raise AssertionError(('corruption accepted',region))
            repeat=copy.deepcopy(won);model.validate('boss-repeat',won,repeat);checks+=1
            stairs=copy.deepcopy(won);stairs.update(position=[12,10],counter=14)
            variables=bytearray(stairs['vars']);struct.pack_into('<H',variables,0x54,14);struct.pack_into('<H',variables,0x56,3);stairs['vars']=bytes(variables)
            model.validate('stairs-no',stairs,stairs);yes=copy.deepcopy(stairs);yes.update(map=[35,4],position=[4,4],section=checkpoint_section)
            flags=bytearray(yes['flags']);flags[48//8]|=1<<(48%8);yes['flags']=bytes(flags)
            model.validate('stairs-yes',stairs,yes);assert native_check(stairs,yes,11)==0;checks+=3
            checkpoint=copy.deepcopy(yes);checkpoint.update(position=[8,6],counter=20)
            variables=bytearray(checkpoint['vars']);struct.pack_into('<H',variables,0x54,20);struct.pack_into('<H',variables,0x56,1);checkpoint['vars']=bytes(variables)
            model.validate('checkpoint',checkpoint,checkpoint);saved=copy.deepcopy(checkpoint);saved['saved']=saved['party']
            model.validate('save',checkpoint,saved);assert native_check(checkpoint,saved,12)==0;checks+=3
            model.same(saved,saved);checks+=1
            (out/f'SYNTHETIC-NOT-GAMEPLAY-chain-{mask}.bin').write_bytes(pack(saved));chains.append(dict(walking_mask=mask,final_friendship=[model.fields.decode(saved['party'][i*100:(i+1)*100])['fields']['friendship'] for i in range(2)]))
        assert sha(original)==config['files'][str(original)] and sha(input_state)==config['files'][str(input_state)]
        source={str(p.relative_to(ROOT)):sha(p) for p in ROOT.joinpath('scripts').glob('**/*') if p.is_file() and p.suffix in ('.py','.c','.h','.json','.route')}
        source.update({str(p.relative_to(ROOT)):sha(p) for p in ROOT.joinpath('engine').rglob('*') if p.is_file() and p.suffix in ('.c','.h','.inc','.json')})
        receipt.update(PASS=True,source_commit=git('rev-parse','HEAD'),engine_tree=git('rev-parse','HEAD:engine'),inherited_base=base,
                       input_pins=config['files'],input_copy_SHA256=sha(copied),observer_source_SHA256=sha(out/'observer.c'),observer_binary_SHA256=sha(out/'observer'),observer_never_invoked=True,
                       proposal=admission.proposal(),route=proposal,budgets=budgets,storage=storage,available_bytes=os.statvfs(out).f_bavail*os.statvfs(out).f_frsize,
                       full_state_checks=checks,native_terminal_cases=7,synthetic_chains=chains,source_inventory=source,
                       actual_ELF_binding_count=len(elf_proof),native_policy_cases=280,native_policy_scope_guards=4,
                       source_reward_proof=rewards,counters=dict(approach=before,postbattle=after),compiler=subprocess.check_output(['cc','-dumpfullversion'],text=True).strip(),
                       retention='Verified local files only; no independent backup or Library transfer',runtime_next_gate='Independent offline review, complete runtime supervisor implementation, full reservation and separate authority')
        write(out/'offline-receipt-private.json',receipt)
        print(json.dumps({k:receipt[k] for k in ('PASS','scope','emulator_processes','runtime_claims','full_state_checks','native_terminal_cases')}))
    except BaseException as error:
        receipt.update(first_failure=type(error).__name__+': '+str(error),traceback=traceback.format_exc())
        write(out/'STOP-offline-private.json',receipt);raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    run(json.loads(args.inputs.read_text()),args.out.resolve())
