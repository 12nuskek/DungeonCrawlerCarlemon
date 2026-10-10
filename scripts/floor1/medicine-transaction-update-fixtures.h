/* Independent execution of the pinned outer function and native Free chain.
 * Synthetic calls are explicit; no emulator core or game RAM is used. */
static unsigned txUpdateChecks,txCompletionChecks,txSkippedCompletions,txUpdateOffsetSeen[0x47];
static void txPacket(const unsigned*regs,unsigned flags,unsigned pc) {
    txCpuAt(pc,regs[13]);memcpy(txCpu.gprs,regs,16*sizeof *regs);
    txCpu.gprs[15]=pc+2;txCpu.cpsr.packed=flags|0x3f;
}
static void txAllocation(unsigned buffer,unsigned coalesce) {
    unsigned block=buffer-16,previous=0x3b38,next=buffer+600;
    put16(gtHeapBase,1);put16(gtHeapBase+2,0xa3a3);put32(gtHeapBase+4,0x80);
    put32(gtHeapBase+12,gtx.internal-16);
    put32(gtx.internal-8,gtHeapBase);put32(gtx.internal-4,previous);
    put16(previous,coalesce?0:1);put16(previous+2,0xa3a3);
    put32(previous+4,block-previous-16);put32(previous+8,gtx.internal-16);put32(previous+12,block);
    put16(block,1);put16(block+2,0xa3a3);put32(block+4,600);put32(block+8,previous);put32(block+12,next);
    put16(next,coalesce?0:1);put16(next+2,0xa3a3);put32(next+4,1000);put32(next+8,block);put32(next+12,gtHeapBase);
    put32(0x03000004,gtHeapBase); /* scoped native sHeapStart relocation */
}
static unsigned txCondition(unsigned condition,unsigned flags) {
    unsigned z=(flags>>30)&1,c=(flags>>29)&1;
    assert(condition==0||condition==1||condition==8||condition==9);
    return condition==0?z:condition==1?!z:condition==8?c&&!z:!c||z;
}
static unsigned txBranchTarget(unsigned base,unsigned pc,unsigned first,unsigned second) {
    int upper=first&0x7ff;if(upper&0x400)upper-=0x800;
    assert((second&0xf800)==0xf800);
    return base+pc+4+upper*4096+(second&0x7ff)*2;
}
/* A general decoder for only the opcodes present in these pinned functions.
 * It does not consume gtCopySteps or the validator's allowed-offset table. */
