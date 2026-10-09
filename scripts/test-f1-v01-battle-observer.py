"""Focused actual-observer/native-layout/symbol negatives; no emulator execution."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('verified_symbols',ROOT/'scripts/floor1/v01-battle-symbols.py');symbols=importlib.util.module_from_spec(spec);spec.loader.exec_module(symbols)
    def row(name,address=0x08000101,size=20,type=2,bind=1,scope='fixture.o'):
        return dict(name=name,value=address,size=size,type=type,bind=bind,scope=scope,index=9)
    rows=[row('Named'),row('.gcc2_compiled.',type=0),row('TrueAlias'),row('Static',address=0x08000201,bind=0)]
    canonical=symbols.functions(rows);assert canonical==symbols.functions(rows[::-1]);assert len(canonical)==2 and len(canonical[0]['aliases'])==2
    assert '.gcc2_compiled.' not in str(canonical)
    assert symbols.functions([row('.gcc2_compiled.')])==[]
    for bad in [[row('Same'),row('Same',address=0x08000201)],[row('A'),row('B',size=24)],[row('Local',bind=0,scope='')]]:
        try:symbols.functions(bad)
        except AssertionError:pass
        else:raise AssertionError('Ambiguous/unresolved identities must fail')
    native=[];cross_build_ids={}
    for name,path in [('before',ROOT/'artifacts/floor1/v01-overworld/build-registered/source/engine'),('after',ROOT/'artifacts/floor1/v01-battle/build-headers/source/engine')]:
        verified=symbols.functions(symbols.elf_symbols(path/'pokeemerald.elf'))
        for r in verified:
            assert r['hash32'] not in cross_build_ids or cross_build_ids[r['hash32']]==r['identity'], 'Cross-build callback identity collision'
            cross_build_ids[r['hash32']]=r['identity']
        native.append(dict(case=name,functions=len(verified),true_alias_groups=sum(len(r['aliases'])>1 for r in verified)))
        required=['L:battle_main.o:HandleTurnActionSelectionState','L:battle_main.o:FreeResetData_ReturnToOvOrDoEvolutions','L:battle_main.o:TryEvolvePokemon','L:battle_main.o:ReturnFromBattleToOverworld','L:battle_setup.o:CB2_EndTrainerBattle','G:CB2_ReturnToFieldContinueScriptPlayMapMusic','L:overworld.o:CB2_ReturnToFieldLocal','G:CB1_Overworld','G:CB2_Overworld','G:BattleMainCB2','L:field_screen_effect.o:Task_WaitForFadeAndEnableScriptCtx']
        for identity in required:assert any(identity in r['aliases'] for r in verified),identity
        routes=symbols.lifecycle_symbols(verified);assert len(routes.splitlines())==11
        for field,identity in symbols.LIFECYCLE_FUNCTIONS.items():
            address=next(r['address'] for r in verified if identity in r['aliases'])
            assert f'{address:08x} V bv_{field}\n' in routes
        try:symbols.lifecycle_symbols([])
        except AssertionError:pass
        else:raise AssertionError('Unresolved lifecycle routing must fail')
        (out/(name+'-verified-functions.json')).write_text(json.dumps(verified,indent=2)+'\n')
    # Actual STOP105 metadata is immutable. Only its retained actor/phase/copy
    # projection is used below. Registry NULL is explicitly a modeled overlay:
    # the original runtime did not separately serialize that pointer value.
    evidence=ROOT/'docs/evidence/floor1/v01/battle/observer-phase'
    stop=json.loads((evidence/'native-stop-diagnostic.json').read_text())
    assert stop['reason']==105 and stop['visual_frame']==14987 and stop['ready_frame']==3155
    assert stop['failed_actor']==0 and stop['failed_sprite']==9 and stop['stage']==3
    assert stop['copy_count']==0 and stop['copy_queue']==[]
    assert 'graphics_registry' not in stop and 'battle_resources' not in stop
    before=json.loads((out/'before-verified-functions.json').read_text())
    phase=next(r for r in before if 'L:battle_main.o:FreeResetData_ReturnToOvOrDoEvolutions' in r['aliases'])
    callback=next(r for r in before if 'G:BattleMainCB2' in r['aliases'])
    assert phase['address']==(stop['native_phase_address']&~1) and phase['hash32']==stop['native_phase_ID']
    assert callback['address']==(stop['CB2']&~1)
    projection=['static void stop105_projection(void){active();']
    for field,row in [('freeReset',phase),('battleCB2',callback)]:
        projection.append(f'v.a.{field}=0x{row["address"]:08x};bv_symbol(&v,v.a.{field},\'F\',"{row["token"]}");')
    projection.append(f'v.frames={stop["visual_frame"]};put32(PHASE,{stop["native_phase_address"]});put32(MAIN+4,{stop["CB2"]});put8(v.a.copyArmed,{stop["copy_armed"]});')
    for actor in stop['actors']:
        b=actor['actor'];sp='SPRITES+68*'+str(actor['sprite'])
        projection.append(f'put8(v.a.ids+{b},{actor["sprite"]});put16(MONS+88*{b}+40,{actor["HP"]});')
        for field,offset,width in [('attr0',0,16),('attr1',2,16),('attr2',4,16),('images',12,32),('flags62',62,8),('flags63',63,8)]:
            projection.append(f'put{width}({sp}+{offset},{actor[field]});')
    projection.extend(['put32(v.a.gfx,0); // Explicit modeled cleared-registry overlay, not a recovered raw value.',
                       'assert(!sample()&&v.lifecycle==BV_RETIRING&&v.exitClean==0);',
                       'puts("PASS actual STOP105 metadata projection with explicitly modeled registry NULL; original runtime remains STOP105, zero emulator frames");}'])
    (out/'stop105-projection.h').write_text('\n'.join(projection)+'\n')
    # Compile the native scheduler and setter verbatim. This proves that a
    # callback selected by CB1 is immediately dispatched as CB2, rather than
    # inventing a full-frame dwell at the saved trainer callback.
    scheduler_source=(ROOT/'engine/src/main.c').read_text()
    scheduler='\n'.join(re.search(r'^'+re.escape(signature)+r'\n\{.*?^\}',scheduler_source,re.M|re.S)[0]
                        for signature in ['static void CallCallbacks(void)','void SetMainCallback2(MainCallback callback)'])
    (out/'native-scheduler.h').write_text('typedef void (*MainCallback)(void);\nstruct {MainCallback callback1,callback2;unsigned state;} gMain;\n'+scheduler+'\n')
    # Pinned 32-bit agbcc, actual native headers; compile-only, no ROM relink.
    engine=ROOT/'artifacts/floor1/v01-battle/build-headers/source/engine'
    cpp=['gcc','-E','-I'+str(engine/'include'),'-I'+str(engine/'gflib'),'-I'+str(engine),'-I'+str(engine/'tools/agbcc/include'),'-I'+str(engine/'tools/agbcc'),'-DMODERN=0','-nostdinc','-undef','-std=gnu89',str(ROOT/'scripts/floor1/v01-battle-layout.c')]
    with (out/'native-layout.i').open('w') as f:subprocess.run(cpp,stdout=f,check=True)
    with (out/'native-layout.log').open('w') as f:subprocess.run([str(engine/'tools/agbcc/bin/agbcc'),'-O2','-mthumb-interwork','-Werror','-o',str(out/'native-layout.s'),str(out/'native-layout.i')],stdout=f,stderr=subprocess.STDOUT,check=True)
    assembly=(out/'native-layout.s').read_text();assert 'ldrb\tr0, [r0, #7]' in assembly and 'lsr\tr0, r0, #7' in assembly
    (out/'cases.c').write_text(r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
struct mCore {unsigned (*busRead8)(struct mCore *,unsigned);unsigned (*busRead16)(struct mCore *,unsigned);unsigned (*busRead32)(struct mCore *,unsigned);};
static unsigned char ram[0x40000],vram[32768];
static unsigned read8(struct mCore *c,unsigned a){(void)c;if(a>=0x02000000&&a<0x02040000)return ram[a-0x02000000];if(a>=0x06010000&&a<0x06018000)return vram[a-0x06010000];return 0;}
static unsigned read16(struct mCore *c,unsigned a){return read8(c,a)|(read8(c,a+1)<<8);}
static unsigned read32(struct mCore *c,unsigned a){return read16(c,a)|(read16(c,a+2)<<16);}
static void put8(unsigned a,unsigned x){assert(a>=0x02000000&&a<0x02040000);ram[a-0x02000000]=x;}
static void put16(unsigned a,unsigned x){put8(a,x);put8(a+1,x>>8);}
static void put32(unsigned a,unsigned x){put16(a,x);put16(a+2,x>>16);}
static unsigned capture(const char *n,unsigned *p,unsigned w,unsigned h){(void)n;(void)p;(void)w;(void)h;return 0;}
#include "v01-battle-observer.h"
static struct mCore core={read8,read16,read32};
static struct BattleVisual v;
enum { MAIN=0x02001000,MONS=0x0200d400,RESULTS=0x02001800,MOVE=0x02001880,GFX=0x02000200,BUFFER=0x02004000,SPRITES=0x0200c000,PHASE=0x02000100,COPIES=0x02019000,COUNT=0x02000108,CTRL=0x02000110,SAVEPTR=0x02000130,SAVE2PTR=0x02000134 };
static const char *token="fn_1111111111111111111111111111111111111111111111111111111111111111";
static const char *intro="fn_2222222222222222222222222222222222222222222222222222222222222222";
static void setup(void){
 memset(ram,0,sizeof ram);memset(vram,0,sizeof vram);memset(&v,0,sizeof v);
 v.a=(struct BattleVisualAddresses){.sprites=SPRITES,.ids=0x02000140,.positions=0x02000150,.gfx=0x02000160,.phase=PHASE,.firstTurn=0x08000100,.battleCB2=0x08000200,.copyCount=COUNT,.copies=COPIES,.copyArmed=0x02000109,.heapStart=0x02000170,.heapSize=0x02000174,.tiles=0x02018000,.palettes=0x02018100};
 bv_symbol(&v,0x08000101,'F',token);bv_symbol(&v,0x08000201,'F',intro);
 unsigned *functions[]={&v.a.freeReset,&v.a.tryEvolve,&v.a.returnBattle,&v.a.endTrainer,&v.a.continueScript,&v.a.returnLocal,&v.a.fieldCB1,&v.a.fieldCB2,&v.a.waitFade};
 for(unsigned i=0;i<9;i++){char name[68];memcpy(name,token,68);memset(name+3,'3'+i,64);*functions[i]=0x08001000+4*i;bv_symbol(&v,*functions[i],'F',name);}
 v.a.fieldHook=0x02000180;v.a.fieldHook2=0x02000184;v.a.fieldLock=0x02000188;v.a.scriptStatus=0x02000189;v.a.fade=0x02000190;v.a.tasks=0x0201a000;v.a.poseState=0x02001900;v.a.battleResources=0x020001a0;v.a.battleStruct=0x020001a4;v.a.battleSprites=0x020001a8;
 put32(MAIN+4,v.a.battleCB2);put32(MAIN+8,v.a.endTrainer);put8(MAIN+0x439,2);put32(PHASE,v.a.battleCB2);put32(v.a.gfx,GFX);put32(GFX,BUFFER);put32(v.a.heapStart,0x02020000);put32(v.a.heapSize,0x1c000);put16(0x02020002,0xa3a3);put32(0x02020004,0x1c000-16);put32(0x0202000c,0x02020000);
 for(unsigned i=0;i<16;i++)put16(v.a.palettes+2*i,65535);
 for(unsigned n=0;n<18;n++)memset(v.poses[n],n+10,2048);
 unsigned species[4]={66,371,52,100},poses[4]={0,17,6,17};
 for(unsigned b=0;b<4;b++){
  put8(v.a.ids+b,b);put8(v.a.positions+b,b);put16(MONS+88*b,species[b]);put16(MONS+88*b+40,30);put32(GFX+4+4*b,BUFFER+8192*b);
  unsigned sp=SPRITES+68*b;put16(sp+2,3<<14);put16(sp+4,64*b);put32(sp+12,GFX+116+32*b);put16(sp+46,b);put16(sp+50,species[b]);put8(sp+62,1);
  for(unsigned i=0;i<4;i++){put32(GFX+116+32*b+8*i,BUFFER+8192*b+2048*i);put16(GFX+116+32*b+8*i+4,2048);}
  memset(ram+BUFFER-0x02000000+8192*b,poses[b]+10,8192);memset(vram+2048*b,poses[b]+10,2048);
 }
 v.readyRequested=1;v.frames=1;
}
static unsigned sample(void){unsigned pixels[1]={0};return bv_sample(&core,&v,MAIN,MONS,RESULTS,0x02001890,0x02001891,MOVE,pixels,1,1);}
static void active(void){setup();put32(PHASE,v.a.firstTurn);assert(!sample()&&v.lifecycle==BV_ACTIVE&&v.exitClean==0);v.frames++;}
static void retire(void){put32(PHASE,v.a.freeReset);put32(v.a.gfx,0);assert(!sample()&&v.lifecycle==BV_RETIRING&&v.exitClean==0);v.frames++;}
static void return_path(void){
 put32(PHASE,v.a.returnBattle);put8(MAIN+0x439,0);put32(MAIN,v.a.fieldCB1);
 // Actual main-loop CB1->CB2 scheduling need not expose EndTrainer for a frame.
 put32(MAIN+4,v.a.continueScript);assert(!sample()&&v.returnPath==3&&!v.endTrainerObserved&&v.savedReturn==v.a.endTrainer&&v.exitClean==0);v.frames++;
 put32(MAIN+4,v.a.returnLocal);put8(MAIN+0x438,0);assert(!sample()&&v.localStates==1&&v.exitClean==0);v.frames++;
 put8(MAIN+0x438,1);assert(!sample()&&v.returnPath==7&&v.exitClean==0);v.frames++;
 put8(MAIN+0x438,2);assert(!sample()&&v.returnPath==7&&v.exitClean==0);assert(!sample());v.frames++;
 put8(MAIN+0x438,3);assert(!sample()&&v.returnPath==15&&v.exitClean==0);v.frames++;
 put32(MAIN+4,v.a.fieldCB2);put8(MAIN+0x438,0);put8(v.a.scriptStatus,2);
}
static void finish_requirements(void){v.recording=1;v.trace=tmpfile();assert(v.trace);v.mask=v.captured=(1u<<0)|(1u<<6)|(1u<<17);v.paletteMask=7;v.seenFaint=2;}
static void stale(unsigned src,unsigned n){put8(COUNT,1);put32(COPIES,src);put32(COPIES+4,0x06010000);put16(COPIES+8,n);}
#include "stop105-projection.h"
#include "native-scheduler.h"
static unsigned dispatch_events;
static void dispatch_continue(void){dispatch_events|=4;}
static void dispatch_end_trainer(void){dispatch_events|=2;SetMainCallback2(dispatch_continue);}
static void dispatch_return_battle(void){dispatch_events|=1;gMain.callback1=NULL;SetMainCallback2(dispatch_end_trainer);}
int main(void){
 gMain.callback1=dispatch_return_battle;gMain.callback2=NULL;gMain.state=99;CallCallbacks();
 assert(dispatch_events==3&&gMain.callback2==dispatch_continue&&gMain.state==0);
 CallCallbacks();assert(dispatch_events==7);
 puts("PASS verbatim native CallCallbacks/SetMainCallback2: CB1-selected saved trainer CB2 executes in the same iteration, wrapper remains for next iteration; zero emulator frames");
 stop105_projection();
 setup();v.a.firstTurn=0;assert(bv_begin(&v)==112); // Readiness phase must resolve from verified functions.
 setup();v.recording=1;v.trace=tmpfile();assert(v.trace&&bv_finish(&v)==110);fclose(v.trace); // Cannot finish without qualified native readiness.
 setup();bv_symbol(&v,0x08000301,'t',".gcc2_compiled.");assert(v.callbackCount==11&&!bv_callback(&v,0x08000301));bv_symbol(&v,0x08000101,'F',token);assert(v.callbackCount==11);
 pid_t pid=fork();assert(pid>=0);if(!pid){bv_symbol(&v,0x08000301,'F',token);exit(0);}int status;waitpid(pid,&status,0);assert(WIFEXITED(status)&&WEXITSTATUS(status)==112);
 setup();put32(SAVEPTR,0x0200e000);put32(SAVE2PTR,0x0201c000);v.trace=tmpfile();assert(v.trace);
 assert(!bv_trace(&core,&v,MONS,MONS,SAVEPTR,SAVE2PTR,MAIN,RESULTS,MOVE,MOVE,MOVE,MOVE,CTRL));
 rewind(v.trace);v.candidate=1;put8(MONS+170,23);
 assert(bv_trace(&core,&v,MONS,MONS,SAVEPTR,SAVE2PTR,MAIN,RESULTS,MOVE,MOVE,MOVE,MOVE,CTRL)==103);
 assert(v.failedTraceByte==170&&v.failedValuesPresent&&v.failedActual==23&&v.failedExpected==0&&v.failedActualRetained&&v.failedExpectedRetained);
 v.cpuAvailable=1;v.cpuPC=0x0806a54c;v.cpuLR=0x0806a54b;v.cpuSP=0x03007e00;v.cpuCPSR=0x3f;
 bv_diagnose(&core,&v,103,MONS,MAIN,MOVE);assert(!rename("visual-stop.json","party-diagnostic-fixture.json"));
 FILE *raw=fopen("visual-stop-actual-private.bin","rb");assert(raw);assert(!fseek(raw,170,SEEK_SET)&&fgetc(raw)==23);assert(!fseek(raw,0,SEEK_END)&&ftell(raw)==2560);fclose(raw);
 rewind(v.trace);put8(MONS+170,0);put8(0x0200e000+0x490+16,77);
 assert(bv_trace(&core,&v,MONS,MONS,SAVEPTR,SAVE2PTR,MAIN,RESULTS,MOVE,MOVE,MOVE,MOVE,CTRL)==103);
 assert(v.failedTraceByte==1268&&!v.failedValuesPresent);bv_diagnose(&core,&v,103,MONS,MAIN,MOVE);
 assert(!rename("visual-stop.json","resource-diagnostic-fixture.json"));
 rewind(v.trace);put8(0x0200e000+0x490+16,0);put8(MONS,99);
 assert(bv_trace(&core,&v,MONS,MONS,SAVEPTR,SAVE2PTR,MAIN,RESULTS,MOVE,MOVE,MOVE,MOVE,CTRL)==103);
 assert(v.failedTraceByte==0&&!v.failedValuesPresent);bv_diagnose(&core,&v,103,MONS,MAIN,MOVE);
 assert(!rename("visual-stop.json","header-diagnostic-fixture.json"));
 fclose(v.trace);v.trace=tmpfile();assert(v.trace);unsigned char shortReference[17]={0};
 assert(fwrite(shortReference,1,17,v.trace)==17);rewind(v.trace);
 assert(bv_trace(&core,&v,MONS,MONS,SAVEPTR,SAVE2PTR,MAIN,RESULTS,MOVE,MOVE,MOVE,MOVE,CTRL)==103);
 assert(v.failedExpectedBytes==17&&!v.failedValuesPresent);bv_diagnose(&core,&v,103,MONS,MAIN,MOVE);
 assert(!rename("visual-stop.json","truncated-diagnostic-fixture.json"));fclose(v.trace);
 puts("PASS actual observer mismatch diagnostics: exact actual/expected party bytes and local full failed records, safe CPU metadata, resource values redacted; no runtime authority inferred");
 setup();memset(vram,255,sizeof vram);assert(!sample()&&!v.enforced&&v.transitionFrames==1);put32(PHASE,v.a.firstTurn);assert(!sample()&&!v.enforced); // Unfilled VRAM in native first-turn phase never falsely becomes ready.
 setup();put32(PHASE,v.a.firstTurn);put32(SPRITES+12,0);assert(!sample()&&!v.enforced); // Trainer/reused64x64 slot is not a mon picture.
 setup();put32(PHASE,v.a.firstTurn);put16(SPRITES+50,52);assert(!sample()&&!v.enforced); // Native species ownership required.
 setup();put32(PHASE,v.a.firstTurn);put8(SPRITES+63,4);assert(!sample()&&!v.enforced); // Picture animation has not begun.
 setup();put32(PHASE,v.a.firstTurn);put8(COUNT,1);put32(COPIES+4,0x06010000);put16(COPIES+8,2048);assert(!sample()&&!v.enforced);put8(COUNT,0);assert(!sample()&&v.enforced&&v.readyFrame==1);
 setup();put32(PHASE,v.a.firstTurn);assert(!sample()&&v.enforced);vram[0]=255;assert(sample()==107&&v.failedActor==0&&v.failedSprite==0&&v.failedStage==4);bv_diagnose(&core,&v,107,MONS,MAIN,MOVE);
 setup();put32(PHASE,v.a.firstTurn);put8(BUFFER,255);vram[0]=255;assert(sample()==107&&v.enforced&&v.failedActor==0); // Completed native copy of invalid pixels still fails immediately.
 setup();put32(PHASE,v.a.firstTurn);assert(!sample()&&v.enforced);put32(SPRITES+12,0);assert(sample()==105&&v.failedActor==0); // Ownership remains mandatory after readiness.
 setup();put16(MOVE,356);assert(sample()==110&&!v.enforced); // No action allowed to slip past unqualified readiness.
 setup();put32(PHASE,0x08000400);assert(sample()==112&&v.failedAddress==0x08000400);
 setup();put32(SAVEPTR,0x0200e000);put32(SAVE2PTR,0x0201c000);put32(CTRL+8,0x08000401);assert(bv_trace(&core,&v,MONS,MONS,SAVEPTR,SAVE2PTR,MAIN,RESULTS,MOVE,MOVE,MOVE,MOVE,CTRL)==112&&v.failedActor==2&&v.failedAddress==0x08000400);
 setup();put8(COUNT,65);assert(sample()==113);

 // Pre-entry field frames, including a falsely populated old exit counter,
 // can never satisfy the postbattle proof. These are memory fixtures only.
 setup();put8(MAIN+0x439,0);put32(MAIN+4,v.a.fieldCB2);put8(v.a.scriptStatus,2);assert(!sample()&&v.lifecycle==BV_UNENTERED&&v.exitClean==0);
 finish_requirements();assert(bv_finish(&v)==110);fclose(v.trace);
 setup();put8(MAIN+0x439,0);v.candidate=1;put8(v.a.poseState+3,1);assert(sample()==105&&v.exitClean==0);
 active();v.exitClean=99;finish_requirements();assert(bv_finish(&v)==114);fclose(v.trace);
 // Graphics still live in a cleanup phase: ownership and pixels stay strict.
 active();put32(PHASE,v.a.freeReset);put32(SPRITES+12,0);assert(sample()==105&&v.failedStage==3);
 active();put32(PHASE,v.a.freeReset);vram[0]=255;assert(sample()==107);
 active();put32(PHASE,v.a.freeReset);assert(!sample()&&v.lifecycle==BV_ACTIVE);
 active();put32(SPRITES+68*3+12,0);assert(sample()==105&&v.failedActor==3);
 active();put32(v.a.gfx,GFX+4);assert(sample()==105&&v.failedStage==9);
 setup();put32(PHASE,v.a.firstTurn);put32(MAIN+8,0);assert(sample()==114&&!v.enforced);
 // Registry retirement is admissible only in the verified native cleanup path.
 active();put32(v.a.gfx,0);assert(sample()==114&&v.lifecycle==BV_ACTIVE);
 active();put32(v.a.gfx,0);put32(PHASE,0x0800ffff);assert(sample()==112);
 active();put32(PHASE,v.a.freeReset);put32(v.a.gfx,0);v.candidate=1;put8(v.a.poseState+9,1);assert(sample()==105&&v.failedStage==10);
 for(unsigned b=0;b<4;b++){
  active();put32(PHASE,v.a.freeReset);put32(v.a.gfx,0);stale(v.retainedBuffers[b],2048);assert(sample()==113&&v.failedActor==b&&v.failedStage==11);
  active();retire();stale(v.retainedBuffers[b]-1,2);assert(sample()==113&&v.failedStage==11);
 }
 active();retire();stale(v.retainedBuffers[0]-1,1);assert(!sample()); // Half-open boundary does not overlap.
 active();retire();stale(v.retainedBuffers[3]+8192,1);assert(!sample());
 active();retire();stale(0xffffffff,1);assert(!sample()); // No 32-bit wrap false positive.
 for(unsigned i=0;i<3;i++){active();retire();unsigned address=i==0?v.a.battleResources:i==1?v.a.battleStruct:v.a.battleSprites;put32(address,GFX);assert(sample()==105);}
 active();retire();put32(v.a.gfx,GFX);assert(sample()==105);
 active();retire();v.candidate=1;put8(v.a.poseState+15,1);assert(sample()==105);
 active();put32(MAIN+8,0);assert(sample()==114);
 active();retire();put32(MAIN+8,0);assert(sample()==114);
 active();retire();put32(PHASE,v.a.firstTurn);assert(sample()==114);
 active();retire();put32(PHASE,v.a.tryEvolve);assert(!sample());put32(PHASE,v.a.freeReset);assert(sample()==114);
 active();retire();put32(MAIN+4,0x0800ffff);assert(sample()==114); // Unknown callback while in battle is forbidden.
 active();put8(MAIN+0x439,0);put32(MAIN+4,v.a.endTrainer);assert(sample()==114); // No skipped retirement.
 active();retire();put8(MAIN+0x439,0);put32(PHASE,v.a.returnBattle);put32(MAIN+4,v.a.fieldCB2);assert(sample()==114); // No skipped native rebuild.
 active();retire();put8(MAIN+0x439,0);put32(PHASE,v.a.returnBattle);put32(MAIN+4,0x0800ffff);assert(sample()==112);
 active();retire();put8(MAIN+0x439,0);put32(PHASE,v.a.returnBattle);put32(MAIN+4,v.a.endTrainer);assert(!sample());put32(MAIN+4,v.a.continueScript);assert(!sample());put32(MAIN+4,v.a.returnLocal);put8(MAIN+0x438,3);assert(sample()==114); // No skipped local rebuild states.
 active();retire();return_path();put32(MAIN,0);assert(!sample()&&v.lifecycle==BV_RETIRING&&v.exitClean==0);finish_requirements();assert(bv_finish(&v)==114);fclose(v.trace);
 active();retire();return_path();put8(v.a.fieldLock,1);assert(!sample()&&v.exitClean==0);put8(v.a.fieldLock,0);put8(v.a.scriptStatus,1);assert(!sample()&&v.exitClean==0);
 put8(v.a.scriptStatus,2);put32(v.a.fieldHook,1);assert(!sample()&&v.exitClean==0);put32(v.a.fieldHook,0);put32(v.a.fieldHook2,1);assert(!sample()&&v.exitClean==0);
 put32(v.a.fieldHook2,0);put8(v.a.fade+7,128);assert(!sample()&&v.exitClean==0);put8(v.a.fade+7,127);
 put8(v.a.tasks+40*15+4,1);put32(v.a.tasks+40*15,v.a.waitFade|1);assert(!sample()&&v.exitClean==0);put8(v.a.tasks+40*15+4,0);
 assert(!sample()&&v.lifecycle==BV_FIELD&&v.exitClean==1&&v.fieldFrame>v.retirementFrame);finish_requirements();assert(!bv_finish(&v));
 put8(v.a.fieldLock,1);assert(sample()==114); // Field proof must remain valid through finish.
 active();put32(PHASE,v.a.tryEvolve);put32(v.a.gfx,0);assert(!sample()&&v.lifecycle==BV_RETIRING);
 active();v.candidate=1;retire();return_path();assert(!sample()&&v.lifecycle==BV_FIELD); // Candidate zeroed pose state.
 puts("PASS lifecycle fixtures: strict live cleanup, four owners, registry/pose retirement, all four retired source ranges and boundaries, verified cleanup/return callbacks, native rebuild order/completion, field callbacks/locks/scripts/hooks/fade/task readiness, pre-entry false exit and incomplete field finish; zero emulator frames");
 puts("PASS actual observer: send-out/unfilled VRAM, native phase and4 registered owners/first-copy completion, invalid pixels/ownership after readiness, action-before-readiness, unknown phase/controller, label filtering/duplicate identity, exact safe STOP diagnostics; zero emulator frames");
}
''')
    with (out/'observer-unit.log').open('w') as log:
        subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'scripts/floor1'),str(out/'cases.c'),'-o',str(out/'cases')],stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'cases')],cwd=out,stdout=log,stderr=subprocess.STDOUT,check=True)
    party_diag=json.loads((out/'party-diagnostic-fixture.json').read_text());resource_diag=json.loads((out/'resource-diagnostic-fixture.json').read_text())
    assert party_diag['failed_trace_byte']==170 and party_diag['actual_byte']==23 and party_diag['expected_byte']==0
    assert party_diag['local_actual_record_retained']==1 and party_diag['local_expected_record_retained']==1
    assert party_diag['CPU_available']==1 and party_diag['CPU_PC_raw']==0x0806a54c
    assert party_diag['serialization_authority']=='unresolved_no_deferral'
    assert resource_diag['failed_trace_byte']==1268 and resource_diag['mismatch_values_present']==0
    assert 'actual_byte' not in resource_diag and 'expected_byte' not in resource_diag
    for name in ['header','truncated']:
        d=json.loads((out/(name+'-diagnostic-fixture.json')).read_text())
        assert not d['mismatch_values_present'] and 'actual_byte' not in d and 'expected_byte' not in d
    assert json.loads((out/'truncated-diagnostic-fixture.json').read_text())['expected_record_bytes']==17

    diagnostic=json.loads((out/'visual-stop.json').read_text());assert diagnostic['failed_actor']==0 and diagnostic['stage']==4 and len(diagnostic['actors'])==4 and 'copy_queue' in diagnostic
    record=dict(STOP105_projection=dict(diagnostic_SHA256=hashlib.sha256((evidence/'native-stop-diagnostic.json').read_bytes()).hexdigest(),registry_NULL='modeled only; original runtime pointer not separately captured',resource_pointers_NULL='modeled only; original runtime did not separately serialize these pointers',original_runtime_result='STOP105 unchanged'),result='PASS',emulator_frames=0,native_layout='Pinned agbcc compile against actual native headers passed',symbols=native,coverage='Original readiness/symbol/ownership negatives plus ACTIVE to RETIRING to FIELD, four live owners, retired registry/pose state and queued source ranges, source-pinned saved trainer callback, same-iteration CB1 to CB2 dispatch, native callback/rebuild order, postbattle readiness, pre-entry false exit, incomplete field return')
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
if __name__=='__main__':main()
