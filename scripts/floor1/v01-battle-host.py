"""Frozen native fortify controller plus read-only graphics/state observations."""
from pathlib import Path
import hashlib,importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    def module(name,path):
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    code,base=module('battle_visual_prior',ROOT/'scripts/floor1/warden-fairness-host.py').generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='b2030b4da242f14d9993cbb00493dd9bb02c746fc12ce75cd994b11b760f0c71'
    replace=module('battle_visual_replace',ROOT/'scripts/floor1/recovery-host.py').replace_once
    addition=(ROOT/'scripts/floor1/v01-native-boundary-adapter.h').read_text()+'\n'+(ROOT/'scripts/floor1/v01-native-boundary-diagnostics.h').read_text()+'\n'+(ROOT/'scripts/floor1/v01-native-timeline.h').read_text()+'\n'+(ROOT/'scripts/floor1/v01-native-boundary-runtime.h').read_text().replace('#include "v01-native-boundary-adapter.h"','').replace('#include "v01-native-boundary-diagnostics.h"','').replace('#include "v01-native-timeline.h"','')+'\n'+(ROOT/'scripts/floor1/party-resource-canonical.h').read_text()+'\n'+(ROOT/'scripts/floor1/v01-battle-observer.h').read_text()
    code=replace(code,'int main(int argc, char **argv)',addition+r'''
struct BvSnapshotContext {struct mCore *core;struct BattleVisual *visual;unsigned party,mons,saveptr,save2ptr,mainstate,results,currentMove,attacker,defender,outcome,controls;};
static unsigned bv_native_snapshot_reader(void *context,unsigned char data[2560])
{struct BvSnapshotContext *c=context;return bv_snapshot(c->core,c->visual,c->party,c->mons,c->saveptr,c->save2ptr,c->mainstate,c->results,c->currentMove,c->attacker,c->defender,c->outcome,c->controls,data);}
int main(int argc, char **argv)''' )
    code=replace(code,'    FILE *symbols=fopen(argv[3], "r");','    struct BattleVisual visual={0};struct BvNativeRuntime native={0};unsigned nativeEntry=0,nativeCaller=0,nativeOpcode=0;\n    FILE *symbols=fopen(argv[3], "r");')
    code=replace(code,'    struct BattleVisual visual={0};','    struct BvTimeline timeline={0};struct BvTimelineConfig timelineConfig={0};\n    struct BattleVisual visual={0};')
    fields={'gSprites':'sprites','gBattlerSpriteIds':'ids','gHealthboxSpriteIds':'healthboxes','sSpriteTileAllocBitmap':'tiles','sSpritePaletteTags':'palettes','sHeapStart':'heapStart','sHeapSize':'heapSize','sDccBattlePoses':'poseState','gPlttBufferUnfaded':'unfaded','gMonSpritesGfxPtr':'gfx','bv_fieldCB2':'fieldCB2','bv_battleCB2':'battleCB2','gBattleMainFunc':'phase','bv_firstTurn':'firstTurn','gBattlerPositions':'positions','sSpriteCopyRequestCount':'copyCount','sSpriteCopyRequests':'copies','sShouldProcessSpriteCopyRequests':'copyArmed','bv_freeReset':'freeReset','bv_tryEvolve':'tryEvolve','bv_returnBattle':'returnBattle','bv_endTrainer':'endTrainer','bv_continueScript':'continueScript','bv_returnLocal':'returnLocal','bv_fieldCB1':'fieldCB1','gFieldCallback':'fieldHook','gFieldCallback2':'fieldHook2','sLockFieldControls':'fieldLock','sGlobalScriptContextStatus':'scriptStatus','gPaletteFade':'fade','gTasks':'tasks','gBattleResources':'battleResources','gBattleStruct':'battleStruct','gBattleSpritesDataPtr':'battleSprites','bv_waitFade':'waitFade'}
    point='        if (!strcmp(symbol,"gTasks")) tasks=addr;'
    code=replace(code,point,point+'\n'+''.join(f'        if (!strcmp(symbol,"{name}")) visual.a.{field}=addr;\n' for name,field in fields.items()))
    code=replace(code,'    fclose(symbols);','    fclose(symbols);\n    if(nativeEntry!=0x080008ac || nativeCaller!=0x080004bf || nativeOpcode!=0xb500)return 115;')
    point='    while (fscanf(symbols, "%x %c %127s", &addr, &type, symbol)==3) {'
    code=replace(code,point,point+'\n        bv_symbol(&visual,addr,type,symbol);\n        if(!strcmp(symbol,"bv_nativeEntry"))nativeEntry=addr;\n        if(!strcmp(symbol,"bv_nativeCaller"))nativeCaller=addr;\n        if(!strcmp(symbol,"bv_nativeOpcode"))nativeOpcode=addr;')
    code=replace(code,point,point+'\n        bv_tl_symbol(&timelineConfig,addr,symbol);')
    code=replace(code,'    core->reset(core);','    core->reset(core);\n    struct BvSnapshotContext snapshot={core,&visual,party,mons,saveptr,save2ptr,mainstate,results,currentMove,attacker,defender,outcome,controls};\n    if(core->busRead16(core,nativeEntry)!=nativeOpcode || bv_native_attach(&native,core,nativeEntry,nativeCaller,&snapshot,bv_native_snapshot_reader))return 115;')
    point='    if(core->busRead16(core,nativeEntry)!=nativeOpcode || bv_native_attach(&native,core,nativeEntry,nativeCaller,&snapshot,bv_native_snapshot_reader))return 115;'
    code=replace(code,point,point+'\n    if(bv_tl_open(&timeline,core,&timelineConfig,"native-timeline-private.bin"))return 119;\n    native.timeline=&timeline;')
    point='    core->runFrame(core); \\\n'
    code=replace(code,point,r'''    if(visual.recording && visual.frames>=36000)exit(109); \
    unsigned vr=bv_native_frame(&native,visual.recording,visual.candidate,visual.trace,visual.frames); \
    if(visual.recording){ \
        const struct ARMCore *cpu=core->cpu; \
        visual.cpuAvailable=cpu!=NULL; \
        if(cpu){visual.cpuPC=(unsigned)cpu->gprs[ARM_PC];visual.cpuLR=(unsigned)cpu->gprs[ARM_LR];visual.cpuSP=(unsigned)cpu->gprs[ARM_SP];visual.cpuCPSR=(unsigned)cpu->cpsr.packed;} \
        if(vr==103)bv_snapshot_mismatch(core,&visual,native.actual,native.expected,native.expectedBytes); \
        if(!vr)vr=bv_sample(core,&visual,mainstate,mons,results,animationActive,animationActor,currentMove,pixels,width,height); \
        if(vr){bv_native_retain_failure(&native);bv_diagnose(core,&visual,vr,mons,mainstate,currentMove);capture("visual-stop.ppm",pixels,width,height);fprintf(stderr,"Battle visual stop reason=%u frame=%u; no further frames\n",vr,visual.frames);printf("result=%u assertions=%u\n",vr,checks);exit(vr);} \
        visual.frames++; \
    }else if(vr){bv_native_retain_failure(&native);fprintf(stderr,"Native frame stop=%u; no further instructions\n",vr);exit(vr);} \
''')
    point='        if (!strcmp(line,"quit\\n")) break;'
    code=replace(code,point,point+r'''
        if(!strcmp(line,"visual input-exact\n")){
            unsigned sb=core->busRead32(core,saveptr),context=core->busRead32(core,core->busRead32(core,save2ptr)+0xAC);
            unsigned char expected[600],actual[600],ef[300],af[300],eo[1272],ao[1272],ec[4],counter[2];
            if(!fieldLock || !fieldCallback || !scriptStatus || core->busRead8(core,fieldLock) || core->busRead8(core,scriptStatus)!=2
                || (core->busRead32(core,mainstate+4)&~1u)!=(fieldCallback&~1u) || (core->busRead8(core,mainstate+0x439)&2)
                || core->busRead8(core,count)!=2 || core->busRead8(core,sb+0x234)!=2){result=111;break;}
            for(unsigned i=0;i<600;i++)actual[i]=core->busRead8(core,party+i);
            for(unsigned i=0;i<300;i++)af[i]=core->busRead8(core,sb+0x1270+i);
            for(unsigned i=0;i<1272;i++)ao[i]=core->busRead8(core,sb+0x490+i);
            if(bv_load("expected-party.bin",expected,600)||bv_load("expected-flags.bin",ef,300)||bv_load("expected-owned.bin",eo,1272)
                ||bv_load("expected-context.bin",ec,4)||bv_load("expected-counter.bin",counter,2)
                ||memcmp(actual,expected,600)||memcmp(af,ef,300)||!resource_equal(eo,resource_word(ec),ao,context)
                ||core->busRead16(core,sb+0x13f0)!=(unsigned)(counter[0]|counter[1]<<8)){result=111;break;}
            checks+=4;printf("PASS retained ordinary input exact600 party/count300 flags1272 logical resources/counter; native field ready\n");continue;
        }
        if(!strcmp(line,"visual start\n")){unsigned vr=bv_begin(&visual);if(vr){result=vr;break;}checks++;continue;}
        if(!strcmp(line,"visual ready\n")){
            unsigned boundary=bv_native_checkpoint(&native);if(boundary){result=boundary;break;}
            if(!visual.recording || !(core->busRead8(core,mainstate+0x439)&2) || core->busRead8(core,results+0x13)!=0){result=110;break;}
            visual.readyRequested=1;checks++;continue;
        }
        if(!strcmp(line,"visual finish\n")){unsigned vr=bv_native_finish(&native);if(!vr)vr=bv_finish(&visual);if(vr){bv_native_retain_failure(&native);result=vr;break;}checks+=8;continue;}
''')
    assert code.count('bv_native_frame(&native,')==1 and code.count('core->runFrame(core);')==0 and 'busWrite' not in code
    code=replace(code,'    mCoreConfigDeinit(&core->config);','    unsigned timelineResult=bv_tl_close(&timeline);if(!result)result=timelineResult;\n    mCoreConfigDeinit(&core->config);')
    return code,base
