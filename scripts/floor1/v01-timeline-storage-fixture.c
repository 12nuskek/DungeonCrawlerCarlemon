/* File/counter operations only. Reuse the zeroed-board helpers without invoking
 * their instruction fixtures or any game/Save/reset/event/interpreter call. */
#define main bv_old_capacity_main_not_invoked
#include "v01-native-timeline-capacity-fixture.c"
#undef main
static unsigned serial;
static struct BvTimeline rolling(void)
{
    char path[80],summary[80];snprintf(path,sizeof path,"detail-%u.bin",serial);snprintf(summary,sizeof summary,"summary-%u.bin",serial++);
    int fd=open(path,O_WRONLY|O_CREAT|O_EXCL,0600);assert(fd>=0);FILE *file=fdopen(fd,"wb");assert(file);
    struct BvTimeline t=writer(file);assert(!bv_tl_write_header(file));assert(!bv_tl_storage_enable(&t,summary));return t;
}
static void add(struct BvTimeline *t,unsigned index,unsigned event,unsigned point)
{struct BvTimelineRecord r=row(index);r.word[BV_TL_LR]=0x080004bf;r.word[BV_TL_RAWPC]=0x080008ae;r.word[BV_TL_CPSR]=0x3f;r.word[BV_TL_PRIV]=0x1f;r.word[BV_TL_MODE]=1;assert(!bv_tl_append(t,r,event,point));}
static void chunk(struct BvTimeline *t,unsigned epoch)
{t->inputEpoch=epoch;t->visualEpoch=epoch;add(t,epoch,BV_TL_FRAME,0);assert(!bv_tl_write_buffer(t));}
static unsigned frozenCounter;
static unsigned actualSnapshotCalls,mutation;
static unsigned char frozenSnapshot[2560];
static uint32_t fixtureFrame(const struct mCore *core){(void)core;return frozenCounter;}
static unsigned fixtureSnapshot(void *context,unsigned char data[2560])
{(void)context;actualSnapshotCalls++;memcpy(data,frozenSnapshot,2560);if(mutation<2560)data[mutation]^=1;return 0;}
static unsigned strictHooks(const char *reference)
{
    FILE *original=fopen(reference,"rb");assert(original);unsigned char bytes[29+2560];assert(fread(bytes,1,sizeof bytes,original)==sizeof bytes&&bytes[0]=='B');fclose(original);
    memcpy(frozenSnapshot,bytes+29,2560);frozenCounter=le32(bytes+21);unsigned keys=le32(bytes+25),cases=0;
    for(unsigned altered=0;altered<2590;altered++){
        unsigned char expected[29+2560];memcpy(expected,bytes,sizeof bytes);
        mutation=altered<2560?altered:UINT_MAX;if(altered>=2560&&altered<2589)expected[altered-2560]^=1;
        struct BvTimeline t=writer(tmpfile());assert(t.file);t.storage=calloc(1,sizeof *t.storage);assert(t.storage);t.storage->summary=tmpfile();assert(t.storage->summary);
        add(&t,0,BV_TL_BEFORE,1u<<BV_TL_WAIT);t.inputEpoch=2045;
        struct mCore core={.frameCounter=fixtureFrame};struct ARMCore cpu={0};struct GBA *gba=calloc(1,sizeof *gba);assert(gba);core.cpu=&cpu;core.board=gba;gba->timing.relativeCycles=&cpu.cycles;
        FILE *stream=fmemopen(expected,sizeof expected,"rb");assert(stream);actualSnapshotCalls=0;
        struct BvNativeRuntime r={.core=&core,.candidate=1,.stream=stream,.snapshot=fixtureSnapshot,.context=&core,.lastInput=keys,.inputEpoch=2045,.timeline=&t};
        unsigned result=bv_native_sample(&r);
        if(altered<2560)assert(result==103&&actualSnapshotCalls==1&&!t.storage->anchored&&!r.sequence.ordinal);
        else if(altered<2589)assert(result==117&&!actualSnapshotCalls&&!t.storage->anchored&&!r.sequence.ordinal);
        else assert(!result&&actualSnapshotCalls==1&&t.storage->anchored&&r.sequence.ordinal==1&&t.storage->anchorIndex==0);
        assert(!bv_tl_close(&t));fclose(stream);free(gba);cases++;
    }
    return cases;
}
static void testStorage(const char *reference)
{
    unsigned cases=0;struct BvTimeline t=rolling();
    for(unsigned i=0;i<BV_TS_STARTUP_CHUNKS;i++){assert(!bv_tl_storage_frame(&t));chunk(&t,i);}
    assert(t.storage->chunks==BV_TS_STARTUP_CHUNKS&&bv_tl_storage_frame(&t)==119);
    unsigned before=t.storage->summaries;assert(bv_tl_flush(&t,119,0)==119&&t.stopped&&t.storage->summaries==before+1);
    before=t.storage->summaries;assert(bv_tl_flush(&t,0,0)==119&&t.storage->summaries==before);assert(bv_tl_close(&t)==119);cases++;
    t=rolling();add(&t,0,BV_TL_BEFORE,1u<<BV_TL_WAIT);assert(!bv_tl_storage_boundary(&t,0));chunk(&t,0);
    for(unsigned i=1;i<BV_TS_ACTIVE_CHUNKS;i++){assert(!bv_tl_storage_frame(&t));chunk(&t,i);}
    assert(t.storage->chunks==250&&bv_tl_storage_frame(&t)==119);assert(bv_tl_flush(&t,119,0)==119);assert(bv_tl_close(&t)==119);cases++;
    t=rolling();chunk(&t,0);add(&t,11,BV_TL_BEFORE,1u<<BV_TL_WAIT);assert(!bv_tl_storage_boundary(&t,0));
    add(&t,22,BV_TL_BEFORE,1u<<BV_TL_WAIT);assert(!bv_tl_storage_boundary(&t,1));add(&t,33,BV_TL_AFTER,1u<<BV_TL_WAIT);chunk(&t,1);
    assert(t.storage->chunks==1&&t.storage->records==3&&t.storage->anchorOrdinal==1);assert(!bv_tl_close(&t));cases++;
    t=rolling();for(unsigned i=0;i<4096;i++)add(&t,i,BV_TL_BEFORE,i==4095?1u<<BV_TL_WAIT:0);
    assert(!bv_tl_storage_boundary(&t,0)&&!bv_tl_write_buffer(&t)&&t.storage->records==1);assert(!bv_tl_close(&t));cases++;
    t=rolling();add(&t,0,BV_TL_BEFORE,0);assert(bv_tl_storage_boundary(&t,0)==119);assert(bv_tl_flush(&t,119,0)==119);assert(bv_tl_close(&t)==119);cases++;
    t=rolling();add(&t,0,BV_TL_BEFORE,1u<<BV_TL_WAIT);assert(!bv_tl_storage_boundary(&t,0));assert(bv_tl_storage_boundary(&t,0)==119);assert(bv_tl_close(&t)==119);cases++;
    for(unsigned kind=0;kind<2;kind++)for(unsigned length=0;length<184;length++){
        t=rolling();struct Sink sink={.shortAt=length};
        if(kind){assert(!fclose(t.storage->summary));t.storage->summary=sinkFile(&sink);}
        else {assert(!fclose(t.file));t.file=sinkFile(&sink);}
        add(&t,0,BV_TL_FRAME,0);assert(bv_tl_write_buffer(&t)==119);assert(bv_tl_close(&t)==119);cases++;
    }
    t=rolling();struct Sink sink={.shortAt=0};assert(!fclose(t.file));t.file=sinkFile(&sink);
    struct BvNativeRuntime runtime={.timeline=&t,.failure={.present=1,.reason=117}};
    t.flushReason=117;add(&t,0,BV_TL_FRAME,0);assert(bv_tl_write_buffer(&t)==119&&bv_native_pending_failure(&runtime)==117&&bv_native_fail(&runtime,119)==117);
    assert(bv_tl_close(&t)==119);cases++;
    t=rolling();t.storage->summaries=BV_TS_SUMMARY_LIMIT;add(&t,0,BV_TL_FRAME,0);assert(bv_tl_write_buffer(&t)==119);assert(bv_tl_close(&t)==119);cases++;
    t=rolling();FILE *file=t.file;assert(bv_tl_storage_enable(&t,"must-not-create.bin")==119&&t.file==file);assert(!bv_tl_close(&t));cases++;
    t=rolling();assert(!fclose(t.file));t.file=fopen("/dev/null","wb");add(&t,0,BV_TL_BEFORE,1u<<BV_TL_WAIT);assert(!bv_tl_storage_boundary(&t,0));assert(bv_tl_write_buffer(&t)==119);assert(bv_tl_close(&t)==119);cases++;
    cases+=strictHooks(reference);
    printf("PASS%u offline rotation/startup/250-window/last-boundary/overflow/short-write/first-failure/freeze cases; zero CPU execution\n",cases);
    printf("{\"cases\":%u,\"record_buffer_bytes\":%zu,\"storage_context_bytes\":%zu,\"active_chunks\":250,\"startup_chunks\":2046,\"CPU_instructions\":0}\n",cases,BV_TL_BUFFER*sizeof(struct BvTimelineRecord),sizeof(struct BvTimelineStorage));
}
static void replayStorage(const char *timeline,const char *boundaries)
{
    unsigned expected[BV_TL_FRAME_CALLS+2]={0};FILE *ref=fopen(boundaries,"rb");assert(ref);unsigned char metadata[29];
    while(fread(metadata,1,29,ref)==29){unsigned epoch=le32(metadata+13);assert(epoch<BV_TL_FRAME_CALLS+2);
        if(metadata[0]=='B'){expected[epoch]++;assert(!fseeko(ref,2560,SEEK_CUR));}
        else assert(metadata[0]=='F'); /* Failed baseline is deliberately partial. */
    }
    assert(feof(ref)&&!ferror(ref));fclose(ref);
    FILE *in=fopen(timeline,"rb");assert(in);unsigned char header[16],bytes[184];assert(fread(header,1,16,in)==16&&!memcmp(header,"BVTIME01",8));
    struct BvTimeline t=rolling();uint64_t ordinal=0;unsigned maximum=0,lastEpoch=0;
    while(fread(bytes,1,184,in)==184){
        struct BvTimelineRecord r;for(unsigned j=0;j<46;j++)r.word[j]=le32(bytes+4*j);
        unsigned epoch=r.word[BV_TL_INPUT_EPOCH];assert(epoch<BV_TL_FRAME_CALLS+2);
        if(epoch!=lastEpoch){assert(!bv_tl_storage_frame(&t));lastEpoch=epoch;}
        t.inputEpoch=epoch;t.visualEpoch=r.word[BV_TL_VISUAL_EPOCH];
        assert(!bv_tl_append(&t,r,r.word[BV_TL_EVENT],r.word[BV_TL_POINT]));
        if(r.word[BV_TL_EVENT]==BV_TL_BEFORE&&(r.word[BV_TL_POINT]&(1u<<BV_TL_WAIT))
            &&r.word[BV_TL_LR]==0x080004bf&&r.word[BV_TL_RAWPC]==0x080008ae
            &&r.word[BV_TL_MODE]==1&&r.word[BV_TL_PRIV]==0x1f&&epoch>2044){
            assert(expected[epoch]);expected[epoch]--;assert(!bv_tl_storage_boundary(&t,ordinal++));
        }
        if(r.word[BV_TL_EVENT]==BV_TL_FRAME){assert(!bv_tl_write_buffer(&t));if(t.storage->chunks>maximum)maximum=t.storage->chunks;}
    }
    assert(feof(in)&&!ferror(in));fclose(in);for(unsigned i=0;i<BV_TL_FRAME_CALLS+2;i++)assert(!expected[i]);
    assert(t.used==2&&ordinal==13721&&t.total==999932);t.reason=119;assert(bv_tl_flush(&t,119,0)==119);
    unsigned summaries=t.storage->summaries,records=t.storage->records;uint64_t anchor=t.storage->anchorOrdinal;
    assert(bv_tl_flush(&t,117,0)==119&&t.storage->summaries==summaries&&t.storage->records==records);
    assert(bv_tl_close(&t)==119);
    printf("{\"observations\":999932,\"accepted_boundaries\":%llu,\"summaries\":%u,\"retained_records\":%u,\"last_anchor_ordinal\":%llu,\"maximum_retained_chunks\":%u,\"CPU_instructions\":0}\n",(unsigned long long)ordinal,summaries,records,(unsigned long long)anchor,maximum);
}
int main(int argc,char **argv)
{if(argc==4&&!strcmp(argv[1],"--replay"))replayStorage(argv[2],argv[3]);else {assert(argc==2);testStorage(argv[1]);}return 0;}
