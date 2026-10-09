/* OFFLINE PROTOTYPE: never wired to the frozen gameplay driver. */
#ifndef V01_NATIVE_BOUNDARY_ADAPTER_H
#define V01_NATIVE_BOUNDARY_ADAPTER_H
#include <stdint.h>
#include <string.h>

struct BvBoundaryAuthority {
    unsigned verified,entry,callerLR,pointId;
};
struct BvBoundaryCpu {
    unsigned available,pcRaw,lr,cpsr,executionMode,privilegeMode,halted;
    int cycles,nextEvent;
    unsigned opcode;
};
/* Installed mGBA hardware check reports next-instruction PC = rawPC-width.
 * SYSTEM mode alone is insufficient: native IntrMain also switches to SYSTEM.
 * Exact entry plus verified unique AgbMain LR is compulsory. */
static inline unsigned bv_boundary_authority(const struct BvBoundaryAuthority *a,
    const struct BvBoundaryCpu *cpu,unsigned hardware,unsigned pointId,unsigned address)
{
    return a && cpu && a->verified && cpu->available && hardware && pointId==a->pointId
        && a->pointId && address==a->entry && cpu->pcRaw==a->entry+2
        && cpu->lr==a->callerLR && (cpu->cpsr&0x3f)==0x3f
        && cpu->executionMode==1 && cpu->privilegeMode==0x1f && !cpu->halted
        && cpu->cycles<cpu->nextEvent && cpu->opcode==0xb500;
}

static inline unsigned bv_boundary_word(const unsigned char *p)
{return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static inline unsigned bv_boundary_party_valid(const unsigned char party[600])
{
    // Native encrypted BoxPokemon checksum; never infer boundary authority from
    // plaintext/checksum recognition. Empty slots must also remain complete.
    for(unsigned mon=0;mon<6;mon++){
        const unsigned char *p=party+100*mon;
        unsigned key=bv_boundary_word(p)^bv_boundary_word(p+4),sum=0;
        if(p[19]&1)return 0;
        for(unsigned i=32;i<80;i+=4){unsigned word=bv_boundary_word(p+i)^key;sum+=(word&65535)+(word>>16);}
        if((sum&65535)!=(unsigned)(p[28]|p[29]<<8))return 0;
    }
    return 1;
}

/* Complete private state/control record remains 2560 bytes. Link-address fields
 * must use existing verified canonical identities. No masks or partial compares.
 * Each boundary is matched by ordinal, video/input epoch and full state.
 * Every video frame records its exact boundary count, including zero. */
struct BvBoundarySequence {uint64_t ordinal;unsigned videoEpoch,inputEpoch,frameCount,seen;};
static inline unsigned bv_boundary_compare(struct BvBoundarySequence *g,unsigned authority,
    uint64_t expectedOrdinal,unsigned video,unsigned expectedVideo,unsigned input,unsigned expectedInput,
    const unsigned char actual[2560],const unsigned char expected[2560])
{
    if(!authority || !actual || !expected)return 115;
    if(expectedOrdinal!=g->ordinal || video!=expectedVideo || input!=expectedInput)return 117;
    if(memcmp(actual,expected,2560))return 103;
    if(!bv_boundary_party_valid(actual) || !bv_boundary_party_valid(expected))return 116;
    g->ordinal++;g->frameCount++;g->videoEpoch=video;g->inputEpoch=input;g->seen=1;return 0;
}
static inline unsigned bv_boundary_end_frame(struct BvBoundarySequence *g,unsigned expectedCount)
{
    if(g->frameCount!=expectedCount)return 117;
    g->frameCount=0;return 0;
}
static inline unsigned bv_boundary_checkpoint(const struct BvBoundarySequence *g,unsigned video,unsigned input)
{
    return g->seen && g->videoEpoch==video && g->inputEpoch==input?0:115;
}
static inline unsigned bv_boundary_finish(const struct BvBoundarySequence *g,uint64_t expectedTotal,unsigned expectedTrailing)
{
    return g->seen && g->ordinal==expectedTotal && !g->frameCount && !expectedTrailing?0:117;
}

/* Frame-loop prototype mirrors _GBACoreRunFrame's original frame/time guard.
 * Events are dispatched before any next instruction and the guard is then
 * rechecked. A breakpoint observes inside the existing loop, without advancing
 * time. It never calls runFrame followed by extra steps, sets keys or changes
 * CPU registers. Actual mGBA callbacks must be bound and reviewed separately. */
struct BvBoundaryDriverOps {
    void *context;
    unsigned (*frame)(void *);
    uint32_t (*time)(void *);
    unsigned (*eventDue)(void *);
    void (*processEvents)(void *);
    unsigned (*observe)(void *);
    void (*step)(void *);
};
static inline unsigned bv_boundary_drive_frame(const struct BvBoundaryDriverOps *ops,unsigned verified,unsigned originalLimit)
{
    if(!verified || !ops || !ops->context || !ops->frame || !ops->time || !ops->eventDue
        || !ops->processEvents || !ops->observe || !ops->step)return 115;
    unsigned frame=ops->frame(ops->context);uint32_t start=ops->time(ops->context);
    while(ops->frame(ops->context)==frame && (uint32_t)(ops->time(ops->context)-start)<originalLimit){
        // Keep the original ARMRunLoop batch boundary: time guard only after
        // processEvents, not midway through its instruction batch.
        while(!ops->eventDue(ops->context)){
            unsigned reason=ops->observe(ops->context);if(reason)return reason;
            ops->step(ops->context);
        }
        ops->processEvents(ops->context);
    }
    return 0;
}
#endif
