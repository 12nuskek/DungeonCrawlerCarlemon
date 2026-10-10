/* Installed interpreter/boundary sidecar tests. Synthetic instructions/RAM,
 * no game ROM, Save, reset, route, battle or execution claim. */
#define _GNU_SOURCE
#define main prior_interpreter_fixture_never_called
#include "v01-native-boundary-interpreter-fixture.c"
#undef main
#include <sys/stat.h>
static struct BvTimelineConfig config(struct Fixture *f)
{
    struct BvTimelineConfig c={.mainAddress=0x030022c0,.copyCount=0x0203a000,
        .copyArmed=0x0203a001,.copies=0x0203a010,.seen=15};
    for(unsigned i=0;i<BV_TL_POINTS;i++){
        unsigned pc=0x08000c00+8*i;
        c.point[i]=(struct BvTimelinePoint){pc,pc,0x46c0,MODE_THUMB,15};
    }
    c.point[BV_TL_READ_ENTRY]=(struct BvTimelinePoint){0x08000080,0x08000080,((uint16_t*)f->code)[0x80/2],1,15};
    c.point[BV_TL_READ_CALL]=(struct BvTimelinePoint){0x080004be,0x080004be,((uint16_t*)f->code)[0x4be/2],1,15};
    c.point[BV_TL_WAIT]=(struct BvTimelinePoint){0x080008ac,0x080008ac,((uint16_t*)f->code)[0x8ac/2],1,15};
    word(f,0xff0,0xe3a03301);
    c.point[BV_TL_IRQ]=(struct BvTimelinePoint){0x03007000,0x08000ff0,0xe3a03301,0,15};
    return c;
}
static void enable(struct Fixture *f,struct BvTimeline *t,const char *path)
{
    struct GBA *g=f->core->board;g->memory.rom=f->code;g->memory.romSize=4096;
    struct BvTimelineConfig c=config(f);assert(!bv_tl_open(t,f->core,&c,path));f->runtime.timeline=t;
    struct stat s;assert(!stat(path,&s)&&(s.st_mode&0777)==0600);
}
static void closeT(struct Fixture *f,struct BvTimeline *t)
{assert(!bv_tl_close(t));((struct GBA*)f->core->board)->memory.rom=NULL;closeFixture(f);}
static void queueEqual(struct Fixture *a,struct Fixture *b)
{
    struct GBA *ga=a->core->board,*gb=b->core->board;
    assert(!memcmp(ga->memory.io,gb->memory.io,sizeof ga->memory.io));
    const struct mTimingEvent *x=ga->timing.root?ga->timing.root:ga->timing.reroot;
    const struct mTimingEvent *y=gb->timing.root?gb->timing.root:gb->timing.reroot;
    for(unsigned n=0;x&&y;n++,x=x->next,y=y->next){assert(n<64);assert(x->when==y->when&&x->priority==y->priority&&x->callback==y->callback);}
    assert(!x&&!y);
}
static void immutable(struct Fixture *f,struct BvTimeline *t)
{
    struct ARMCore cpu=*(struct ARMCore*)f->core->cpu;struct GBA gba=*(struct GBA*)f->core->board;
    struct BvTimelineRecord r;assert(!bv_tl_collect(t,&r));assert(!bv_tl_before(t));
    assert(!memcmp(&cpu,f->core->cpu,sizeof cpu)&&!memcmp(&gba,f->core->board,sizeof gba));
    assert(!bv_tl_events_before(t));assert(!bv_tl_events_after(t));
    assert(!memcmp(&cpu,f->core->cpu,sizeof cpu)&&!memcmp(&gba,f->core->board,sizeof gba));
}
static ssize_t failWrite(void *cookie,const char *bytes,size_t n)
{(void)cookie;(void)bytes;(void)n;errno=EIO;return -1;}
static void ioFailure(struct BvTimeline *t)
{assert(!fclose(t->file));t->file=fopencookie(NULL,"w",(cookie_io_functions_t){.write=failWrite});assert(t->file);assert(!setvbuf(t->file,NULL,_IONBF,0));}
int main(void)
{
    unsigned cases=0;char path[80];
    for(unsigned kind=0;kind<3;kind++)for(unsigned due=0;due<2;due++)for(unsigned irq=0;irq<2;irq++){
        struct Fixture a,b;struct BvTimeline t;init(&a,0,kind,due,5,irq?2:0);init(&b,1,kind,due,5,irq?2:0);attach(&b);
        snprintf(path,sizeof path,"case-%u-private.bin",cases);enable(&b,&t,path);immutable(&b,&t);
        original(&a);assert(!bv_native_frame(&b.runtime,0,0,NULL,0));equal(&a,&b);queueEqual(&a,&b);
        assert(t.total&&t.used==0);closeFixture(&a);closeT(&b,&t);cases++;
    }
    puts("PASS12 trace-on vs original ARMRunLoop: exact interpreter/register/banked/prefetch/cycle/event-deadline/order/frame/input/RAM/IO parity; whole same-core CPU/GBA byte neutrality of observations");
    {struct Fixture a,b;struct BvTimeline t;init(&a,0,1,0,5,2);init(&b,1,1,0,5,2);attach(&b);enable(&b,&t,"fixed-input-private.bin");
     const unsigned keys[]={0,128,0,1,0,0,64,0};
     for(unsigned i=0;i<8;i++){a.core->setKeys(a.core,keys[i]);b.core->setKeys(b.core,keys[i]);original(&a);assert(!bv_native_frame(&b.runtime,0,0,NULL,i));equal(&a,&b);queueEqual(&a,&b);cases++;}
     closeFixture(&a);closeT(&b,&t);}
    puts("PASS8 fixed input epochs unchanged; no hidden setKeys/post-frame instruction");
    {struct Fixture a,b;struct BvTimeline t;init(&a,0,2,0,8,0);init(&b,1,2,0,8,0);attach(&a);attach(&b);enable(&b,&t,"typed-match-private.bin");
     FILE *stream=tmpfile();assert(stream);assert(!bv_native_frame(&a.runtime,1,0,stream,0));assert(!bv_native_finish(&a.runtime));rewind(stream);
     assert(!bv_native_frame(&b.runtime,1,1,stream,0)&&!bv_native_finish(&b.runtime));assert(fgetc(stream)==EOF);equal(&a,&b);queueEqual(&a,&b);
     closeFixture(&a);closeT(&b,&t);fclose(stream);cases++;}
    puts("PASS strict complete2560/typed B/F/E stream unchanged with trace enabled");
    {struct Fixture f;struct BvTimeline t;init(&f,0,2,0,8,0);attach(&f);enable(&f,&t,"capacity-private.bin");t.limit=69;
     ((struct ARMCore*)f.core->cpu)->nextEvent=11; /* Explicit instruction-ready synthetic initial state. */
     struct ARMCore cpu=*(struct ARMCore*)f.core->cpu;struct GBA gba=*(struct GBA*)f.core->board;
     assert(bv_native_frame(&f.runtime,0,0,NULL,0)==119);
     assert(!memcmp(&cpu,f.core->cpu,sizeof cpu)&&!memcmp(&gba,f.core->board,sizeof gba));
     assert(bv_native_frame(&f.runtime,0,0,NULL,0)==119);assert(!memcmp(&cpu,f.core->cpu,sizeof cpu));
     assert(bv_tl_close(&t)==119);((struct GBA*)f.core->board)->memory.rom=NULL;closeFixture(&f);cases++;}
    {struct Fixture f;struct BvTimeline t;init(&f,0,0,1,1,0);attach(&f);enable(&f,&t,"due-capacity-private.bin");t.limit=2;
     struct ARMCore cpu=*(struct ARMCore*)f.core->cpu;struct GBA gba=*(struct GBA*)f.core->board;
     assert(bv_native_frame(&f.runtime,0,0,NULL,0)==119&&f.events==0);
     assert(!memcmp(&cpu,f.core->cpu,sizeof cpu)&&!memcmp(&gba,f.core->board,sizeof gba));
     assert(bv_tl_close(&t)==119);((struct GBA*)f.core->board)->memory.rom=NULL;closeFixture(&f);cases++;}
    puts("PASS capacity fails before next instruction or due event, immutable first failure/no CPU/event/stream advancement");
    {struct Fixture f;struct BvTimeline t;init(&f,0,2,0,8,0);attach(&f);enable(&f,&t,"bad-prefetch-private.bin");t.config.point[BV_TL_READ_ENTRY].opcode^=1;
     ((struct ARMCore*)f.core->cpu)->nextEvent=11;
     struct ARMCore cpu=*(struct ARMCore*)f.core->cpu;assert(bv_native_frame(&f.runtime,0,0,NULL,0)==119);assert(!memcmp(&cpu,f.core->cpu,sizeof cpu));
     assert(bv_tl_close(&t)==119);((struct GBA*)f.core->board)->memory.rom=NULL;closeFixture(&f);cases++;}
    {struct Fixture f;struct BvTimeline t;init(&f,0,0,0,5,0);attach(&f);enable(&f,&t,"bad-queue-private.bin");
     ((unsigned char*)((struct GBA*)f.core->board)->memory.wram)[0x3a000]=65;
     struct ARMCore cpu=*(struct ARMCore*)f.core->cpu;assert(bv_native_frame(&f.runtime,0,0,NULL,0)==119);assert(!memcmp(&cpu,f.core->cpu,sizeof cpu));
     assert(bv_tl_close(&t)==119);((struct GBA*)f.core->board)->memory.rom=NULL;closeFixture(&f);cases++;}
    {struct Fixture f;struct BvTimeline t;init(&f,0,0,0,5,0);attach(&f);enable(&f,&t,"queue-cycle-private.bin");f.event.next=&f.event;
     struct ARMCore cpu=*(struct ARMCore*)f.core->cpu;assert(bv_native_frame(&f.runtime,0,0,NULL,0)==119);assert(!memcmp(&cpu,f.core->cpu,sizeof cpu));
     assert(bv_tl_close(&t)==119);mTimingClear(&((struct GBA*)f.core->board)->timing);((struct GBA*)f.core->board)->memory.rom=NULL;closeFixture(&f);cases++;}
    puts("PASS corrupt opcode/oversized queue/cyclic event chain fail closed without execution");
    {struct Fixture f;struct BvTimeline t,other;init(&f,0,0,0,5,0);attach(&f);enable(&f,&t,"exclusive-private.bin");
     struct BvTimelineConfig c=config(&f);assert(bv_tl_open(&other,f.core,&c,"exclusive-private.bin")==119);assert(!other.file&&!other.buffer);
     closeT(&f,&t);cases++;}
    puts("PASS private mode0600 exclusive create; existing evidence never overwritten");
    for(unsigned bad=0;bad<7;bad++){
        struct Fixture f;struct BvTimeline t;init(&f,0,2,0,8,0);struct GBA *g=f.core->board;
        g->memory.rom=f.code;g->memory.romSize=4096;struct BvTimelineConfig c=config(&f);
        if(bad==0)c.seen=0;
        if(bad==1)c.point[3].seen=7;
        if(bad==2)c.mainAddress=0x02040000;
        if(bad==3)c.point[3].opcode^=1;
        if(bad==4)c.point[3].pc++;
        if(bad==5)c.point[3].mode=2;
        if(bad==6)g->memory.rom=NULL;
        struct ARMCore cpu=*(struct ARMCore*)f.core->cpu;struct GBA board=*g;
        snprintf(path,sizeof path,"preflight-%u-private.bin",bad);
        assert(bv_tl_open(&t,f.core,&c,path)==119&&!t.file&&!t.buffer&&access(path,F_OK));
        assert(!memcmp(&cpu,f.core->cpu,sizeof cpu)&&!memcmp(&board,g,sizeof board));g->memory.rom=NULL;closeFixture(&f);cases++;
    }
    puts("PASS7 incomplete/invalid pins/opcode/mode/span/missing synthetic code fail before file creation or execution");
    {struct Fixture a,b;struct BvTimeline t;init(&a,0,0,0,5,0);init(&b,1,0,0,5,0);attach(&b);enable(&b,&t,"io-failure-private.bin");ioFailure(&t);
     original(&a);assert(bv_native_frame(&b.runtime,0,0,NULL,0)==119);equal(&a,&b);queueEqual(&a,&b);
     struct ARMCore cpu=*(struct ARMCore*)b.core->cpu;assert(bv_native_frame(&b.runtime,0,0,NULL,0)==119);assert(!memcmp(&cpu,b.core->cpu,sizeof cpu));
     assert(bv_tl_close(&t)==119);((struct GBA*)b.core->board)->memory.rom=NULL;closeFixture(&a);closeFixture(&b);cases++;}
    puts("PASS write EIO fails after original frame, before any further execution; failed record never treated complete");
    {struct Fixture f;struct BvTimeline t;init(&f,0,2,0,8,0);attach(&f);enable(&f,&t,"queue-items-private.bin");
     struct GBA *g=f.core->board;unsigned char *ram=(unsigned char*)g->memory.wram;
     ram[0x3a000]=2;ram[0x3a001]=1;
     for(unsigned i=0;i<2;i++){bv_native_u32(ram+0x3a010+12*i,0x08010000+2048*i);bv_native_u32(ram+0x3a014+12*i,0x06010000+2048*i);ram[0x3a018+12*i+1]=8;}
     t.config.point[BV_TL_COPY]=t.config.point[BV_TL_READ_ENTRY];immutable(&f,&t);
     assert(t.buffer[0].word[BV_TL_COPY_BYTES]==4096&&t.used==3);
     assert(t.buffer[1].word[BV_TL_EVENT]==BV_TL_QUEUE&&t.buffer[1].word[BV_TL_SIZE]==2048);
     assert(t.buffer[2].word[BV_TL_SRC]==0x08010800&&t.buffer[2].word[BV_TL_DEST]==0x06010800);
     assert(!bv_tl_flush(&t,0,0));closeT(&f,&t);cases++;}
    puts("PASS source-pinned queue stride/size/ordered descriptors, direct read only");
    {struct Fixture a,b;struct BvTimeline t;init(&a,0,2,0,8,0);attach(&a);FILE *stream=tmpfile();assert(stream);assert(!bv_native_frame(&a.runtime,1,0,stream,0));
     assert(!fseek(stream,0,SEEK_SET));int byte=fgetc(stream);assert(!fseek(stream,0,SEEK_SET));assert(fputc(byte^1,stream)!=EOF);rewind(stream);
     init(&b,1,2,0,8,0);attach(&b);enable(&b,&t,"strict-stop-private.bin");assert(bv_native_frame(&b.runtime,1,1,stream,0)==117);
     struct ARMCore cpu=*(struct ARMCore*)b.core->cpu;long pos=ftell(stream);unsigned records=t.total;
     assert(bv_native_frame(&b.runtime,1,1,stream,0)==117&&ftell(stream)==pos&&t.total==records);assert(!memcmp(&cpu,b.core->cpu,sizeof cpu));
     closeFixture(&a);closeT(&b,&t);fclose(stream);cases++;}
    {struct Fixture a,b;struct BvTimeline t;init(&a,0,2,0,8,0);attach(&a);FILE *stream=tmpfile();assert(stream);assert(!bv_native_frame(&a.runtime,1,0,stream,0));
     rewind(stream);int byte=fgetc(stream);rewind(stream);assert(fputc(byte^1,stream)!=EOF);rewind(stream);
     init(&b,1,2,0,8,0);attach(&b);enable(&b,&t,"first-reason-private.bin");ioFailure(&t);
     assert(bv_native_frame(&b.runtime,1,1,stream,0)==117&&t.reason==119&&b.runtime.failure.reason==117);
     assert(bv_native_frame(&b.runtime,1,1,stream,0)==117);
     assert(bv_tl_close(&t)==119);((struct GBA*)b.core->board)->memory.rom=NULL;closeFixture(&a);closeFixture(&b);fclose(stream);cases++;}
    puts("PASS original strict117 remains first failure even when trace retention also fails119");
    printf("PASS strict typed first mismatch retained/no post-stop stepping or realignment; total%u synthetic timeline cases\n",cases);
    return 0;
}
