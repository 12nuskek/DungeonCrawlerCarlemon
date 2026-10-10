/* Actual installed ARMRunLoop/ARMRun/GBA event/timing fixture, synthetic bytes
 * in an instruction memory region. No ROM/Save/game/reset/gameplay capture. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <mgba/gba/core.h>
#include <mgba/internal/arm/isa-inlines.h>
#ifdef BV_COMPLETE_SNAPSHOT_FIXTURE
#define main bv_gameplay_host_never_called
#include "observer.c" /* Compile generated host; its main is NEVER invoked. */
#undef main
#else
#include "v01-native-boundary-runtime.h"
#endif
struct Fixture {
    struct mCore *core;struct BvNativeRuntime runtime;
    struct mTimingEvent event;
    uint32_t code[1024];
    unsigned events,frameEvent,irqEvent,seen,mutate,order[64],late[64];
#ifdef BV_COMPLETE_SNAPSHOT_FIXTURE
    struct BattleVisual visual;
#endif
};
static struct Fixture *fixtures[2];
static struct Fixture *owner(struct ARMCore *cpu)
{for(unsigned i=0;i<2;i++)if(fixtures[i] && fixtures[i]->core->cpu==cpu)return fixtures[i];abort();}
static void region(struct ARMCore *cpu,uint32_t address)
{
    (void)address;struct Fixture *f=owner(cpu);cpu->memory.activeRegion=f->code;
    cpu->memory.activeMask=4095;cpu->memory.activeSeqCycles32=1;cpu->memory.activeSeqCycles16=1;
    cpu->memory.activeNonseqCycles32=1;cpu->memory.activeNonseqCycles16=1;
}
static void half(struct Fixture *f,unsigned at,unsigned value)
{((unsigned char *)f->code)[at]=value;((unsigned char *)f->code)[at+1]=value>>8;}
static void word(struct Fixture *f,unsigned at,unsigned value)
{for(unsigned i=0;i<4;i++)((unsigned char *)f->code)[at+i]=value>>(8*i);}
static void event(struct mTiming *timing,void *context,uint32_t late)
{
    struct Fixture *f=context;struct ARMCore *cpu=f->core->cpu;unsigned n=++f->events;
    assert(n<64);f->order[n]=f->core->frameCounter(f->core);f->late[n]=late;
    if(n==f->irqEvent)ARMRaiseIRQ(cpu);
    if(n%f->frameEvent==0)((struct GBA *)f->core->board)->video.frameCounter++;
    mTimingSchedule(timing,&f->event,11);
}
static unsigned snapshot(void *context,unsigned char data[2560])
{
    struct Fixture *f=context;f->seen++;memset(data,0,2560);
    /* Valid zero encrypted party; include synthetic registers in scalar domain.
     * Real host binds the COMPLETE native snapshot reader instead. */
#ifdef BV_COMPLETE_SNAPSHOT_FIXTURE
    unsigned reason=bv_snapshot(f->core,&f->visual,0x02000000,0x02000400,0x02000800,0x02000804,
        0x02000c00,0x02001200,0x02001300,0x02001304,0x02001308,0x0200130c,0x02002000,data);
    assert(!reason);
    assert(data[600]==0x31&&data[952]==0x42&&data[1252]==0x53&&data[2525]==7&&data[2526]==9);
#else
    const struct ARMCore *cpu=f->core->cpu;
    for(unsigned i=0;i<12;i++)bv_native_u32(data+2000+4*i,(unsigned)cpu->gprs[i]);
    bv_native_u32(data+2050,f->seen);
#endif
    if(f->mutate)data[f->mutate]=1;
    return 0;
}
static void init(struct Fixture *f,unsigned slot,unsigned kind,unsigned initiallyDue,unsigned frameEvent,unsigned irqEvent)
{
    memset(f,0,sizeof *f);fixtures[slot]=f;
    f->core=GBACoreCreate();assert(f->core&&f->core->init(f->core));
    struct ARMCore *cpu=f->core->cpu;struct GBA *gba=f->core->board;
#ifdef BV_COMPLETE_SNAPSHOT_FIXTURE
    /* Synthetic EWRAM fixture, not a game or Save. Complete installed bus API
     * snapshot reads every original domain through the production reader. */
    unsigned char *ram=(unsigned char *)gba->memory.wram;
    memset(ram,0,0x40000);
    bv_native_u32(ram+0x800,0x02010000);bv_native_u32(ram+0x804,0x02018000);
    ram[0x400]=0x31;ram[0x10000+0x1270]=0x42;
    ram[0x10000+0x490]=0x53;ram[0x1200+0x13]=7;ram[0x1300]=9;
#endif
    mTimingClear(&gba->timing);f->frameEvent=frameEvent;f->irqEvent=irqEvent;
    cpu->memory.setActiveRegion=region;region(cpu,0);
    cpu->cycles=0;cpu->nextEvent=0;cpu->privilegeMode=MODE_SYSTEM;cpu->executionMode=MODE_THUMB;cpu->cpsr.packed=0x3f;
    cpu->gprs[ARM_SP]=0x02003000;cpu->gprs[ARM_LR]=0x080004bf;
    for(unsigned i=0;i<sizeof f->code;i+=2)half(f,i,0x46c0); // Thumb nop.
    if(kind==0){ // Thumb arithmetic loop, no boundary.
        half(f,0x80,0x3001);half(f,0x82,0xe7fd);
    }else if(kind==1){ // Thumb -> ARM -> Thumb, actual BX scheduling.
        half(f,0x80,0x3001);half(f,0x82,0x4708);cpu->gprs[1]=0x08000100;
        word(f,0x100,0xe2800001);word(f,0x104,0xe12fff12);cpu->gprs[2]=0x08000181;
        half(f,0x180,0x3001);half(f,0x182,0x4708);
    }else{ // Complete-boundary entry push/return followed by a native-shaped loop.
        half(f,0x80,0x4720);cpu->gprs[4]=0x080008ad;
        half(f,0x8ac,0xb500);half(f,0x8ae,0xbd00); // push {lr}; pop {pc}.
        half(f,0x4be,0x3001);half(f,0x4c0,0x4720);
    }
    // IRQ vector: actual MSR to SYSTEM still retains ARM execution; then return
    // through BX to Thumb main. Thus SYSTEM alone never qualifies authority.
    word(f,0x18,0xe321f01f);word(f,0x1c,0xe12fff15);cpu->gprs[5]=0x08000081;
    cpu->gprs[ARM_PC]=0x08000080;ThumbWritePC(cpu);
    cpu->cycles=0;f->event=(struct mTimingEvent){.context=f,.callback=event,.name="synthetic frame/IRQ"};
    mTimingSchedule(&gba->timing,&f->event,initiallyDue?0:11);
}
static void original(struct Fixture *f)
{f->core->runFrame(f->core);}
static void equal(struct Fixture *a,struct Fixture *b)
{
    const struct ARMCore *x=a->core->cpu,*y=b->core->cpu;
    assert(!memcmp(&x->regs,&y->regs,sizeof x->regs));assert(!memcmp(x->bankedRegisters,y->bankedRegisters,sizeof x->bankedRegisters));
    assert(!memcmp(x->bankedSPSRs,y->bankedSPSRs,sizeof x->bankedSPSRs));assert(!memcmp(x->prefetch,y->prefetch,sizeof x->prefetch));
    assert(x->cycles==y->cycles&&x->nextEvent==y->nextEvent&&x->halted==y->halted);
    assert(x->executionMode==y->executionMode&&x->privilegeMode==y->privilegeMode);
    assert(x->shifterOperand==y->shifterOperand&&x->shifterCarryOut==y->shifterCarryOut);
    assert(a->events==b->events&&!memcmp(a->order,b->order,sizeof a->order)&&!memcmp(a->late,b->late,sizeof a->late));
    const struct GBA *ga=a->core->board,*gb=b->core->board;
    assert(mTimingCurrentTime(&ga->timing)==mTimingCurrentTime(&gb->timing));
    assert(ga->timing.globalCycles==gb->timing.globalCycles&&ga->bus==gb->bus);
    assert(a->core->frameCounter(a->core)==b->core->frameCounter(b->core));assert(a->core->getKeys(a->core)==b->core->getKeys(b->core));
    assert(!memcmp(ga->memory.wram,gb->memory.wram,0x40000));assert(!memcmp(ga->memory.iwram,gb->memory.iwram,0x8000));
}
static void attach(struct Fixture *f)
{assert(!bv_native_attach(&f->runtime,f->core,0x080008ac,0x080004bf,f,snapshot));}
static void closeFixture(struct Fixture *f)
{if(f->core->debugger)f->core->detachDebugger(f->core);f->core->deinit(f->core);}
int main(void)
{
    setvbuf(stdout,NULL,_IONBF,0);unsigned cases=0;
    for(unsigned kind=0;kind<3;kind++)for(unsigned due=0;due<2;due++)for(unsigned irq=0;irq<2;irq++){
        struct Fixture a,b;init(&a,0,kind,due,5,irq?2:0);init(&b,1,kind,due,5,irq?2:0);attach(&b);
        FILE *stream=tmpfile();assert(stream);original(&a);assert(!bv_native_frame(&b.runtime,1,0,stream,0));equal(&a,&b);
        assert(a.events==5&&a.core->frameCounter(a.core)==1);cases++;
        closeFixture(&a);closeFixture(&b);fclose(stream);
    }
    printf("PASS actual installed interpreter/event parity: %u cases; Thumb arithmetic, ARM/Thumb BX, due event, ARMRaiseIRQ, MSR IRQ-to-SYSTEM, banked registers, CPSR/SPSR/prefetch/cycles/nextEvent/RAM/input/time/event order/lateness/frame exact; no instruction after frame end\n",cases);
    // Due frame-ending event at entry: zero instructions, identical interpreter
    // and GBA scheduler state. Standard event-first step would cross this stop.
    {struct Fixture a,b;init(&a,0,1,1,1,0);init(&b,1,1,1,1,0);attach(&b);
     original(&a);assert(!bv_native_frame(&b.runtime,0,0,NULL,0));equal(&a,&b);
     assert(((struct ARMCore *)b.core->cpu)->gprs[ARM_PC]==0x08000082);
     closeFixture(&a);closeFixture(&b);}
    puts("PASS actual due frame-end event: zero instructions after event at entry, exact original CPU/event/frame state");
    {struct Fixture a,b;init(&a,0,1,0,5,2);init(&b,1,1,0,5,2);attach(&b);
     const unsigned keys[]={0,128,0,1,0,0,64,0};
     for(unsigned i=0;i<8;i++){a.core->setKeys(a.core,keys[i]);b.core->setKeys(b.core,keys[i]);original(&a);
       assert(!bv_native_frame(&b.runtime,0,0,NULL,i));equal(&a,&b);assert(b.runtime.inputEpoch==i+1);}
     closeFixture(&a);closeFixture(&b);}
    puts("PASS actual eight-frame fixed input cadence: all original interpreter/video/event/key states exact, no hidden setKeys or post-frame step");
    {struct Fixture a,b;init(&a,0,0,0,63,0);init(&b,1,0,0,63,0);attach(&b);
     struct GBA *ga=a.core->board,*gb=b.core->board;
     mTimingDeschedule(&ga->timing,&a.event);mTimingDeschedule(&gb->timing,&b.event);
     mTimingSchedule(&ga->timing,&a.event,VIDEO_TOTAL_LENGTH+VIDEO_HORIZONTAL_LENGTH+10);
     mTimingSchedule(&gb->timing,&b.event,VIDEO_TOTAL_LENGTH+VIDEO_HORIZONTAL_LENGTH+10);
     original(&a);assert(bv_native_frame(&b.runtime,0,0,NULL,0)==118);equal(&a,&b);
     assert(a.events==1&&a.core->frameCounter(a.core)==0);closeFixture(&a);closeFixture(&b);}
    puts("PASS actual original batch timeout: identical long interpreter batch/event/time/CPU state, no frame fabricated, binding stops118");
    // Record real installed-interpreter boundary stream, match all boundaries,
    // frame counts (including zero), input epochs and typed finish trailer.
    struct Fixture a,b;init(&a,0,2,0,8,0);init(&b,1,2,0,8,0);attach(&a);attach(&b);
    FILE *stream=tmpfile();assert(stream);assert(!bv_native_frame(&a.runtime,1,0,stream,0));
    assert(a.seen>1&&a.runtime.lastCount==a.seen);assert(!bv_native_finish(&a.runtime));rewind(stream);
    assert(!bv_native_frame(&b.runtime,1,1,stream,0));assert(!bv_native_finish(&b.runtime));assert(fgetc(stream)==EOF);equal(&a,&b);
    printf("PASS actual hardware boundary sequence: %u complete snapshots, exact ordinal/frame/input/key/count/trailer; no CPU writes by observation\n",a.seen);
    closeFixture(&a);closeFixture(&b);fclose(stream);
    // Zero-boundary frame must still have a compared F record, and cannot grant
    // a checkpoint. Removing it/missing a boundary cannot silently align later.
    init(&a,0,0,1,1,0);attach(&a);stream=tmpfile();assert(!bv_native_frame(&a.runtime,1,0,stream,0));
    assert(a.seen==0&&a.runtime.lastCount==0&&ftell(stream)==29&&bv_native_checkpoint(&a.runtime)==115);closeFixture(&a);fclose(stream);
    // First full-record mutation stops BEFORE executing the entry push.
    init(&a,0,2,0,8,0);attach(&a);stream=tmpfile();assert(!bv_native_frame(&a.runtime,1,0,stream,0));rewind(stream);
    init(&b,1,2,0,8,0);attach(&b);b.mutate=900;
    assert(bv_native_frame(&b.runtime,1,1,stream,0)==103);assert(b.runtime.sequence.ordinal==0);
    assert(((struct ARMCore *)b.core->cpu)->gprs[ARM_PC]==0x080008ae);assert(b.events<a.events);
    assert(bv_native_frame(&b.runtime,1,1,stream,0)==103);assert(b.seen==1);
    closeFixture(&a);closeFixture(&b);fclose(stream);
    // Exact entry with foreign LR is unqualified even in Thumb SYSTEM mode.
    init(&a,0,2,0,8,0);attach(&a);((struct ARMCore *)a.core->cpu)->gprs[ARM_LR]=0x03000001;
    stream=tmpfile();assert(bv_native_frame(&a.runtime,1,0,stream,0)==115&&a.seen==0);closeFixture(&a);fclose(stream);
    // Corrupt EACH metadata byte independently. This exercises type, 64-bit
    // ordinal, video/input epoch, count, absolute frame and key checks on the
    // actual installed hardware path, with no accepted boundary advancement.
    unsigned metadataCases=0;
    for(unsigned i=0;i<29;i++){
      init(&a,0,2,0,8,0);attach(&a);stream=tmpfile();assert(!bv_native_frame(&a.runtime,1,0,stream,0));
      assert(!fseek(stream,i,SEEK_SET));int byte=fgetc(stream);assert(byte!=EOF);assert(!fseek(stream,i,SEEK_SET));fputc(byte^1,stream);rewind(stream);
      init(&b,1,2,0,8,0);attach(&b);assert(bv_native_frame(&b.runtime,1,1,stream,0)==117);
      assert(b.seen==0&&b.runtime.sequence.ordinal==0&&((struct ARMCore *)b.core->cpu)->gprs[ARM_PC]==0x080008ae);
      closeFixture(&a);closeFixture(&b);fclose(stream);metadataCases++;
    }
    printf("PASS actual hardware stream metadata negatives: %u independent byte corruptions, no accepted ordinal/instruction advancement\n",metadataCases);
    // Mutate each complete snapshot byte in the reference independently;
    // every domain, padding and encrypted party representation stays strict.
    init(&a,0,2,0,8,0);attach(&a);stream=tmpfile();assert(!bv_native_frame(&a.runtime,1,0,stream,0));
    unsigned byteCases=0;
    for(unsigned i=0;i<2560;i++){
      assert(!fseek(stream,29+i,SEEK_SET));int byte=fgetc(stream);assert(byte!=EOF);
      assert(!fseek(stream,29+i,SEEK_SET));fputc(byte^1,stream);rewind(stream);
      init(&b,1,2,0,8,0);attach(&b);assert(bv_native_frame(&b.runtime,1,1,stream,0)==103);
      assert(b.runtime.sequence.ordinal==0&&b.seen==1&&((struct ARMCore *)b.core->cpu)->gprs[ARM_PC]==0x080008ae);
      closeFixture(&b);assert(!fseek(stream,29+i,SEEK_SET));fputc(byte,stream);rewind(stream);byteCases++;
    }
    closeFixture(&a);fclose(stream);printf("PASS actual hardware full-record negatives: every %u byte position rejected before entry instruction; zero masks\n",byteCases);
    // Missing/reordered/duplicated boundaries, missing frame count, corrupt
    // completed-frame metadata, and trailing data cannot silently align.
    init(&a,0,2,0,8,0);attach(&a);stream=tmpfile();assert(!bv_native_frame(&a.runtime,1,0,stream,0));assert(!bv_native_finish(&a.runtime));
    long length=ftell(stream);assert(length>2*2589&&length<20000);unsigned char saved[20000];rewind(stream);
    assert(fread(saved,1,length,stream)==(size_t)length);fclose(stream);closeFixture(&a);
    for(unsigned kind=0;kind<6;kind++){
      stream=tmpfile();assert(stream);
      if(kind==0){assert(fwrite(saved+2589,1,length-2589,stream)==(size_t)length-2589);} // missing first boundary
      if(kind==1){assert(fwrite(saved,1,2589,stream)==2589);assert(fwrite(saved,1,length,stream)==(size_t)length);} // duplicate
      if(kind==2){assert(fwrite(saved+2589,1,2589,stream)==2589);assert(fwrite(saved,1,2589,stream)==2589);assert(fwrite(saved+5178,1,length-5178,stream)==(size_t)length-5178);} // reorder
      if(kind==3){assert(fwrite(saved,1,length-58,stream)==(size_t)length-58);assert(fwrite(saved+length-29,1,29,stream)==29);} // missing F
      if(kind==4){saved[length-58+17]^=1;assert(fwrite(saved,1,length,stream)==(size_t)length);saved[length-58+17]^=1;} // wrong F count
      if(kind==5){assert(fwrite(saved,1,length,stream)==(size_t)length);fputc('X',stream);} // trailing
      rewind(stream);init(&b,1,2,0,8,0);attach(&b);unsigned reason=bv_native_frame(&b.runtime,1,1,stream,0);
      if(kind==5){assert(!reason);reason=bv_native_finish(&b.runtime);}assert(reason==117);
      closeFixture(&b);fclose(stream);
    }
    puts("PASS actual stream ordering/end negatives: missing/duplicate/reordered boundary, missing frame-count record, wrong completed-frame count, trailing finish data");
    init(&a,0,2,0,8,0);attach(&a);stream=tmpfile();assert(!bv_native_frame(&a.runtime,1,0,stream,0));assert(!bv_native_checkpoint(&a.runtime));
    struct GBA *ga=a.core->board;mTimingDeschedule(&ga->timing,&a.event);a.frameEvent=1;mTimingSchedule(&ga->timing,&a.event,0);
    assert(!bv_native_frame(&a.runtime,1,0,stream,1));assert(a.runtime.lastCount==0&&bv_native_checkpoint(&a.runtime)==115);
    closeFixture(&a);fclose(stream);puts("PASS actual stale-checkpoint rejection after a zero-boundary frame; no stepping to refresh authority");
    // Both invalid checksum and BadEgg stop the baseline too; two equal invalid
    // records cannot pass merely because their bytes match.
    const unsigned invalid[]={19,32};
    for(unsigned i=0;i<2;i++){
      init(&a,0,2,0,8,0);attach(&a);a.mutate=invalid[i];stream=tmpfile();
      assert(bv_native_frame(&a.runtime,1,0,stream,0)==116&&a.runtime.sequence.ordinal==0);
      assert(((struct ARMCore *)a.core->cpu)->gprs[ARM_PC]==0x080008ae);closeFixture(&a);fclose(stream);
    }
    // Truncated snapshot cannot become an implicit zero-padded accepted record.
    init(&a,0,2,0,8,0);attach(&a);stream=tmpfile();assert(!bv_native_frame(&a.runtime,1,0,stream,0));
    assert(!fflush(stream));assert(!ftruncate(fileno(stream),29+17));rewind(stream);init(&b,1,2,0,8,0);attach(&b);
    assert(bv_native_frame(&b.runtime,1,1,stream,0)==103&&b.runtime.expectedBytes==17&&b.runtime.sequence.ordinal==0);
    closeFixture(&a);closeFixture(&b);fclose(stream);
    // An actual IRQ callback enters SYSTEM and branches to this entry, but its
    // caller is foreign: do not authorise it based on mode/PC alone.
    init(&a,0,0,0,8,1);attach(&a);word(&a,0x1c,0xe1a0e006);word(&a,0x20,0xe12fff14);
    ((struct ARMCore *)a.core->cpu)->gprs[4]=0x080008ad;((struct ARMCore *)a.core->cpu)->gprs[6]=0x03000001;
    stream=tmpfile();assert(bv_native_frame(&a.runtime,1,0,stream,0)==115&&a.seen==0);
    assert(((struct ARMCore *)a.core->cpu)->privilegeMode==MODE_SYSTEM);closeFixture(&a);fclose(stream);
    puts("PASS actual stream/native integrity negatives: BadEgg, equal invalid checksum, truncated full snapshot, actual IRQ-to-SYSTEM foreign caller rejected");
#ifdef BV_COMPLETE_SNAPSHOT_FIXTURE
    puts("PASS production complete snapshot reader at installed hardware entry: native bus APIs read all 2560 bytes, all domains/padding retained, exact callback identity checks; generated gameplay host compiled/NEVER invoked");
#endif
    puts("PASS actual interpreter negative cases: zero-count frame/fresh checkpoint rejection, full-record mutation STOP before entry instruction, sticky first STOP/no retry, foreign caller in SYSTEM rejected; no ROMs/Saves/gameplay/new execution claims");
    return 0;
}
