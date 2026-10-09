/* Concrete mGBA 0.10.5 interpreter binding. No game equivalence claim. */
#ifndef V01_NATIVE_BOUNDARY_RUNTIME_H
#define V01_NATIVE_BOUNDARY_RUNTIME_H
#include <stddef.h>
#include <stdio.h>
#include <errno.h>
#include <mgba/core/core.h>
#include <mgba/core/timing.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/arm/debugger/debugger.h>
#include "v01-native-boundary-adapter.h"
#include "v01-native-boundary-diagnostics.h"
#include "v01-native-timeline.h"
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
    struct BvNativeMetadata pendingMetadata;
    struct BvNativeFailure failure;
    unsigned retentionAttempted,privateDiagnosticRetained,safeDiagnosticRetained;
    struct BvTimeline *timeline; /* Optional in isolated fixtures; mandatory host. */
};
/* Typed little-endian stream records: B=boundary, F=completed video frame,
 * E=finish. All ordinals/epochs/counts/keys are compared, including zero counts.
 * Full 2560-byte snapshots are never shortened, normalised or masked. */
static inline void bv_native_u32(unsigned char *p,unsigned n)
{for(unsigned i=0;i<4;i++)p[i]=(n>>(8*i))&255;}
static inline void bv_native_u64(unsigned char *p,uint64_t n)
{for(unsigned i=0;i<8;i++)p[i]=(n>>(8*i))&255;}
static inline void bv_native_header(struct BvNativeRuntime *r,unsigned char p[29],unsigned kind,unsigned count,unsigned keys)
{
    memset(p,0,29);p[0]=kind;
    bv_native_u64(p+1,r->sequence.ordinal);bv_native_u32(p+9,r->video);
    bv_native_u32(p+13,r->inputEpoch);bv_native_u32(p+17,count);
    bv_native_u32(p+21,r->core->frameCounter(r->core));bv_native_u32(p+25,keys);
}
static inline unsigned bv_native_capture117(struct BvNativeRuntime *r,unsigned origin,
    const struct BvNativeMetadata *metadata,uint64_t expectedOrdinal,unsigned expectedCount,
    unsigned observedKeys,unsigned observedKeysAvailable,unsigned trailingPresent,unsigned trailingByte)
{
    if(r->failure.present)return r->failure.reason;
    struct BvNativeFailure *d=&r->failure;memset(d,0,sizeof *d);
    d->present=1;d->reason=117;d->origin=origin;d->metadata=*metadata;d->firstDifference=bv_diag_difference(metadata);
    d->ordinal=r->sequence.ordinal;d->expectedOrdinal=expectedOrdinal;d->frameCount=r->sequence.frameCount;d->expectedCount=expectedCount;
    d->guardVideo=d->guardExpectedVideo=r->video;d->guardInput=d->guardExpectedInput=r->inputEpoch;
    d->video=r->video;d->inputEpoch=r->inputEpoch;d->lastCount=r->lastCount;d->started=r->started;d->finished=r->finished;
    d->keysAtFrameStart=r->lastInput;d->observedKeys=observedKeys;d->observedKeysAvailable=observedKeysAvailable;
    d->trailingPresent=trailingPresent;d->trailingByte=trailingByte;
    const struct ARMCore *cpu=r->core->cpu;const struct GBA *gba=r->core->board;
    if(cpu){d->cpuAvailable=1;d->pc=cpu->gprs[ARM_PC];d->lr=cpu->gprs[ARM_LR];d->sp=cpu->gprs[ARM_SP];d->cpsr=cpu->cpsr.packed;
        d->executionMode=cpu->executionMode;d->privilegeMode=cpu->privilegeMode;d->halted=cpu->halted;
        d->cycles=cpu->cycles;d->nextEvent=cpu->nextEvent;d->eventDue=cpu->cycles>=cpu->nextEvent;}
    if(gba){d->frame=gba->video.frameCounter;d->timingCurrent=(uint32_t)mTimingCurrentTime(&gba->timing);d->masterCycles=gba->timing.masterCycles;d->globalCycles=gba->timing.globalCycles;}
    r->reason=117;return 117;
}
static inline void bv_native_guard_headers(struct BvNativeRuntime *r,struct BvNativeMetadata *m,
    unsigned kind,unsigned actualCount,unsigned expectedCount,unsigned actualKeys)
{
    memset(m,0,sizeof *m);m->kind=kind;m->actualBytes=m->expectedBytes=29;
    m->actualSource=m->expectedSource=BV_HEADER_GUARD;
    bv_native_header(r,m->actual,kind,actualCount,actualKeys);bv_native_header(r,m->expected,kind,expectedCount,r->lastInput);
    m->startPosition=m->endPosition=r->stream?(int64_t)ftello(r->stream):-1;
}
static inline unsigned bv_native_metadata(struct BvNativeRuntime *r,unsigned type,unsigned count)
{
    if(r->reason || r->failure.present)return r->failure.present?r->failure.reason:r->reason;
    struct BvNativeMetadata *m=&r->pendingMetadata;memset(m,0,sizeof *m);
    m->kind=type;m->actualBytes=29;m->actualSource=BV_HEADER_RECORD;
    bv_native_header(r,m->actual,type,count,r->lastInput);m->startPosition=(int64_t)ftello(r->stream);
    if(r->candidate){
        m->expectedSource=BV_HEADER_RECORD;
        m->expectedBytes=m->headerReadBytes=m->operationReadBytes=(unsigned)fread(m->expected,1,29,r->stream);
        m->ioError=ferror(r->stream)!=0;m->ioErrno=m->ioError?errno:0;m->eof=feof(r->stream)!=0;m->endPosition=(int64_t)ftello(r->stream);
        if(m->expectedBytes!=29)return bv_native_capture117(r,BV_FAIL_METADATA_SHORT,m,r->sequence.ordinal,count,r->lastInput,1,0,0);
        if(memcmp(m->actual,m->expected,29))return bv_native_capture117(r,BV_FAIL_METADATA_DIFFERENT,m,r->sequence.ordinal,count,r->lastInput,1,0,0);
    }else{
        // No reference header exists for a baseline write. Expected is explicitly
        // the intended output, not a fabricated reference-stream read.
        memcpy(m->expected,m->actual,29);m->expectedBytes=29;m->expectedSource=BV_HEADER_OUTPUT;
        m->writeBytes=(unsigned)fwrite(m->actual,1,29,r->stream);
        m->ioError=ferror(r->stream)!=0;m->ioErrno=m->ioError?errno:0;m->eof=feof(r->stream)!=0;m->endPosition=(int64_t)ftello(r->stream);
        if(m->writeBytes!=29)return bv_native_capture117(r,BV_FAIL_METADATA_WRITE,m,r->sequence.ordinal,count,r->lastInput,1,0,0);
    }
    return 0;
}
static inline unsigned bv_native_compare(struct BvNativeRuntime *r,uint64_t expectedOrdinal,
    unsigned video,unsigned expectedVideo,unsigned input,unsigned expectedInput)
{
    if(r->reason || r->failure.present)return r->failure.present?r->failure.reason:r->reason;
    unsigned reason=bv_boundary_compare(&r->sequence,1,expectedOrdinal,video,expectedVideo,input,expectedInput,r->actual,r->expected);
    if(reason==117){
        bv_native_capture117(r,BV_FAIL_BOUNDARY_SEQUENCE,&r->pendingMetadata,expectedOrdinal,r->sequence.frameCount,r->lastInput,1,0,0);
        r->failure.guardVideo=video;r->failure.guardExpectedVideo=expectedVideo;
        r->failure.guardInput=input;r->failure.guardExpectedInput=expectedInput;
        return reason;
    }
    return reason;
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
    reason=bv_native_compare(r,r->sequence.ordinal,r->video,r->video,r->inputEpoch,r->inputEpoch);
    if(reason)return reason;
    if(!r->candidate && fwrite(r->actual,1,2560,r->stream)!=2560)return 103;
    if(bv_tl_storage_boundary(r->timeline,r->sequence.ordinal-1))return 119;
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
{
    struct BvNativeRuntime *r=p;struct ARMCore *cpu=r->core->cpu;
    if(bv_tl_events_before(r->timeline))return;
    cpu->irqh.processEvents(cpu);bv_tl_events_after(r->timeline);
}
static inline unsigned bv_native_observe(void *p)
{
    struct BvNativeRuntime *r=p;
    if(r->reason || r->failure.present)return r->failure.present?r->failure.reason:r->reason;
    unsigned trace=bv_tl_before(r->timeline);if(trace)return trace;
    struct ARMCore *cpu=r->core->cpu;
    /* An installed hardware observation must leave the ENTIRE CPU unchanged. */
    struct ARMCore original=*cpu;r->debugger.platform->checkBreakpoints(r->debugger.platform);
    if(memcmp(cpu,&original,sizeof original))return 115;
    return r->reason;
}
static inline void bv_native_step(void *p)
{
    struct BvNativeRuntime *r=p;struct ARMCore *cpu=r->core->cpu;
    /* Only reached inside cycles<nextEvent. ARMRun cannot dispatch an event here.
     * Its installed interpreter executes precisely the next original instruction.
     * BX/MSR/IRQ scheduling changes force the inner batch to exit normally. */
    ARMRun(cpu);
    bv_tl_after(r->timeline);
}
static inline unsigned bv_native_pending_failure(void *p)
{
    const struct BvNativeRuntime *r=p;
    return r->failure.present?r->failure.reason:r->reason?r->reason:r->timeline?r->timeline->reason:0;
}
static inline unsigned bv_native_fail(struct BvNativeRuntime *r,unsigned reason)
{
    if(r && r->failure.present)return r->failure.reason;
    if(r && reason==117)return bv_native_capture117(r,BV_FAIL_FALLBACK,&r->pendingMetadata,r->sequence.ordinal,r->sequence.frameCount,r->lastInput,0,0,0);
    if(r)r->reason=reason;
    return reason;
}
static inline unsigned bv_native_frame(struct BvNativeRuntime *r,unsigned active,unsigned candidate,FILE *stream,unsigned video)
{
    if(!r || !r->core || !r->authority.verified || r->reason || (active && !stream))return bv_native_fail(r,r && r->reason?r->reason:115);
    if((r->finished && active) || (r->started && !r->finished && (!active || r->candidate!=candidate || r->stream!=stream)))return bv_native_fail(r,115);
    if(bv_tl_storage_frame(r->timeline))return bv_native_fail(r,119);
    if(active)r->started=1;
    r->active=active;r->candidate=candidate;r->stream=stream;r->video=video;
    r->lastInput=r->core->getKeys(r->core);r->inputEpoch++;
    if(r->timeline){r->timeline->inputEpoch=r->inputEpoch;r->timeline->visualEpoch=video;}
    unsigned before=r->core->frameCounter(r->core);
    struct BvBoundaryDriverOps ops={r,bv_native_frame_counter,bv_native_time,bv_native_due,bv_native_events,bv_native_observe,bv_native_step,bv_native_pending_failure};
    unsigned reason=bv_boundary_drive_frame(&ops,1,VIDEO_TOTAL_LENGTH+VIDEO_HORIZONTAL_LENGTH);
    if(!reason && r->core->frameCounter(r->core)!=before+1)reason=118;
    if(!reason){unsigned observedKeys=r->core->getKeys(r->core);
        if(observedKeys!=r->lastInput){struct BvNativeMetadata m;
            bv_native_guard_headers(r,&m,'F',r->sequence.frameCount,r->sequence.frameCount,observedKeys);
            reason=bv_native_capture117(r,BV_FAIL_FRAME_KEYS,&m,r->sequence.ordinal,r->sequence.frameCount,observedKeys,1,0,0);}
    }
    if(!reason && active){
        r->lastCount=r->sequence.frameCount;reason=bv_native_metadata(r,'F',r->lastCount);
        if(!reason){reason=bv_boundary_end_frame(&r->sequence,r->lastCount);
            if(reason==117)reason=bv_native_capture117(r,BV_FAIL_FRAME_COUNT,&r->pendingMetadata,r->sequence.ordinal,r->lastCount,r->lastInput,1,0,0);}
    }
    unsigned trace=bv_tl_flush(r->timeline,reason,0);if(!reason)reason=trace;
    r->reason=reason;return reason;
}
static inline unsigned bv_native_checkpoint(const struct BvNativeRuntime *r)
{return bv_boundary_checkpoint(&r->sequence,r->video,r->inputEpoch);}
static inline unsigned bv_native_finish(struct BvNativeRuntime *r)
{
    if(!r || !r->started || r->finished || r->reason)return bv_native_fail(r,r && r->reason?r->reason:115);
    unsigned reason=bv_native_checkpoint(r);if(reason)return bv_native_fail(r,reason);
    reason=bv_boundary_finish(&r->sequence,r->sequence.ordinal,0);
    if(reason==117){struct BvNativeMetadata m;bv_native_guard_headers(r,&m,'E',r->sequence.frameCount,0,r->lastInput);
        return bv_native_capture117(r,BV_FAIL_FINISH_SEQUENCE,&m,r->sequence.ordinal,0,r->lastInput,1,0,0);}
    if(reason)return bv_native_fail(r,reason);
    reason=bv_native_metadata(r,'E',0);if(reason)return bv_native_fail(r,reason);
    if(r->candidate){
        struct BvNativeMetadata m=r->pendingMetadata;m.startPosition=(int64_t)ftello(r->stream);
        int trailing=fgetc(r->stream);m.operationReadBytes=trailing==EOF?0:1;
        m.ioError=ferror(r->stream)!=0;m.ioErrno=m.ioError?errno:0;m.eof=feof(r->stream)!=0;m.endPosition=(int64_t)ftello(r->stream);
        if(trailing!=EOF)return bv_native_capture117(r,BV_FAIL_TRAILING_BYTE,&m,r->sequence.ordinal,0,r->lastInput,1,1,(unsigned char)trailing);
        if(m.ioError)return bv_native_capture117(r,BV_FAIL_TRAILING_IO,&m,r->sequence.ordinal,0,r->lastInput,1,0,0);
    }
    r->finished=1;unsigned trace=bv_tl_flush(r->timeline,0,1);if(trace)r->reason=trace;return trace;
}
static inline void bv_native_retain_failure(struct BvNativeRuntime *r)
{
    if(!r || !r->failure.present || r->retentionAttempted)return;
    r->retentionAttempted=1;
    bv_tl_flush(r->timeline,r->failure.reason,0);
    r->privateDiagnosticRetained=bv_diag_write(&r->failure,"visual-stop-native-boundary-private.json",1);
    r->safeDiagnosticRetained=bv_diag_write(&r->failure,"visual-stop-native-boundary.json",0);
    fprintf(stderr,"Native first failure origin=%s reason=%u private_diagnostic_complete=%u safe_diagnostic_complete=%u; no further instructions\n",bv_diag_origin(r->failure.origin),r->failure.reason,r->privateDiagnosticRetained,r->safeDiagnosticRetained);
}
#endif
