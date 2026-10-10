/* Scratch Apply instruction/guard experiment. No ROM/Save/reset/gameplay.
 * Only bounded ELF function/data segments enter synthetic instruction memory.
 * Unit ROM bus costs, synthetic RAM, CpuSet/queue stubs: not game cycle costs. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <mgba/core/core.h>
#include <mgba/gba/core.h>
#include <mgba/internal/arm/isa-inlines.h>
#include <mgba/internal/gba/gba.h>
static uint32_t *code;
static uint32_t (*load32)(struct ARMCore*,uint32_t,int*);
static void region(struct ARMCore *c,uint32_t address)
{
    (void)address;c->memory.activeRegion=code;c->memory.activeMask=0xffffff;
    c->memory.activeSeqCycles32=c->memory.activeSeqCycles16=1;
    c->memory.activeNonseqCycles32=c->memory.activeNonseqCycles16=1;
}
static uint32_t literal(struct ARMCore *c,uint32_t address,int *cycles)
{
    if(address>>24==8){if(cycles)*cycles+=1;return code[(address&0xffffff)/4];}
    return load32(c,address,cycles);
}
static void store(struct GBA *g,unsigned address,unsigned value)
{assert(address>=0x02000000&&address<0x02040000);memcpy((char*)g->memory.wram+address-0x02000000,&value,4);}
static void ret(struct ARMCore *c)
{c->executionMode=MODE_THUMB;c->cpsr.t=1;c->gprs[ARM_PC]=c->gprs[ARM_LR]&~1;ThumbWritePC(c);}
int main(int argc,char **argv)
{
    assert(argc==2);code=calloc(1,0x1000000);assert(code);
    FILE *f=fopen(argv[1],"rb");assert(f);unsigned start,count;
    assert(fread(&start,4,1,f)==1&&fread(&count,4,1,f)==1);
    for(unsigned i=0;i<count;i++){unsigned a,n;assert(fread(&a,4,1,f)==1&&fread(&n,4,1,f)==1);assert(a>=0x08000000&&a+n<=0x09000000);assert(fread((char*)code+(a&0xffffff),1,n,f)==n);}
    assert(fgetc(f)==EOF);fclose(f);
    for(unsigned same=0;same<2;same++)for(unsigned guard=0;guard<7;guard++){
        struct mCore *core=GBACoreCreate();assert(core&&core->init(core));
        struct GBA *g=core->board;struct ARMCore *c=core->cpu;
        mTimingClear(&g->timing);memset(g->memory.wram,0,0x40000);
        /* Battler0, sprite0, position0; all ownership fields are native offsets. */
        store(g,0x020244d4,guard==1?0:0x02028000);
        ((char*)g->memory.wram)[0x241e4]=guard==2?64:0;
        ((char*)g->memory.wram)[0x20630+0x3e]=guard==4?0:1;
        store(g,0x02020630+12,guard==5?0x02028094:0x02028074);
        store(g,0x02028004,guard==6?0:0x02030000);
        ((char*)g->memory.wram)[0x3cf68+3]=same?1:0;
        c->memory.setActiveRegion=region;region(c,start);load32=c->memory.load32;c->memory.load32=literal;
        ARMSetPrivilegeMode(c,MODE_SYSTEM);c->executionMode=MODE_THUMB;c->cpsr.packed=0x3f;
        c->gprs[ARM_SP]=0x03007c00;c->gprs[ARM_LR]=0x08000081;
        c->gprs[0]=0;c->gprs[1]=guard==3?17:0;c->gprs[ARM_PC]=start;ThumbWritePC(c);
        c->cycles=0;c->nextEvent=INT_MAX;
        unsigned steps=0,position=0,copies=0,bytes=0,requests=0;
        for(;steps<2000;steps++){
            unsigned pc=(unsigned)c->gprs[ARM_PC]-(c->executionMode==MODE_THUMB?2:4);
            if(pc==0x08000080)break;
            if(pc==0x080a6670)position++;
            if(pc==0x082ea928){ /* CpuSet synthetic copy semantics; no BIOS cost. */
                unsigned n=((unsigned)c->gprs[2]&0x1fffff)*4;assert(n==2048);
                unsigned src=c->gprs[0],dst=c->gprs[1];assert(src>=0x08000000&&src+n<=0x09000000&&dst>=0x02030000&&dst+n<=0x02032000);
                memcpy((char*)g->memory.wram+dst-0x02000000,(char*)code+(src&0xffffff),n);copies++;bytes+=n;ret(c);
            }else if(pc==0x080074ec){ /* RequestSpriteCopy address verified by driver. */
                assert(c->gprs[0]==0x02030000&&c->gprs[1]==0x06010000&&c->gprs[2]==2048);requests++;ret(c);
            }else ARMRun(c);
        }
        if(steps==2000)fprintf(stderr,"fixture instruction limit pc=%08x mode=%u r0=%08x r1=%08x copies=%u requests=%u\n",c->gprs[ARM_PC],c->executionMode,c->gprs[0],c->gprs[1],copies,requests);
        assert(steps<2000);
        unsigned applied=((unsigned char*)g->memory.wram)[0x3cf68+3];
        unsigned changed=guard==0&&!same;
        assert(copies==4*changed&&bytes==8192*changed&&requests==changed);
        assert(applied==(same||changed));
        for(unsigned i=0;i<8192;i++){
            unsigned char actual=((unsigned char*)g->memory.wram)[0x30000+i];
            unsigned source=code[(0x08e46bc4&0xffffff)/4];
            unsigned char expected=changed?((unsigned char*)code)[(source&0xffffff)+i%2048]:0;
            assert(actual==expected); /* All four frames exact; every blocked path writes none. */
        }
        printf("{\"samePose\":%u,\"guard\":%u,\"interpreterStepsIncludingStubs\":%u,\"syntheticCyclesExcludingCopyQueueStubs\":%u,\"positionCalls\":%u,\"CpuSetCalls\":%u,\"copiedBytes\":%u,\"requested2048ByteTransfers\":%u,\"applied\":%u,\"PASS\":true}\n",same,guard,steps,(unsigned)mTimingCurrentTime(&g->timing),position,copies,bytes,requests,applied);
        core->deinit(core);
    }
    free(code);return 0;
}
