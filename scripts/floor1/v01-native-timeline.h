/* Passive sidecar. Direct reads only; no bus API, callback substitution, keys,
 * CPU writes, scheduling, debugger calls or execution. File I/O occurs outside
 * interpreter/event dispatch. Actual binary records stay private/local. */
#ifndef V01_NATIVE_TIMELINE_H
#define V01_NATIVE_TIMELINE_H
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <mgba/core/core.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/gba/io.h>
/* Pinned route: 2044 boot steps, then the generated host's 36000-frame guard.
 * Each frame can retain at most one 4096-record buffer (including its marker).
 * Add the largest pre-instruction reserve and one final terminal marker. This
 * is a route/buffer proof, independent of observed trace density. */
enum { BV_TL_POINTS=21, BV_TL_WORDS=46, BV_TL_BUFFER=4096,
       BV_TL_PREVISUAL_FRAMES=2044, BV_TL_VISUAL_FRAMES=36000,
       BV_TL_FRAME_CALLS=BV_TL_PREVISUAL_FRAMES+BV_TL_VISUAL_FRAMES,
       BV_TL_INSTRUCTION_RESERVE=70, BV_TL_TERMINAL_RECORDS=1,
       BV_TL_LIMIT=BV_TL_FRAME_CALLS*BV_TL_BUFFER
           +BV_TL_INSTRUCTION_RESERVE+BV_TL_TERMINAL_RECORDS,
       BV_TL_QUEUE_LIMIT=64, BV_TL_FAILURE=119 };
_Static_assert(BV_TL_LIMIT==155828295, "Pinned route capacity changed");
_Static_assert(sizeof(unsigned)>=4, "Timeline counters require 32 bits");
enum { BV_TL_BEFORE=1,BV_TL_AFTER,BV_TL_EVENTS_BEFORE,BV_TL_EVENTS_AFTER,
       BV_TL_VIDEO_AFTER_DRAIN,BV_TL_FRAME,BV_TL_FINISH,BV_TL_STOP,BV_TL_QUEUE };
enum { BV_TL_READ_CALL,BV_TL_READ_ENTRY,BV_TL_READ_EXIT,BV_TL_DISPATCH,
       BV_TL_CB1_RESUME,BV_TL_CB2_RESUME,BV_TL_DISPATCH_EXIT,BV_TL_WAIT,
       BV_TL_WAIT_CLEAR,BV_TL_WAIT_EXIT,BV_TL_VBLANK,BV_TL_BIOS_SET,
       BV_TL_MAIN_SET,BV_TL_VBLANK_EXIT,BV_TL_COPY,BV_TL_COPY_EXIT,
       BV_TL_VBCB,BV_TL_VBCB_EXIT,BV_TL_PLAYTIME,BV_TL_MUSIC,BV_TL_IRQ,
       BV_TL_CB1_ENTRY,BV_TL_CB2_ENTRY };
enum { BV_TL_EVENT,BV_TL_PHASE,BV_TL_PC,BV_TL_RAWPC,BV_TL_LR,BV_TL_CPSR,
       BV_TL_MODE,BV_TL_PRIV,BV_TL_HALTED,BV_TL_CYCLES,BV_TL_NEXT,
       BV_TL_TIME,BV_TL_MASTER,BV_TL_GLOBAL_LO,BV_TL_GLOBAL_HI,BV_TL_VIDEO,
       BV_TL_IE,BV_TL_IF,BV_TL_IME,BV_TL_FLAG,BV_TL_BIOS_FLAG,BV_TL_CB1,
       BV_TL_CB2,BV_TL_VBLANK_CB,BV_TL_ROOT,BV_TL_ROOT_WHEN,BV_TL_ROOT_PRIORITY,
       BV_TL_IRQ_PENDING,BV_TL_IRQ_WHEN,BV_TL_IRQ_PRIORITY,BV_TL_REROOT,
       BV_TL_COPY_COUNT,BV_TL_COPY_ARMED,BV_TL_COPY_BYTES,BV_TL_COPY_HASH,
       BV_TL_READ_ITER,BV_TL_DISPATCH_ITER,BV_TL_CB1_ITER,BV_TL_CB2_ITER,
       BV_TL_INPUT_EPOCH,BV_TL_VISUAL_EPOCH,BV_TL_POINT,BV_TL_SRC,BV_TL_DEST,
       BV_TL_SIZE,BV_TL_INDEX };
