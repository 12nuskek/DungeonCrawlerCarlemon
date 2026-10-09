/* Offline diagnostics fixture. Reuse installed synthetic interpreter helpers;
 * its historical main is compiled but not called. No ROM/Save/reset/gameplay. */
#define _GNU_SOURCE
#define main bv_prior_interpreter_fixture_not_called
#include "v01-native-boundary-interpreter-fixture.c"
#undef main
#include <errno.h>
struct Cookie {
    unsigned char data[128];size_t size,pos;
    unsigned errorAtEnd,shortWrite,mutateCount;
    struct BvNativeRuntime *runtime;
};
static ssize_t cookieRead(void *context,char *data,size_t size)
{
    struct Cookie *c=context;
    if(c->pos==c->size){if(c->errorAtEnd){errno=EIO;return -1;}return 0;}
    if(size>c->size-c->pos)size=c->size-c->pos;
    memcpy(data,c->data+c->pos,size);c->pos+=size;
    if(c->mutateCount && c->pos==c->size)c->runtime->sequence.frameCount++;
    return (ssize_t)size;
}
static ssize_t cookieWrite(void *context,const char *data,size_t size)
{
    struct Cookie *c=context;(void)data;
    if(c->shortWrite){errno=EIO;return size?1:0;}
    c->pos+=size;return (ssize_t)size;
}
static int cookieSeek(void *context,off64_t *offset,int whence)
{
    struct Cookie *c=context;off64_t target=*offset;
    if(whence==SEEK_CUR)target+=(off64_t)c->pos;
    else if(whence==SEEK_END)target+=(off64_t)c->size;
    if(target<0){errno=EINVAL;return -1;}c->pos=(size_t)target;*offset=target;return 0;
}
static FILE *cookieFile(struct Cookie *c,const char *mode)
{
    cookie_io_functions_t io={.read=cookieRead,.write=cookieWrite,.seek=cookieSeek};
    FILE *f=fopencookie(c,mode,io);assert(f);assert(!setvbuf(f,NULL,_IONBF,0));return f;
}
static void state(struct Fixture *f,FILE *stream,unsigned candidate)
{
    init(f,0,0,1,1,0);attach(f);
    struct BvNativeRuntime *r=&f->runtime;r->stream=stream;r->candidate=candidate;r->started=1;
    r->video=7;r->inputEpoch=9;r->lastInput=0x12345678;r->lastCount=3;
    r->sequence=(struct BvBoundarySequence){.ordinal=42,.videoEpoch=7,.inputEpoch=9,.seen=1};
}
static void sticky(struct Fixture *f,unsigned origin)
{
    static unsigned serial;
    struct BvNativeRuntime *r=&f->runtime;struct BvNativeFailure saved=r->failure;
    assert(saved.present&&saved.reason==117&&saved.origin==origin&&r->reason==117);
    struct ARMCore cpu=*(struct ARMCore *)f->core->cpu;struct GBA *gba=f->core->board;
    uint32_t time=mTimingCurrentTime(&gba->timing);uint64_t global=gba->timing.globalCycles;
    long pos=ftell(r->stream);struct BvBoundarySequence seq=r->sequence;
    assert(bv_native_metadata(r,'E',77)==117);assert(bv_native_sample(r)==117);
    assert(bv_native_compare(r,999,1,2,3,4)==117);
    assert(bv_native_observe(r)==117);assert(bv_native_fail(r,103)==117);
    assert(bv_native_frame(r,1,r->candidate,r->stream,999)==117);assert(bv_native_finish(r)==117);
    assert(!memcmp(&saved,&r->failure,sizeof saved));assert(!memcmp(&seq,&r->sequence,sizeof seq));
    assert(!memcmp(&cpu,f->core->cpu,sizeof cpu)&&(uint32_t)mTimingCurrentTime(&gba->timing)==time&&gba->timing.globalCycles==global);
    assert(ftell(r->stream)==pos);
    char privatePath[80],safePath[80];serial++;
    snprintf(privatePath,sizeof privatePath,"case-%03u-%u-private.json",serial,origin);
    snprintf(safePath,sizeof safePath,"case-%03u-%u-safe.json",serial,origin);
    assert(bv_diag_write(&r->failure,privatePath,1)&&bv_diag_write(&r->failure,safePath,0));
    assert(!bv_diag_write(&r->failure,privatePath,1)&&!bv_diag_write(&r->failure,safePath,0));
    assert(!memcmp(&saved,&r->failure,sizeof saved)&&ftell(r->stream)==pos&&!memcmp(&cpu,f->core->cpu,sizeof cpu));
}
static void release(struct Fixture *f,FILE *stream)
{closeFixture(f);fclose(stream);}
static void changedKeys(struct mTiming *timing,void *context,uint32_t late)
{struct Fixture *f=context;event(timing,context,late);f->core->setKeys(f->core,0x80);}
int main(void)
{
    setvbuf(stdout,NULL,_IONBF,0);unsigned metadataCases=0,shortCases=0;
    const unsigned kinds[]={'B','F','E'};
    for(unsigned k=0;k<3;k++)for(unsigned i=0;i<29;i++){
        struct Fixture f;FILE *stream=tmpfile();assert(stream);state(&f,stream,1);
        unsigned char expected[29];bv_native_header(&f.runtime,expected,kinds[k],3,f.runtime.lastInput);expected[i]^=1;
        assert(fwrite(expected,1,29,stream)==29);rewind(stream);
        struct ARMCore before=*(struct ARMCore *)f.core->cpu;
        assert(bv_native_metadata(&f.runtime,kinds[k],3)==117);
        const struct BvNativeFailure *d=&f.runtime.failure;
        assert(d->firstDifference==i&&d->metadata.headerReadBytes==29&&d->metadata.operationReadBytes==29);
        assert(d->metadata.kind==kinds[k]&&d->metadata.startPosition==0&&d->metadata.endPosition==29);
        assert(!memcmp(d->metadata.expected,expected,29)&&d->metadata.actualSource==BV_HEADER_RECORD&&d->metadata.expectedSource==BV_HEADER_RECORD);
        assert(d->ordinal==42&&d->video==7&&d->inputEpoch==9&&d->lastCount==3&&d->cpuAvailable);
        assert(d->pc==(unsigned)before.gprs[ARM_PC]&&d->cycles==before.cycles&&d->nextEvent==before.nextEvent);
        assert(!memcmp(&before,f.core->cpu,sizeof before));sticky(&f,BV_FAIL_METADATA_DIFFERENT);
        if(k==0&&i==25){
            assert(bv_diag_write(d,"private.json",1)&&bv_diag_write(d,"safe.json",0));
            assert(!bv_diag_write(d,"private.json",1)&&!bv_diag_write(d,"safe.json",0));
            assert(!bv_diag_write(d,"missing-dir/diagnostic.json",1));
        }
        release(&f,stream);metadataCases++;
    }
    printf("PASS %u typed-header mutations: B/F/E every29 byte, wrong kind/ordinal/video/input/count/absolute-frame/keys, exact first offset and original29 read; immutable failure and CPU/stream/ordinal\n",metadataCases);
    /* Exact production hardware-hook entry, not only direct metadata calls.
     * Reference is separately recorded from synthetic instructions/events. */
    for(unsigned i=0;i<29;i++){
        struct Fixture a,b;init(&a,0,2,0,8,0);attach(&a);FILE *stream=tmpfile();
        assert(!bv_native_frame(&a.runtime,1,0,stream,0));
        assert(!fseek(stream,i,SEEK_SET));int value=fgetc(stream);assert(value!=EOF);
        assert(!fseek(stream,i,SEEK_SET));fputc(value^1,stream);rewind(stream);
        init(&b,1,2,0,8,0);attach(&b);assert(bv_native_frame(&b.runtime,1,1,stream,0)==117);
        assert(b.runtime.failure.firstDifference==i&&b.runtime.failure.metadata.endPosition==29);
        assert(b.runtime.failure.pc==0x080008ae&&b.runtime.failure.lr==0x080004bf&&b.runtime.failure.ordinal==0&&b.seen==0);
        sticky(&b,BV_FAIL_METADATA_DIFFERENT);closeFixture(&a);release(&b,stream);
    }
    puts("PASS installed hardware entry every29 header byte: retained actual PC/LR/timing, zero snapshot acceptance/entry instruction, sticky failure without stream/CPU advancement");
    for(unsigned error=0;error<2;error++)for(unsigned n=0;n<29;n++){
        struct Cookie c={.size=n,.errorAtEnd=error};FILE *stream=cookieFile(&c,"r");struct Fixture f;state(&f,stream,1);
        bv_native_header(&f.runtime,c.data,'B',3,f.runtime.lastInput);
        assert(bv_native_metadata(&f.runtime,'B',3)==117);const struct BvNativeFailure *d=&f.runtime.failure;
        assert(d->firstDifference==n&&d->metadata.expectedBytes==n&&d->metadata.headerReadBytes==n&&d->metadata.operationReadBytes==n);
        assert(d->metadata.startPosition==0&&d->metadata.endPosition==n&&d->metadata.ioError==error&&d->metadata.eof==!error);
        assert(d->metadata.ioErrno==(error?EIO:0));assert(!memcmp(d->metadata.actual,d->metadata.expected,n));
        for(unsigned i=n;i<29;i++)assert(!d->metadata.expected[i]);
        sticky(&f,BV_FAIL_METADATA_SHORT);release(&f,stream);shortCases++;
    }
    {struct Cookie c={.size=8};FILE *stream=cookieFile(&c,"r");struct Fixture f;state(&f,stream,1);
     bv_native_header(&f.runtime,c.data,'B',3,f.runtime.lastInput);c.data[2]^=1;assert(bv_native_metadata(&f.runtime,'B',3)==117);
     assert(f.runtime.failure.origin==BV_FAIL_METADATA_SHORT&&f.runtime.failure.firstDifference==2);release(&f,stream);}
    printf("PASS %u short headers: all0..28 original read lengths, EOF and EIO, zero unread tail distinguished; earlier prefix mismatch retained without realignment\n",shortCases);
    {struct Cookie c={.size=1};cookie_io_functions_t io={.read=cookieRead};
     FILE *stream=fopencookie(&c,"r",io);assert(stream);assert(!setvbuf(stream,NULL,_IONBF,0));struct Fixture f;state(&f,stream,1);
     c.data[0]='B';assert(bv_native_metadata(&f.runtime,'B',3)==117);
     assert(f.runtime.failure.metadata.startPosition==-1&&f.runtime.failure.metadata.endPosition==-1&&f.runtime.failure.metadata.headerReadBytes==1);
     assert(!f.runtime.failure.metadata.ioErrno);sticky(&f,BV_FAIL_METADATA_SHORT);release(&f,stream);}
    {struct Cookie c={.shortWrite=1};FILE *stream=cookieFile(&c,"w");struct Fixture f;state(&f,stream,0);
     assert(bv_native_metadata(&f.runtime,'F',0)==117);const struct BvNativeFailure *d=&f.runtime.failure;
     assert(d->metadata.writeBytes==1&&d->metadata.headerReadBytes==0&&d->metadata.expectedSource==BV_HEADER_OUTPUT&&d->firstDifference==29);
     sticky(&f,BV_FAIL_METADATA_WRITE);release(&f,stream);}
    for(unsigned variant=0;variant<3;variant++){
        FILE *stream=tmpfile();struct Fixture f;state(&f,stream,0);assert(!bv_native_metadata(&f.runtime,'B',0));
        assert(bv_native_compare(&f.runtime,42+(variant==0),7,7+(variant==1),9,9+(variant==2))==117);
        assert(f.runtime.failure.expectedOrdinal==42+(variant==0));
        assert(f.runtime.failure.guardVideo==7&&f.runtime.failure.guardExpectedVideo==7+(variant==1));
        assert(f.runtime.failure.guardInput==9&&f.runtime.failure.guardExpectedInput==9+(variant==2));
        sticky(&f,BV_FAIL_BOUNDARY_SEQUENCE);release(&f,stream);
    }
    puts("PASS metadata short write and original boundary sequence ordinal/video/input guard failures; original accepted headers distinct from guard values");
    {struct Fixture f;init(&f,0,0,1,1,0);attach(&f);f.event.callback=changedKeys;
     FILE *stream=tmpfile();assert(bv_native_frame(&f.runtime,1,0,stream,0)==117);
     const struct BvNativeFailure *d=&f.runtime.failure;
     assert(f.events==1&&f.core->frameCounter(f.core)==1&&d->keysAtFrameStart==0&&d->observedKeys==0x80);
     assert(d->metadata.actualSource==BV_HEADER_GUARD&&d->metadata.expectedSource==BV_HEADER_GUARD&&d->firstDifference==25&&ftell(stream)==0);
     assert(d->metadata.headerReadBytes==0&&d->metadata.actual[0]=='F');sticky(&f,BV_FAIL_FRAME_KEYS);release(&f,stream);}
    for(unsigned count=0;count<4;count++){
        struct Cookie c={.size=29,.mutateCount=1};FILE *stream=cookieFile(&c,"r");struct Fixture f;
        init(&f,0,0,1,1,0);attach(&f);c.runtime=&f.runtime;f.runtime.sequence.frameCount=count;
        f.runtime.inputEpoch=1;bv_native_header(&f.runtime,c.data,'F',count,f.runtime.lastInput);bv_native_u32(c.data+21,1);f.runtime.inputEpoch=0;
        assert(bv_native_frame(&f.runtime,1,1,stream,0)==117);const struct BvNativeFailure *d=&f.runtime.failure;
        assert(d->frameCount==count+1&&d->expectedCount==count&&d->firstDifference==29);
        assert(d->metadata.headerReadBytes==29&&!memcmp(d->metadata.actual,d->metadata.expected,29));
        assert(d->metadata.actualSource==BV_HEADER_RECORD);sticky(&f,BV_FAIL_FRAME_COUNT);release(&f,stream);
    }
    for(unsigned count=1;count<5;count++){
        FILE *stream=tmpfile();struct Fixture f;state(&f,stream,1);f.runtime.sequence.frameCount=count;
        assert(bv_native_finish(&f.runtime)==117);const struct BvNativeFailure *d=&f.runtime.failure;
        assert(d->frameCount==count&&d->expectedCount==0&&d->firstDifference==17&&d->metadata.kind=='E');
        assert(d->metadata.actualSource==BV_HEADER_GUARD&&d->metadata.headerReadBytes==0&&ftell(stream)==0);
        sticky(&f,BV_FAIL_FINISH_SEQUENCE);release(&f,stream);
    }
    puts("PASS installed due-event frame-key failure without extra instruction; four frame-count and four finish-count guard cases; matched actual headers never replaced by invented mismatches");
    for(unsigned error=0;error<2;error++){
        struct Cookie c={.size=error?29:30,.errorAtEnd=error};FILE *stream=cookieFile(&c,"r");struct Fixture f;state(&f,stream,1);
        bv_native_header(&f.runtime,c.data,'E',0,f.runtime.lastInput);c.data[29]=0xab;
        assert(bv_native_finish(&f.runtime)==117);const struct BvNativeFailure *d=&f.runtime.failure;
        assert(d->metadata.kind=='E'&&d->firstDifference==29&&d->metadata.headerReadBytes==29);
        assert(d->metadata.startPosition==29&&d->metadata.endPosition==(int64_t)c.size&&d->metadata.operationReadBytes==!error);
        assert(d->trailingPresent==!error&&d->metadata.ioError==error&&d->metadata.ioErrno==(error?EIO:0));
        if(!error)assert(d->trailingByte==0xab);
        sticky(&f,error?BV_FAIL_TRAILING_IO:BV_FAIL_TRAILING_BYTE);release(&f,stream);
    }
    {FILE *stream=tmpfile();struct Fixture f;state(&f,stream,0);assert(bv_native_fail(&f.runtime,117)==117);
     sticky(&f,BV_FAIL_FALLBACK);release(&f,stream);}
    {FILE *stream=tmpfile();struct Fixture f;state(&f,stream,1);unsigned char header[29];bv_native_header(&f.runtime,header,'B',0,f.runtime.lastInput);
     assert(fwrite(header,1,29,stream)==29);fputc(0,stream);rewind(stream);assert(bv_native_sample(&f.runtime)==103);
     assert(!f.runtime.failure.present&&f.runtime.expectedBytes==1&&ftell(stream)==30);release(&f,stream);}
    puts("PASS one original trailing read: unexpected byte and EIO retained with accepted E header; fallback117 first-only; truncated full snapshot remains103");
    /* Export a separate first failure using the exact host retention entry;
     * a repeated call must not overwrite or advance anything. */
    {FILE *stream=tmpfile();struct Fixture f;state(&f,stream,1);assert(bv_native_metadata(&f.runtime,'B',0)==117);
     bv_native_retain_failure(&f.runtime);assert(f.runtime.retentionAttempted&&f.runtime.privateDiagnosticRetained&&f.runtime.safeDiagnosticRetained);
     bv_native_retain_failure(&f.runtime);sticky(&f,BV_FAIL_METADATA_SHORT);release(&f,stream);}
    {FILE *stream=tmpfile();struct Fixture f;state(&f,stream,0);assert(bv_native_fail(&f.runtime,117)==117);
     bv_native_retain_failure(&f.runtime);assert(f.runtime.retentionAttempted&&!f.runtime.privateDiagnosticRetained&&!f.runtime.safeDiagnosticRetained);
     bv_native_retain_failure(&f.runtime);sticky(&f,BV_FAIL_FALLBACK);release(&f,stream);}
    puts("PASS all10 STOP117 origins, first-only host retention/O_EXCL/missing-directory and existing-file failure, nonseekable position=-1; safe projection and exact private header exported for offline schema checks; ZERO gameplay/new claims");
    return 0;
}
