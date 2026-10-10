/* Bounded passive input evidence. No game function calls or CPU/memory writes.
 * Native point records are coalesced only if their complete context is identical
 * within the same frame. File I/O is outside interpreter/event dispatch. */
enum {C01_EDGE_POINTS=12,C01_EDGE_WORDS=40,C01_EDGE_BUFFER=64,
      C01_EDGE_MAX_ROWS=18000*64+156*3+1};
struct C01EdgePoint {unsigned pc,opcode,function,role,kind,seen;};
struct C01Edge {
    struct C01EdgePoint point[C01_EDGE_POINTS];
    struct BattleVisual *visual;struct mCore *core;unsigned tasks,fade;
    FILE *file;unsigned active,reason,command,requested,epoch,used,rows,coalesced;
    unsigned desiredKind,desiredActor,receivingKind,linkValid,linkResult,linkEpoch;
    unsigned last[C01_EDGE_POINTS][C01_EDGE_WORDS],seen[C01_EDGE_POINTS];
    unsigned buffer[C01_EDGE_BUFFER][C01_EDGE_WORDS];
};
static struct C01Edge edge;
static unsigned c01_edge_read(unsigned address,unsigned n)
{const struct GBA *g=edge.core->board;return bv_tl_read(g,address,n);}
static unsigned c01_edge_identity(unsigned address)
{return bv_callback(edge.visual,address&~1u);}
static unsigned c01_edge_flush(void)
{
    if(!edge.file)return 0;
    unsigned char bytes[C01_EDGE_WORDS*4];
    for(unsigned i=0;i<edge.used;i++){
        bv_ts_pack(bytes,edge.buffer[i],C01_EDGE_WORDS);
        if(edge.rows>=C01_EDGE_MAX_ROWS || fwrite(bytes,1,sizeof bytes,edge.file)!=sizeof bytes)return edge.reason=125;
        edge.rows++;
    }
    edge.used=0;return fflush(edge.file)||ferror(edge.file)?edge.reason=125:0;
}
static unsigned c01_edge_record(unsigned tag,unsigned point,unsigned r0,unsigned pc)
{
    if(!edge.active)return 0;
    if(edge.reason)return edge.reason;
    unsigned w[C01_EDGE_WORDS]={0};const struct GBA *g=edge.core->board;
    w[0]=tag;w[1]=edge.command;w[2]=edge.epoch;w[3]=edge.visual->frames;
    w[4]=edge.requested;w[5]=g->memory.io[REG_KEYINPUT/2];
    for(unsigned i=0;i<6;i++)w[6+i]=c01_edge_read(ui.mainstate+0x28+2*i,2);
    w[12]=c01_edge_identity(c01_edge_read(ui.mainstate,4));
    w[13]=c01_edge_identity(c01_edge_read(ui.mainstate+4,4));
    w[14]=edge.receivingKind;w[15]=0xffffffffu;
    if(edge.receivingKind>=4 && edge.receivingKind<=7){
        unsigned fn=ui.a[8+edge.receivingKind]&~1u;
        for(unsigned i=0;i<16;i++)if(c01_edge_read(edge.tasks+40*i+4,1)
            && (c01_edge_read(edge.tasks+40*i,4)&~1u)==fn){
                w[15]=i;w[16]=c01_edge_identity(fn);w[17]=1;break;
        }
    }
    unsigned f=c01_edge_read(edge.fade+7,1),fin=c01_edge_read(edge.fade+10,1);
    w[18]=(f>>7)&1;w[19]=(fin>>1)&1;
    w[20]=(c01_edge_read(edge.fade+9,2)>>4)&31;
    w[21]=(c01_edge_read(edge.fade+4,2)>>6)&31;
    w[22]=(c01_edge_read(edge.fade+5,1)>>3)&31;
    w[23]=edge.linkValid;w[24]=edge.linkResult;w[25]=edge.linkEpoch;
    w[26]=c01_edge_read(ui.link[0],1);w[27]=c01_edge_read(ui.link[1],1);
    w[28]=c01_edge_read(ui.link[2],1);w[29]=(w[26]?w[28]:w[27])>=3;
    w[30]=r0;w[31]=tag==6 && r0==0xfffffffeu && (w[9]&2)!=0;
    for(unsigned i=0;i<16;i++)if(c01_edge_read(edge.tasks+40*i+4,1)
        && (c01_edge_read(edge.tasks+40*i,4)&~1u)==edge.point[11].function)w[32]|=1u<<i;
    w[33]=edge.desiredKind;w[34]=edge.desiredActor;w[35]=pc;
    w[36]=point<C01_EDGE_POINTS?c01_edge_identity(edge.point[point].function):0;
    w[37]=c01_edge_read(ui.mainstate+0x438,1);w[38]=c01_edge_read(ui.link[3],1);
    w[39]=point;
    if(point<C01_EDGE_POINTS){
        if(edge.seen[point] && !memcmp(w,edge.last[point],sizeof w)){edge.coalesced++;return 0;}
        memcpy(edge.last[point],w,sizeof w);edge.seen[point]=1;
    }
    if(edge.used>=C01_EDGE_BUFFER)return edge.reason=125;
    memcpy(edge.buffer[edge.used++],w,sizeof w);return 0;
}
static unsigned c01_edge_observe(struct mCore *core,unsigned epoch)
{
    if(!edge.active)return 0;
    edge.epoch=epoch;const struct ARMCore *cpu=core->cpu;
    unsigned pc=cpu->gprs[ARM_PC]-(cpu->executionMode==MODE_THUMB?2:4);
    if(cpu->executionMode!=MODE_THUMB)return 0;
    for(unsigned i=0;i<C01_EDGE_POINTS;i++)if(pc==edge.point[i].pc){
        unsigned role=edge.point[i].role,r0=cpu->gprs[0];
        if(role==1 || role==5 || role==6)edge.receivingKind=edge.point[i].kind;
        if(role==2){edge.linkValid=1;edge.linkResult=r0&255;edge.linkEpoch=epoch;}
        unsigned tag=role==1?3:role==2?4:role==3?5:role==4?6:7;
        return c01_edge_record(tag,i,r0,pc);
    }
    return edge.reason;
}
static unsigned c01_edge_frame_begin(unsigned epoch)
{edge.epoch=epoch;if(!edge.active)return 0;memset(edge.seen,0,sizeof edge.seen);return edge.reason;}
static unsigned c01_edge_frame_end(struct mCore *core)
{(void)core;if(!edge.active)return 0;unsigned reason=c01_edge_record(8,C01_EDGE_POINTS,0,0);return reason?reason:c01_edge_flush();}
static unsigned c01_edge_open(struct mCore *core,struct BattleVisual *visual,unsigned tasks,unsigned fade)
{
    edge.core=core;edge.visual=visual;edge.tasks=tasks;edge.fade=fade;
    const struct GBA *g=core->board;
    if(!bv_tl_valid_ram(ui.mainstate,0x43c)||!bv_tl_valid_ram(tasks,640)||!bv_tl_valid_ram(fade,12))return 125;
    for(unsigned i=0;i<4;i++)if(!bv_tl_valid_ram(ui.link[i],1))return 125;
    for(unsigned i=0;i<C01_EDGE_POINTS;i++){
        struct C01EdgePoint *p=&edge.point[i];
        if(p->seen!=63 || !c01_edge_identity(p->function) || p->pc<0x08000000
            || p->pc-0x08000000+2>g->memory.romSize)return 125;
        const unsigned char *b=(const unsigned char*)g->memory.rom+p->pc-0x08000000;
        if((unsigned)(b[0]|b[1]<<8)!=p->opcode)return 125;
    }
    edge.file=fopen("native-input-edge-private.bin","wbx");if(!edge.file)return 125;
    if(fchmod(fileno(edge.file),0600))return 125;
    unsigned char header[16]={'C','0','1','E','D','G','E','4'};
    unsigned values[2]={C01_EDGE_WORDS,C01_EDGE_MAX_ROWS};bv_ts_pack(header+8,values,2);
    if(fwrite(header,1,sizeof header,edge.file)!=sizeof header)return 125;
    edge.active=1;return c01_edge_record(1,C01_EDGE_POINTS,0,0);
}
static unsigned c01_edge_keys(unsigned keys)
{edge.requested=keys;return c01_edge_record(2,C01_EDGE_POINTS,0,0);}
static unsigned c01_edge_command(void)
{edge.command++;edge.desiredKind=edge.desiredActor=0;return c01_edge_record(1,C01_EDGE_POINTS,0,0);}
static unsigned c01_edge_close(unsigned result)
{
    if(!edge.file)return 0;
    unsigned oldReason=edge.reason;edge.reason=0;
    unsigned reason=c01_edge_flush();
    if(!reason)reason=c01_edge_record(11,C01_EDGE_POINTS,result,0);
    if(!reason)reason=c01_edge_flush();
    if(fclose(edge.file)&&!reason)reason=125;
    edge.file=NULL;edge.active=0;
    return oldReason?oldReason:reason;
}