struct BvTimelinePoint {unsigned pc,rom,opcode,mode,seen;};
struct BvTimelineConfig {unsigned mainAddress,copyCount,copyArmed,copies,seen;struct BvTimelinePoint point[BV_TL_POINTS];};
struct BvTimelineRecord {uint32_t word[BV_TL_WORDS];};
struct BvTimelineStorage;
struct BvTimeline {
    struct mCore *core;struct BvTimelineConfig config;
    struct BvTimelineRecord *buffer,eventsBefore;
    FILE *file;unsigned used,total,limit,reason,pending,reads,dispatches,cb1,cb2,stopped;
    unsigned inputEpoch,visualEpoch;
    struct BvTimelineStorage *storage;
    unsigned flushReason,flushFinish;
};
static inline unsigned bv_tl_valid_ram(unsigned a,unsigned n)
{return (a>=0x02000000&&a<=0x02040000&&n<=0x02040000-a)
     || (a>=0x03000000&&a<=0x03008000&&n<=0x03008000-a);}
static inline unsigned bv_tl_read(const struct GBA *g,unsigned a,unsigned n)
{
    const unsigned char *p=a>=0x03000000?(const unsigned char*)g->memory.iwram+a-0x03000000
        :(const unsigned char*)g->memory.wram+a-0x02000000;
    unsigned v=0;for(unsigned i=0;i<n;i++)v|=(unsigned)p[i]<<(8*i);return v;
}
static inline unsigned bv_tl_event_id(const struct GBA *g,const struct mTimingEvent *e)
{
    if(!e)return 0;
    if(e==&g->irqEvent)return 1;
    if(e==&g->video.event)return 2;
    if(e==&g->memory.dmaEvent)return 3;
    return 4; /* Other event, never inferred IRQ. */
}
static inline unsigned bv_tl_collect(struct BvTimeline *t,struct BvTimelineRecord *record)
{
    const struct ARMCore *c=t->core->cpu;const struct GBA *g=t->core->board;
    memset(record,0,sizeof *record);uint32_t *w=record->word;
    w[BV_TL_PC]=(unsigned)c->gprs[ARM_PC]-(c->executionMode==MODE_THUMB?2:4);
    w[BV_TL_RAWPC]=c->gprs[ARM_PC];w[BV_TL_LR]=c->gprs[ARM_LR];w[BV_TL_CPSR]=c->cpsr.packed;
    w[BV_TL_MODE]=c->executionMode;w[BV_TL_PRIV]=c->privilegeMode;w[BV_TL_HALTED]=c->halted;
    w[BV_TL_CYCLES]=(uint32_t)c->cycles;w[BV_TL_NEXT]=(uint32_t)c->nextEvent;
    w[BV_TL_TIME]=g->timing.masterCycles+c->cycles;w[BV_TL_MASTER]=g->timing.masterCycles;
    uint64_t global=g->timing.globalCycles+c->cycles;
    w[BV_TL_GLOBAL_LO]=(uint32_t)global;w[BV_TL_GLOBAL_HI]=(uint32_t)(global>>32);
    w[BV_TL_VIDEO]=g->video.frameCounter;w[BV_TL_IE]=g->memory.io[REG_IE/2];
    w[BV_TL_IF]=g->memory.io[REG_IF/2];w[BV_TL_IME]=g->memory.io[REG_IME/2];
    w[BV_TL_FLAG]=bv_tl_read(g,t->config.mainAddress+28,2);w[BV_TL_BIOS_FLAG]=bv_tl_read(g,0x03007ff8,2);
    w[BV_TL_CB1]=bv_tl_read(g,t->config.mainAddress,4);w[BV_TL_CB2]=bv_tl_read(g,t->config.mainAddress+4,4);
    w[BV_TL_VBLANK_CB]=bv_tl_read(g,t->config.mainAddress+12,4);
    const struct mTimingEvent *root=g->timing.root?g->timing.root:g->timing.reroot;
    w[BV_TL_ROOT]=bv_tl_event_id(g,root);w[BV_TL_REROOT]=g->timing.reroot!=NULL;
    if(root){w[BV_TL_ROOT_WHEN]=root->when;w[BV_TL_ROOT_PRIORITY]=root->priority;}
    unsigned count=0;for(const struct mTimingEvent *e=root;e;e=e->next){
        if(++count>BV_TL_QUEUE_LIMIT)return t->reason=BV_TL_FAILURE;
        if(e==&g->irqEvent){w[BV_TL_IRQ_PENDING]=1;w[BV_TL_IRQ_WHEN]=e->when;w[BV_TL_IRQ_PRIORITY]=e->priority;}
    }
    w[BV_TL_COPY_COUNT]=bv_tl_read(g,t->config.copyCount,1);
    w[BV_TL_COPY_ARMED]=bv_tl_read(g,t->config.copyArmed,1);
    if(w[BV_TL_COPY_COUNT]>64)return t->reason=BV_TL_FAILURE;
    unsigned hash=2166136261u;
    for(unsigned i=0;i<w[BV_TL_COPY_COUNT];i++){
        unsigned a=t->config.copies+12*i;w[BV_TL_COPY_BYTES]+=bv_tl_read(g,a+8,2);
        for(unsigned j=0;j<10;j++)hash=(hash^bv_tl_read(g,a+j,1))*16777619u;
    }
    w[BV_TL_COPY_HASH]=hash;w[BV_TL_READ_ITER]=t->reads;w[BV_TL_DISPATCH_ITER]=t->dispatches;
    w[BV_TL_CB1_ITER]=t->cb1;w[BV_TL_CB2_ITER]=t->cb2;
    w[BV_TL_INPUT_EPOCH]=t->inputEpoch;w[BV_TL_VISUAL_EPOCH]=t->visualEpoch;return 0;
}
static inline unsigned bv_tl_reserve(struct BvTimeline *t,unsigned n)
{
    if(t->reason)return t->reason;
    if(n>BV_TL_BUFFER-t->used||t->total>t->limit||n>t->limit-t->total)return t->reason=BV_TL_FAILURE;
    return 0;
}
static inline unsigned bv_tl_append(struct BvTimeline *t,struct BvTimelineRecord record,unsigned event,unsigned point)
{
    if(bv_tl_reserve(t,1))return t->reason;
    record.word[BV_TL_EVENT]=event;record.word[BV_TL_POINT]=point;
    record.word[BV_TL_PHASE]=(event==BV_TL_BEFORE||event==BV_TL_EVENTS_BEFORE)?1:2;
    t->buffer[t->used++]=record;t->total++;return 0;
}
static inline unsigned bv_tl_before(struct BvTimeline *t)
{
    if(!t)return 0;
    if(bv_tl_reserve(t,BV_TL_INSTRUCTION_RESERVE))return t->reason;
    const struct ARMCore *c=t->core->cpu;const struct GBA *g=t->core->board;t->pending=0;
    if(c->halted)return 0;
    unsigned pc=(unsigned)c->gprs[ARM_PC]-(c->executionMode==MODE_THUMB?2:4),mask=0;
    for(unsigned i=0;i<BV_TL_POINTS;i++)if(pc==t->config.point[i].pc){
        const struct BvTimelinePoint *p=&t->config.point[i];
        if((unsigned)c->executionMode!=p->mode||c->prefetch[0]!=p->opcode)return t->reason=BV_TL_FAILURE;
        mask|=1u<<i;
    }
    if(c->executionMode==MODE_THUMB&&c->privilegeMode==MODE_SYSTEM){
        unsigned cb1=bv_tl_read(g,t->config.mainAddress,4),cb2=bv_tl_read(g,t->config.mainAddress+4,4);
        if(cb1&&pc==(cb1&~1u)&&(unsigned)c->gprs[ARM_LR]==(t->config.point[BV_TL_CB1_RESUME].pc|1u))mask|=1u<<BV_TL_CB1_ENTRY;
        if(cb2&&pc==(cb2&~1u)&&(unsigned)c->gprs[ARM_LR]==(t->config.point[BV_TL_CB2_RESUME].pc|1u))mask|=1u<<BV_TL_CB2_ENTRY;
    }
    if(!mask)return 0;
    if(mask&(1u<<BV_TL_READ_ENTRY))t->reads++;
    if(mask&(1u<<BV_TL_DISPATCH))t->dispatches++;
    if(mask&(1u<<BV_TL_CB1_ENTRY))t->cb1++;
    if(mask&(1u<<BV_TL_CB2_ENTRY))t->cb2++;
    struct BvTimelineRecord record;if(bv_tl_collect(t,&record))return t->reason;
    if(bv_tl_append(t,record,BV_TL_BEFORE,mask))return t->reason;
    if(mask&(1u<<BV_TL_COPY))for(unsigned i=0;i<record.word[BV_TL_COPY_COUNT];i++){
        struct BvTimelineRecord item=record;unsigned a=t->config.copies+12*i;
        item.word[BV_TL_SRC]=bv_tl_read(g,a,4);item.word[BV_TL_DEST]=bv_tl_read(g,a+4,4);
        item.word[BV_TL_SIZE]=bv_tl_read(g,a+8,2);item.word[BV_TL_INDEX]=i;
        if(bv_tl_append(t,item,BV_TL_QUEUE,mask))return t->reason;
    }
    t->pending=mask;return 0;
}
static inline unsigned bv_tl_after(struct BvTimeline *t)
{
    if(!t||!t->pending)return 0;
    struct BvTimelineRecord record;
    unsigned mask=t->pending;t->pending=0;if(bv_tl_collect(t,&record))return t->reason;
    return bv_tl_append(t,record,BV_TL_AFTER,mask);
}
static inline unsigned bv_tl_events_before(struct BvTimeline *t)
{if(!t)return 0;if(bv_tl_reserve(t,3))return t->reason;return bv_tl_collect(t,&t->eventsBefore);}
static inline unsigned bv_tl_events_after(struct BvTimeline *t)
{
    if(!t)return 0;
    struct BvTimelineRecord after;if(bv_tl_collect(t,&after))return t->reason;
    const uint32_t *a=t->eventsBefore.word,*b=after.word;
    if(a[BV_TL_VIDEO]==b[BV_TL_VIDEO]&&a[BV_TL_IRQ_PENDING]==b[BV_TL_IRQ_PENDING]
        &&a[BV_TL_IE]==b[BV_TL_IE]&&a[BV_TL_IF]==b[BV_TL_IF]&&a[BV_TL_IME]==b[BV_TL_IME]
        &&a[BV_TL_PRIV]==b[BV_TL_PRIV])return 0;
    if(bv_tl_append(t,t->eventsBefore,BV_TL_EVENTS_BEFORE,0)||bv_tl_append(t,after,BV_TL_EVENTS_AFTER,0))return t->reason;
    if(a[BV_TL_VIDEO]!=b[BV_TL_VIDEO])return bv_tl_append(t,after,BV_TL_VIDEO_AFTER_DRAIN,0);
    return 0;
}
static inline void bv_tl_symbol(struct BvTimelineConfig *c,unsigned value,const char *name)
{
    if(!strcmp(name,"bv_tlMain")){c->mainAddress=value;c->seen|=1;}
    else if(!strcmp(name,"bv_tlCopyCount")){c->copyCount=value;c->seen|=2;}
    else if(!strcmp(name,"bv_tlCopyArmed")){c->copyArmed=value;c->seen|=4;}
    else if(!strcmp(name,"bv_tlCopies")){c->copies=value;c->seen|=8;}
    unsigned i;char extra;
    if(sscanf(name,"bv_tlPC%u%c",&i,&extra)==1&&i<BV_TL_POINTS){c->point[i].pc=value;c->point[i].seen|=1;}
    else if(sscanf(name,"bv_tlROM%u%c",&i,&extra)==1&&i<BV_TL_POINTS){c->point[i].rom=value;c->point[i].seen|=2;}
    else if(sscanf(name,"bv_tlOP%u%c",&i,&extra)==1&&i<BV_TL_POINTS){c->point[i].opcode=value;c->point[i].seen|=4;}
    else if(sscanf(name,"bv_tlMODE%u%c",&i,&extra)==1&&i<BV_TL_POINTS){c->point[i].mode=value;c->point[i].seen|=8;}
}
static inline unsigned bv_tl_write_header(FILE *file)
{
    unsigned char header[16]={'B','V','T','I','M','E','0','2'};
    for(unsigned k=0;k<4;k++){
        header[8+k]=(uint32_t)BV_TL_WORDS>>(8*k);
        header[12+k]=(uint32_t)BV_TL_LIMIT>>(8*k);
    }
    return fwrite(header,1,sizeof header,file)!=sizeof header||fflush(file)||ferror(file)
        ?BV_TL_FAILURE:0;
}
#include "v01-native-timeline-storage.h"
static inline unsigned bv_tl_open(struct BvTimeline *t,struct mCore *core,const struct BvTimelineConfig *config,const char *path)
{
    memset(t,0,sizeof *t);t->core=core;t->config=*config;t->limit=BV_TL_LIMIT;
    const struct GBA *g=core->board;
    if(config->seen!=15||!bv_tl_valid_ram(config->mainAddress,32)||!bv_tl_valid_ram(config->copyCount,1)
        ||!bv_tl_valid_ram(config->copyArmed,1)||!bv_tl_valid_ram(config->copies,768))return t->reason=BV_TL_FAILURE;
    for(unsigned i=0;i<BV_TL_POINTS;i++){
        const struct BvTimelinePoint *p=&config->point[i];unsigned n=p->mode==MODE_THUMB?2:4;
        if(p->seen!=15||p->mode>1||p->rom<0x08000000||p->rom-0x08000000>g->memory.romSize
            ||n>g->memory.romSize-(p->rom-0x08000000)||!g->memory.rom)return t->reason=BV_TL_FAILURE;
        if(i==BV_TL_IRQ){if(p->mode!=MODE_ARM||!bv_tl_valid_ram(p->pc,4))return t->reason=BV_TL_FAILURE;}
        else if(p->pc!=p->rom||p->mode!=MODE_THUMB)return t->reason=BV_TL_FAILURE;
        const unsigned char *b=(const unsigned char*)g->memory.rom+p->rom-0x08000000;
        unsigned opcode=0;for(unsigned j=0;j<n;j++)opcode|=(unsigned)b[j]<<(8*j);
        if(opcode!=p->opcode)return t->reason=BV_TL_FAILURE;
    }
    t->buffer=calloc(BV_TL_BUFFER,sizeof *t->buffer);if(!t->buffer)return t->reason=BV_TL_FAILURE;
    int fd=open(path,O_WRONLY|O_CREAT|O_EXCL,0600);if(fd<0){free(t->buffer);t->buffer=NULL;return t->reason=BV_TL_FAILURE;}
    t->file=fdopen(fd,"wb");if(!t->file){close(fd);free(t->buffer);t->buffer=NULL;return t->reason=BV_TL_FAILURE;}
    if(bv_tl_write_header(t->file))return t->reason=BV_TL_FAILURE;
    return 0;
}
/* Same production serialization, usable offline with retained records and no
 * core/CPU. Never grows the buffer or treats a short write as a whole record. */
