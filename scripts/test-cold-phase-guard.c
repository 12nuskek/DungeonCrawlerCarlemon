/* Ordinary host fixture arrays only; same pure contract as the live adapter. */
#define main original_walking_fixture_suite
#include "test-walking-preservation.c"
#undef main
#include "floor1/cold-phase-guard.h"
struct TestReader {struct ColdSnapshot current;unsigned reads,resourceReads;};
static unsigned test_read(void *opaque,struct ColdSnapshot *out,unsigned resources)
{
    struct TestReader *r=opaque;r->reads++;r->resourceReads+=resources;
    unsigned char owned[LOGICAL_OWNED_BYTES];memcpy(owned,out->owned,sizeof owned);unsigned context=out->context;
    *out=r->current;if(!resources) {memcpy(out->owned,owned,sizeof owned);out->context=context;}return 0;
}
static struct ColdGuard fresh(struct TestReader *r)
{
    struct ColdGuard g={0};native_encode(g.last.party,3,88,4,9);native_encode(g.last.party+100,9,84,4,9);
    g.last.count=g.last.savedCount=2;g.last.counter=8;g.last.group=35;g.last.map=4;g.last.section=218;g.last.flags[6]=1;
    g.expected=g.last;g.frames=g.armedFrame=g.lastAcceptedFrame=2044;r->current=g.last;r->reads=r->resourceReads=0;return g;
}
int main(void)
{
    original_walking_fixture_suite();unsigned baseline=cases;
    CHECK(cold_native_phase(0x101,0x201,0x301,0,0x100,0x200,0x300));
    CHECK(!cold_native_phase(0x100,0x200,0,0,0x100,0x200,0x300));
    CHECK(!cold_native_phase(0,0x200,0x300,0,0x100,0x200,0x300));
    CHECK(!cold_native_phase(0x100,0x400,0x300,0,0x100,0x200,0x300));
    CHECK(!cold_native_phase(0x100,0x200,0x300,1,0x100,0x200,0x300));
    struct TestReader r;struct ColdGuard g=fresh(&r);struct ColdSnapshot last=g.last,expected=g.expected;
    r.current.counter=5953;r.current.flags[0]=1;r.current.owned[0]=1;r.current.party[0]^=1;
    for(unsigned i=0;i<25;i++) {CHECK(!cold_after_frame(&g,0));CHECK(!cold_sample(&g,0,0,0,test_read,&r));}
    CHECK(r.reads==0 && r.resourceReads==0);CHECK(!memcmp(&last,&g.last,sizeof last));CHECK(!memcmp(&expected,&g.expected,sizeof expected));
    CHECK(g.deferredFrames==25 && g.validFrames==0 && g.checkpoints==0 && g.reentries==0);
    CHECK(cold_sample(&g,0,1,0,test_read,&r)==40);CHECK(r.reads==0);
    r.current=last;r.current.flags[299]=1;CHECK(cold_sample(&g,1,0,0,test_read,&r)==57);
    CHECK(!memcmp(&g.last,&last,sizeof last));CHECK(g.deferred==1 && g.reentries==0);
    r.current=last;r.current.owned[0]=1;CHECK(cold_sample(&g,1,0,0,test_read,&r)==57);
    r.current=last;r.current.party[599]=1;CHECK(cold_sample(&g,1,0,0,test_read,&r)==53);
    r.current=last;r.current.count=3;CHECK(cold_sample(&g,1,0,0,test_read,&r)==57);
    r.current=last;r.current.counter=10;CHECK(cold_sample(&g,1,0,0,test_read,&r)==57);
    r.current=last;CHECK(!cold_sample(&g,1,0,0,test_read,&r));CHECK(g.reentries==1 && g.validFrames==1 && g.deferred==0);
    CHECK(!memcmp(&g.expected,&expected,sizeof expected));
    CHECK(!cold_sample(&g,1,1,0,test_read,&r));CHECK(g.checkpoints==1 && g.validFrames==1);
    /* Exact rekey is allowed on re-entry; corruption is not. */
    g=fresh(&r);CHECK(!cold_sample(&g,0,0,0,test_read,&r));
    resource_canonical(r.current.owned,g.last.owned,0x12345678);r.current.context=0x12345678;
    CHECK(!cold_sample(&g,1,0,0,test_read,&r));CHECK(resource_equal(g.expected.owned,g.expected.context,g.last.owned,g.last.context));
    /* No new friendship tolerance while deferred or after re-entry. */
    g=fresh(&r);native_encode(r.current.party,3,89,4,9);r.current.counter=9;
    CHECK(!cold_sample(&g,0,0,0,test_read,&r));CHECK(cold_sample(&g,1,0,0,test_read,&r)==53);
    g=fresh(&r);g.last.counter=g.expected.counter=127;r.current=g.last;r.current.counter=0;native_encode(r.current.party,3,89,4,9);
    CHECK(!cold_sample(&g,0,0,0,test_read,&r));CHECK(!cold_sample(&g,1,0,0,test_read,&r));CHECK(g.events==1);
    g=fresh(&r);g.last.counter=g.expected.counter=127;r.current=g.last;r.current.counter=0;native_encode(r.current.party,3,90,4,9);
    CHECK(cold_sample(&g,1,0,0,test_read,&r)==53);
    /* Battle guards apply independently of native validity and arming. */
    g=fresh(&r);CHECK(!cold_sample(&g,0,0,0,test_read,&r));CHECK(cold_before_frame(&g,1)==70);
    CHECK(cold_after_frame(&g,1)==70);CHECK(g.frames==2045);CHECK(r.reads==0);
    /* Batch clocks update once per real frame, not at batch completion. */
    g=fresh(&r);unsigned batches[]={52,68,300},wanted=2044;
    for(unsigned batch=0;batch<3;batch++) for(unsigned i=0;i<batches[batch];i++) {
        CHECK(!cold_before_frame(&g,0));CHECK(!cold_after_frame(&g,0));CHECK(g.frames==++wanted);
    }
    CHECK(g.frames==2464);g.frames=23999;CHECK(!cold_before_frame(&g,0));CHECK(!cold_after_frame(&g,0));
    CHECK(g.frames==24000);CHECK(cold_before_frame(&g,0)==51);CHECK(g.frames==24000);
    printf("PASS %u additional exact-header phase/clock cases:deferred no reads/anchor mutation;stable corruption/rekey;strict friendship;transition battle detection;distinct sample counts;absolute batch labels/24000 bound\n",cases-baseline);
    return 0;
}
