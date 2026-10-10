/* Read-only host observer. Donut owns native Bag; native callbacks perform use. */
struct GcAddresses {unsigned tasks,fade,bagMain,bagInput,context,partyMain,partyInput,partyMenu,
    bagPosition,menu,selected,owner,order,indexes,actions,itemCB,medicine,useExit,internal,
    exitBattle,completeItem,bufferRun,hpTask,restored,closeText,returnBag,messagePrinters,printWait,closeFade,setupReshow,reshowEntry,reshow,textFlags,disablePrinters,string4;};
struct GcMedicine {struct GcAddresses a;struct CoSnapshot before,ui,healed;
    unsigned stage,start,recipient,slot,position,hp,max,heals,turn,decided,choice,uses,battleHp,healingCount;
    unsigned ack,ackFrame,keys,released,printerFinished,taskDestroyed,fadeSeen,exitSeen,setupSeen,reshowEntrySeen,reshowSeen;
    unsigned char order[3],owned[1272];};
static struct GcMedicine gc;
static unsigned gc_choice(unsigned c,unsigned cm,unsigned d,unsigned dm,unsigned alive,unsigned n,unsigned strike,unsigned brace) {
    if(c>cm||d>dm||cm>36||dm>28||n>2||strike>8||brace>40||alive>1)return 103;
    if(!c||!d)return 90;
    if(!strike&&brace)return 92;
    unsigned cr=c<=(alive?27u:12u),dr=d<=12;
    if(cr&&dr)return 100;
    if(!cr&&!dr)return 0;
    if(!n)return 101;
    unsigned hp=cr?c:d,max=cr?cm:dm,cap=hp+20;if(cap>max)cap=max;
    if(cap<=(cr&&alive?27u:12u))return 102;
    return cr?1:2;
}
static unsigned gc_quantity(const unsigned char*p) {
    unsigned total=0;for(unsigned i=0;i<30;i++)if(walk_u16(p+0xd0+4*i)==13)total+=walk_u16(p+0xd2+4*i);return total;
}
static unsigned gc_remove(unsigned char*p,unsigned pos) {
    if(pos>=30||!gc_quantity(p))return 0;
    /* One medicine consumption: exact preferred slot, then matching slots. */
    for(unsigned pass=0;pass<31;pass++) {
        unsigned i=pass?pass-1:pos;if(pass&&i==pos)continue;
        unsigned char*s=p+0xd0+4*i;unsigned q=walk_u16(s+2);
        if(walk_u16(s)==13&&q){walk_put16(s+2,q-1);if(q==1)walk_put16(s,0);return 1;}
    }return 0;
}
static void gc_compact(unsigned char*p) {
    for(unsigned i=0;i<29;i++)for(unsigned j=i+1;j<30;j++)if(!walk_u16(p+0xd2+4*i)) {
        unsigned char tmp[4];memcpy(tmp,p+0xd0+4*i,4);memcpy(p+0xd0+4*i,p+0xd0+4*j,4);memcpy(p+0xd0+4*j,tmp,4);
    }
}
static unsigned gc_order(const unsigned char*order,unsigned*positions) {
    unsigned seen=0;for(unsigned i=0;i<6;i++){unsigned v=i&1?order[i/2]&15:order[i/2]>>4;if(v>5||(seen&(1u<<v)))return 0;seen|=1u<<v;positions[i]=v;}
    return seen==63&&((positions[0]==0&&positions[1]==1)||(positions[0]==1&&positions[1]==0));
}
static void gc_permute(const unsigned char*in,unsigned char*out,const unsigned*positions,unsigned field) {
    for(unsigned i=0;i<6;i++)memcpy(out+100*(field?positions[i]:i),in+100*(field?i:positions[i]),100);
}
static unsigned gc_same(const struct CoSnapshot*a,const struct CoSnapshot*b) {
    unsigned char x[1272],y[1272];resource_canonical(x,a->owned,a->context);resource_canonical(y,b->owned,b->context);
    return !memcmp(a->party,b->party,600)&&!memcmp(a->flags,b->flags,300)&&!memcmp(x,y,1272)
      &&!memcmp(a->vars,b->vars,512)&&!memcmp(a->saved,b->saved,600)
      &&a->counter==b->counter&&a->count==b->count&&a->savedCount==b->savedCount
      &&a->group==b->group&&a->map==b->map&&a->section==b->section&&a->x==b->x&&a->y==b->y&&a->facing==b->facing;
}
static unsigned gc_task(struct mCore*c,unsigned callback) {
    unsigned hit=0,found=UINT_MAX;
    for(unsigned i=0;i<16;i++){unsigned t=gc.a.tasks+40*i;if(c->busRead8(c,t+4)&&(c->busRead32(c,t)&~1u)==(callback&~1u)){hit++;found=t;}}
    return hit==1?found:UINT_MAX;
}
static unsigned gc_ready(struct mCore*c,unsigned cb,unsigned task) {
    return (c->busRead32(c,co.a.main+4)&~1u)==(cb&~1u)&&!(c->busRead8(c,gc.a.fade+7)&128)&&gc_task(c,task)!=UINT_MAX;
}
static unsigned gc_owned_exact(struct CoSnapshot*s) {
    unsigned char now[1272],expected[1272];resource_canonical(now,s->owned,s->context);memcpy(expected,gc.owned,1272);
    unsigned initial=resource_word(co.before.owned)^co.before.context,money=resource_word(now);
    if(money!=initial&&money!=initial+320)return 0;
    memcpy(expected,now,4);return !memcmp(now,expected,1272);
}
static unsigned gc_read(struct mCore*c,struct CoSnapshot*s); /* Source-identical read below, without field CB gate. */
static unsigned gc_owner(struct mCore*c) {
    return c->busRead8(c,gc.a.owner)==2&&c->busRead16(c,gc.a.indexes)==0&&c->busRead16(c,gc.a.indexes+4)==1
      &&c->busRead8(c,gc.a.actions)==0&&c->busRead8(c,gc.a.actions+2)==1
      &&c->busRead16(c,co.a.chosen)==355
      &&(c->busRead32(c,co.a.controls+8)&~1u)==(gc.a.completeItem&~1u);
}
static void gc_dump(struct CoSnapshot*s,const char*kind) {
    char name[80];snprintf(name,sizeof name,"medicine-%02u-%s",gc.uses+1,kind);co_dump(s,name);
}
/* Native text.o TextPrinter[32], 36-byte records; WIN_MSG=PARTY_SIZE=6.
 * Layout/constants are admitted by the compile-only native ABI and scoped ELF. */
