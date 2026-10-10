/* Passive native chronology. No file I/O inside interpreter dispatch, CPU or
 * emulated-memory writes, game calls, keys, scheduling or extra instructions. */
enum {DG_POINTS=96,DG_DATA=11,DG_WORDS=64,DG_BUFFER=4096,DG_FRAMES=925,
      DG_NORMAL_LIMIT=DG_FRAMES*DG_BUFFER,DG_TOTAL_LIMIT=DG_NORMAL_LIMIT+1,
      DG_FAILURE=126};
struct DgPoint {unsigned pc,rom,opcode,mode,function,identity,role,size,seen;};
struct DgDiagnostic {
    struct DgPoint point[DG_POINTS];unsigned data[DG_DATA],dataSeen,count;
    struct mCore *core;FILE *file;unsigned active,reason,command,epoch,visual,
        requested,used,rows,frames,terminal,queueSeen,queue[128][4];
    unsigned buffer[DG_BUFFER][DG_WORDS];
};
static struct DgDiagnostic dg;
static unsigned dg_read(unsigned a,unsigned n)
{return bv_tl_read((const struct GBA *)dg.core->board,a,n);}
static unsigned dg_io(unsigned a)
{const struct GBA *g=dg.core->board;return g->memory.io[a/2]|(unsigned)g->memory.io[a/2+1]<<16;}
static unsigned dg_add(const unsigned w[DG_WORDS],unsigned terminal,unsigned frame)
{
    if(dg.reason&&!terminal)return dg.reason;
    unsigned limit=terminal?DG_TOTAL_LIMIT:DG_NORMAL_LIMIT;
    /* A frame marker gets the last buffer slot. Command/key/queue rows share
     * the same buffer budget; terminal uses a separately reserved file row. */
    if(dg.rows+dg.used>=limit || dg.used>=(frame||terminal?DG_BUFFER:DG_BUFFER-1))return dg.reason=DG_FAILURE;
    memcpy(dg.buffer[dg.used++],w,DG_WORDS*4);return 0;
}
static unsigned dg_collect(unsigned w[DG_WORDS],unsigned tag,unsigned point)
{
    memset(w,0,DG_WORDS*4);const struct ARMCore *c=dg.core->cpu;const struct GBA *g=dg.core->board;
    w[0]=tag;w[1]=point;w[2]=dg.command;w[3]=dg.epoch;w[4]=dg.visual;
    w[5]=(unsigned)c->gprs[ARM_PC]-(c->executionMode==MODE_THUMB?2:4);w[6]=c->gprs[ARM_PC];
    w[7]=c->gprs[ARM_LR];w[8]=c->gprs[ARM_SP];w[9]=c->cpsr.packed;
    for(unsigned i=0;i<4;i++)w[10+i]=c->gprs[i];
    w[14]=c->cycles;w[15]=c->nextEvent;
    w[16]=g->timing.masterCycles;uint64_t time=g->timing.globalCycles+c->cycles;w[17]=time;w[18]=time>>32;
    w[19]=g->video.frameCounter;w[20]=g->memory.io[REG_VCOUNT/2];
    w[21]=g->memory.io[REG_IE/2]|(unsigned)g->memory.io[REG_IF/2]<<16;w[22]=g->memory.io[REG_IME/2]|(unsigned)g->memory.io[REG_DMA3CNT_LO/2]<<16;
    const struct mTimingEvent *root=g->timing.root?g->timing.root:g->timing.reroot;
    w[23]=bv_tl_event_id(g,root)<<8|(unsigned)g->memory.io[REG_DMA3CNT_HI/2]<<16;w[24]=root?root->when:0;
    unsigned events=0;for(const struct mTimingEvent *e=root;e;e=e->next){if(++events>64)return dg.reason=DG_FAILURE;if(e==&g->irqEvent)w[23]|=1;}
    w[25]=dg_read(dg.data[0],1);w[26]=dg_read(dg.data[1],1);
    w[27]=w[25]<4?dg_read(dg.data[2]+512*w[25],1):0xffffffffu;
    w[28]=dg_read(dg.data[3],4);
    for(unsigned i=0;i<4;i++)w[29+i]=c01_edge_identity(dg_read(dg.data[4]+4*i,4));
    w[33]=c01_edge_identity(dg_read(dg.data[5],4));
    w[34]=c01_edge_identity(dg_read(dg.data[6],4));w[35]=c01_edge_identity(dg_read(dg.data[6]+4,4));
    w[36]=dg_read(dg.data[8],1);w[37]=dg_read(dg.data[9],1);if(w[37]>=128)return dg.reason=DG_FAILURE;
    unsigned hash=2166136261u;
    for(unsigned i=0;i<128;i++){
        unsigned a=dg.data[7]+16*i,size=dg_read(a+8,2);if(size){w[38]++;w[39]+=size;}
        for(unsigned j=0;j<16;j++)hash=(hash^dg_read(a+j,1))*16777619u;
    }
    w[40]=hash;for(unsigned i=0;i<4;i++)w[41+i]=dg_read(dg.data[10]+4*i,4);
    w[45]=dg_io(REG_DMA3SAD_LO);w[46]=dg_io(REG_DMA3DAD_LO);
    unsigned slot=w[37];if(point<dg.count && dg.point[point].role==8 && (unsigned)c->gprs[0]<128)slot=c->gprs[0];
    w[51]=slot;for(unsigned i=0;i<4;i++)w[47+i]=dg_read(dg.data[7]+16*slot+4*i,4);
    unsigned sp=w[8];if(!(sp&3)&&bv_tl_valid_ram(sp,32)){w[52]=8;for(unsigned i=0;i<8;i++)w[53+i]=dg_read(sp+4*i,4);}
    unsigned role=point<dg.count?dg.point[point].role:0,ptr=0;
    if(role==10){w[61]=c->gprs[1]&255;ptr=c->gprs[0];}
    if(role==11&&bv_tl_valid_ram(c->gprs[0],16)){ptr=dg_read(c->gprs[0],4);w[61]=dg_read(c->gprs[0]+4,2)|((unsigned)c->gprs[1]&255)<<16;}
    if(ptr){unsigned textHash=2166136261u;for(unsigned i=0;i<256&&bv_tl_valid_ram(ptr+i,1);i++){unsigned b=dg_read(ptr+i,1);textHash=(textHash^b)*16777619u;if(b==255)break;}w[62]=textHash;}
    w[63]=dg.requested|g->memory.io[REG_KEYINPUT/2]<<16;return 0;
}
static unsigned dg_record(unsigned tag,unsigned point,unsigned frame)
{
    if(!dg.active)return 0;
    unsigned w[DG_WORDS];if(dg_collect(w,tag,point))return dg.reason;
    if(dg_add(w,0,frame))return dg.reason;
    /* Full initial queue and every changed 16-byte slot, including removals.
     * This allows exact queue reconstruction, not just aggregate inference. */
    for(unsigned i=0;i<128;i++){
        unsigned q[4];for(unsigned j=0;j<4;j++)q[j]=dg_read(dg.data[7]+16*i+4*j,4);
        if(!dg.queueSeen || memcmp(q,dg.queue[i],sizeof q)){
            unsigned row[DG_WORDS];memcpy(row,w,sizeof row);row[0]=4;row[51]=i;memcpy(row+47,q,sizeof q);
            if(dg_add(row,0,0))return dg.reason;
            memcpy(dg.queue[i],q,sizeof q);
        }
    }
    dg.queueSeen=1;return 0;
}
static unsigned dg_flush(void)
{
    if(!dg.file)return 0;
    if(ferror(dg.file))return dg.reason=DG_FAILURE;
    unsigned done=0,reason=0;unsigned char b[DG_WORDS*4];
    for(;done<dg.used;done++){
        bv_ts_pack(b,dg.buffer[done],DG_WORDS);
        if(fwrite(b,1,sizeof b,dg.file)!=sizeof b){reason=DG_FAILURE;break;}dg.rows++;
    }
    dg.used-=done;if(done&&dg.used)memmove(dg.buffer,dg.buffer+done,dg.used*sizeof dg.buffer[0]);
    if(fflush(dg.file)||ferror(dg.file))reason=DG_FAILURE;
    if(reason)dg.reason=reason;
    return reason;
}
static unsigned dg_open(struct mCore *core)
{
    dg.core=core;const struct GBA *g=core->board;unsigned sizes[DG_DATA]={1,1,2048,4,16,4,0x43c,2048,1,1,16};
    if(dg.dataSeen!=(1u<<DG_DATA)-1 || !dg.count || dg.count>DG_POINTS)return DG_FAILURE;
    for(unsigned i=0;i<DG_DATA;i++)if(!bv_tl_valid_ram(dg.data[i],sizes[i]))return DG_FAILURE;
    for(unsigned i=0;i<dg.count;i++){
        struct DgPoint *p=&dg.point[i];if(p->seen!=511 || !p->role || p->role>11 || !p->size || p->rom<p->function || p->rom-p->function+(p->mode?2:4)>p->size || p->mode>1 || p->rom<0x08000000 || p->rom-0x08000000+(p->mode?2:4)>g->memory.romSize
          || !p->identity || c01_edge_identity(p->function)!=p->identity)return DG_FAILURE;
        const unsigned char *b=(const unsigned char *)g->memory.rom+p->rom-0x08000000;
        unsigned op=b[0]|b[1]<<8;if(!p->mode)op|=(unsigned)b[2]<<16|(unsigned)b[3]<<24;
        if(op!=p->opcode || (p->mode && p->pc!=p->rom) || (!p->mode&&!bv_tl_valid_ram(p->pc,4)))return DG_FAILURE;
    }
    dg.file=fopen("controller-dma-diagnostic-private.bin","wbx");if(!dg.file || fchmod(fileno(dg.file),0600))return DG_FAILURE;
    unsigned char header[16]="C01DIAG1";unsigned words[2]={DG_WORDS,DG_TOTAL_LIMIT};bv_ts_pack(header+8,words,2);
    if(fwrite(header,1,16,dg.file)!=16||fflush(dg.file))return dg.reason=DG_FAILURE;
    return 0;
}
static unsigned dg_command(void)
{
    dg.command++;if(dg.command==25)dg.active=1;
    if(dg.active){dg.visual=edge.visual->frames;dg.epoch=edge.epoch;}
    return dg_record(1,DG_POINTS,0);
}
static unsigned dg_keys(unsigned keys)
{dg.requested=keys;if(dg.active){dg.visual=edge.visual->frames;dg.epoch=edge.epoch;}return dg_record(2,DG_POINTS,0);}
static unsigned dg_observe(struct mCore *core,unsigned epoch)
{
    if(!dg.active)return 0;
    dg.epoch=epoch;dg.visual=edge.visual->frames;
    if(dg.reason)return dg.reason;
    const struct ARMCore *c=core->cpu;
    unsigned pc=(unsigned)c->gprs[ARM_PC]-(c->executionMode==MODE_THUMB?2:4);
    for(unsigned i=0;i<dg.count;i++)if(pc==dg.point[i].pc){
        if((unsigned)c->executionMode!=dg.point[i].mode || c->prefetch[0]!=dg.point[i].opcode)return dg.reason=DG_FAILURE;
        if(dg_record(3,i,0))return dg.reason;
    }
    return 0;
}
static unsigned dg_frame_end(void)
{
    if(!dg.active)return 0;
    if(dg.frames>=DG_FRAMES)return dg.reason=DG_FAILURE;
    dg.frames++;unsigned reason=dg_record(8,DG_POINTS,1);return reason?reason:dg_flush();
}
static unsigned dg_close(unsigned result)
{
    if(!dg.file)return 0;
    unsigned old=dg.reason;dg.reason=0;
    unsigned reason=dg_flush();
    if(!reason && dg.active){
        unsigned w[DG_WORDS];reason=dg_collect(w,11,DG_POINTS);w[1]=result;
        if(!reason)reason=dg_add(w,1,1);
        if(!reason)reason=dg_flush();
        dg.terminal=!reason;
    }
    if(fclose(dg.file)&&!reason)reason=DG_FAILURE;
    dg.file=NULL;dg.active=0;
    printf("DIAGNOSTIC_CLOSE result=%u retention=%u rows=%u frames=%u terminal=%u native_read=%lld ui_read=%lld full_acceptance=0\n",result,old?old:reason,dg.rows,dg.frames,dg.terminal,
      edge.visual&&edge.visual->trace?(long long)ftello(edge.visual->trace):-1LL,ui.trace?(long long)ftello(ui.trace):-1LL);
    return old?old:reason;
}
