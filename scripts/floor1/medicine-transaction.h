/* Passive source-bound exceptions only. Stable readers remain checksum strict. */
enum {GT_NONE=UINT_MAX,GT_ERROR=108};
struct GtContext {unsigned r[16],pc,irq,flags;};
struct GtTransaction {unsigned valid,owner,wait,internal,priority,copyProgress,copyBuffer,freed;
    unsigned char ownerData[32];};
static struct GtTransaction gtx;
static unsigned gt_read_progressive(struct mCore*,struct CoSnapshot*,const unsigned char*);
static unsigned gt_context(struct mCore*c,struct GtContext*out) {
    if(!c->cpu)return 0;
    const struct ARMCore*cpu=c->cpu;memcpy(out->r,cpu->gprs,sizeof out->r);out->irq=0;
    unsigned status=(unsigned)cpu->cpsr.packed;out->flags=status&0xf0000000;
    if((status&255)==0x3f&&cpu->executionMode==MODE_THUMB&&cpu->privilegeMode==MODE_SYSTEM)out->pc=out->r[15]-2;
    else if((status&255)==0x92&&cpu->executionMode==MODE_ARM&&cpu->privilegeMode==MODE_IRQ
        &&out->r[15]==0x1c&&out->r[13]==0x03007fa0&&((unsigned)cpu->spsr.packed&255)==0x3f
        &&status==(((unsigned)cpu->spsr.packed&~255u)|0x92)) {
        /* Actual ARMRaiseIRQ saves system SP/LR before replacing IRQ LR.
         * At the verified fresh vector entry no BIOS instruction has run. */
        out->pc=out->r[14]-4;out->r[13]=(unsigned)cpu->bankedRegisters[BANK_NONE][0];
        out->r[14]=(unsigned)cpu->bankedRegisters[BANK_NONE][1];out->irq=1;out->flags=(unsigned)cpu->spsr.packed&0xf0000000;
    }else return 0;
    unsigned instruction=0;
    for(unsigned i=0;i<sizeof gtInstructionPoints/sizeof *gtInstructionPoints;i++)if(out->pc==gtInstructionPoints[i])instruction=1;
    /* Each actual stack access is independently bounded by gt_stack. Native
     * WaitForVBlank's retained SP0x03007e24 needs only its one return word. */
    return instruction&&!(out->r[13]&3)&&out->r[13]>=0x03000000&&out->r[13]<=0x03007e40-4;
}
static unsigned gt_stack(struct mCore*c,unsigned address,unsigned expected) {
    return !(address&3)&&address>=0x03000000&&address+4<=0x03007e40&&c->busRead32(c,address)==expected;
}
static unsigned gt_task_frame(struct mCore*c,unsigned sp,unsigned bytes,unsigned task) {
    return gt_stack(c,sp,gc.a.tasks+40*task)&&gt_stack(c,sp+4,gc.a.tasks)
        &&gt_stack(c,sp+bytes-4,(GT_RUNTASKS+0x1e)|1)
        &&gt_stack(c,sp+bytes+8,(GT_PARTY+6)|1);
}
static unsigned gt_heap_range(unsigned pointer,unsigned size) {
    return !(pointer&3)&&pointer>=gtHeapBase+16&&size<=gtHeapSize
        &&pointer<=gtHeapBase+gtHeapSize-size;
}
static unsigned gt_live(struct mCore*c,unsigned pointer,unsigned size) {
    if(!gt_heap_range(pointer,size))return 0;
    unsigned bytes=c->busRead32(c,pointer-12);
    return c->busRead16(c,pointer-16)==1&&c->busRead16(c,pointer-14)==0xa3a3
        &&!(bytes&3)&&bytes>=size&&bytes<size+32&&gt_heap_range(pointer,bytes);
}
static unsigned gt_dead(struct mCore*c,unsigned pointer) {
    if(!gt_heap_range(pointer,8))return 0;
    unsigned magic=c->busRead16(c,pointer-14);
    return !c->busRead16(c,pointer-16)&&(magic==0||magic==0xa3a3);
}
static unsigned gt_freed_copy(struct mCore*c,unsigned pointer) {
    /* FreeInternal preserves this header's size, even when previous/next
     * blocks coalesce. Read header metadata only; never follow freed data. */
    if(!gt_heap_range(pointer,600)||!gt_dead(c,pointer))return 0;
    unsigned size=c->busRead32(c,pointer-12);
    return size>=600&&!(size&3)&&gt_heap_range(pointer,size);
}
static void gt_reset(struct mCore*c) {
    memset(&gtx,0,sizeof gtx);gtx.owner=gtx.wait=UINT_MAX;
    unsigned task=gc_task(c,gc.a.partyInput);
    if(task!=UINT_MAX)gtx.owner=(task-gc.a.tasks)/40;
    gtx.internal=c->busRead32(c,gc.a.internal);
}
static unsigned gt_activate(struct mCore*c) {
    if(gtx.owner>=16||!gt_live(c,gtx.internal,568)||c->busRead32(c,gc.a.internal)!=gtx.internal)return GT_ERROR;
    unsigned task=gc.a.tasks+40*gtx.owner;
    unsigned fn=c->busRead32(c,task)&~1u;
    if(!c->busRead8(c,task+4)||(fn!=(gc.a.restored&~1u)&&fn!=(gc.a.closeText&~1u)))return GT_ERROR;
    co_bytes(c,task+8,gtx.ownerData,32);gtx.priority=c->busRead8(c,task+7);gtx.valid=1;return 0;
}
static unsigned gt_roles(struct mCore*c,unsigned ownerActive,unsigned ownerFn,unsigned waitActive) {
    unsigned task=gc.a.tasks+40*gtx.owner;unsigned char data[32];co_bytes(c,task+8,data,32);
    if(c->busRead8(c,task+4)!=ownerActive||(c->busRead32(c,task)&~1u)!=(ownerFn&~1u)
        ||c->busRead8(c,task+7)!=gtx.priority||memcmp(data,gtx.ownerData,32))return 0;
    unsigned callbacks[]={gc.a.restored,gc.a.closeText,gc.a.closeFade};
    for(unsigned i=0;i<3;i++)if(gc_task_count(c,callbacks[i])!=(ownerActive&&callbacks[i]==ownerFn))return 0;
    if(gc_task_count(c,gc.a.printWait)!=waitActive)return 0;
    if(waitActive) {
        unsigned wait=gc_task(c,gc.a.printWait);if(wait==UINT_MAX||wait==task)return 0;
        unsigned id=(wait-gc.a.tasks)/40;if(gtx.wait!=UINT_MAX&&gtx.wait!=id)return 0;
        if(c->busRead8(c,wait+7)!=1)return 0;
        co_bytes(c,wait+8,data,32);for(unsigned i=0;i<32;i++)if(data[i])return 0;
        gtx.wait=id;
    }
    return 1;
}
static unsigned gt_common(struct mCore*c,unsigned cb,unsigned live) {
    if(!gtx.valid||gtx.owner>=16||gc.heals!=1||!gc_owner(c)||gc.keys||c->busRead8(c,gc.a.useExit)!=1
        ||c->busRead8(c,co.a.turn-16)!=gc.healingCount+1||c->busRead16(c,gc.a.selected)!=13
        ||c->busRead8(c,gc.a.partyMenu+9)!=gc.slot||c->busRead8(c,gc.a.partyMenu+8)!=0x11
        ||c->busRead8(c,gc.a.partyMenu+11)!=3||c->busRead32(c,gc.a.internal)!=gtx.internal)return 0;
    if(cb!=(gc.a.partyMain&~1u)&&cb!=(gc.a.exitBattle&~1u))return 0;
    if(live) {
        if(gtx.freed||!gt_live(c,gtx.internal,568)||(c->busRead32(c,gtx.internal+4)&~1u)!=(gc.a.exitBattle&~1u))return 0;
    }else if(!gt_dead(c,gtx.internal))return 0; /* Never follow a freed allocation. */
    return 1;
}
static unsigned gt_snapshot(struct mCore*c,const unsigned char*party,unsigned progressive) {
    struct CoSnapshot now={0},expected=gc.healed;memcpy(expected.party,party,600);
    unsigned error=progressive?gt_read_progressive(c,&now,party):gc_read(c,&now);
    if(error)return error;
    /* Every byte outside the precise raw party transaction remains exact. */
    return memcmp(&now,&expected,sizeof now)?106:0;
}
static unsigned gt_copy_frame(struct mCore*c,const struct GtContext*x,unsigned sp) {
    (void)x;
    return gt_stack(c,sp,gc.a.partyMenu)&&gt_stack(c,sp+4,gtx.owner)
        &&gt_stack(c,sp+12,(GT_CLOSEFADE+0x22)|1)&&gt_task_frame(c,sp+16,12,gtx.owner);
}
static unsigned gt_value(unsigned kind,unsigned value,unsigned dest,unsigned source,unsigned buffer,unsigned record) {
    if(kind==1)return dest+value;
    if(kind==2)return source+value;
    if(kind==4)return value;
    if(kind==5)return buffer;
    if(kind==6)return record;
    if(kind==8)return dest|source;
    return 0;
}
static unsigned gt_copy(struct mCore*c,const struct GtContext*x,const unsigned*positions) {
    unsigned buffer=0,record=0,copied=0,matched=0,afterFree=0;
    if(x->pc>=GT_COPY&&x->pc<=GT_COPY+0x5c) {
        /* LR alone is insufficient: memcpy frame, UpdatePartyToFieldOrder,
         * task frame and RunTasks -> party callback call sites all bind. */
        for(unsigned i=0;i<sizeof gtCopySteps/sizeof *gtCopySteps;i++) {
            const struct GtCopyStep*s=gtCopySteps+i;if(x->pc!=GT_COPY+s->pc||x->flags!=s->flags)continue;
            unsigned sp=x->r[13],parent=sp+12*s->pushed;
            /* Validate the whole caller frame before reading saved operands.
             * A context-valid SP alone does not admit SP+4 at the stack top. */
            if(x->r[14]!=((GT_UPDATE+0x36)|1)||!gt_copy_frame(c,x,parent)
                ||(s->pushed&&!gt_stack(c,sp+8,(GT_UPDATE+0x36)|1)))continue;
            unsigned rec=s->pushed?c->busRead32(c,sp):x->r[4];
            unsigned buf=s->pushed?c->busRead32(c,sp+4):x->r[5];
            if(rec>=6||!gt_live(c,buf,600))continue;
            unsigned dest=co.a.party+100*positions[rec],source=buf+100*rec,valid=1;
            for(unsigned reg=0;reg<7;reg++) {
                unsigned kind=s->kind[reg];if(!kind)continue;
                unsigned wanted=kind==3?resource_word(gc.healed.party+100*rec+s->value[reg]):gt_value(kind,s->value[reg],dest,source,buf,rec);
                if(x->r[reg]!=wanted){valid=0;break;}
            }
            if(valid){if(matched)return GT_ERROR;matched=1;buffer=buf;record=rec;copied=s->copied;}
        }
    }else if(x->pc>=GT_UPDATE+0x16&&x->pc<=GT_UPDATE+0x46) {
        unsigned offset=x->pc-GT_UPDATE;
        const unsigned points[]={0x16,0x18,0x1a,0x1c,0x20,0x22,0x24,0x26,0x28,0x2a,0x2c,0x2e,0x30,0x32,0x36,0x38,0x3a,0x3c,0x3e,0x40,0x42,0x46};
        for(unsigned i=0;i<sizeof points/sizeof *points;i++)if(offset==points[i])matched=1;
        if(!matched||!gt_copy_frame(c,x,x->r[13]))return GT_ERROR;
        buffer=x->r[5];record=x->r[4];
        if(offset==0x16){if(record!=600)return GT_ERROR;record=0;}
        else if(offset==0x36||offset==0x38||offset==0x3a){copied=100;}
        if(record>6||(record==6&&copied))return GT_ERROR;
        if(record==6&&offset!=0x3c&&offset!=0x3e&&offset!=0x40&&offset!=0x42&&offset!=0x46)return GT_ERROR;
        if(offset==0x16&&x->r[0]!=buffer)return GT_ERROR;
        if(offset==0x1c&&x->r[0]!=record)return GT_ERROR;
        if(record<6) {
            unsigned destination=co.a.party+100*positions[record],source=buffer+100*record,slot=positions[record];
            unsigned r0=x->r[0],r1=x->r[1];
            if((offset==0x20||offset==0x24)&&r0!=slot)return GT_ERROR;
            if(offset==0x22&&r0!=(slot<<24))return GT_ERROR;
            if((offset==0x26||offset==0x28)&&r0!=100*slot)return GT_ERROR;
            if((offset==0x2a||offset==0x2c||offset==0x2e||offset==0x30||offset==0x32||offset==0x36)&&r0!=destination)return GT_ERROR;
            if((offset==0x28||offset==0x2a)&&r1!=co.a.party)return GT_ERROR;
            if(offset==0x2c&&r1!=record)return GT_ERROR;
            if(offset==0x2e&&r1!=100*record)return GT_ERROR;
            if((offset==0x30||offset==0x32)&&r1!=source)return GT_ERROR;
            if(offset==0x32&&x->r[2]!=100)return GT_ERROR;
            if(offset==0x38&&r0!=record+1)return GT_ERROR;
            if(offset==0x3a&&r0!=((record+1)<<24))return GT_ERROR;
        }
        if((offset==0x3c||offset==0x3e||offset==0x40)&&x->r[0]!=(record<<24))return GT_ERROR;
        if(offset==0x42&&x->r[0]!=buffer)return GT_ERROR;
        afterFree=offset==0x46;
        if(offset>=0x1a&&x->r[6]!=100)return GT_ERROR;
        /* A complete synchronous copy may occur between frame observations.
         * +0x46 is exactly Free's return: R4=6/R6=100, the preserved R5 token,
         * and the Update/owned-task/callback stacks bind this completion.
         * A previously observed buffer must still match below. No intermediate
         * observation is required or synthesized; full final bytes are strict. */
        if(afterFree){
            unsigned sp=x->r[13];
            /* Native Free/FreeInternal have just popped these unchanged
             * system-stack slots. They independently bind the actual buffer
             * operand even when no copy instruction was previously sampled. */
            if(record!=6||x->r[0]!=((GT_UPDATE+0x46)|1)||x->r[14]!=((GT_FREE+0xc)|1)
                ||!gt_stack(c,sp-4,(GT_UPDATE+0x46)|1)||!gt_stack(c,sp-8,(GT_FREE+0xc)|1)
                ||!gt_stack(c,sp-12,buffer)||!gt_stack(c,sp-16,6)||!gt_freed_copy(c,buffer))return GT_ERROR;
        }
        else if(!gt_live(c,buffer,600))return GT_ERROR;
    }else return GT_ERROR;
    if(!matched)return GT_ERROR;
    if(gtx.copyBuffer&&buffer!=gtx.copyBuffer)return GT_ERROR;
    unsigned progress=record*100+copied;if(progress<gtx.copyProgress||progress>600)return GT_ERROR;
    if(!afterFree) {
        unsigned char source[600];co_bytes(c,buffer,source,600);if(memcmp(source,gc.healed.party,600))return GT_ERROR;
    }
    unsigned char expected[600];memcpy(expected,gc.healed.party,600);
    for(unsigned i=0;i<record;i++)memcpy(expected+100*positions[i],gc.healed.party+100*i,100);
    if(record<6)memcpy(expected+100*positions[record],gc.healed.party+100*record,copied);
    unsigned result=gt_snapshot(c,expected,copied%100!=0);if(result)return result;
    gtx.copyBuffer=buffer;gtx.copyProgress=progress;return 0;
}
static unsigned gt_wait_boundary(struct mCore*c,const struct GtContext*x) {
    const unsigned points[]={0x1a,0x1c,0x1e,0x20,0x22};
    for(unsigned i=0;i<sizeof points/sizeof *points;i++)if(x->pc==GT_WAITVBLANK+points[i])
        return gt_stack(c,x->r[13],0x080004bf); /* actual AgbMain -> WaitForVBlank return */
    return 0;
}
static unsigned gt_close_frame(struct mCore*c,unsigned sp) {
    return gt_stack(c,sp,0)&&gt_stack(c,sp+4,gtx.owner)
        &&gt_stack(c,sp+8,(GT_CLOSETEXT+0x26)|1)&&gt_stack(c,sp+12,gc.a.tasks+40*gtx.owner)
        &&gt_stack(c,sp+16,(GT_RUNTASKS+0x1e)|1)&&gt_stack(c,sp+28,(GT_PARTY+6)|1);
}
static unsigned gt_transition(struct mCore*c,unsigned cb,const unsigned*positions) {
    if(!gtx.valid||gtx.owner>=16)return GT_ERROR;
    if(gc.ack&&co.frames>gc.ackFrame&&!gc.keys)gc.released=1;
    unsigned active=c->busRead8(c,gc_message(c)+27),wait=gc_task_count(c,gc.a.printWait),fade=c->busRead8(c,gc.a.fade+7)&128;
    unsigned restored=gc_task_count(c,gc.a.restored),close=gc_task_count(c,gc.a.closeText),closing=gc_task_count(c,gc.a.closeFade);
    unsigned ownActive=c->busRead8(c,gc.a.tasks+40*gtx.owner+4);
    unsigned creation=!gc.ack&&restored==1&&wait==1;
    unsigned printing=gc.ack&&!active&&wait==1;
    unsigned fading=gc.ack&&fade&&close==1;
    unsigned copying=gc.ack&&!fade&&closing==1&&cb==(gc.a.partyMain&~1u);
    unsigned cleanup=gc.ack&&cb==(gc.a.exitBattle&~1u);
    if(!(creation||printing||fading||copying||cleanup)) {
        if(cb==(gc.a.partyMain&~1u)&&gtx.valid&&!gt_live(c,gtx.internal,568))return GT_ERROR;
        return GT_NONE;
    }
    struct GtContext x={0};if(!gt_context(c,&x))return GT_ERROR;
    if(creation) {
        if(!gt_common(c,cb,1)||!gt_roles(c,1,gc.a.restored,1)||fade||active!=1||c->busRead8(c,gc_message(c)+28)!=0)return GT_ERROR;
        unsigned valid=0;
        if(x.pc>=GT_DISPLAY+0x12&&x.pc<=GT_DISPLAY+0x22) {
            valid=x.r[4]==0&&gt_stack(c,x.r[13]+4,(GT_RESTORED+0x2e)|1)
                &&gt_task_frame(c,x.r[13]+8,12,gtx.owner);
        }else if(x.pc==GT_CREATE+0x36||x.pc==GT_CREATE+0x38||x.pc==GT_CREATE+0x4c) {
            valid=x.r[4]==gc.a.tasks+40*gtx.wait&&x.r[5]==40*gtx.wait&&x.r[6]==gtx.wait&&x.r[7]==gc.a.tasks
                &&gt_stack(c,x.r[13]+16,(GT_DISPLAY+0x12)|1)&&gt_stack(c,x.r[13]+20,0)
                &&gt_stack(c,x.r[13]+24,(GT_RESTORED+0x2e)|1)&&gt_task_frame(c,x.r[13]+28,12,gtx.owner);
        }
        unsigned offset=x.pc-GT_RESTORED;
        const unsigned points[]={0x2e,0x30,0x34,0x38,0x3a,0x3c,0x3e,0x40,0x42,0x44};
        for(unsigned i=0;i<sizeof points/sizeof *points;i++)if(offset==points[i])
            valid=x.r[5]==gtx.owner&&gt_task_frame(c,x.r[13],12,gtx.owner);
        if(!valid)return GT_ERROR;
        return gt_snapshot(c,gc.healed.party,0);
    }
    if(!gc.released||gc.keys||gc.heals!=1)return GT_ERROR;
    if(printing) {
        if(!gt_common(c,cb,1)||!gt_roles(c,1,gc.a.closeText,1)||fade)return GT_ERROR;
        unsigned valid=0;
        if(x.pc>=GT_TEXT+0x70&&x.pc<=GT_TEXT+0x7c&&!(x.pc&1)) {
            unsigned sp=x.r[13],offset=x.pc-GT_TEXT,printer=gc_message(c);
            valid=x.r[4]==1&&x.r[6]==216u+(offset>=0x72?36u:0u)
                &&x.r[5]==printer+4+(offset>=0x74?36u:0u)
                &&x.r[8]==printer+(offset>=0x78?36u:0u)&&x.r[7]==25u-(offset>=0x7a?1u:0u)
                &&gt_stack(c,sp+4,6)&&gt_stack(c,sp+8,gtx.wait)
                &&gt_stack(c,sp+20,(GT_TEXTRET+0xc)|1)&&gt_stack(c,sp+24,gtx.wait)
                &&gt_stack(c,sp+28,(GT_PRINTWAIT+0xe)|1)&&gt_task_frame(c,sp+32,12,gtx.wait);
        }else if(x.pc>=GT_PRINTWAIT+0xe&&x.pc<=GT_PRINTWAIT+0x38&&!(x.pc&1))
            valid=x.r[4]==gtx.wait&&x.r[5]==gtx.wait&&gt_task_frame(c,x.r[13],12,gtx.wait);
        if(!valid)return GT_ERROR;
        unsigned result=gt_snapshot(c,gc.healed.party,0);if(!result)gc.printerFinished=1;return result;
    }
    if(fading) {
        if(!gc.printerFinished||!gc.taskDestroyed||!gt_common(c,cb,1)||!gt_roles(c,1,gc.a.closeText,0))return GT_ERROR;
        unsigned offset=x.pc-GT_CLOSE;
        unsigned valid=offset>=0x1a&&offset<=0x26&&x.r[4]==gtx.owner&&gt_close_frame(c,x.r[13]);
        if(x.pc>=GT_FADE+0xb8&&x.pc<=GT_FADE+0x12c)
            valid=gt_stack(c,x.r[13]+4,gtx.owner)&&gt_stack(c,x.r[13]+20,(GT_CLOSE+0x1a)|1)
                &&gt_close_frame(c,x.r[13]+24);
        if(!valid)return GT_ERROR;
        unsigned result=gt_snapshot(c,gc.healed.party,0);if(!result)gc.fadeSeen=1;return result;
    }
    if(copying) {
        if(!gc.printerFinished||!gc.taskDestroyed||!gc.fadeSeen||!gt_common(c,cb,1)||!gt_roles(c,1,gc.a.closeFade,0))return GT_ERROR;
        if(gt_wait_boundary(c,&x))return gt_snapshot(c,gc.healed.party,0); /* final inactive fade frame, before copy */
        return gt_copy(c,&x,positions);
    }
    if(cleanup) {
        if(!gc.printerFinished||!gc.taskDestroyed||!gc.fadeSeen||wait||close||fade)return GT_ERROR;
        unsigned live=gt_live(c,gtx.internal,568),valid=0,finished=0;
        if(x.pc==GT_CLOSEFADE+0x30||x.pc==GT_CLOSEFADE+0x46||x.pc==GT_CLOSEFADE+0x4a) {
            valid=ownActive&&live&&x.r[4]==gc.a.partyMenu&&x.r[5]==gtx.owner&&gt_task_frame(c,x.r[13],12,gtx.owner);
        }else if(x.pc==GT_CLOSEFADE+0x4e||x.pc==GT_CLOSEFADE+0x50||x.pc==GT_CLOSEFADE+0x54) {
            valid=gt_dead(c,gtx.internal)&&x.r[4]==gc.a.partyMenu&&x.r[5]==gtx.owner&&gt_task_frame(c,x.r[13],12,gtx.owner)
                &&ownActive==(x.pc==GT_CLOSEFADE+0x54?0u:1u);finished=x.pc==GT_CLOSEFADE+0x54;
        }else if(x.pc>=GT_FREEPOINTERS+0xe&&x.pc<=GT_FREEPOINTERS+0x36&&!(x.pc&1)) {
            valid=ownActive&&!live&&x.r[4]==gc.a.partyMenu&&x.r[5]==gtx.owner
                &&gt_stack(c,x.r[13],(GT_CLOSEFADE+0x4e)|1)&&gt_task_frame(c,x.r[13]+4,12,gtx.owner);
        }else if(x.pc>=GT_DESTROY+0x1a&&x.pc<=GT_DESTROY+0x6a&&!(x.pc&1)) {
            valid=!ownActive&&!live&&x.r[4]==gc.a.tasks&&x.r[2]==gc.a.tasks+40*gtx.owner
                &&gt_stack(c,x.r[13],gc.a.partyMenu)&&gt_stack(c,x.r[13]+4,(GT_CLOSEFADE+0x54)|1)
                &&gt_task_frame(c,x.r[13]+8,12,gtx.owner);
        }else if(gt_wait_boundary(c,&x)){valid=!ownActive&&!live;finished=1;}
        if(!valid||!gt_common(c,cb,live)||!gt_roles(c,ownActive,gc.a.closeFade,0))return GT_ERROR;
        unsigned char expected[600];gc_permute(gc.healed.party,expected,positions,1);
        unsigned result=gt_snapshot(c,expected,0);if(result)return result;
        if(!live)gtx.freed=1;
        gtx.copyProgress=600;
        if(finished){gc.exitSeen=1;return 0;} /* no premature completion inside cleanup */
        return 0;
    }
    return GT_ERROR;
}
