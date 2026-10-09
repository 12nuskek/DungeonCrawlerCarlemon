/* Concrete mGBA 0.10.5 interpreter binding. No game equivalence claim. */
#ifndef V01_NATIVE_BOUNDARY_RUNTIME_H
#define V01_NATIVE_BOUNDARY_RUNTIME_H
#include <stddef.h>
#include <stdio.h>
#include <mgba/core/core.h>
#include <mgba/core/timing.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/arm/debugger/debugger.h>
#include "v01-native-boundary-adapter.h"
struct BvNativeRuntime {
    struct mDebugger debugger; /* First member: passive hook owns this instance. */
    struct mCore *core;
    struct BvBoundaryAuthority authority;
    struct BvBoundarySequence sequence;
    void *context;
    unsigned (*snapshot)(void *,unsigned char [2560]);
    unsigned reason,active,candidate,video,inputEpoch,lastInput,lastCount,started,finished;
    unsigned char actual[2560],expected[2560];
    unsigned expectedBytes;
    FILE *stream;
};
/* Typed little-endian stream records: B=boundary, F=completed video frame,
 * E=finish. All ordinals/epochs/counts/keys are compared, including zero counts.
 * Full 2560-byte snapshots are never shortened, normalised or masked. */
static inline void bv_native_u32(unsigned char *p,unsigned n)
{for(unsigned i=0;i<4;i++)p[i]=(n>>(8*i))&255;}
static inline void bv_native_u64(unsigned char *p,uint64_t n)
{for(unsigned i=0;i<8;i++)p[i]=(n>>(8*i))&255;}
static inline unsigned bv_native_metadata(struct BvNativeRuntime *r,unsigned type,unsigned count)
{
    unsigned char actual[29]={0},expected[29]={0};actual[0]=type;
    bv_native_u64(actual+1,r->sequence.ordinal);bv_native_u32(actual+9,r->video);
    bv_native_u32(actual+13,r->inputEpoch);bv_native_u32(actual+17,count);
    bv_native_u32(actual+21,r->core->frameCounter(r->core));bv_native_u32(actual+25,r->lastInput);
    if(r->candidate){
        if(fread(expected,1,sizeof expected,r->stream)!=sizeof expected || memcmp(actual,expected,sizeof actual))return 117;
    }else if(fwrite(actual,1,sizeof actual,r->stream)!=sizeof actual)return 117;
    return 0;
}
static inline unsigned bv_native_sample(struct BvNativeRuntime *r)
{
    unsigned reason=bv_native_metadata(r,'B',r->sequence.frameCount);if(reason)return reason;
    memset(r->actual,0,sizeof r->actual);memset(r->expected,0,sizeof r->expected);
    reason=r->snapshot(r->context,r->actual);if(reason)return reason;
    if(r->candidate){
        r->expectedBytes=(unsigned)fread(r->expected,1,2560,r->stream);
        if(r->expectedBytes!=2560)return 103;
    }else{
        memcpy(r->expected,r->actual,2560);r->expectedBytes=2560;
    }
    reason=bv_boundary_compare(&r->sequence,1,r->sequence.ordinal,r->video,r->video,
        r->inputEpoch,r->inputEpoch,r->actual,r->expected);
    if(reason)return reason;
    if(!r->candidate && fwrite(r->actual,1,2560,r->stream)!=2560)return 103;
    return 0;
}
static inline void bv_native_enter(struct mDebuggerPlatform *p,enum mDebuggerEntryReason why,struct mDebuggerEntryInfo *info)
{
    struct BvNativeRuntime *r=(struct BvNativeRuntime *)p->p;
    const struct ARMCore *cpu=r->core->cpu;
    struct BvBoundaryCpu c={1,(unsigned)cpu->gprs[ARM_PC],(unsigned)cpu->gprs[ARM_LR],(unsigned)cpu->cpsr.packed,
        cpu->executionMode,cpu->privilegeMode,cpu->halted,cpu->cycles,cpu->nextEvent,cpu->prefetch[0]};
    if(why!=DEBUGGER_ENTER_BREAKPOINT || !info || !bv_boundary_authority(&r->authority,&c,
        info->type.bp.breakType==BREAKPOINT_HARDWARE,(unsigned)info->pointId,info->address))r->reason=115;
    else if(r->active)r->reason=bv_native_sample(r);
    /* Do not invoke default ARMDebuggerEnter: it writes nextEvent=cycles.
     * Never restore/write any CPU state as compensation. */
    p->p->state=DEBUGGER_RUNNING;
}
static inline unsigned bv_native_attach(struct BvNativeRuntime *r,struct mCore *core,
    unsigned entry,unsigned callerLR,void *context,unsigned (*snapshot)(void *,unsigned char [2560]))
{
    if(!r || !core || !core->cpu || !core->board || core->debugger || !snapshot || !context
        || entry!=0x080008ac || callerLR!=0x080004bf || !core->supportsDebuggerType(core,DEBUGGER_CUSTOM))return 115;
    r->core=core;r->context=context;r->snapshot=snapshot;
    r->debugger.type=DEBUGGER_CUSTOM;mDebuggerAttach(&r->debugger,core);
    struct mDebuggerPlatform *p=r->debugger.platform;
    if(!p || !p->setBreakpoint || !p->checkBreakpoints || p->getStackTraceMode(p)!=STACK_TRACE_DISABLED)return 115;
    p->entered=bv_native_enter;
    struct mBreakpoint bp={.address=entry,.segment=-1,.type=BREAKPOINT_HARDWARE};
    ssize_t id=p->setBreakpoint(p,&bp);if(id<=0 || (uint64_t)id>UINT32_MAX)return 115;
    r->authority=(struct BvBoundaryAuthority){1,entry,callerLR,(unsigned)id};return 0;
}
static inline unsigned bv_native_frame_counter(void *p)
{struct BvNativeRuntime *r=p;return r->core->frameCounter(r->core);}
static inline uint32_t bv_native_time(void *p)
{struct BvNativeRuntime *r=p;return (uint32_t)mTimingCurrentTime(&((struct GBA *)r->core->board)->timing);}
static inline unsigned bv_native_due(void *p)
{const struct ARMCore *cpu=((struct BvNativeRuntime *)p)->core->cpu;return cpu->cycles>=cpu->nextEvent;}
static inline void bv_native_events(void *p)
{struct ARMCore *cpu=((struct BvNativeRuntime *)p)->core->cpu;cpu->irqh.processEvents(cpu);}
static inline unsigned bv_native_observe(void *p)
{
    struct BvNativeRuntime *r=p;struct ARMCore *cpu=r->core->cpu;
    /* An installed hardware observation must leave the ENTIRE CPU unchanged. */
    struct ARMCore original=*cpu;r->debugger.platform->checkBreakpoints(r->debugger.platform);
    if(memcmp(cpu,&original,sizeof original))return 115;
    return r->reason;
}
static inline void bv_native_step(void *p)
{
    struct ARMCore *cpu=((struct BvNativeRuntime *)p)->core->cpu;
    /* Only reached inside cycles<nextEvent. ARMRun cannot dispatch an event here.
     * Its installed interpreter executes precisely the next original instruction.
     * BX/MSR/IRQ scheduling changes force the inner batch to exit normally. */
    ARMRun(cpu);
}
static inline unsigned bv_native_fail(struct BvNativeRuntime *r,unsigned reason)
{if(r)r->reason=reason;return reason;}
static inline unsigned bv_native_frame(struct BvNativeRuntime *r,unsigned active,unsigned candidate,FILE *stream,unsigned video)
{
    if(!r || !r->core || !r->authority.verified || r->reason || (active && !stream))return bv_native_fail(r,r && r->reason?r->reason:115);
    if((r->finished && active) || (r->started && !r->finished && (!active || r->candidate!=candidate || r->stream!=stream)))return bv_native_fail(r,115);
    if(active)r->started=1;
    r->active=active;r->candidate=candidate;r->stream=stream;r->video=video;
    r->lastInput=r->core->getKeys(r->core);r->inputEpoch++;
    unsigned before=r->core->frameCounter(r->core);
    struct BvBoundaryDriverOps ops={r,bv_native_frame_counter,bv_native_time,bv_native_due,bv_native_events,bv_native_observe,bv_native_step};
    unsigned reason=bv_boundary_drive_frame(&ops,1,VIDEO_TOTAL_LENGTH+VIDEO_HORIZONTAL_LENGTH);
    if(!reason && r->core->frameCounter(r->core)!=before+1)reason=118;
    if(!reason && r->core->getKeys(r->core)!=r->lastInput)reason=117;
    if(!reason && active){
        r->lastCount=r->sequence.frameCount;reason=bv_native_metadata(r,'F',r->lastCount);
        if(!reason)reason=bv_boundary_end_frame(&r->sequence,r->lastCount);
    }
    r->reason=reason;return reason;
}
static inline unsigned bv_native_checkpoint(const struct BvNativeRuntime *r)
{return bv_boundary_checkpoint(&r->sequence,r->video,r->inputEpoch);}
static inline unsigned bv_native_finish(struct BvNativeRuntime *r)
{
    if(!r || !r->started || r->finished || r->reason)return bv_native_fail(r,r && r->reason?r->reason:115);
    unsigned reason=bv_native_checkpoint(r);if(reason)return bv_native_fail(r,reason);
    reason=bv_boundary_finish(&r->sequence,r->sequence.ordinal,0);if(reason)return bv_native_fail(r,reason);
    reason=bv_native_metadata(r,'E',0);if(reason)return bv_native_fail(r,reason);
    if(r->candidate && (fgetc(r->stream)!=EOF || ferror(r->stream)))return bv_native_fail(r,117);
    r->finished=1;return 0;
}
#endif
