/* Offline mechanism fixture: retained native Wait instructions, official video
 * callback bodies and installed mGBA IRQ/interpreter. No game, Save or reset.
 * Callback delay, instruction bus cost and IRQ service body are synthetic. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <mgba/gba/core.h>
#include <mgba/core/core.h>
#include <mgba/core/sync.h>
#include <mgba/internal/arm/isa-inlines.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/gba/dma.h>
#include <mgba/internal/gba/io.h>
static struct mCore *core;
static uint32_t code[1024];
static uint32_t (*load32)(struct ARMCore*,uint32_t,int*);
static void (*store16)(struct ARMCore*,uint32_t,int16_t,int*);
static unsigned clears,sets,entries,reads,exits,irqActive;
static unsigned regionSwitch,regionTarget;
static void trace(const char *event)
{
    struct GBA *g=core->board;struct ARMCore *c=core->cpu;
    const struct mTimingEvent *q=g->timing.root;
    printf("{\"event\":\"%s\",\"time\":%u,\"frame\":%u,\"nextPC\":%u,\"PCPhase\":\"%s\",\"rawPC\":%u,\"flag\":%u,\"IE\":%u,\"IF\":%u,\"IME\":%u,\"CPSR\":%u,\"nextEvent\":%d,\"queueRoot\":\"%s\",\"queueDue\":%u}\n",
        event,(unsigned)mTimingCurrentTime(&g->timing),g->video.frameCounter,
        regionSwitch?regionTarget:(unsigned)c->gprs[ARM_PC]-(c->executionMode==MODE_THUMB?2:4),
        regionSwitch?"selected-region-target-before-prefetch":"interpreter-observation",(unsigned)c->gprs[ARM_PC],
        ((uint16_t*)g->memory.iwram)[0x22dc/2],g->memory.io[REG_IE/2],
        g->memory.io[REG_IF/2],g->memory.io[REG_IME/2],c->cpsr.packed,
        c->nextEvent,q?q->name:"none",q?q->when:0);
}
static void region(struct ARMCore *c,uint32_t address)
{
    regionSwitch=1;regionTarget=address;
    if(address==0x18&&c->privilegeMode==MODE_IRQ){
        irqActive=1;
        trace("IRQ-entry");((struct GBA*)core->board)->memory.io[REG_IF/2]&=~1;
        trace("synthetic-dispatcher-IF-ack");
    }
    if(irqActive&&c->privilegeMode==MODE_SYSTEM){irqActive=0;trace("IRQ-return");}
    c->memory.activeRegion=code;c->memory.activeMask=4095;
    c->memory.activeSeqCycles32=c->memory.activeSeqCycles16=1;
    c->memory.activeNonseqCycles32=c->memory.activeNonseqCycles16=1;
    regionSwitch=0;
}
static uint32_t literal(struct ARMCore *c,uint32_t address,int *cycles)
{
    if(address>>24==8||address<4096){if(cycles)*cycles+=1;return code[(address&4095)/4];}
    return load32(c,address,cycles);
}
static void flagStore(struct ARMCore *c,uint32_t address,int16_t value,int *cycles)
{
    store16(c,address,value,cycles);
    if(address==0x030022dc){
        if(c->privilegeMode==MODE_IRQ){sets++;trace("IRQ-service-flag-set");}
        else{clears++;trace("Wait-flag-clear");}
    }
}
static void audit_hdraw(struct mTiming*,void*,uint32_t);
static void audit_hblank(struct mTiming*,void*,uint32_t);
static void raised(struct GBA *g,enum GBAIRQ irq,uint32_t late)
{GBARaiseIRQ(g,irq,late);if(irq==GBA_IRQ_VBLANK)trace("video-IRQ-raised-before-frame-increment");}
#define GBARaiseIRQ raised
#include "video_callbacks.h" /* Hash-checked official bodies, renamed only. */
#undef GBARaiseIRQ
static void audit_hdraw(struct mTiming *t,void *v,uint32_t late)
{
    unsigned before=((struct GBAVideo*)v)->frameCounter;
    audit_hdraw_body(t,v,late);
    if(((struct GBAVideo*)v)->frameCounter!=before)trace("video-frame-increment");
}
static void audit_hblank(struct mTiming *t,void *v,uint32_t late)
{audit_hblank_body(t,v,late);}
static void half(unsigned at,unsigned value){((uint16_t*)code)[at/2]=value;}
static void word(unsigned at,unsigned value){code[at/4]=value;}
static void run(const char *name,const char *waitFile,unsigned delay,unsigned deadline,unsigned mask)
{
    printf("{\"case\":\"%s\",\"syntheticPostCallbackNOPs\":%u,\"firstVideoDeadline\":%u,\"maskUntilClear\":%u}\n",name,delay,deadline,mask);
    core=GBACoreCreate();assert(core&&core->init(core));
    struct GBA *g=core->board;struct ARMCore *c=core->cpu;
    mTimingClear(&g->timing);memset(code,0,sizeof code);clears=sets=entries=reads=exits=irqActive=0;
    for(unsigned i=0;i<4096;i+=2)half(i,0x46c0);
    FILE *f=fopen(waitFile,"rb");assert(f);
    assert(fread((char*)code+0x8ac,1,48,f)==48&&fgetc(f)==EOF);fclose(f);
    /* Synthetic IRQ: preserve r0/r1, set native flag, restore IRQ CPSR/PC.
     * The production dispatcher and VBlank work are audited separately. */
    word(0x18,0xe92d0003);word(0x1c,0xe59f0020);
    word(0x20,0xe1d010b0);word(0x24,0xe3811001);
    word(0x28,0xe1c010b0);word(0x2c,0xe8bd0003);
    word(0x30,0xe25ef004);word(0x44,0x030022dc);
    half(0x100+2*delay,0x4720); /* BX r4 into full native Wait. */
    half(0x4be,0xe7b4); /* Retained AgbMain branch to ReadKeys call site. */
    half(0x42a,0x2601);half(0x42c,0x3701); /* Synthetic next iteration markers. */
    c->memory.setActiveRegion=region;region(c,0);
    load32=c->memory.load32;store16=c->memory.store16;
    c->memory.load32=literal;c->memory.store16=flagStore;
    ARMSetPrivilegeMode(c,MODE_IRQ);c->gprs[ARM_SP]=0x03007e00;
    ARMSetPrivilegeMode(c,MODE_SYSTEM);c->gprs[ARM_SP]=0x03007c00;
    c->executionMode=MODE_THUMB;c->cpsr.packed=0x3f|(mask?0x80:0);
    c->gprs[4]=0x080008ad;c->gprs[ARM_LR]=0x080004bf;
    c->gprs[ARM_PC]=0x08000100;ThumbWritePC(c);c->cycles=0;
    g->memory.io[REG_IE/2]=1;g->memory.io[REG_IME/2]=1;
    g->memory.io[REG_DISPSTAT/2]=8;g->video.vcount=159;
    g->video.event.callback=audit_hdraw;
    mTimingSchedule(&g->timing,&g->video.event,deadline);
    trace("synthetic-callback-complete");
    for(unsigned step=0;step<500000;step++){
        unsigned pc=(unsigned)c->gprs[ARM_PC]-(c->executionMode==MODE_THUMB?2:4);
        if(pc==0x080008ac&&c->executionMode==MODE_THUMB){entries++;trace("Wait-entry");}
        if(pc==0x080004be&&c->executionMode==MODE_THUMB){exits++;trace("Wait-exit");}
        if(pc==0x0800042a&&c->executionMode==MODE_THUMB){reads++;trace("next-native-ReadKeys-call-site");}
        if(pc==0x0800042e&&c->executionMode==MODE_THUMB){assert(c->gprs[6]==1&&c->gprs[7]==1);trace("next-synthetic-callback-iteration");break;}
        ARMRun(c);
        if(mask&&clears){mask=0;c->cpsr.i=0;GBATestIRQ(g,0);trace("synthetic-IRQ-unmask-after-clear");}
    }
    assert(entries==1&&clears==1&&reads==1&&exits==1);
    unsigned frames=g->video.frameCounter;
    assert(frames==(delay==120?2:1));
    printf("{\"result\":\"PASS\",\"framesBeforeNextIteration\":%u,\"WaitEntries\":%u,\"flagClears\":%u,\"IRQFlagSets\":%u,\"nextIterations\":%u}\n",frames,entries,clears,sets,reads);
    core->deinit(core);
}
static void queue(const char *name,unsigned late)
{
    core=GBACoreCreate();assert(core&&core->init(core));
    struct GBA *g=core->board;struct ARMCore *c=core->cpu;
    irqActive=0;memset(code,0,sizeof code);c->memory.setActiveRegion=region;region(c,0);
    ARMSetPrivilegeMode(c,MODE_SYSTEM);c->executionMode=MODE_THUMB;c->cpsr.packed=0x3f;
    c->gprs[ARM_PC]=0x08000100;ThumbWritePC(c);c->cycles=0;
    mTimingClear(&g->timing);g->memory.io[REG_IE/2]=1;g->memory.io[REG_IME/2]=1;
    g->memory.io[REG_DISPSTAT/2]=8;g->video.vcount=159;g->video.event.callback=audit_hdraw;
    mTimingSchedule(&g->timing,&g->video.event,100);
    printf("{\"case\":\"%s\",\"explicitTickLateness\":%u}\n",name,late);
    mTimingTick(&g->timing,100+late);trace("timing-drain-return");
    assert(g->video.frameCounter==1&&g->earlyExit);
    assert((c->privilegeMode==MODE_IRQ)==(late>=7));
    assert(mTimingIsScheduled(&g->timing,&g->irqEvent)==(late<7));
    puts("{\"result\":\"PASS\",\"nativeIRQBodyExecuted\":false}");core->deinit(core);
}
static void inert(struct mTiming *t,void *c,uint32_t late){(void)t;(void)c;(void)late;}
static void six(unsigned irq)
{
    core=GBACoreCreate();assert(core&&core->init(core));
    struct GBA *g=core->board;struct ARMCore *c=core->cpu;
    mTimingClear(&g->timing);c->cycles=0;c->nextEvent=INT_MAX;
    g->memory.io[REG_IE/2]=1;g->memory.io[REG_IME/2]=1;
    struct mTimingEvent other={.name="synthetic unrelated event",.callback=inert,.priority=3};
    if(irq)GBARaiseIRQ(g,GBA_IRQ_VBLANK,1);else mTimingSchedule(&g->timing,&other,6);
    puts(irq?"{\"case\":\"nextEvent6-IRQ\"}":"{\"case\":\"nextEvent6-unrelated\"}");
    trace("same-deadline-different-event-identity");assert(c->nextEvent==6);
    puts("{\"result\":\"PASS\"}");core->deinit(core);
}
int main(int argc,char **argv)
{
    assert(argc==2);setvbuf(stdout,NULL,_IONBF,0);
    run("clear-before-video",argv[1],0,300,0);
    run("video-before-Wait-pending-masked-IRQ",argv[1],40,50,1);
    run("serviced-flag-before-late-clear",argv[1],120,50,0);
    queue("punctual-frame-end-leaves-IRQ-pending",0);
    queue("late-frame-end-drains-IRQ-after-increment",8);
    six(1);six(0);
    return 0;
}
