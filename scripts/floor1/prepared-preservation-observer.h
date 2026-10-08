/* Read-only host snapshots; raw identities/contexts stay private. */
struct WalkAddresses {unsigned party,saveptr,save2ptr,mapgroups,mainstate,objects,avatar,choice;};
struct WalkPreservation {
    unsigned armed,counter,checks,events,snapshots,actualYes,pendingStairs;
    unsigned char last[600],flags[300],owned[LOGICAL_OWNED_BYTES];unsigned context;
};
static void walk_read(struct mCore *core,unsigned address,unsigned char *out,unsigned n)
{for(unsigned i=0;i<n;i++) out[i]=core->busRead8(core,address+i);}
static void walk_write(const char *name,const unsigned char *data,unsigned n)
{
    FILE *f=fopen(name,"wb");if(!f || fwrite(data,1,n,f)!=n || fclose(f)) {fprintf(stderr,"Private walking capture failed; STOP\n");exit(60);}
}
static unsigned walk_section(struct mCore *core,struct WalkAddresses a)
{
    unsigned sb=core->busRead32(core,a.saveptr),group=core->busRead8(core,sb+4),map=core->busRead8(core,sb+5);
    if(group!=35 || (map!=3 && map!=4)) return 256;
    unsigned maps=core->busRead32(core,a.mapgroups+4*group),header=core->busRead32(core,maps+4*map);
    return core->busRead8(core,header+0x14);
}
static void walk_snapshot(struct mCore *core,struct WalkAddresses a,const char *prefix)
{
    unsigned sb=core->busRead32(core,a.saveptr),context=core->busRead32(core,core->busRead32(core,a.save2ptr)+0xAC);
    unsigned char party[600],flags[300],owned[LOGICAL_OWNED_BYTES];char name[100];
    walk_read(core,a.party,party,600);walk_read(core,sb+0x1270,flags,300);walk_read(core,sb+0x490,owned,sizeof owned);
#define WALK_DUMP(suffix,data,n) do {snprintf(name,sizeof name,"%s-" suffix ".bin",prefix);walk_write(name,data,n);} while(0)
    WALK_DUMP("party",party,600);WALK_DUMP("flags",flags,300);WALK_DUMP("owned",owned,sizeof owned);
    WALK_DUMP("context",(const unsigned char *)&context,4);
#undef WALK_DUMP
    snprintf(name,sizeof name,"%s-metadata.json",prefix);FILE *f=fopen(name,"w");if(!f) exit(60);
    fprintf(f,"{\"counter\":%u,\"party_count\":%u,\"map\":[%u,%u]}\n",core->busRead16(core,sb+0x13f0),core->busRead8(core,sb+0x234),core->busRead8(core,sb+4),core->busRead8(core,sb+5));
    if(fclose(f)) exit(60);
}
static unsigned walk_arm(struct mCore *core,struct WalkPreservation *p,struct WalkAddresses a,unsigned frame)
{
    unsigned sb=core->busRead32(core,a.saveptr),section=walk_section(core,a);unsigned char plain[48];
    if(p->armed || section>255 || core->busRead8(core,sb+0x234)!=2 || (core->busRead8(core,a.mainstate+0x439)&2)) return 53;
    walk_read(core,a.party,p->last,600);walk_read(core,sb+0x1270,p->flags,300);walk_read(core,sb+0x490,p->owned,sizeof p->owned);
    for(unsigned i=0;i<2;i++) {
        const unsigned char *raw=p->last+100*i;walk_decode(raw,plain);const unsigned char *order=walk_orders[resource_word(raw)%24];
        if(!walk_valid(raw) || walk_u16(plain+12*order[0]+2)!=0 || ((walk_u16(plain+12*order[3]+2)>>11)&15)==11 || plain[12*order[3]+1]==section) return 53;
    }
    p->context=core->busRead32(core,core->busRead32(core,a.save2ptr)+0xAC);p->counter=core->busRead16(core,sb+0x13f0);
    if(p->counter>=128) return 57;
    /* Cold uses first-clear's actual final snapshot as a read-only host input. */
    FILE *expected=fopen("expected-party.bin","rb");
    if(expected) {
        unsigned char data[LOGICAL_OWNED_BYTES],owned[LOGICAL_OWNED_BYTES],context[4],counter[2];
        unsigned n=fread(data,1,600,expected);if(fclose(expected) || n!=600 || memcmp(data,p->last,600)) return 53;
#define WALK_EXPECT(name,out,size) do {expected=fopen(name,"rb");if(!expected || fread(out,1,size,expected)!=size || fclose(expected)) return 57;} while(0)
        WALK_EXPECT("expected-flags.bin",data,300);if(memcmp(data,p->flags,300)) return 57;
        WALK_EXPECT("expected-owned.bin",owned,sizeof owned);WALK_EXPECT("expected-context.bin",context,4);
        if(!resource_equal(owned,resource_word(context),p->owned,p->context)) return 57;
        WALK_EXPECT("expected-counter.bin",counter,2);if(walk_u16(counter)!=p->counter) return 57;
#undef WALK_EXPECT
        printf("PASS exact cold boot600 party/count/counter/flags/full logical resources from actual completed Save\n");
    }
    p->armed=1;walk_snapshot(core,a,"anchor");
    printf("PASS walking preservation armed frame=%u counter=%u actual_friendship=%u,%u count=2 no_bonus=1\n",frame,p->counter,walk_friend(p->last),walk_friend(p->last+100));return 0;
}
static unsigned walk_frame_check(struct mCore *core,struct WalkPreservation *p,struct WalkAddresses a,unsigned frame)
{
    if(!p->armed) return 0;
    unsigned sb=core->busRead32(core,a.saveptr),counter=core->busRead16(core,sb+0x13f0),section=walk_section(core,a);
    unsigned boundary=p->counter==127 && counter==0,effects[2]={0,0};unsigned char current[600],flags[300];
    walk_read(core,a.party,current,600);walk_read(core,sb+0x1270,flags,300);p->checks++;
    if(section>255 || !walk_party_equal(p->last,current,boundary,section,effects)) return 53;
    if(!walk_counter_valid(p->counter,counter) || core->busRead8(core,sb+0x234)!=2
        || (core->busRead8(core,a.mainstate+0x439)&2) || !walk_flags_equal(p->flags,flags,p->actualYes)) return 57;
    if(boundary) {
        char name[80];snprintf(name,sizeof name,"walking-event-%02u-before-party.bin",p->events);walk_write(name,p->last,600);
        snprintf(name,sizeof name,"walking-event-%02u-after",p->events);walk_snapshot(core,a,name);
        printf("WALK_EVENT index=%u frame=%u counter=127->0 before=%u,%u after=%u,%u native_target=%u,%u section=%u\n",p->events++,frame,
            walk_friend(p->last),walk_friend(p->last+100),walk_friend(current),walk_friend(current+100),walk_target(p->last,section,0),walk_target(p->last+100,section,0),section);
    }
    if(counter!=p->counter) printf("WALK_STEP frame=%u counter=%u->%u\n",frame,p->counter,counter);
    if((flags[6]&1)!=(p->flags[6]&1)) printf("PASS checkpoint48 transition after actual staircase YES frame=%u\n",frame);
    memcpy(p->last,current,600);memcpy(p->flags,flags,300);p->counter=counter;return 0;
}
static unsigned walk_stable_check(struct mCore *core,struct WalkPreservation *p,struct WalkAddresses a,unsigned frame)
{
    if(!p->armed) return 0;
    unsigned reason=walk_frame_check(core,p,a,frame);if(reason) return reason;
    unsigned sb=core->busRead32(core,a.saveptr),context=core->busRead32(core,core->busRead32(core,a.save2ptr)+0xAC);unsigned char owned[LOGICAL_OWNED_BYTES];
    walk_read(core,sb+0x490,owned,sizeof owned);char name[80];snprintf(name,sizeof name,"stable-%02u",p->snapshots++);walk_snapshot(core,a,name);
    if(!resource_equal(p->owned,p->context,owned,context)) return 57;
    printf("PASS logical resources exact checkpoint=%u frame=%u actual_context=1\n",p->snapshots-1,frame);return 0;
}
