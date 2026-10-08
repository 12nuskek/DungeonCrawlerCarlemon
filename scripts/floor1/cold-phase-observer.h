/* Native read adapter: one callback gate protects all actual SaveBlock reads. */
struct WalkAddresses {unsigned party,saveptr,save2ptr,mapgroups,mainstate,objects,avatar,choice,count,cb1,cb2,vblank;};
struct WalkPreservation {unsigned armed,actualYes,pendingStairs;struct ColdGuard guard;};
struct ColdReader {struct mCore *core;struct WalkAddresses a;};
static unsigned cold_phase_ready(struct mCore *core,struct WalkAddresses a)
{
    return cold_native_phase(core->busRead32(core,a.mainstate),core->busRead32(core,a.mainstate+4),
        core->busRead32(core,a.mainstate+0x0c),(core->busRead8(core,a.mainstate+0x439)&2)!=0,a.cb1,a.cb2,a.vblank);
}
static void walk_read(struct mCore *core,unsigned address,unsigned char *out,unsigned n)
{for(unsigned i=0;i<n;i++) out[i]=core->busRead8(core,address+i);}
static void walk_write(const char *name,const unsigned char *data,unsigned n)
{
    FILE *f=fopen(name,"wb");if(!f || fwrite(data,1,n,f)!=n || fclose(f)) {fprintf(stderr,"Private cold capture failed; STOP\n");exit(60);}
}
static unsigned cold_read_snapshot(void *opaque,struct ColdSnapshot *s,unsigned resources)
{
    struct ColdReader *reader=opaque;struct mCore *core=reader->core;struct WalkAddresses a=reader->a;
    if(!cold_phase_ready(core,a)) return 40; /* no pointer/data read before gate */
    unsigned sb=core->busRead32(core,a.saveptr);
    s->group=core->busRead8(core,sb+4);s->map=core->busRead8(core,sb+5);
    if(s->group!=35 || (s->map!=3 && s->map!=4)) return 57;
    unsigned maps=core->busRead32(core,a.mapgroups+4*s->group),header=core->busRead32(core,maps+4*s->map);
    s->section=core->busRead8(core,header+0x14);s->counter=core->busRead16(core,sb+0x13f0);
    s->count=core->busRead8(core,a.count);s->savedCount=core->busRead8(core,sb+0x234);
    walk_read(core,a.party,s->party,600);walk_read(core,sb+0x1270,s->flags,300);
    if(resources) {
        s->context=core->busRead32(core,core->busRead32(core,a.save2ptr)+0xAC);
        walk_read(core,sb+0x490,s->owned,sizeof s->owned);
    }
    return 0;
}
static void cold_dump(const struct ColdSnapshot *s,const char *prefix,unsigned frame,unsigned nativeValid)
{
    char name[100];
#define COLD_DUMP(suffix,data,n) do {snprintf(name,sizeof name,"%s-" suffix ".bin",prefix);walk_write(name,data,n);} while(0)
    COLD_DUMP("party",s->party,600);COLD_DUMP("flags",s->flags,300);COLD_DUMP("owned",s->owned,sizeof s->owned);
    COLD_DUMP("context",(const unsigned char *)&s->context,4);
#undef COLD_DUMP
    snprintf(name,sizeof name,"%s-metadata.json",prefix);FILE *f=fopen(name,"w");if(!f) exit(60);
    fprintf(f,"{\"absolute_frame\":%u,\"native_phase_valid\":%s,\"counter\":%u,\"count\":%u,\"saved_count\":%u,\"map\":[%u,%u]}\n",frame,nativeValid?"true":"false",s->counter,s->count,s->savedCount,s->group,s->map);
    if(fclose(f)) exit(60);
}
static void cold_stop_snapshot(struct mCore *core,struct WalkPreservation *p,struct WalkAddresses a)
{
    cold_dump(&p->guard.last,"stop-last-accepted",p->guard.lastAcceptedFrame,1);
    unsigned valid=cold_phase_ready(core,a);struct ColdSnapshot live=p->guard.last;
    if(valid) {struct ColdReader reader={core,a};if(!cold_read_snapshot(&reader,&live,1)) cold_dump(&live,"stop-live",p->guard.frames,1);}
    else {unsigned char party[600];walk_read(core,a.party,party,600);walk_write("stop-live-party.bin",party,600);}
    FILE *f=fopen("stop-clock.json","w");if(!f) exit(60);
    fprintf(f,"{\"absolute_frame\":%u,\"native_phase_valid\":%s,\"last_accepted_frame\":%u,\"valid_frame_samples\":%u,\"deferred_frame_samples\":%u,\"explicit_checkpoints\":%u}\n",p->guard.frames,valid?"true":"false",p->guard.lastAcceptedFrame,p->guard.validFrames,p->guard.deferredFrames,p->guard.checkpoints);if(fclose(f)) exit(60);
}
static unsigned walk_arm(struct mCore *core,struct WalkPreservation *p,struct WalkAddresses a,unsigned frame)
{
    if(p->armed || !cold_phase_ready(core,a)) return 40;
    struct ColdReader reader={core,a};struct ColdSnapshot snapshot={0};unsigned reason=cold_read_snapshot(&reader,&snapshot,1);if(reason) return reason;
    if(snapshot.count!=2 || snapshot.savedCount!=2 || snapshot.counter>=128) return 57;
    for(unsigned i=0;i<2;i++) {
        const unsigned char *raw=snapshot.party+100*i;unsigned char plain[48];walk_decode(raw,plain);const unsigned char *order=walk_orders[resource_word(raw)%24];
        if(!walk_valid(raw) || walk_u16(plain+12*order[0]+2)!=0 || ((walk_u16(plain+12*order[3]+2)>>11)&15)==11 || plain[12*order[3]+1]==snapshot.section) return 53;
    }
    unsigned char data[LOGICAL_OWNED_BYTES],owned[LOGICAL_OWNED_BYTES],context[4],counter[2];FILE *f;
#define COLD_EXPECT(name,out,size) do {f=fopen(name,"rb");if(!f || fread(out,1,size,f)!=size || fclose(f)) return 60;} while(0)
    COLD_EXPECT("expected-party.bin",data,600);if(memcmp(data,snapshot.party,600)) return 53;
    COLD_EXPECT("expected-flags.bin",data,300);if(memcmp(data,snapshot.flags,300)) return 57;
    COLD_EXPECT("expected-owned.bin",owned,sizeof owned);COLD_EXPECT("expected-context.bin",context,4);
    if(!resource_equal(owned,resource_word(context),snapshot.owned,snapshot.context)) return 57;
    COLD_EXPECT("expected-counter.bin",counter,2);if(walk_u16(counter)!=snapshot.counter) return 57;
#undef COLD_EXPECT
    p->guard.expected=p->guard.last=snapshot;p->guard.armedFrame=p->guard.lastAcceptedFrame=frame;p->armed=1;
    cold_dump(&snapshot,"anchor",frame,1);
    printf("PASS exact cold boot600 party/count/counter/flags/full logical resources frame=%u friendship=%u,%u counter=%u\n",frame,walk_friend(snapshot.party),walk_friend(snapshot.party+100),snapshot.counter);return 0;
}
static unsigned cold_sample_native(struct mCore *core,struct WalkPreservation *p,struct WalkAddresses a,unsigned checkpoint)
{
    if(!p->armed) return 0;
    unsigned valid=cold_phase_ready(core,a),wasDeferred=p->guard.deferred,oldCounter=p->guard.last.counter,oldEvents=p->guard.events;
    unsigned char before[600];memcpy(before,p->guard.last.party,600);unsigned oldAccepted=p->guard.lastAcceptedFrame;
    struct ColdReader reader={core,a};unsigned reason=cold_sample(&p->guard,valid,checkpoint,p->actualYes,cold_read_snapshot,&reader);if(reason) return reason;
    if(!valid) {if(!wasDeferred) printf("PHASE defer absolute_frame=%u last_accepted_frame=%u\n",p->guard.frames,oldAccepted);return 0;}
    if(wasDeferred) {
        char name[80];snprintf(name,sizeof name,"reentry-%02u",p->guard.reentries-1);cold_dump(&p->guard.last,name,p->guard.frames,1);
        printf("PASS PHASE reentry absolute_frame=%u last_accepted_frame=%u complete_party_count_counter_flags_resources=1\n",p->guard.frames,oldAccepted);
    }
    if(p->guard.events!=oldEvents) {
        char name[80];snprintf(name,sizeof name,"walking-event-%02u-before-party.bin",oldEvents);walk_write(name,before,600);
        snprintf(name,sizeof name,"walking-event-%02u-after",oldEvents);cold_dump(&p->guard.last,name,p->guard.frames,1);
        printf("WALK_EVENT absolute_frame=%u observed_boundary=127->0 before=%u,%u after=%u,%u deferred_interval_start=%u\n",p->guard.frames,walk_friend(before),walk_friend(before+100),walk_friend(p->guard.last.party),walk_friend(p->guard.last.party+100),wasDeferred?oldAccepted+1:p->guard.frames);
    }
    if(oldCounter!=p->guard.last.counter) printf("WALK_STEP absolute_frame=%u counter=%u->%u\n",p->guard.frames,oldCounter,p->guard.last.counter);
    if(checkpoint) {char name[80];snprintf(name,sizeof name,"stable-%02u",p->guard.checkpoints-1);cold_dump(&p->guard.last,name,p->guard.frames,1);printf("PASS explicit stable checkpoint=%u absolute_frame=%u party_count_counter_flags_resources=1\n",p->guard.checkpoints-1,p->guard.frames);}
    return 0;
}
static unsigned walk_frame_check(struct mCore *core,struct WalkPreservation *p,struct WalkAddresses a,unsigned frame)
{(void)frame;return cold_sample_native(core,p,a,0);}
static unsigned walk_stable_check(struct mCore *core,struct WalkPreservation *p,struct WalkAddresses a,unsigned frame)
{(void)frame;return cold_sample_native(core,p,a,1);}
