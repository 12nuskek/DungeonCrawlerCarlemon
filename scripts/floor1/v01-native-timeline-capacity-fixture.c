/* Offline file/counter fixture. No reset, ROM, Save, interpreter or event calls.
 * A zeroed synthetic board supplies only the read-only terminal snapshot. */
#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include "v01-native-boundary-runtime.h"

struct Sink {uint64_t bytes,records;unsigned shortAt,header,verify;};
static unsigned le32(const unsigned char *p)
{return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static ssize_t sinkWrite(void *cookie,const char *bytes,size_t n)
{
    struct Sink *s=cookie;const unsigned char *p=(const unsigned char*)bytes;
    if(s->shortAt!=UINT_MAX){size_t take=s->shortAt<n?s->shortAt:n;s->bytes+=take;errno=EIO;return (ssize_t)take;}
    if(!s->header){assert(n==16&&!memcmp(p,"BVTIME02",8));
        assert(le32(p+8)==BV_TL_WORDS&&le32(p+12)==BV_TL_LIMIT);s->header=1;
    }else{
        assert(n==sizeof(struct BvTimelineRecord));
        if(s->verify){unsigned event=le32(p),index=le32(p+4*BV_TL_INDEX);
            if(event==BV_TL_BEFORE){assert(index==s->records&&le32(p+4)==1);}
            else if(event==BV_TL_FRAME){assert(s->records%BV_TL_BUFFER==BV_TL_BUFFER-1);}
            else {assert(event==BV_TL_FINISH&&s->records==BV_TL_FRAME_CALLS*BV_TL_BUFFER);}
        }
        s->records++;
    }
    s->bytes+=n;return (ssize_t)n;
}
static FILE *sinkFile(struct Sink *s)
{FILE *f=fopencookie(s,"w",(cookie_io_functions_t){.write=sinkWrite});assert(f);assert(!setvbuf(f,NULL,_IONBF,0));return f;}
static struct BvTimeline writer(FILE *file)
{
    struct BvTimeline t={.file=file,.limit=BV_TL_LIMIT};
    t.buffer=calloc(BV_TL_BUFFER,sizeof *t.buffer);assert(t.buffer);return t;
}
static struct BvTimelineRecord row(unsigned index)
{struct BvTimelineRecord r={0};r.word[BV_TL_INDEX]=index;return r;}
static void board(struct mCore *core,struct ARMCore *cpu,struct GBA *gba)
{
    memset(core,0,sizeof *core);memset(cpu,0,sizeof *cpu);memset(gba,0,sizeof *gba);
    core->cpu=cpu;core->board=gba;gba->memory.wram=calloc(1,0x40000);gba->memory.iwram=calloc(1,0x8000);
    assert(gba->memory.wram&&gba->memory.iwram);
}
static void configure(struct BvTimeline *t,struct mCore *core)
{t->core=core;t->config.mainAddress=0x030022c0;t->config.copyCount=0x02000000;t->config.copyArmed=0x02000001;}
static void freeBoard(struct GBA *g)
{free(g->memory.wram);free(g->memory.iwram);free(g);}
static void replay(const char *input,const char *output)
{
    FILE *in=fopen(input,"rb");assert(in);unsigned char bytes[sizeof(struct BvTimelineRecord)],header[16];
    assert(fread(header,1,16,in)==16&&!memcmp(header,"BVTIME01",8)&&le32(header+8)==46&&le32(header+12)==1000000);
    int fd=open(output,O_WRONLY|O_CREAT|O_EXCL,0600);assert(fd>=0);FILE *out=fdopen(fd,"wb");assert(out);
    struct BvTimeline t=writer(out);assert(!bv_tl_write_header(out));unsigned batchMax=0,frames=0;
    for(;;){size_t got=fread(bytes,1,sizeof bytes,in);if(!got){assert(feof(in)&&!ferror(in));break;}assert(got==sizeof bytes);
        struct BvTimelineRecord r;for(unsigned j=0;j<BV_TL_WORDS;j++)r.word[j]=le32(bytes+4*j);
        unsigned event=r.word[BV_TL_EVENT];assert(!bv_tl_append(&t,r,event,r.word[BV_TL_POINT]));
        assert(r.word[BV_TL_PHASE]==t.buffer[t.used-1].word[BV_TL_PHASE]);
        if(t.used>batchMax)batchMax=t.used;
        if(event==BV_TL_FRAME||event==BV_TL_STOP||event==BV_TL_FINISH){assert(!bv_tl_write_buffer(&t));frames++;}
    }
    assert(!bv_tl_write_buffer(&t));unsigned total=t.total;assert(!bv_tl_close(&t)&&!fclose(in));
    printf("{\"replayed_records\":%u,\"frame_flushes\":%u,\"max_buffer_records\":%u,\"CPU_instructions\":0}\n",total,frames,batchMax);
}
static void tests(void)
{
    unsigned cases=0;struct mCore core;struct ARMCore cpu;struct GBA *gba=calloc(1,sizeof *gba);assert(gba);board(&core,&cpu,gba);
    /* Stream every maximum-size frame to a checked byte-counting sink: no 28GB
     * file, sparse hole, skipped frame or unbounded allocation. */
    struct Sink sink={.shortAt=UINT_MAX,.verify=1};struct BvTimeline t=writer(sinkFile(&sink));configure(&t,&core);
    assert(!bv_tl_write_header(t.file));
    struct ARMCore cpuBefore=cpu;struct GBA gbaBefore=*gba;
    for(unsigned frame=0;frame<BV_TL_FRAME_CALLS;frame++){
        assert(!bv_tl_reserve(&t,BV_TL_INSTRUCTION_RESERVE));
        for(unsigned i=0;i<BV_TL_BUFFER-1;i++)assert(!bv_tl_append(&t,row(t.total),BV_TL_BEFORE,5));
        assert(!bv_tl_flush(&t,0,0)&&!t.used&&!t.reason&&!t.stopped);
    }
    assert(t.total==BV_TL_FRAME_CALLS*BV_TL_BUFFER);
    assert(!bv_tl_reserve(&t,BV_TL_INSTRUCTION_RESERVE));assert(!bv_tl_flush(&t,0,1)&&t.stopped);
    assert(sink.records==BV_TL_FRAME_CALLS*BV_TL_BUFFER+1);
    assert(sink.bytes==16+sink.records*sizeof(struct BvTimelineRecord));
    assert(!memcmp(&cpuBefore,&cpu,sizeof cpu)&&!memcmp(&gbaBefore,gba,sizeof *gba));
    unsigned terminalTotal=t.total;assert(!bv_tl_flush(&t,0,1)&&t.total==terminalTotal);
    assert(!bv_tl_close(&t));cases++;
    puts("PASS all38044 maximum4096-record frame flushes + separate FINISH; byte-checked streaming sink; fixed754KB buffer; zero CPU/event execution");
    /* Recreate the exact original total-cap fault without its CPU or trace. */
    sink=(struct Sink){.shortAt=UINT_MAX};t=writer(sinkFile(&sink));t.total=999932;
    assert(!bv_tl_reserve(&t,70));t.limit=1000000;assert(bv_tl_reserve(&t,70)==119&&t.total==999932);
    assert(bv_tl_close(&t)==119);cases++;
    for(unsigned n=999930;n<=1000001;n++){
        sink=(struct Sink){.shortAt=UINT_MAX};t=writer(sinkFile(&sink));t.total=n;
        assert(!bv_tl_reserve(&t,70));assert(!bv_tl_append(&t,row(n),BV_TL_BEFORE,5));
        assert(t.total==n+1);assert(!bv_tl_close(&t));cases++;
    }
    puts("PASS exact999932/70 reserve fault only under old limit; every counter999930..1000001 accepted under derived limit");
    for(unsigned n=BV_TL_LIMIT-71;n<=BV_TL_LIMIT+1;n++){
        sink=(struct Sink){.shortAt=UINT_MAX};t=writer(sinkFile(&sink));t.total=n;
        assert(bv_tl_reserve(&t,70)==(n<=BV_TL_LIMIT-70?0:119));assert(t.total==n);
        assert(bv_tl_close(&t)==(n<=BV_TL_LIMIT-70?0:119));cases++;
    }
    sink=(struct Sink){.shortAt=UINT_MAX};t=writer(sinkFile(&sink));t.total=UINT_MAX;
    assert(bv_tl_reserve(&t,1)==119&&t.total==UINT_MAX);assert(bv_tl_close(&t)==119);cases++;
    sink=(struct Sink){.shortAt=UINT_MAX};t=writer(sinkFile(&sink));t.used=BV_TL_BUFFER;
    assert(bv_tl_reserve(&t,1)==119&&t.used==BV_TL_BUFFER);assert(bv_tl_close(&t)==119);cases++;
    puts("PASS derived total-ceiling neighborhood, UINT_MAX and unchanged per-frame overflow fail closed before append");
    for(unsigned terminal=0;terminal<2;terminal++){
        sink=(struct Sink){.shortAt=UINT_MAX};t=writer(sinkFile(&sink));configure(&t,&core);assert(!bv_tl_write_header(t.file));
        t.total=BV_TL_LIMIT-1;assert(!bv_tl_flush(&t,terminal?0:117,terminal));
        assert(t.total==BV_TL_LIMIT&&sink.records==1&&t.stopped);assert(!bv_tl_close(&t));cases++;
    }
    for(unsigned size=0;size<184;size++){
        sink=(struct Sink){.shortAt=UINT_MAX};t=writer(sinkFile(&sink));assert(!bv_tl_write_header(t.file));
        sink.shortAt=size;assert(!bv_tl_append(&t,row(0),BV_TL_BEFORE,5));assert(bv_tl_write_buffer(&t)==119);
        assert(t.reason==119&&sink.bytes==16+size);assert(bv_tl_reserve(&t,1)==119);assert(bv_tl_close(&t)==119);cases++;
    }
    for(unsigned size=0;size<16;size++){
        sink=(struct Sink){.shortAt=size};FILE *f=sinkFile(&sink);assert(bv_tl_write_header(f)==119);fclose(f);cases++;
    }
    puts("PASS separate STOP/FINISH retained at exact global limit; all184 short record writes and16 short header writes rejected");
    sink=(struct Sink){.shortAt=UINT_MAX};t=writer(sinkFile(&sink));configure(&t,&core);assert(!bv_tl_write_header(t.file));sink.shortAt=0;
    struct BvNativeRuntime runtime={.timeline=&t,.failure={.present=1,.reason=117}};
    assert(!bv_tl_append(&t,row(0),BV_TL_BEFORE,5));assert(bv_tl_flush(&t,117,0)==119);
    assert(bv_native_pending_failure(&runtime)==117&&bv_native_fail(&runtime,119)==117);
    unsigned total=t.total;uint64_t bytes=sink.bytes;assert(bv_tl_flush(&t,117,0)==119&&t.total==total&&sink.bytes==bytes);
    assert(bv_tl_close(&t)==119);cases++;
    assert(!memcmp(&cpuBefore,&cpu,sizeof cpu)&&!memcmp(&gbaBefore,gba,sizeof *gba));freeBoard(gba);
    printf("PASS original strict117 first despite retention119; idempotent stopped flush; total%u offline capacity cases\n",cases);
    printf("{\"cases\":%u,\"frame_calls\":%u,\"total_limit\":%u,\"max_file_bytes\":%llu,\"buffer_bytes\":%zu,\"CPU_instructions\":0}\n",
        cases,BV_TL_FRAME_CALLS,BV_TL_LIMIT,(unsigned long long)(16+(uint64_t)BV_TL_LIMIT*sizeof(struct BvTimelineRecord)),BV_TL_BUFFER*sizeof(struct BvTimelineRecord));
}
int main(int argc,char **argv)
{if(argc==4&&!strcmp(argv[1],"--replay"))replay(argv[2],argv[3]);else {assert(argc==1);tests();}return 0;}
