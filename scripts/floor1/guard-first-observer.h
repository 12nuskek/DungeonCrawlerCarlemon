/* Current route domains and declared native mutation milestones. No RAM writes. */
struct PatrolSnapshot {
    unsigned char party[600],flags[300],owned[LOGICAL_OWNED_BYTES];
    unsigned context,counter,count,savedCount,group,map,section,x,y;
};
struct PatrolAddresses {unsigned party,saveptr,save2ptr,mapgroups,mainstate,objects,avatar,count,cb1,cb2,vblank,trainer;};
struct PatrolGuard {struct PatrolSnapshot last;unsigned armed,pending,frames,lastAccepted,valid,deferred,unarmedFrames,mutationFrames,checkpoints,reentries,wasDeferred,battleFrames,encounterFrames[2],battleAttempts,battleWas,stage,approach;};
static unsigned patrol_phase(struct mCore *c,struct PatrolAddresses a)
{
    return !(c->busRead8(c,a.mainstate+0x439)&2)
        && (c->busRead32(c,a.mainstate)&~1u)==(a.cb1&~1u)
        && (c->busRead32(c,a.mainstate+4)&~1u)==(a.cb2&~1u)
        && (c->busRead32(c,a.mainstate+0x0c)&~1u)==(a.vblank&~1u);
}
static void patrol_bytes(struct mCore *c,unsigned addr,unsigned char *p,unsigned n)
{for(unsigned i=0;i<n;i++)p[i]=c->busRead8(c,addr+i);}
static unsigned patrol_read(struct mCore *c,struct PatrolAddresses a,struct PatrolSnapshot *s,unsigned resources,unsigned approach)
{
    if(!patrol_phase(c,a))return 40; /* before ALL actual SaveBlock pointer/data reads */
    unsigned sb=c->busRead32(c,a.saveptr);s->group=c->busRead8(c,sb+4);s->map=c->busRead8(c,sb+5);
    if(s->group!=35 || (s->map!=0 && s->map!=1 && !(approach && s->map==3)))return 57;
    unsigned maps=c->busRead32(c,a.mapgroups+4*s->group),header=c->busRead32(c,maps+4*s->map),obj=a.objects+c->busRead8(c,a.avatar+5)*0x24;
    s->section=c->busRead8(c,header+0x14);s->counter=c->busRead16(c,sb+0x13f0);s->count=c->busRead8(c,a.count);s->savedCount=c->busRead8(c,sb+0x234);
    s->x=(short)c->busRead16(c,obj+0x10)-7;s->y=(short)c->busRead16(c,obj+0x12)-7;
    patrol_bytes(c,a.party,s->party,600);patrol_bytes(c,sb+0x1270,s->flags,300);
    if(resources){s->context=c->busRead32(c,c->busRead32(c,a.save2ptr)+0xAC);patrol_bytes(c,sb+0x490,s->owned,sizeof s->owned);}
    return 0;
}
static void patrol_file(const char *name,const unsigned char *p,unsigned n)
{FILE*f=fopen(name,"wb");if(!f||fwrite(p,1,n,f)!=n||fclose(f))exit(60);}
static void patrol_dump(struct PatrolSnapshot *s,const char *prefix,unsigned frame)
{
    char name[128];
#define PATROL_DUMP(kind,p,n) do{snprintf(name,sizeof name,"%s-"kind".bin",prefix);patrol_file(name,p,n);}while(0)
    PATROL_DUMP("party",s->party,600);PATROL_DUMP("flags",s->flags,300);PATROL_DUMP("owned",s->owned,sizeof s->owned);PATROL_DUMP("context",(unsigned char*)&s->context,4);
#undef PATROL_DUMP
    snprintf(name,sizeof name,"%s-metadata.json",prefix);FILE*f=fopen(name,"w");if(!f)exit(60);
    fprintf(f,"{\"native_phase_valid\":true,\"absolute_frame\":%u,\"counter\":%u,\"count\":%u,\"saved_count\":%u,\"map\":[%u,%u],\"position\":[%u,%u],\"section\":%u}\n",frame,s->counter,s->count,s->savedCount,s->group,s->map,s->x,s->y,s->section);if(fclose(f))exit(60);
}
static unsigned patrol_sample(struct mCore *c,struct PatrolGuard*g,struct PatrolAddresses a,unsigned explicit)
{
    if(!g->armed||g->pending)return 0;
    if(!patrol_phase(c,a)){if(explicit)return 40;g->deferred++;g->wasDeferred=1;return 0;}
    struct PatrolSnapshot s=g->last;unsigned effects[2]={0,0},resources=explicit||g->wasDeferred;
    unsigned reason=patrol_read(c,a,&s,resources,g->approach);if(reason)return reason;
    if(!walk_party_equal(g->last.party,s.party,g->last.counter==127&&s.counter==0,s.section,effects))return 53;
    if(s.count!=2||s.savedCount!=2||!walk_counter_valid(g->last.counter,s.counter)||!walk_flags_equal(g->last.flags,s.flags,0))return 57;
    if(resources&&!resource_equal(g->last.owned,g->last.context,s.owned,s.context))return 57;
    if(g->last.counter!=s.counter)printf("WALK_STEP absolute_frame=%u counter=%u->%u friendship=%u,%u\n",g->frames,g->last.counter,s.counter,walk_friend(s.party),walk_friend(s.party+100));
    if(g->wasDeferred){g->reentries++;printf("PASS native reentry absolute_frame=%u last_accepted=%u complete_state=1\n",g->frames,g->lastAccepted);}
    g->last=s;g->lastAccepted=g->frames;g->wasDeferred=0;if(!explicit)g->valid++;return 0;
}
static unsigned patrol_frame(struct mCore*c,struct PatrolGuard*g,struct PatrolAddresses a)
{
    unsigned battle=(c->busRead8(c,a.mainstate+0x439)&2)!=0;
    if(g->frames>=100000)return 51;
    if(battle&&g->pending!=1&&g->pending!=2)return 70;
    c->runFrame(c);g->frames++;battle=(c->busRead8(c,a.mainstate+0x439)&2)!=0;
    if(battle){
        if(g->pending!=1&&g->pending!=2)return 70;
        if(c->busRead16(c,a.trainer)!=(g->pending==1?856:857))return 70;
        if(!g->battleWas){if(g->battleAttempts!=g->pending-1)return 70;g->battleAttempts++;}
        g->battleFrames++;g->encounterFrames[g->pending-1]++;if(g->encounterFrames[g->pending-1]>36000)return 51;
    }
    g->battleWas=battle;
    if(!g->armed){g->unarmedFrames++;return 0;}
    if(g->pending){g->mutationFrames++;return 0;}
    return patrol_sample(c,g,a,0);
}
