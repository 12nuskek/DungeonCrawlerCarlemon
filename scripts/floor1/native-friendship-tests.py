#!/usr/bin/env python3
"""Offline actual-input/native walking parity; no emulator or Save fabrication."""
from pathlib import Path
import copy,hashlib,json,struct,subprocess,tempfile,types
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
state=module('nf_state',ROOT/'scripts/floor1/guard-first-state.py');f=state.friendship
retained=ROOT/'artifacts/floor1/guard-first-current/runtime/patrol';before=state.snapshot(retained/'guard-before');after=state.snapshot(retained/'stop-live');seed=state.snapshot(retained/'expected')
assert before['section']==after['section'] and before['map']==after['map']==[35,0]
raw=before['party'][:100];canonical=state.fields.decode(raw)['canonical'];met=canonical[69];section=after['section'];assert met==section
ball=(struct.unpack_from('<H',canonical,70)[0]>>11)&15;assert ball!=11
checks=0
def expect(value,wanted,**kw):
 global checks
 params=dict(levels=1,met_location=met,section=section,ball=ball,held_item=0,pokerus=0);params.update(kw)
 assert f.level_ups(value,**params)==wanted;checks+=1

def rejected(fn):
 global checks
 try:fn()
 except AssertionError:checks+=1;return
 raise AssertionError('invalid native transition accepted')

# Actual retained matching Field, plus explicit nonmatching source comparison.
expect(75,81);expect(75,80,section=(section+1)%256)
for value,wanted in ((99,104),(100,103),(199,202),(200,202)):
 expect(value,wanted,section=(section+1)%256)
for value,wanted in ((99,105),(100,104),(199,203),(200,203)):
 expect(value,wanted)
expect(98,109,levels=3,section=(section+1)%256);expect(98,112,levels=3)
expect(198,205,levels=3,section=(section+1)%256);expect(198,208,levels=3)
for value in (253,254,255):expect(value,255)
expect(75,81,ball=11,section=(section+1)%256);expect(75,82,ball=11);expect(75,75,levels=0)
# Native positive held-effect rounding is modelled, while route-held inputs reject.
assert f.target(75,event='GROW_LEVEL',met_location=met,section=(section+1)%256,ball=ball,hold_effect=27)==82;checks+=1
assert f.target(100,event='GROW_LEVEL',met_location=met,section=(section+1)%256,ball=ball,hold_effect=27)==104;checks+=1
assert f.target(200,event='GROW_LEVEL',met_location=met,section=(section+1)%256,ball=ball,hold_effect=27)==203;checks+=1
for held in (1,13,218):rejected(lambda held=held:f.level_ups(75,levels=1,met_location=met,section=section,ball=ball,held_item=held,pokerus=0))
rejected(lambda:f.level_ups(75,levels=1,met_location=met,section=section,ball=ball,held_item=0,pokerus=1))
state.validate('guard-win',before,after,seed);checks+=1
# Original validator still rejects at its frozen identity. Preserve its STOP.
historical=types.ModuleType('frozen_PR109_state');historical.__file__=str(ROOT/'scripts/floor1/guard-first-state.py')
exec(compile(subprocess.check_output(['git','show','cad9eadfd8405f8eb040e478a7f7c7fb8948788c:scripts/floor1/guard-first-state.py'],cwd=ROOT,text=True),historical.__file__,'exec'),historical.__dict__)
rejected(lambda:historical.validate('guard-win',before,after,seed))
for delta in (-1,1):
 bad=copy.deepcopy(after);c=bytearray(state.fields.decode(bad['party'][:100])['canonical']);c[41]+=delta;bad['party']=state.encode(c,bad['party'][:100])+bad['party'][100:];rejected(lambda:state.validate('guard-win',before,bad,seed))
