/* Pure host phase/state contract. Deferred samples never read or accept state. */
#ifndef COLD_PHASE_GUARD_H
#define COLD_PHASE_GUARD_H
struct ColdSnapshot {
    unsigned char party[600],flags[300],owned[LOGICAL_OWNED_BYTES];
    unsigned context,counter,count,savedCount,group,map,section;
};
struct ColdGuard {
    struct ColdSnapshot expected,last;
    unsigned frames,armedFrame,lastAcceptedFrame,validFrames,deferredFrames,checkpoints,reentries;
    unsigned deferred,events;
};
static unsigned cold_native_phase(unsigned cb1,unsigned cb2,unsigned vblank,unsigned battle,
                                  unsigned wanted1,unsigned wanted2,unsigned wantedVblank)
{
    return wanted1 && wanted2 && wantedVblank && !battle
        && (cb1&~1u)==(wanted1&~1u) && (cb2&~1u)==(wanted2&~1u) && (vblank&~1u)==(wantedVblank&~1u);
}
static unsigned cold_before_frame(const struct ColdGuard *g,unsigned battle)
{return battle?70:(g->frames>=24000?51:0);}
static unsigned cold_after_frame(struct ColdGuard *g,unsigned battle)
{g->frames++;return battle?70:0;}
typedef unsigned (*ColdReadSnapshot)(void *,struct ColdSnapshot *,unsigned);
static unsigned cold_sample(struct ColdGuard *g,unsigned valid,unsigned checkpoint,unsigned actualYes,
                             ColdReadSnapshot read,void *data)
{
    if(!valid) {
        if(checkpoint) return 40;
        g->deferredFrames++;g->deferred=1;return 0;
    }
    unsigned reentry=g->deferred,resources=checkpoint || reentry,effects[2]={0,0};
    struct ColdSnapshot current=g->last;unsigned reason=read(data,&current,resources);
    if(reason) return reason;
    unsigned boundary=g->last.counter==127 && current.counter==0;
    if(!walk_party_equal(g->last.party,current.party,boundary,current.section,effects)) return 53;
    if(current.count!=2 || current.savedCount!=2 || !walk_counter_valid(g->last.counter,current.counter)
        || current.group!=35 || (current.map!=3 && current.map!=4)
        || !walk_flags_equal(g->last.flags,current.flags,actualYes)) return 57;
    if(resources && !resource_equal(g->expected.owned,g->expected.context,current.owned,current.context)) return 57;
    if(checkpoint) g->checkpoints++;else g->validFrames++;
    if(reentry) g->reentries++;
    if(boundary) g->events++;
    g->last=current;g->lastAcceptedFrame=g->frames;g->deferred=0;return 0;
}
#endif