static unsigned txNative(unsigned base,const unsigned*opcodes,unsigned bytes,unsigned*regs,
    unsigned*flags,unsigned mode,unsigned buffer,unsigned coalesce) {
    unsigned pc=0,partialObserved=0;
    for(unsigned steps=0;steps<3000;steps++) {
        assert(pc+2<=bytes&&!(pc&1));unsigned ins=opcodes[pc/2],next=pc+2;
        if(base==GT_UPDATE&&pc>=0x16&&pc<=0x46&&mode==0) {
            txPacket(regs,*flags,base+pc);txAcceptBoth();assert(!txCheck());txUpdateChecks++;
            txUpdateOffsetSeen[pc]++;assert(!gc.exitSeen);
            unsigned old=txCpu.gprs[4];txCpu.gprs[4]=7;txReject();txCpu.gprs[4]=old;
            old=txCpu.gprs[5];txCpu.gprs[5]+=4;txReject();txCpu.gprs[5]=old;
            if(pc>=0x1a){old=txCpu.gprs[6];txCpu.gprs[6]=99;txReject();txCpu.gprs[6]=old;}
            old=r32(&mock,regs[13]+12);put32(regs[13]+12,old^4);txReject();put32(regs[13]+12,old);
        }
        if(base==GT_COPY&&mode==2&&regs[14]==((GT_UPDATE+0x36)|1)
            &&r32(&mock,regs[13])==0&&pc==0x1e&&!partialObserved) {
            txPacket(regs,*flags,base+pc);txAcceptBoth();assert(!txCheck());
            assert(gtx.copyProgress==4&&gtx.copyBuffer==buffer);partialObserved=1;
        }
        if(base==GT_UPDATE&&pc==0x46) {
            assert(regs[4]==6&&regs[5]==buffer&&regs[6]==100);
            assert(gtx.copyProgress==(mode==0?600u:mode==1?0u:4u));
            assert(gtx.copyBuffer==(mode==1?0u:buffer));
            /* Actual native Free ran. Any payload read by the observer now is
             * a hard fixture failure; only header/stack metadata may be read. */
            txDeadStart=buffer;txDeadSize=600;
            memset(memory+buffer,0xa5,600);
            txPacket(regs,*flags,base+pc);txAcceptBoth();assert(!txCheck());
            assert(gtx.copyProgress==600&&gtx.copyBuffer==buffer&&!gc.exitSeen);txCompletionChecks++;if(mode)txSkippedCompletions++;
            unsigned old=txCpu.gprs[5],other=0xe000;put16(other-16,0);put16(other-14,0xa3a3);put32(other-12,600);
            txCpu.gprs[5]=other;txReject();txCpu.gprs[5]=old; /* stale actual operand remains bound */
            for(unsigned delta=4;delta<=16;delta+=4){old=r32(&mock,regs[13]-delta);put32(regs[13]-delta,old^4);txReject();put32(regs[13]-delta,old);}
            old=txCpu.gprs[0];txCpu.gprs[0]^=4;txReject();txCpu.gprs[0]=old;
            old=txCpu.gprs[14];txCpu.gprs[14]^=4;txReject();txCpu.gprs[14]=old;
            old=r32(&mock,buffer-12);put32(buffer-12,596);txReject();put32(buffer-12,old);
            old=memory[buffer-16];memory[buffer-16]=1;txReject();memory[buffer-16]=old;
            old=memory[buffer-14];memory[buffer-14]^=1;txReject();memory[buffer-14]=old;
            old=memory[co.a.party+599];memory[co.a.party+599]^=1;txReject();memory[co.a.party+599]=old;
            old=memory[0x4490+0xd6];memory[0x4490+0xd6]^=1;txReject();memory[0x4490+0xd6]=old;
            txDeadSize=0;return GT_UPDATE+0x46;
        }
        if((ins&0xfe00)==0xb400) {
            unsigned list=ins&255,count=!!(ins&256);for(unsigned i=0;i<8;i++)count+=(list>>i)&1;
            regs[13]-=4*count;unsigned cursor=regs[13];
            for(unsigned i=0;i<8;i++)if(list&(1u<<i)){put32(cursor,regs[i]);cursor+=4;}
            if(ins&256)put32(cursor,regs[14]);
        }else if((ins&0xfe00)==0xbc00) {
            for(unsigned i=0;i<8;i++)if(ins&(1u<<i)){regs[i]=r32(&mock,regs[13]);regs[13]+=4;}
            if(ins&256){unsigned target=r32(&mock,regs[13]);regs[13]+=4;return target;}
        }else if((ins&0xff87)==0x4700) {return regs[(ins>>3)&15];
        }else if((ins&0xf800)==0x0000||(ins&0xf800)==0x0800) {
            unsigned dst=ins&7,src=(ins>>3)&7,n=(ins>>6)&31,value=regs[src],carry=(*flags>>29)&1;
            if((ins&0xf800)==0x0800){if(!n)n=32;carry=(value>>(n-1))&1;regs[dst]=n==32?0:value>>n;}
            else {if(n)carry=(value>>(32-n))&1;regs[dst]=value<<n;}
            *flags=txNz(*flags,regs[dst]);*flags=(*flags&~0x20000000u)|(carry<<29);
        }else if((ins&0xfe00)==0x1c00||(ins&0xfe00)==0x1800) {
            unsigned dst=ins&7,a=regs[(ins>>3)&7],b=(ins&0x0400)?(ins>>6)&7:regs[(ins>>6)&7];
            regs[dst]=a+b;*flags=txArithmetic(a,b,regs[dst],0);
        }else if((ins&0xf800)==0x2000){regs[(ins>>8)&7]=ins&255;*flags=txNz(*flags,ins&255);
        }else if((ins&0xf800)==0x3000||(ins&0xf800)==0x3800) {
            unsigned reg=(ins>>8)&7,a=regs[reg],b=ins&255,subtract=(ins&0xf800)==0x3800;
            regs[reg]=subtract?a-b:a+b;*flags=txArithmetic(a,b,regs[reg],subtract);
        }else if((ins&0xffc0)==0x4300){regs[ins&7]|=regs[(ins>>3)&7];*flags=txNz(*flags,regs[ins&7]);
        }else if((ins&0xffc0)==0x4000){regs[ins&7]&=regs[(ins>>3)&7];*flags=txNz(*flags,regs[ins&7]);
        }else if((ins&0xffc0)==0x4340){regs[ins&7]*=regs[(ins>>3)&7];*flags=txNz(*flags,regs[ins&7]);
        }else if((ins&0xffc0)==0x4240){unsigned b=regs[(ins>>3)&7];regs[ins&7]=0u-b;*flags=txArithmetic(0,b,regs[ins&7],1);
        }else if((ins&0xf800)==0x2800){unsigned a=regs[(ins>>8)&7],b=ins&255;*flags=txArithmetic(a,b,a-b,1);
        }else if((ins&0xffc0)==0x4280){unsigned a=regs[ins&7],b=regs[(ins>>3)&7];*flags=txArithmetic(a,b,a-b,1);
        }else if((ins&0xff00)==0xcb00){assert((ins&255)==1);regs[0]=r32(&mock,regs[3]);regs[3]+=4;
        }else if((ins&0xff00)==0xc100){assert((ins&255)==1);put32(regs[1],regs[0]);regs[1]+=4;
        }else if((ins&0xf800)==0x4800) {
            unsigned literal=((pc+4)&~3u)+4*(ins&255);assert(literal+4<=bytes);
            unsigned value=opcodes[literal/2]|(opcodes[literal/2+1]<<16);
            assert(value==txNativeParty||value==0x03000004);regs[(ins>>8)&7]=value==txNativeParty?co.a.party:value;
        }else if((ins&0xf800)==0x6800||(ins&0xf800)==0x6000) {
            unsigned address=regs[(ins>>3)&7]+4*((ins>>6)&31),reg=ins&7;
            if((ins&0xf800)==0x6800)regs[reg]=r32(&mock,address);else put32(address,regs[reg]);
        }else if((ins&0xf800)==0x8800||(ins&0xf800)==0x8000) {
            unsigned address=regs[(ins>>3)&7]+2*((ins>>6)&31),reg=ins&7;
            if((ins&0xf800)==0x8800)regs[reg]=r16(&mock,address);else put16(address,regs[reg]);
        }else if((ins&0xf000)==0xd000) {
            if(txCondition((ins>>8)&15,*flags))next=pc+4+2*(signed char)(ins&255);
        }else if((ins&0xf800)==0xe000) {
            int offset=ins&0x7ff;if(offset&0x400)offset-=0x800;next=pc+4+2*offset;
        }else if((ins&0xf800)==0xf000) {
            unsigned target=txBranchTarget(base,pc,ins,opcodes[pc/2+1]);next=pc+4;regs[14]=(base+next)|1;
            if(target==GT_ALLOC){assert(regs[0]==600);txAllocation(buffer,coalesce);regs[0]=buffer;}
            else if(target==GT_GETSLOT){unsigned index=regs[0];assert(index<6);regs[2]=index/2;regs[0]=(memory[gc.a.order+index/2]>>(index&1?0:4))&15;*flags=txArithmetic(regs[0],0,regs[0],0);regs[1]=regs[14];}
            else if(target==GT_COPY){assert(regs[2]==100||regs[2]==600);assert(txNative(GT_COPY,txMemcpyOpcodes,sizeof txMemcpyOpcodes/sizeof *txMemcpyOpcodes*2,regs,flags,mode,buffer,coalesce)==((base+next)|1));}
            else if(target==GT_FREE){assert(regs[0]==buffer);assert(txNative(GT_FREE,txFreeOpcodes,sizeof txFreeOpcodes/sizeof *txFreeOpcodes*2,regs,flags,mode,buffer,coalesce)==((base+next)|1));}
            else if(target==GT_FREEINTERNAL){assert(regs[0]==gtHeapBase&&regs[1]==buffer);assert(txNative(GT_FREEINTERNAL,txFreeInternalOpcodes,sizeof txFreeInternalOpcodes/sizeof *txFreeInternalOpcodes*2,regs,flags,mode,buffer,coalesce)==((base+next)|1));}
            else {fprintf(stderr,"unsupported fixture BL %08x\n",target);assert(0);}
        }else {fprintf(stderr,"unsupported outer opcode %04x at %08x\n",ins,base+pc);assert(0);}
        pc=next;
    }
    assert(0);return 0;
}
static void txUpdateAll(void) {
    for(unsigned mode=0;mode<3;mode++)for(unsigned coalesce=0;coalesce<2;coalesce++) {
        txRestore();nativeMessageSetup();txAcknowledged();medicineTask(gc.a.closeFade);
        unsigned regs[16]={0},flags=0;regs[4]=gc.a.partyMenu;regs[5]=gtx.owner;regs[13]=0x03006000;regs[14]=(GT_CLOSEFADE+0x22)|1;
        txTaskFrame(regs[13],12,gtx.owner);unsigned advancesBefore=advances;
        assert(txNative(GT_UPDATE,txUpdateOpcodes,sizeof txUpdateOpcodes/sizeof *txUpdateOpcodes*2,regs,&flags,mode,0xd000,coalesce)==GT_UPDATE+0x46);
        assert(advances==advancesBefore&&!gc.exitSeen&&gtx.copyProgress==600);
    }
    const unsigned points[]={0x16,0x18,0x1a,0x1c,0x20,0x22,0x24,0x26,0x28,0x2a,0x2c,0x2e,0x30,0x32,0x36,0x38,0x3a,0x3c,0x3e,0x40,0x42,0x46};
    for(unsigned i=0;i<sizeof points/sizeof *points;i++)assert(txUpdateOffsetSeen[points[i]]);
    printf("PASS independently executed outer Update/Free chain direct_checks=%u offsets=22 completion_checks=%u skipped_completion_checks=%u modes=all_direct/no_copy_sample/one_actual_prefix coalescing=both freed_payload_reads=0\n",txUpdateChecks,txCompletionChecks,txSkippedCompletions);
}
