"""Focused actual-observer/native-layout/symbol negatives; no emulator execution."""
from pathlib import Path
import argparse,importlib.util,json,subprocess
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
        assert any('L:battle_main.o:HandleTurnActionSelectionState' in r['aliases'] for r in verified)
        (out/(name+'-verified-functions.json')).write_text(json.dumps(verified,indent=2)+'\n')
    # Pinned 32-bit agbcc, actual native headers; compile-only, no ROM relink.
    engine=ROOT/'artifacts/floor1/v01-battle/build-headers/source/engine'
    cpp=['gcc','-E','-I'+str(engine/'include'),'-I'+str(engine/'gflib'),'-I'+str(engine),'-I'+str(engine/'tools/agbcc/include'),'-I'+str(engine/'tools/agbcc'),'-DMODERN=0','-nostdinc','-undef','-std=gnu89',str(ROOT/'scripts/floor1/v01-battle-layout.c')]
    with (out/'native-layout.i').open('w') as f:subprocess.run(cpp,stdout=f,check=True)
    with (out/'native-layout.log').open('w') as f:subprocess.run([str(engine/'tools/agbcc/bin/agbcc'),'-O2','-mthumb-interwork','-Werror','-o',str(out/'native-layout.s'),str(out/'native-layout.i')],stdout=f,stderr=subprocess.STDOUT,check=True)
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
 put32(MAIN+4,v.a.battleCB2);put8(MAIN+0x439,2);put32(PHASE,v.a.battleCB2);put32(v.a.gfx,GFX);put32(GFX,BUFFER);put32(v.a.heapStart,0x02020000);put32(v.a.heapSize,0x1c000);put16(0x02020002,0xa3a3);put32(0x02020004,0x1c000-16);put32(0x0202000c,0x02020000);
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
int main(void){
 setup();v.a.firstTurn=0;assert(bv_begin(&v)==112); // Readiness phase must resolve from verified functions.
 setup();v.recording=1;v.trace=tmpfile();assert(v.trace&&bv_finish(&v)==110);fclose(v.trace); // Cannot finish without qualified native readiness.
 setup();bv_symbol(&v,0x08000301,'t',".gcc2_compiled.");assert(v.callbackCount==2&&!bv_callback(&v,0x08000301));bv_symbol(&v,0x08000101,'F',token);assert(v.callbackCount==2);
 pid_t pid=fork();assert(pid>=0);if(!pid){bv_symbol(&v,0x08000301,'F',token);exit(0);}int status;waitpid(pid,&status,0);assert(WIFEXITED(status)&&WEXITSTATUS(status)==112);
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
 puts("PASS actual observer: send-out/unfilled VRAM, native phase and4 registered owners/first-copy completion, invalid pixels/ownership after readiness, action-before-readiness, unknown phase/controller, label filtering/duplicate identity, exact safe STOP diagnostics; zero emulator frames");
}
''')
    with (out/'observer-unit.log').open('w') as log:
        subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'scripts/floor1'),str(out/'cases.c'),'-o',str(out/'cases')],stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'cases')],cwd=out,stdout=log,stderr=subprocess.STDOUT,check=True)
    diagnostic=json.loads((out/'visual-stop.json').read_text());assert diagnostic['failed_actor']==0 and diagnostic['stage']==4 and len(diagnostic['actors'])==4 and 'copy_queue' in diagnostic
    record=dict(result='PASS',emulator_frames=0,native_layout='Pinned agbcc compile against actual native headers passed',symbols=native,coverage='send-out/unfilled VRAM, ownership/readiness/copy completion, invalid pixels after readiness, label filtering/alias order/unresolved/ambiguous identities, unknown callbacks, exact actor/sprite/phase/copy diagnostics')
    (out/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
if __name__=='__main__':main()
