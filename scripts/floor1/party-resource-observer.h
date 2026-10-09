/* Private read-only buffers, strict first-mismatch stop; never write game RAM. */
#define PROBE_PARTY_BYTES 600
#define PROBE_RES_BYTES (0x988 - 0x490)
#define PROBE_FLAG_BYTES 300
struct PartyProbe {
    unsigned armed, counter, anchorCounter, lastFrame, frame, checks;
    unsigned count, lastCount, transitions;
    unsigned anchorContext, lastContext, lastResourceFrame, resourceChecks;
    unsigned char anchor[PROBE_PARTY_BYTES], last[PROBE_PARTY_BYTES];
    unsigned char resources[PROBE_RES_BYTES], lastResources[PROBE_RES_BYTES], flags[PROBE_FLAG_BYTES];
};

static void probe_read(struct mCore *core, unsigned address, unsigned char *data, unsigned size)
{
    for (unsigned i=0;i<size;i++) data[i]=core->busRead8(core,address+i);
}

static void probe_write(const char *name, const unsigned char *data, unsigned size)
{
    FILE *f=fopen(name,"wb");
    if (!f || fwrite(data,1,size,f)!=size || fclose(f)) {
        fprintf(stderr,"Private probe capture failed; STOP\n");exit(60);
    }
}

static void probe_dump(struct mCore *core, struct PartyProbe *p, unsigned party, unsigned saveptr,
                       unsigned save2ptr, unsigned objects, unsigned avatar, unsigned frame, unsigned reason)
{
    unsigned sb=core->busRead32(core,saveptr), obj=objects+core->busRead8(core,avatar+5)*0x24;
    unsigned context=core->busRead32(core,core->busRead32(core,save2ptr)+0xAC);
    unsigned char current[PROBE_PARTY_BYTES], owned[PROBE_RES_BYTES], flags[PROBE_FLAG_BYTES];
    probe_read(core,party,current,sizeof current);probe_read(core,sb+0x490,owned,sizeof owned);
    probe_read(core,sb+0x1270,flags,sizeof flags);
    probe_write("anchor-party.bin",p->anchor,sizeof p->anchor);
    probe_write("last-stable-party.bin",p->last,sizeof p->last);
    probe_write("after-party.bin",current,sizeof current);
    probe_write("anchor-owned.bin",p->resources,sizeof p->resources);
    probe_write("after-owned.bin",owned,sizeof owned);
    probe_write("last-stable-owned.bin",p->lastResources,sizeof p->lastResources);
    probe_write("anchor-context.bin",(const unsigned char *)&p->anchorContext,4);
    probe_write("last-stable-context.bin",(const unsigned char *)&p->lastContext,4);
    probe_write("after-context.bin",(const unsigned char *)&context,4);
    probe_write("anchor-flags.bin",p->flags,sizeof p->flags);
    probe_write("after-flags.bin",flags,sizeof flags);
    unsigned differing=0;
    for(unsigned i=0;i<200;i++) if(p->anchor[i]!=current[i]) differing++;
    FILE *f=fopen("private-buffer-metadata.json","w");
    if(!f) {fprintf(stderr,"Private metadata failed; STOP\n");exit(60);}
    fprintf(f,"{\"reason\":%u,\"frame\":%u,\"last_stable_frame\":%u,\"armed_frame\":%u,"
        "\"counter_anchor\":%u,\"counter_last_stable\":%u,\"counter_after\":%u,\"counter_transitions\":%u,"
        "\"party_count_before\":%u,\"party_count_after\":%u,\"strict200_changed_bytes\":%u,"
        "\"map\":[%u,%u],\"position\":[%d,%d],\"other400_exact\":%s,\"owned_exact\":%s,\"flags_exact\":%s}\n",
        reason,frame,p->lastFrame,p->frame,p->anchorCounter,p->counter,core->busRead16(core,sb+0x13f0),p->transitions,
        p->count,core->busRead8(core,sb+0x234),differing,core->busRead8(core,sb+4),core->busRead8(core,sb+5),
        (short)core->busRead16(core,obj+0x10)-7,(short)core->busRead16(core,obj+0x12)-7,
        memcmp(p->anchor+200,current+200,400)?"false":"true",resource_equal(p->resources,p->anchorContext,owned,context)?"true":"false",
        memcmp(p->flags,flags,sizeof flags)?"false":"true");
    if(fclose(f)) exit(60);
    printf("RESOURCES stable_checks=%u last_stable_resource_frame=%u context_changed=%u logical_equal=%u\n",p->resourceChecks,p->lastResourceFrame,p->anchorContext!=context,resource_equal(p->resources,p->anchorContext,owned,context));
}