static inline unsigned bv_tl_write_buffer(struct BvTimeline *t)
{
    if(t->storage)return bv_tl_storage_write(t);
    for(unsigned i=0;i<t->used;i++){
        unsigned char bytes[BV_TL_WORDS*4];for(unsigned j=0;j<BV_TL_WORDS;j++)for(unsigned k=0;k<4;k++)bytes[4*j+k]=t->buffer[i].word[j]>>(8*k);
        if(fwrite(bytes,1,sizeof bytes,t->file)!=sizeof bytes||ferror(t->file)){t->reason=BV_TL_FAILURE;break;}
    }
    t->used=0;if(fflush(t->file)||ferror(t->file))t->reason=BV_TL_FAILURE;
    return t->reason;
}
static inline unsigned bv_tl_flush(struct BvTimeline *t,unsigned reason,unsigned finish)
{
    if(!t)return 0;
    if(t->stopped)return t->reason;
    t->flushReason=reason;t->flushFinish=finish;
    if(!t->reason){struct BvTimelineRecord r;if(!bv_tl_collect(t,&r))bv_tl_append(t,r,reason?BV_TL_STOP:finish?BV_TL_FINISH:BV_TL_FRAME,reason);}
    bv_tl_write_buffer(t);
    if(reason||finish||t->reason)t->stopped=1;
    return t->reason;
}
static inline unsigned bv_tl_close(struct BvTimeline *t)
{if(!t)return 0;if(bv_tl_storage_close(t))t->reason=BV_TL_FAILURE;if(t->file&&fclose(t->file))t->reason=BV_TL_FAILURE;t->file=NULL;free(t->buffer);t->buffer=NULL;return t->reason;}
#endif
