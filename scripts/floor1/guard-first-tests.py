#!/usr/bin/env python3
"""Focused rejection tests, mock native phases only; NEVER emulator execution."""
from pathlib import Path
import importlib.util,json,tempfile,subprocess,copy,struct
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
state=module('gf_test_state',ROOT/'scripts/floor1/guard-first-state.py');runner=module('gf_test_runner',ROOT/'scripts/test-f1-g01e-guard-first-current.py');host=module('gf_test_host',ROOT/'scripts/floor1/guard-first-host.py')
def rejected(fn):
 try:fn()
 except AssertionError:return
 raise AssertionError('invalid evidence accepted')
seed=ROOT/'artifacts/floor1/recovery/runtime-menu-repair/seed.sav'
with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/floor1/guard-first-current') as tmp:
 d=Path(tmp);state.seed_snapshot(seed,d/'expected');s=state.snapshot(d/'expected');s['section']=state.snapshot(ROOT/'artifacts/floor1/guard-first-current/runtime/patrol/guard-before')['section']
 state.validate('boot',s,s,s);checks=1
 for f in d.glob('expected-*'):__import__('shutil').copyfile(f,d/f.name.replace('expected-','current-'))
 subprocess.run(['python3',str(ROOT/'scripts/floor1/guard-first-state.py'),'boot'],cwd=d,check=True);checks+=1
 for key in ('party','flags','logical','counter','map','position','count','saved_count'):
  changed=copy.deepcopy(s)
  if isinstance(changed[key],bytes):v=bytearray(changed[key]);v[0]^=1;changed[key]=bytes(v)
  elif isinstance(changed[key],list):changed[key][0]+=1
  else:changed[key]+=1
  rejected(lambda:state.validate('boot',s,changed,s));checks+=1
 # Derive comparison-only legal victory fixture from native seed, then require
 # complete identity/XP/reward/gate preservation and reject individual defects.
 after=copy.deepcopy(s);after['flags']=bytearray(s['flags']);after['flags'][2136//8]|=1<<(2136%8);after['flags']=bytes(after['flags']);logical=bytearray(s['logical']);struct.pack_into('<I',logical,0,struct.unpack_from('<I',logical)[0]+320);after['logical']=bytes(logical)
 party=bytearray(s['party'])
 for i in range(2):
  raw=s['party'][i*100:i*100+100];c=bytearray(state.fields.decode(raw)['canonical']);struct.pack_into('<I',c,36,(627,937)[i]);c[59]+=1;c[60]+=1
  c[41]=state.friendship.level_ups(c[41],levels=(10,9)[i]-c[84],met_location=c[69],section=s['section'],ball=(struct.unpack_from('<H',c,70)[0]>>11)&15,held_item=struct.unpack_from('<H',c,34)[0],pokerus=c[68])
  c[84]=(10,9)[i];stats=state.level_stats(c,c[84]);struct.pack_into('<6H',c,88,*stats);struct.pack_into('<H',c,86,stats[0]);c[52]-=1;party[i*100:i*100+100]=state.encode(c,raw)
 after['party']=bytes(party);state.validate('guard-win',s,after,s);checks+=1
 for key,index in [('party',36),('party',8),('party',212),('flags',6),('flags',2137//8),('logical',0),('logical',20)]:
  changed=copy.deepcopy(after);v=bytearray(changed[key]);v[index]^=1;changed[key]=bytes(v);rejected(lambda:state.validate('guard-win',s,changed,s));checks+=1
 gate=copy.deepcopy(s);v=bytearray(gate['flags']);v[2135//8]&=~(1<<(2135%8));gate['flags']=bytes(v);rejected(lambda:state.validate('guard-win',gate,after,s));checks+=1
 rejected(lambda:state.validate('howler-win',s,after,s));checks+=1
 # Guide fixture may change exactly HP/status/PP/checksum/native ciphertext.
 before=copy.deepcopy(after);before['map']=[35,1];before['position']=[4,5];healed=copy.deepcopy(before);party=bytearray(before['party'])
 for i in range(2):
  raw=before['party'][100*i:100*(i+1)];c=bytearray(state.fields.decode(raw)['canonical']);c[52:56]=bytes((8 if i==0 else 2,40,0,0));c[86:88]=c[88:90];party[100*i:100*(i+1)]=state.encode(c,raw)
 healed['party']=bytes(party);state.validate('guide-guard',before,healed,s);checks+=1
 rejected(lambda:state.validate('guide-guard',before,before,s));checks+=1
 log='\n'.join(f'MEASURE name={name} frames=900 walking={walk} tiles={steps} warps=1' for name,walk,steps in [('guard-out',112,7),('guard-back',112,7),('howler-out',272,17),('howler-back',272,17),('preboss-out',272,17),('preboss-back',431,27)])
 runner.travel(log);checks+=1
 for lines in (log.splitlines()[1:],log.splitlines()[:-1],log.splitlines()+[log.splitlines()[0]],log.splitlines()+['MEASURE name=unknown frames=900 walking=1 tiles=1 warps=0']):rejected(lambda:runner.travel('\n'.join(lines)));checks+=1
 rejected(lambda:runner.travel(log.replace('walking=431','walking=432')));checks+=1
 # Native phase mock: invalid callbacks never reach any SaveBlock pointer/data;
 # accepted state retained; Field/Quiet allowed, arena scoped, checkpoint denied.
 c='''#include <mgba/core/core.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
'''+(ROOT/'scripts/floor1/party-resource-canonical.h').read_text()+'\n'+(ROOT/'scripts/floor1/walking-preservation.h').read_text()+'\n'+(ROOT/'scripts/floor1/guard-first-observer.h').read_text()+'''
static unsigned valid=0,map=0,saveReads=0,frames=0,battle=0;
static uint32_t r32(struct mCore*c,uint32_t a){(void)c;if(a==100)return valid?200:0;if(a==104)return valid?300:0;if(a==112)return valid?400:0;if(a==500){saveReads++;return 1000;}return 0;}
static uint32_t r16(struct mCore*c,uint32_t a){(void)c;(void)a;return 0;}
static uint32_t r8(struct mCore*c,uint32_t a){(void)c;if(a==100+0x439)return battle?2:0;if(a==1004)return 35;if(a==1005)return map;return 0;}
static void frame(struct mCore*c){(void)c;frames++;}
int main(void){struct mCore c={.busRead32=r32,.busRead16=r16,.busRead8=r8,.runFrame=frame};struct PatrolAddresses a={.mainstate=100,.saveptr=500,.cb1=200,.cb2=300,.vblank=400};struct PatrolSnapshot s={0};struct PatrolGuard g={.armed=1};
 assert(patrol_read(&c,a,&s,1,0)==40&&saveReads==0);g.last.counter=72;assert(!patrol_sample(&c,&g,a,0)&&g.last.counter==72&&saveReads==0&&g.deferred==1);assert(patrol_sample(&c,&g,a,1)==40&&saveReads==0);
 valid=1;for(map=0;map<=1;map++)assert(!patrol_read(&c,a,&s,1,0));map=3;assert(patrol_read(&c,a,&s,1,0)==57);assert(!patrol_read(&c,a,&s,1,1));map=4;assert(patrol_read(&c,a,&s,1,1)==57);
 battle=1;saveReads=0;assert(patrol_read(&c,a,&s,1,1)==40&&saveReads==0);assert(patrol_frame(&c,&g,a)==70&&frames==0&&g.frames==0);battle=0;g.frames=100000;assert(patrol_frame(&c,&g,a)==51&&frames==0);puts("PASS11 native phase/domain/clock rejection cases; no emulator");return 0;}
'''
 (d/'phase-test.c').write_text(c);subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function',str(d/'phase-test.c'),'-o',str(d/'phase-test')],check=True);subprocess.run([str(d/'phase-test')],check=True);checks+=11
 def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
 code,_=host.generate(git);prior=module('gf_original_policy',ROOT/'scripts/floor1/new-save-recovery-host.py').generate(git)[0]
 def policy(c):return c[c.index('                if (elapsed%12==0) {'):c.index('                    if (rescue && potionStage==0 && actor==0')]
 assert policy(code)==policy(prior) and code.count('runFrame(')==1 and 'busWrite' not in code;checks+=3
 print('PASS',checks,'focused native state/phase/domain/clock/travel/policy cases; no emulator')