static void probe_arm(struct mCore *core, struct PartyProbe *p, unsigned party, unsigned saveptr, unsigned save2ptr, unsigned frame)
{
    unsigned sb=core->busRead32(core,saveptr);
    if(p->armed || !sb || core->busRead8(core,sb+0x234)!=2 || core->busRead16(core,sb+0x13f0)!=66) {
        fprintf(stderr,"Frozen probe input/counter differs; STOP\n");exit(54);
    }
    probe_read(core,party,p->anchor,sizeof p->anchor);memcpy(p->last,p->anchor,sizeof p->last);
    probe_read(core,sb+0x490,p->resources,sizeof p->resources);probe_read(core,sb+0x1270,p->flags,sizeof p->flags);
    p->anchorContext=p->lastContext=core->busRead32(core,core->busRead32(core,save2ptr)+0xAC);
    memcpy(p->lastResources,p->resources,sizeof p->lastResources);p->lastResourceFrame=frame;
    p->count=p->lastCount=2;p->anchorCounter=p->counter=66;p->frame=p->lastFrame=frame;p->armed=1;
    printf("PASS probe armed frame=%u counter=66 party=2 strict=200 all_party=600\n",frame);
}

static unsigned probe_check(struct mCore *core, struct PartyProbe *p, unsigned party, unsigned saveptr, unsigned frame)
{
    if(!p->armed) return 0;
    unsigned sb=core->busRead32(core,saveptr), count=core->busRead8(core,sb+0x234), counter=core->busRead16(core,sb+0x13f0);
    unsigned char current[PROBE_PARTY_BYTES], flags[PROBE_FLAG_BYTES];
    probe_read(core,party,current,sizeof current);probe_read(core,sb+0x1270,flags,sizeof flags);
    p->checks++;
    unsigned reason=party_guard_reason(p->anchor,current,p->count,count,p->flags,flags);
    if(reason) return reason;
    if(counter!=p->counter) {
        p->transitions++;printf("STEP frame=%u counter=%u->%u transition=%u\n",frame,p->counter,counter,p->transitions);
        if(counter!=(p->counter+1)%128) return 57;
    }
    memcpy(p->last,current,sizeof p->last);p->lastFrame=frame;p->lastCount=count;p->counter=counter;
    return 0;
}

/* Called only by existing ready/preservation checkpoints, never the frame hook. */
static unsigned probe_resources_ready(struct mCore *core,struct PartyProbe *p,unsigned party,unsigned saveptr,unsigned save2ptr,unsigned frame)
{
    unsigned sb=core->busRead32(core,saveptr), context=core->busRead32(core,core->busRead32(core,save2ptr)+0xAC);
    unsigned char current[PROBE_PARTY_BYTES],owned[PROBE_RES_BYTES],flags[PROBE_FLAG_BYTES];
    probe_read(core,party,current,sizeof current);probe_read(core,sb+0x490,owned,sizeof owned);probe_read(core,sb+0x1270,flags,sizeof flags);
    unsigned reason=party_resource_reason(p->anchor,current,p->count,core->busRead8(core,sb+0x234),p->flags,flags,
        p->resources,p->anchorContext,owned,context);
    char name[80];unsigned index=p->resourceChecks++;
    snprintf(name,sizeof name,"ready-%02u-owned.bin",index);probe_write(name,owned,sizeof owned);
    snprintf(name,sizeof name,"ready-%02u-context.bin",index);probe_write(name,(const unsigned char *)&context,4);
    printf("RESOURCE frame=%u checkpoint=%u context_changed=%u logical_exact=%u reason=%u\n",frame,index,
        context!=p->anchorContext,resource_equal(p->resources,p->anchorContext,owned,context),reason);
    if(!reason) {memcpy(p->lastResources,owned,sizeof owned);p->lastContext=context;p->lastResourceFrame=frame;}
    return reason;
}