for kind,index in (('party',8),('party',28),('party',212),('flags',46//8),('flags',2137//8),('logical',0),('logical',20)):
 bad=copy.deepcopy(after);b=bytearray(bad[kind]);b[index]^=1;bad[kind]=bytes(b);rejected(lambda:state.validate('guard-win',before,bad,seed))
for field in ('held','pokerus'):
 bad=copy.deepcopy(before);c=bytearray(state.fields.decode(bad['party'][:100])['canonical'])
 if field=='held':struct.pack_into('<H',c,34,218)
 else:c[68]=1
 bad['party']=state.encode(c,bad['party'][:100])+bad['party'][100:];rejected(lambda:state.validate('guard-win',bad,after,seed))
# All friendship values/bands, Luxury/met separately/together, pure C unchanged
# walking helper: exact boundary increase OR zero, off-boundary increase rejects.
records=[]
for value in range(256):
 for matching in (False,True):
  for luxury in (False,True):
   for effect in (0,27):
    c=bytearray(canonical);c[41]=value;origin=struct.unpack_from('<H',c,70)[0];struct.pack_into('<H',c,70,(origin&~0x7800)|((11 if luxury else ball)<<11))
    original=state.encode(c,raw);sec=section if matching else (section+1)%256
    target=f.target(value,event='WALKING',met_location=met,section=sec,ball=11 if luxury else ball,hold_effect=effect)
    c[41]=target;changed=state.encode(c,raw)
    wrong=next(x for x in (0,1,2,253,254,255) if x not in (value,target));c[41]=wrong;corrupt=state.encode(c,raw)
    records.append(struct.pack('<III',sec,effect,target)+original+changed+corrupt)
with tempfile.TemporaryDirectory(dir=ROOT/'artifacts/floor1/guard-first-corrected') as tmp:
 d=Path(tmp);(d/'fixtures.bin').write_bytes(b''.join(records))
 c='''#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
'''+(ROOT/'scripts/floor1/party-resource-canonical.h').read_text()+'\n'+(ROOT/'scripts/floor1/walking-preservation.h').read_text()+'''
int main(int argc,char**argv){assert(argc==2);FILE*f=fopen(argv[1],"rb");assert(f);unsigned char b[312];unsigned cases=0,assertions=0;
 while(fread(b,1,sizeof b,f)==sizeof b){unsigned section=resource_word(b),effect=resource_word(b+4),target=resource_word(b+8);unsigned char *before=b+12,*after=b+112,*wrong=b+212;
  assert(walk_target(before,section,effect)==target);assertions++;
  assert(walk_member_equal(before,before,0,section,effect));assertions++;
  assert(walk_member_equal(before,before,1,section,effect));assertions++;
  assert(walk_member_equal(before,after,1,section,effect));assertions++;
  assert(walk_member_equal(before,after,0,section,effect)==(walk_friend(before)==target));assertions++;
  assert(!walk_member_equal(before,wrong,1,section,effect));assertions++;
  assert(!walk_member_equal(before,wrong,0,section,effect));assertions++;
  unsigned char bad[100];memcpy(bad,after,100);bad[8]^=1;assert(!walk_member_equal(before,bad,1,section,effect));assertions++;
  memcpy(bad,after,100);bad[28]^=1;assert(!walk_member_equal(before,bad,1,section,effect));assertions++;
  unsigned char partyA[600]={0},partyB[600]={0};memcpy(partyA,before,100);memcpy(partyA+100,before,100);memcpy(partyB,after,100);memcpy(partyB+100,after,100);unsigned effects[2]={effect,effect};
  assert(walk_party_equal(partyA,partyB,1,section,effects));assertions++;partyB[212]^=1;assert(!walk_party_equal(partyA,partyB,1,section,effects));assertions++;
  cases++;
 }assert(!ferror(f)&&cases==2048);fclose(f);printf("PASS walking parity %u cases/%u assertions; unchanged native helper; no emulator\\n",cases,assertions);return 0;}
'''
 (d/'parity.c').write_text(c);subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-function',str(d/'parity.c'),'-o',str(d/'parity')],check=True);subprocess.run([str(d/'parity'),str(d/'fixtures.bin')],check=True)
print('PASS',checks,'friendship/source/actual-native/complete-state/rejection cases;',len(records),'walking parity cases; no emulator')
