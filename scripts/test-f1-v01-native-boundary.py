"""Offline symbol/capability/frame-loop/sequence tests. Never loads a game."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    p=ROOT/'scripts/floor1/v01-native-boundary-symbols.py';s=importlib.util.spec_from_file_location('boundary_symbols',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    builds={}
    for case,build in [('before','artifacts/floor1/v01-overworld/build-registered/source/engine'),('after','artifacts/floor1/v01-battle/build-headers/source/engine')]:
        builds[case]=m.write(ROOT/build/'pokeemerald.elf',out/(case+'-boundary.json'))
    for r in builds.values():assert r['entry']==0x080008ac and r['caller_BL']==0x080004ba and r['caller_LR']==0x080004bf
    assert builds['before']['functions']['L:main.o:WaitForVBlank']['compiled_SHA256']==builds['after']['functions']['L:main.o:WaitForVBlank']['compiled_SHA256']
    compiler=['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'scripts/floor1')]
    with (out/'capability.log').open('w') as f:
        subprocess.run(compiler+[str(ROOT/'scripts/floor1/v01-native-boundary-capability.c'),'-lmgba','-o',str(out/'capability')],stdout=f,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'capability')],stdout=f,stderr=subprocess.STDOUT,check=True)
    (out/'cases.c').write_text(r'''
#include <assert.h>
#include <stdio.h>
#include "v01-native-boundary-adapter.h"
struct Model {unsigned frame,time,cycles,event,events,steps,observations,keys,inputEpoch,stop,eventAdvancesFrame;};
static unsigned frame(void *v){return ((struct Model *)v)->frame;}
static uint32_t timeNow(void *v){return ((struct Model *)v)->time+((struct Model *)v)->cycles;}
static unsigned due(void *v){struct Model *m=v;return m->cycles>=m->event;}
static void events(void *v){struct Model *m=v;m->time+=m->cycles;m->cycles=0;m->events++;if(m->eventAdvancesFrame)m->frame++;}
static void step(void *v){struct Model *m=v;assert(!due(v));m->cycles+=3;m->steps++;}
static unsigned observe(void *v){struct Model *m=v;m->observations++;return m->stop;}
static struct BvBoundaryDriverOps ops(struct Model *m){return (struct BvBoundaryDriverOps){m,frame,timeNow,due,events,observe,step,NULL};}
// Model the ORIGINAL runFrame -> ARMRunLoop batch and event ordering.
static void original(struct Model *m,unsigned limit){unsigned f=m->frame;uint32_t t=timeNow(m);
 while(m->frame==f && (uint32_t)(timeNow(m)-t)<limit){while(!due(m))step(m);events(m);}}
static void equal(struct Model a,struct Model b){assert(a.frame==b.frame&&a.time==b.time&&a.cycles==b.cycles&&a.events==b.events&&a.steps==b.steps&&a.keys==b.keys&&a.inputEpoch==b.inputEpoch);}
int main(void){
 for(unsigned event=1;event<40;event++)for(unsigned initiallyDue=0;initiallyDue<2;initiallyDue++){
  struct Model a={.event=event,.keys=128,.inputEpoch=7,.eventAdvancesFrame=1,.cycles=initiallyDue*event},b=a;
  original(&a,282128);struct BvBoundaryDriverOps d=ops(&b);assert(!bv_boundary_drive_frame(&d,1,282128));equal(a,b);
  assert(b.frame==1&&b.events==1&&b.observations==b.steps); // No step after final frame event.
 }
 // Original timeout guard is evaluated after its instruction/event batch.
 struct Model a={.event=20,.keys=0,.inputEpoch=4},b=a;original(&a,10);
 struct BvBoundaryDriverOps d=ops(&b);assert(!bv_boundary_drive_frame(&d,1,10));equal(a,b);assert(b.steps==7&&b.time==21);
 // Counterexample: standard ARMRun-style step dispatches a due frame event,
 // then executes an extra instruction before the caller can check frame end.
 a=(struct Model){.event=10,.cycles=10,.eventAdvancesFrame=1};b=a;original(&a,282128);
 while(due(&b)){events(&b);}
 step(&b);assert(a.frame==b.frame&&a.steps==0&&b.steps==1&&b.cycles==3);
 // Neutral fixed input epochs: all observation is inside the original loop.
 a=(struct Model){.event=13,.eventAdvancesFrame=1};b=a;
 const unsigned keys[]={0,128,0,1,0,0,64,0};
 for(unsigned i=0;i<8;i++){a.keys=b.keys=keys[i];a.inputEpoch=b.inputEpoch=i;original(&a,282128);d=ops(&b);assert(!bv_boundary_drive_frame(&d,1,282128));equal(a,b);}
 b=(struct Model){.event=10};d=ops(&b);assert(bv_boundary_drive_frame(&d,0,282128)==115&&b.steps==0&&b.events==0);
 b.stop=103;assert(bv_boundary_drive_frame(&d,1,282128)==103&&b.steps==0&&b.events==0);
 struct BvBoundaryAuthority auth={1,0x080008ac,0x080004bf,1};
 struct BvBoundaryCpu cpu={1,0x080008ae,0x080004bf,0x3f,1,0x1f,0,1,2,0xb500};
 assert(bv_boundary_authority(&auth,&cpu,1,1,auth.entry));
 assert(!bv_boundary_authority(NULL,&cpu,1,1,auth.entry));assert(!bv_boundary_authority(&auth,NULL,1,1,auth.entry));
 struct BvBoundaryCpu good=cpu;cpu.available=0;assert(!bv_boundary_authority(&auth,&cpu,1,1,auth.entry));cpu=good;
 cpu.lr=0x03000001;assert(!bv_boundary_authority(&auth,&cpu,1,1,auth.entry));cpu=good;
 cpu.cpsr=0x32;cpu.privilegeMode=0x12;assert(!bv_boundary_authority(&auth,&cpu,1,1,auth.entry));cpu=good;
 cpu.pcRaw+=2;assert(!bv_boundary_authority(&auth,&cpu,1,1,auth.entry));cpu=good;
 cpu.cycles=2;assert(!bv_boundary_authority(&auth,&cpu,1,1,auth.entry));cpu=good;
 cpu.opcode=0;assert(!bv_boundary_authority(&auth,&cpu,1,1,auth.entry));cpu=good;
 assert(!bv_boundary_authority(&auth,&cpu,0,1,auth.entry));assert(!bv_boundary_authority(&auth,&cpu,1,2,auth.entry));
 auth.verified=0;assert(!bv_boundary_authority(&auth,&cpu,1,1,auth.entry));
 unsigned char expected[2560]={0},actual[2560]={0};struct BvBoundarySequence g={0};
 assert(bv_boundary_compare(&g,0,0,1,1,1,1,actual,expected)==115&&g.ordinal==0);
 assert(bv_boundary_compare(&g,1,0,1,1,1,1,NULL,expected)==115&&g.ordinal==0);
 assert(bv_boundary_compare(&g,1,0,1,1,1,1,actual,NULL)==115&&g.ordinal==0);
 assert(!bv_boundary_compare(&g,1,0,1,1,1,1,actual,expected));
 assert(bv_boundary_compare(&g,1,0,1,1,1,1,actual,expected)==117); // Duplicate/reordered.
 assert(bv_boundary_compare(&g,1,2,1,1,1,1,actual,expected)==117); // Missing ordinal.
 assert(bv_boundary_compare(&g,1,1,2,1,1,1,actual,expected)==117);
 assert(bv_boundary_compare(&g,1,1,1,1,2,1,actual,expected)==117);
 assert(!bv_boundary_checkpoint(&g,1,1));assert(bv_boundary_checkpoint(&g,2,1)==115);
 assert(bv_boundary_end_frame(&g,2)==117);assert(!bv_boundary_end_frame(&g,1));assert(!bv_boundary_end_frame(&g,0));
 // Every byte of every domain, control tail and padding remains exact.
 for(unsigned byte=0;byte<2560;byte++){actual[byte]=1;assert(bv_boundary_compare(&g,1,1,2,2,2,2,actual,expected)==103&&g.ordinal==1);actual[byte]=0;}
 actual[19]=expected[19]=1;assert(bv_boundary_compare(&g,1,1,2,2,2,2,actual,expected)==116&&g.ordinal==1);actual[19]=expected[19]=0;
 actual[32]=expected[32]=1;assert(bv_boundary_compare(&g,1,1,2,2,2,2,actual,expected)==116&&g.ordinal==1);actual[32]=expected[32]=0;
 assert(!bv_boundary_compare(&g,1,1,2,2,2,2,actual,expected));assert(!bv_boundary_end_frame(&g,1));
 assert(!bv_boundary_finish(&g,2,0));assert(bv_boundary_finish(&g,3,0)==117);assert(bv_boundary_finish(&g,2,1)==117);
 puts("PASS modeled original/frame adapter neutrality: identical instruction/event/cycle/video/input sequence, due event at entry, batch timeout guard, no extra post-frame instruction, unchanged input cadence, first STOP before another step");
 puts("PASS boundary authority/order/full2560-byte negatives: exact entry/caller/mode/hardware identity, missing CPU, pending event, duplicate/missing/reordered boundary, mismatched video/input epoch, missing frame count, stale explicit checkpoint, persistent mutation in EVERY party/BattleMons/flags/resource/control/padding byte; zero gameplay");
}
''')
    with (out/'fixtures.log').open('w') as f:
        subprocess.run(compiler+[str(out/'cases.c'),'-o',str(out/'cases')],stdout=f,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'cases')],stdout=f,stderr=subprocess.STDOUT,check=True)
    result={'result':'PASS installed hardware capability and synthetic offline adapter fixtures','emulator_gameplay_frames':0,'ROMs_loaded':0,'Saves_loaded':0,'CPU_instructions_executed_by_capability_probe':0,'new_execution_claims':0,'live_adapter':'not integrated or enabled; actual game/frame equivalence unverified','before_ELF_SHA256':builds['before']['ELF_SHA256'],'after_ELF_SHA256':builds['after']['ELF_SHA256'],'installed_library_SHA256':sha('/usr/lib/x86_64-linux-gnu/libmgba.so.0.10'),'capability_binary_SHA256':sha(out/'capability'),'fixture_binary_SHA256':sha(out/'cases')}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