static unsigned gc_task_count(struct mCore*c,unsigned callback) {
    unsigned count=0;for(unsigned i=0;i<16;i++){unsigned a=gc.a.tasks+40*i;
        if(c->busRead8(c,a+4)&&(c->busRead32(c,a)&~1u)==(callback&~1u))count++;}return count;
}
static unsigned gc_message(struct mCore*c) {(void)c;return gc.a.messagePrinters+36*6;}
static unsigned gc_ack_ready(struct mCore*c) {
    unsigned printer=gc_message(c),wait=gc_task(c,gc.a.printWait),internal=c->busRead32(c,gc.a.internal);
    unsigned current=c->busRead32(c,printer);
    return gc_ready(c,gc.a.partyMain,gc.a.closeText)&&wait!=UINT_MAX&&c->busRead16(c,wait+8)==0
        &&gc_owner(c)&&gc.heals==1&&c->busRead8(c,gc.a.useExit)==1
        &&c->busRead8(c,co.a.turn-16)==gc.healingCount+1
        &&c->busRead16(c,gc.a.selected)==13&&c->busRead8(c,gc.a.partyMenu+9)==gc.slot
        &&c->busRead8(c,gc.a.partyMenu+8)==0x11&&c->busRead8(c,gc.a.partyMenu+11)==3
        &&internal&&(c->busRead32(c,internal+4)&~1u)==(gc.a.exitBattle&~1u)
        &&c->busRead8(c,printer+27)==1&&c->busRead8(c,printer+28)==1
        &&c->busRead8(c,printer+4)==6&&c->busRead8(c,printer+5)==1&&!c->busRead32(c,printer+16)
        &&!(c->busRead8(c,gc.a.textFlags)&4)&&!c->busRead8(c,gc.a.disablePrinters)
        &&current>=gc.a.string4+2&&current<gc.a.string4+1000
        &&c->busRead8(c,current-2)==0xfc&&c->busRead8(c,current-1)==9&&c->busRead8(c,current)==255;
}
static unsigned gc_lifecycle(struct mCore*c,unsigned cb,const unsigned*positions) {
    unsigned printer=gc_message(c),active=c->busRead8(c,printer+27),state=c->busRead8(c,printer+28);
    unsigned waitCount=gc_task_count(c,gc.a.printWait),closeCount=gc_task_count(c,gc.a.closeText);
    unsigned fadeCount=gc_task_count(c,gc.a.closeFade),fade=c->busRead8(c,gc.a.fade+7)&128;
    if(waitCount>1||closeCount>1||fadeCount>1)return 107;
    struct CoSnapshot now={0},expected=gc.healed;unsigned err=gc_read(c,&now);if(err)return err;
    if(cb!=(gc.a.partyMain&~1u))gc_permute(gc.healed.party,expected.party,positions,1);
    if(!gc_same(&expected,&now))return 106;
    if(c->busRead8(c,gc.a.owner)!=2||c->busRead8(c,gc.a.actions)!=0||c->busRead8(c,gc.a.actions+2)!=1
        ||c->busRead16(c,co.a.chosen)!=355||gc.heals!=1
        ||c->busRead8(c,co.a.turn-16)!=gc.healingCount+1)return 105;
    if(cb==(gc.a.partyMain&~1u)) {
        unsigned internal=c->busRead32(c,gc.a.internal);
        if(!gc_owner(c)||!internal||(c->busRead32(c,internal+4)&~1u)!=(gc.a.exitBattle&~1u)
            ||c->busRead8(c,gc.a.useExit)!=1||c->busRead16(c,gc.a.selected)!=13
            ||c->busRead8(c,gc.a.partyMenu+9)!=gc.slot||c->busRead8(c,gc.a.partyMenu+8)!=0x11
            ||c->busRead8(c,gc.a.partyMenu+11)!=3)return 105;
    }
    if(!gc.ack) {
        if(cb!=(gc.a.partyMain&~1u)||fade)return 107;
        /* DisplayHPRestoredMessage may still be scheduled at the healed boundary. */
        if(gc_task_count(c,gc.a.restored)==1&&!closeCount&&!waitCount)return 0;
        if(closeCount!=1||waitCount!=1||!active||!gc_owner(c))return 107;
        if(state==0)return 0; /* Ordinary printing: no input. */
        if(state!=1||!gc_ack_ready(c))return 107;
        return 0;
    }
    if(co.frames>gc.ackFrame&&!gc.keys)gc.released=1;
    if(gc.keys&&co.frames>gc.ackFrame+1)return 107;
    if(!active&&waitCount)return 107; /* RunTextPrinters FALSE destroys its task in the same native call. */
    if(!active)gc.printerFinished=1;
    if(!waitCount){if(active)return 107;gc.taskDestroyed=1;}
    if(gc.printerFinished&&active)return 107;
    if(gc.taskDestroyed&&waitCount)return 107;
    if(cb==(gc.a.partyMain&~1u)) {
        if(fadeCount) {
            if(!gc.released||!gc.printerFinished||!gc.taskDestroyed||closeCount||(!fade&&!gc.fadeSeen))return 107;
            gc.fadeSeen=1;
        }else if(fade||closeCount!=1)return 107;
        return 0;
    }
    if(!gc.released||!gc.printerFinished||!gc.taskDestroyed||!gc.fadeSeen||waitCount||closeCount||fadeCount)return 107;
    if(cb==(gc.a.exitBattle&~1u)) {if(fade)return 107;gc.exitSeen=1;return 0;}
    if(cb==(gc.a.setupReshow&~1u)) {if(!gc.exitSeen)return 107;gc.setupSeen=1;return 0;}
    if(cb==(gc.a.reshowEntry&~1u)) {if(!gc.setupSeen)return 107;gc.reshowEntrySeen=1;return 0;}
    if(cb==(gc.a.reshow&~1u)) {if(!gc.reshowEntrySeen)return 107;gc.reshowSeen=1;return 0;}
    if(cb==(co.a.battleMain&~1u))return gc.reshowSeen?0:107;
    return 107;
}
static unsigned gc_observe(struct mCore*c,const color_t*p,unsigned w,unsigned h) {
    if(!gc.stage)return 0;
    if(co.kind!=CO_GUARD||gc.uses>=2||co.frames-gc.start>=3600)return 104;
    if(gc.stage<4)return 0; // Party order is not consumed before native menu setup.
    unsigned positions[6];unsigned char nativeOrder[3];co_bytes(c,gc.a.order,nativeOrder,3);
    if(gc.stage>=4&&memcmp(nativeOrder,gc.order,3))return 103;
    if(gc.stage<4)memcpy(gc.order,nativeOrder,3);
    if(!gc_order(nativeOrder,positions))return 103;
    unsigned cb=c->busRead32(c,co.a.main+4)&~1u;
    if(cb==(gc.a.returnBag&~1u))return 105;
    /* Native battle HP is set once by medicine; party HP then animates separately. */
    unsigned hp=c->busRead16(c,co.a.mons+(gc.recipient?2:0)*88+40);
    if(hp!=gc.battleHp) {
        unsigned cap=gc.hp+20;if(cap>gc.max)cap=gc.max;
        if(gc.heals||hp!=cap)return 106;
        gc.heals++;gc.battleHp=hp;
    }
    if(gc.stage==4&&gc_task(c,gc.a.hpTask)!=UINT_MAX) {
        unsigned task=gc_task(c,gc.a.hpTask),cap=gc.hp+20;if(cap>gc.max)cap=gc.max;
        unsigned animation=c->busRead16(c,task+8),remaining=c->busRead16(c,task+14);
        if(c->busRead16(c,task+10)!=gc.max||c->busRead16(c,task+12)!=1
            ||c->busRead16(c,task+16)!=gc.slot||c->busRead16(c,task+18)!=gc.hp
            ||animation<gc.hp||animation>=cap||remaining!=cap-animation||gc.heals!=1)return 106;
        struct CoSnapshot now={0},expected=gc.ui;unsigned err=gc_read(c,&now);if(err)return err;
        unsigned partyHP=walk_u16(now.party+100*gc.slot+86);
        if(partyHP!=animation&&!(animation==gc.hp&&partyHP==cap))return 106;
        walk_put16(expected.party+100*gc.slot+86,partyHP);
        unsigned char logical[1272];resource_canonical(logical,expected.owned,expected.context);if(!gc_remove(logical,gc.position))return 101;
        resource_canonical(expected.owned,logical,expected.context);if(!gc_same(&expected,&now))return 106;
    }
    if(gc.stage==4&&(gc_ready(c,gc.a.partyMain,gc.a.restored)||gc_ready(c,gc.a.partyMain,gc.a.closeText))) {
        if(!gc_owner(c)||gc.heals!=1||!c->busRead8(c,gc.a.useExit)
            ||c->busRead8(c,co.a.turn-16)!=gc.healingCount+1
            ||c->busRead16(c,gc.a.selected)!=13||c->busRead8(c,gc.a.partyMenu+9)!=gc.slot)return 105;
        unsigned internal=c->busRead32(c,gc.a.internal);
        if(!internal||(c->busRead32(c,internal+4)&~1u)!=(gc.a.exitBattle&~1u))return 105;
        struct CoSnapshot now={0},expected=gc.ui;unsigned err=gc_read(c,&now);if(err)return err;
        unsigned cap=gc.hp+20;if(cap>gc.max)cap=gc.max;walk_put16(expected.party+100*gc.slot+86,cap);
        unsigned char logical[1272];resource_canonical(logical,expected.owned,expected.context);
        if(!gc_remove(logical,gc.position))return 101;
        resource_canonical(expected.owned,logical,expected.context);
        if(!gc_same(&expected,&now))return 106;
        memcpy(gc.owned,logical,1272);gc.healed=now;gc_dump(&now,"healed");gc.stage=5;
        char name[80];snprintf(name,sizeof name,"medicine-%02u-healed.ppm",gc.uses+1);if(capture(name,p,w,h))return 84;
        printf("MEDICINE_HEAL absolute=%u turn=%u owner=2 recipient=%u UI=%u HP=%u->%u restored=%u wasted=%u Potion=%u->%u CarlSTRIKE=355 DonutItemPP=0\n",
            co.frames,gc.turn,gc.recipient,gc.slot,gc.hp,cap,cap-gc.hp,20-(cap-gc.hp),gc_quantity(logical)+1,gc_quantity(logical));
    }
    if(gc.stage==5){unsigned err=gc_lifecycle(c,cb,positions);if(err)return err;}
    if(gc.stage==5&&cb==(co.a.battleMain&~1u)&&!(c->busRead8(c,gc.a.fade+7)&128)) {
        unsigned controller=c->busRead32(c,co.a.controls+8)&~1u;
        if(controller!=(gc.a.completeItem&~1u)&&controller!=(gc.a.bufferRun&~1u))return 105;
        if(c->busRead8(c,gc.a.owner)!=2||c->busRead8(c,gc.a.actions)!=0||c->busRead8(c,gc.a.actions+2)!=1
            ||c->busRead16(c,co.a.chosen)!=355)return 105;
        struct CoSnapshot now={0},expected=gc.healed;unsigned err=gc_read(c,&now);if(err)return err;
        gc_permute(gc.healed.party,expected.party,positions,1);
        if(!gc_same(&expected,&now)||gc.heals!=1)return 106;
        gc_dump(&now,"return");gc.uses++;gc.stage=0;
        printf("MEDICINE_RETURN absolute=%u turn=%u uses=%u full_state_exact=1 ack_frame=%u released=1 printer_done=1 print_task_destroyed=1 party_fade=1 field_order=1 exit=1 setup=1 reshow_entry=1 reshow=1\n",co.frames,gc.turn,gc.uses,gc.ackFrame);
    }
    return 0;
}
static unsigned gc_buttons(struct mCore*c,unsigned*key,const color_t*p,unsigned w,unsigned h) {
    *key=0;
    if(gc.stage==5&&!gc.ack) {
        unsigned positions[6];if(!gc_order(gc.order,positions))return 103;
        unsigned err=gc_lifecycle(c,c->busRead32(c,co.a.main+4)&~1u,positions);if(err)return err;
        if(gc_ack_ready(c)) {
            if(gc.keys)return 107; /* No held A: a fresh native JOY_NEW edge only. */
            gc.ack=1;gc.ackFrame=co.frames;*key=1;
            printf("MEDICINE_ACK absolute=%u turn=%u use=%u WAIT=1 owner=2 fresh_A=1 full_state_exact=1\n",co.frames,gc.turn,gc.uses+1);
        }
        return 0;
    }
    if(gc.stage==1&&gc_ready(c,gc.a.bagMain,gc.a.bagInput)) {
        if(!gc_owner(c)||c->busRead8(c,gc.a.bagPosition+4)!=1||c->busRead8(c,gc.a.bagPosition+5))return 105;
        struct CoSnapshot now={0},expected=gc.before;unsigned err=gc_read(c,&now);if(err)return err;
        unsigned char logical[1272];resource_canonical(logical,expected.owned,expected.context);gc_compact(logical);
        resource_canonical(expected.owned,logical,expected.context);if(!gc_same(&expected,&now))return 106;
        memcpy(gc.owned,logical,1272);
        gc.position=c->busRead16(c,gc.a.bagPosition+8)+c->busRead16(c,gc.a.bagPosition+18);
        if(gc.position>=30||walk_u16(logical+0xd0+4*gc.position)!=13)return 105;
        gc.before=now;gc_dump(&now,"bag");*key=1;gc.stage=2;
        char name[80];snprintf(name,sizeof name,"medicine-%02u-bag.ppm",gc.uses+1);if(capture(name,p,w,h))return 84;
    }else if(gc.stage==2&&gc_ready(c,gc.a.bagMain,gc.a.context)) {
        if(!gc_owner(c)||c->busRead16(c,gc.a.selected)!=13||c->busRead8(c,gc.a.menu+2))return 105;
        *key=1;gc.stage=3;
    }else if(gc.stage==3&&gc_ready(c,gc.a.partyMain,gc.a.partyInput)) {
        if(!gc_owner(c)||c->busRead16(c,gc.a.selected)!=13||c->busRead8(c,gc.a.partyMenu+8)!=0x11
            ||c->busRead8(c,gc.a.partyMenu+11)!=3||(c->busRead32(c,gc.a.itemCB)&~1u)!=(gc.a.medicine&~1u))return 105;
        unsigned positions[6];co_bytes(c,gc.a.order,gc.order,3);if(!gc_order(gc.order,positions))return 103;
        gc.slot=UINT_MAX;for(unsigned i=0;i<6;i++)if(positions[i]==gc.recipient)gc.slot=i;
        if(gc.slot>1)return 103;
        struct CoSnapshot now={0},expected=gc.before;unsigned err=gc_read(c,&now);if(err)return err;
        gc_permute(gc.before.party,expected.party,positions,0);if(!gc_same(&expected,&now))return 106;
        unsigned cursor=c->busRead8(c,gc.a.partyMenu+9);if(cursor>1)return 105;
        if(cursor!=gc.slot){*key=gc.slot?128:64;return 0;}
        gc.ui=now;gc.hp=walk_u16(now.party+100*gc.slot+86);gc.max=walk_u16(now.party+100*gc.slot+88);
        gc.battleHp=c->busRead16(c,co.a.mons+(gc.recipient?2:0)*88+40);if(gc.battleHp!=gc.hp||!gc.hp||gc.hp>=gc.max)return 103;
        gc_dump(&now,"before");
        char filename[80];snprintf(filename,sizeof filename,"medicine-%02u-order.bin",gc.uses+1);FILE*f=fopen(filename,"wb");
        if(!f||fwrite(gc.order,1,3,f)!=3||fclose(f))return 84;
        printf("MEDICINE_CONFIRM absolute=%u turn=%u owner=2 recipient=%u UI=%u position=%u HP=%u max=%u\n",co.frames,gc.turn,gc.recipient,gc.slot,gc.position,gc.hp,gc.max);
        snprintf(filename,sizeof filename,"medicine-%02u-recipient.ppm",gc.uses+1);if(capture(filename,p,w,h))return 84;
        gc.healingCount=c->busRead8(c,co.a.turn-16);gc.heals=0;
        gc.ack=gc.ackFrame=gc.released=gc.printerFinished=gc.taskDestroyed=gc.fadeSeen=gc.exitSeen=gc.setupSeen=gc.reshowEntrySeen=gc.reshowSeen=0;gc.stage=4;*key=1;
    }
    return 0;
}
