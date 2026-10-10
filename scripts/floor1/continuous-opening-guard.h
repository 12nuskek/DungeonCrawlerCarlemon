/* Host-only continuous phase, native reads and bounded lossless RGB chunks. */
/* Verified against native sizeof(Pokemon), offsetof(mail), MAIL_NONE by compile-only ABI. */
enum {CO_POKEMON_BYTES=100,CO_MAIL_OFFSET=85,CO_MAIL_NONE=0xFF};
struct CoSnapshot {unsigned char party[600],flags[300],owned[1272],vars[512],saved[600];
    unsigned context,counter,count,savedCount,group,map,section,x,y,facing;};
_Static_assert(sizeof(struct CoSnapshot)==3324,"Frozen complete native snapshot layout");
struct CoAddresses {unsigned party,count,save1,save2,main,cb1,cb2,vblank,objects,avatar,maps,trainer,outcome,newGame,continueGame,grid,mons,turn,move,power,crit,attacker,target,controls,chosen,moveResults,damage,battleMain;};
enum CoKind {CO_BOOT,CO_STABLE,CO_NOTE,CO_SUPPLY,CO_GUIDE,CO_TRIAL,CO_SCRAP,CO_POTION,CO_GUARD,CO_HOWLER,CO_BOSS,CO_STAIRS,CO_SAVE,CO_COLD};
struct CoGuard {struct CoSnapshot last,before;struct CoAddresses a;unsigned frames,limit,kind,armed,pending,attempts,battleWas,encounterFrames[4],newSeen,continueSeen,valid,deferred,phaseFrames;FILE *motion,*trace,*index,*battleTrace;unsigned chunk,chunkFrames,cold,combatLoaded;struct mCore*core;};
static struct CoGuard co;
static unsigned co_task_state(struct mCore*c,unsigned tasks,unsigned callback,unsigned index,unsigned low,unsigned high) {
    unsigned found=0,value=0;
    for(unsigned i=0;i<16;i++){unsigned t=tasks+40*i;if(c->busRead8(c,t+4)&&(c->busRead32(c,t)&~1u)==(callback&~1u)){found++;value=c->busRead16(c,t+8+2*index);}}
    return found==1&&value>=low&&value<=high;
}
static unsigned co_phase(struct mCore*c) {
    return !(c->busRead8(c,co.a.main+0x439)&2)
        && (c->busRead32(c,co.a.main)&~1u)==(co.a.cb1&~1u)
        && (c->busRead32(c,co.a.main+4)&~1u)==(co.a.cb2&~1u)
        && (c->busRead32(c,co.a.main+12)&~1u)==(co.a.vblank&~1u);
}
static void co_bytes(struct mCore*c,unsigned addr,unsigned char*p,unsigned n) {for(unsigned i=0;i<n;i++)p[i]=c->busRead8(c,addr+i);}
static unsigned co_read(struct mCore*c,struct CoSnapshot*s) {
    if(!co_phase(c))return 80;
    unsigned sb=c->busRead32(c,co.a.save1),sb2=c->busRead32(c,co.a.save2);
    s->count=c->busRead8(c,co.a.count);s->savedCount=c->busRead32(c,sb+0x234);
    s->group=c->busRead8(c,sb+4);s->map=c->busRead8(c,sb+5);s->counter=c->busRead16(c,sb+0x13f0);
    if(s->group!=35||s->map>4||s->map==2||s->count!=2||s->counter>=128)return 81;
    unsigned maps=c->busRead32(c,co.a.maps+4*s->group),header=c->busRead32(c,maps+4*s->map);
    unsigned player=c->busRead8(c,co.a.avatar+5);if(player>=16)return 81;
    unsigned obj=co.a.objects+36*player;s->x=(short)c->busRead16(c,obj+16)-7;s->y=(short)c->busRead16(c,obj+18)-7;
    s->facing=c->busRead8(c,obj+24)&15;s->section=c->busRead8(c,header+20);
    unsigned gx=c->busRead16(c,obj+16),gy=c->busRead16(c,obj+18);
    unsigned width=c->busRead32(c,co.a.grid),height=c->busRead32(c,co.a.grid+4),grid=c->busRead32(c,co.a.grid+8);
    if(!width||!height||gx>=width||gy>=height||width*height>10240
        ||(c->busRead16(c,grid+2*(gx+width*gy))&0xc00))return 81;
    co_bytes(c,co.a.party,s->party,600);co_bytes(c,sb+0x1270,s->flags,300);
    co_bytes(c,sb+0x490,s->owned,1272);co_bytes(c,sb+0x139c,s->vars,512);co_bytes(c,sb+0x238,s->saved,600);
    s->context=c->busRead32(c,sb2+0xac);
    for(unsigned i=0;i<6;i++) {
        unsigned char plain[48];const unsigned char*p=s->party+100*i;walk_decode(p,plain);
        if(walk_checksum(plain)!=walk_u16(p+28))return 82;
        if(i<2&&(!walk_valid(p)||!walk_u16(p+86)))return 82;
        if(i>=2){unsigned char empty[CO_POKEMON_BYTES]={0};empty[CO_MAIL_OFFSET]=CO_MAIL_NONE;if(memcmp(p,empty,CO_POKEMON_BYTES))return 82;}
    }
    const unsigned skipped[]={35,40,41,42,43,44,45,46,49,2139};
    for(unsigned i=0;i<sizeof skipped/sizeof *skipped;i++)if(s->flags[skipped[i]/8]&(1u<<(skipped[i]%8)))return 83;
    return 0;
}
static void co_dump(struct CoSnapshot*s,const char*name) {
    char fn[128];snprintf(fn,sizeof fn,"%s-state.bin",name);FILE*f=fopen(fn,"wb");if(!f||fwrite(s,1,sizeof *s,f)!=sizeof *s||fclose(f))exit(84);
}
static unsigned co_flags_allowed(unsigned flag) {
    if(co.kind==CO_BOOT)return flag==32;
    if(co.kind==CO_NOTE)return flag==33||flag==36;
    if(co.kind==CO_SUPPLY)return flag==38;
    if(co.kind==CO_GUIDE)return flag==34;
    if(co.kind==CO_TRIAL)return flag==37||flag==2135;
    if(co.kind==CO_SCRAP)return flag==39;
    if(co.kind==CO_GUARD)return flag==2136;
    if(co.kind==CO_HOWLER)return flag==2137;
    if(co.kind==CO_BOSS)return flag==47||flag==2138;
    if(co.kind==CO_STAIRS)return flag==48;
    return 0;
}
static void co_canonical(const unsigned char*raw,unsigned char*out) {
    unsigned char plain[48];walk_decode(raw,plain);memcpy(out,raw,100);
    for(unsigned i=0;i<4;i++)memcpy(out+32+12*i,plain+12*walk_orders[resource_word(raw)%24][i],12);
}
static unsigned co_mutable_member(unsigned member,const unsigned char*old,const unsigned char*now) {
    unsigned char a[100],b[100],seed[100];co_canonical(old,a);co_canonical(now,b);co_canonical(co.before.party+100*member,seed);
    if(co.kind==CO_GUIDE) {
        unsigned char healed[100];memcpy(healed,a,100);healed[52]=member?2:8;healed[53]=40;healed[54]=healed[55]=0;
        memset(healed+80,0,4);memcpy(healed+86,healed+88,2);
        memcpy(a+28,b+28,2);memcpy(healed+28,b+28,2);
        return !memcmp(a,b,100)||!memcmp(healed,b,100);
    }
    if(co.kind==CO_POTION) {
        if(member==0)return !memcmp(old,now,100);
        unsigned hp=walk_u16(seed+86),max=walk_u16(seed+88),expected=hp+20;if(expected>max)expected=max;
        if(walk_u16(b+86)!=hp&&walk_u16(b+86)!=expected)return 0;
        memcpy(a+86,b+86,2);return !memcmp(a,b,100);
    }
    const unsigned xpGain=co.kind==CO_TRIAL?96:co.kind==CO_GUARD?132:co.kind==CO_HOWLER?121:226;
    unsigned xp=resource_word(b+36);if(xp!=resource_word(seed+36)&&xp!=resource_word(seed+36)+xpGain)return 0;
    const unsigned ev[4][6]={{1,0,0,1,0,0},{0,0,0,1,1,0},{1,0,0,1,0,0},{3,0,0,0,0,0}};
    unsigned which=co.kind==CO_TRIAL?0:co.kind==CO_GUARD?1:co.kind==CO_HOWLER?2:3;
    for(unsigned i=0;i<6;i++){if(b[56+i]<seed[56+i]||b[56+i]>seed[56+i]+ev[which][i])return 0;a[56+i]=b[56+i];}
    if(b[84]<seed[84]||b[84]>seed[84]+1)return 0;
    unsigned expectedFriend=seed[41];if(b[84]!=seed[84])expectedFriend+=(expectedFriend>199?2:expectedFriend>99?3:5)+((walk_u16(seed+70)>>11)==11)+(seed[69]==co.last.section);
    if(expectedFriend>255)expectedFriend=255;
    if(b[41]!=expectedFriend)return 0;
    if(resource_word(b+80)||walk_u16(b+86)>walk_u16(b+88))return 0;
    for(unsigned i=0;i<4;i++){if(b[52+i]>seed[52+i]||b[52+i]>a[52+i])return 0;a[52+i]=b[52+i];}
    const unsigned bases[2][6]={{70,80,50,35,35,35},{40,45,35,90,40,40}};
    unsigned iv=resource_word(b+72),nature=resource_word(b)%25;
    for(unsigned j=0;j<6;j++) {
        unsigned stat=((2*bases[member][j]+((iv>>(5*j))&31)+b[56+j]/4)*b[84])/100+(j?5:b[84]+10);
        if(j&&nature/5!=nature%5){if(j-1==nature/5)stat=stat*110/100;if(j-1==nature%5)stat=stat*90/100;}
        if(walk_u16(b+88+2*j)!=stat)return 0;
    }
    memcpy(a+28,b+28,2);memcpy(a+36,b+36,4);a[41]=b[41];a[84]=b[84];memcpy(a+86,b+86,14);
    return !memcmp(a,b,100);
}
static unsigned co_owned_valid(struct CoSnapshot*s) {
    unsigned char a[1272],b[1272],seed[1272];resource_canonical(a,co.last.owned,co.last.context);resource_canonical(b,s->owned,s->context);resource_canonical(seed,co.before.owned,co.before.context);
    unsigned battle=co.kind==CO_TRIAL||co.kind==CO_GUARD||co.kind==CO_HOWLER||co.kind==CO_BOSS;
    if(battle){unsigned gain=co.kind==CO_TRIAL||co.kind==CO_GUARD?320:360;
        unsigned money=resource_word(b),initial=resource_word(seed);if(money!=initial&&money!=initial+gain)return 0;
        memcpy(a,b,4);return !memcmp(a,b,1272);}
    if(co.kind==CO_SUPPLY||co.kind==CO_SCRAP||co.kind==CO_POTION) {
        unsigned id=co.kind==CO_SCRAP?378:13,slot=UINT_MAX;
        for(unsigned i=0;i<30;i++)if(walk_u16(seed+0xd0+4*i)==id){slot=0xd0+4*i;break;}
        if(slot==UINT_MAX){if(co.kind==CO_POTION)return 0;for(unsigned i=0;i<30;i++)if(!walk_u16(seed+0xd0+4*i)){slot=0xd0+4*i;break;}}
        if(slot==UINT_MAX)return 0;
        unsigned target=co.kind==CO_POTION?walk_u16(seed+slot+2)-1:walk_u16(seed+slot+2)+2;
        unsigned char expected[1272];memcpy(expected,seed,1272);walk_put16(expected+slot,id);walk_put16(expected+slot+2,target);
        return !memcmp(b,seed,1272)||!memcmp(b,expected,1272);
    }
    return !memcmp(a,b,1272);
}
static unsigned co_field_validate(struct CoSnapshot*s) {
    if(!co.armed){co.last=*s;co.armed=1;return 0;}
    if(!walk_counter_valid(co.last.counter,s->counter))return 85;
    if(memcmp(co.last.party+200,s->party+200,400))return 85;
    for(unsigned flag=0;flag<2400;flag++) {
        unsigned before=(co.last.flags[flag/8]>>(flag%8))&1,after=(s->flags[flag/8]>>(flag%8))&1;
        if(before!=after&&(!co_flags_allowed(flag)||before))return 83;
    }
    unsigned mutableParty=co.kind==CO_GUIDE||co.kind==CO_TRIAL||co.kind==CO_GUARD||co.kind==CO_HOWLER||co.kind==CO_BOSS||co.kind==CO_POTION;
    if(!mutableParty){unsigned effects[2]={0};if(!walk_party_equal(co.last.party,s->party,co.last.counter==127&&s->counter==0,s->section,effects))return 85;}
    else for(unsigned member=0;member<2;member++)if(!co_mutable_member(member,co.last.party+100*member,s->party+100*member))return 85;
    unsigned mutableOwned=co.kind==CO_SUPPLY||co.kind==CO_SCRAP||co.kind==CO_POTION||co.kind==CO_TRIAL||co.kind==CO_GUARD||co.kind==CO_HOWLER||co.kind==CO_BOSS;
    if(mutableOwned?!co_owned_valid(s):!resource_equal(co.last.owned,co.last.context,s->owned,s->context))return 86;
    /* Native step counters are inside vars, not a blanket variable mask.
       Skipped trap keeps TEMP_0=0; Field intro sets TEMP_1=1 after warp reset. */
    unsigned char variables[512];memcpy(variables,co.last.vars,512);
    unsigned changedMap=s->map!=co.last.map;
    unsigned temp=walk_u16(s->vars+2),oldtemp=walk_u16(co.last.vars+2);
    if(walk_u16(s->vars)||temp>1||(temp!=oldtemp&&!((changedMap&&temp==0)||(s->map==0&&oldtemp==0&&temp==1))))return 86;
    walk_put16(variables,0);walk_put16(variables+2,temp);walk_put16(variables+0x54,s->counter);
    unsigned poison=walk_u16(s->vars+0x56),oldpoison=walk_u16(co.last.vars+0x56);
    unsigned combat=co.kind==CO_TRIAL||co.kind==CO_GUARD||co.kind==CO_HOWLER||co.kind==CO_BOSS;
    if(poison>3||poison!=(s->counter==co.last.counter?oldpoison:(oldpoison+1)%4)) {
        if(!combat||poison!=0)return 86;
    }
    walk_put16(variables+0x56,poison);if(memcmp(variables,s->vars,512))return 86;
    if(co.kind!=CO_SAVE&&(s->savedCount!=co.last.savedCount||memcmp(co.last.saved,s->saved,600)))return 86;
    co.last=*s;return 0;
}
static void co_stop(unsigned reason,const color_t*p,unsigned w,unsigned h) {
    /* Read-only CPU registers at the exact stop boundary; never advance/restore. */
    unsigned regs[20]={co.frames,reason,0,0};
    if(co.core&&co.core->readRegister)for(unsigned i=0;i<16;i++) {
        char name[8];snprintf(name,sizeof name,"r%u",i);
        if(co.core->readRegister(co.core,name,regs+4+i))regs[2]|=1u<<i;
    }
    unsigned psr[4]={0};
    if(co.core&&co.core->readRegister){psr[0]=co.core->readRegister(co.core,"cpsr",psr+2);psr[1]=co.core->readRegister(co.core,"spsr",psr+3);}
    FILE*cpu=fopen("first-failure-CPU-context-private.bin","wb");
    if(cpu){fwrite(regs,1,sizeof regs,cpu);fwrite(psr,1,sizeof psr,cpu);fclose(cpu);}
    capture("first-failure.ppm",p,w,h);if(co.armed)co_dump(&co.last,"last-accepted");
    fprintf(stderr,"CONTINUOUS STOP reason=%u frame=%u phase=%u encounters=%u\n",reason,co.frames,co.kind,co.attempts);fflush(stdout);exit(reason);
}
static void co_capture_frame(const color_t*p,unsigned w,unsigned h,unsigned after) {
    if(w!=240||h!=160)co_stop(87,p,w,h);
    if(!co.motion||co.chunkFrames==2000) {
        if(co.motion&&fclose(co.motion))co_stop(84,p,w,h);
        char name[64];snprintf(name,sizeof name,"motion-%03u.rgb",co.chunk++);co.motion=fopen(name,"wb");co.chunkFrames=0;if(!co.motion)co_stop(84,p,w,h);
    }
    unsigned char rgb[240*160*3];for(unsigned i=0;i<240*160;i++){rgb[3*i]=p[i]&255;rgb[3*i+1]=(p[i]>>8)&255;rgb[3*i+2]=(p[i]>>16)&255;}
    if(fwrite(rgb,1,sizeof rgb,co.motion)!=sizeof rgb)co_stop(84,p,w,h);
    /* Last word is accepted entries BEFORE this frame's admission. */
    unsigned idx[4]={co.frames,co.kind,after,co.attempts};if(fwrite(idx,1,sizeof idx,co.index)!=sizeof idx)co_stop(84,p,w,h);co.chunkFrames++;
}
static void co_run(struct mCore*c,const color_t*p,unsigned w,unsigned h) {
    co.core=c;
    if(w!=240||h!=160||co.frames>=co.limit)co_stop(87,p,w,h);
    unsigned before=(c->busRead8(c,co.a.main+0x439)&2)!=0;
    if(before){unsigned i=0;const unsigned phases[]={CO_TRIAL,CO_GUARD,CO_HOWLER,CO_BOSS};
        while(i<4&&phases[i]!=co.kind)i++;
        if(i==4||co.encounterFrames[i]>=(i==3?30000u:36000u))co_stop(87,p,w,h);}
    unsigned cb=c->busRead32(c,co.a.main+4)&~1u;
    if(cb==(co.a.newGame&~1u))co.newSeen=1;
    if(cb==(co.a.continueGame&~1u))co.continueSeen=1;
    if((co.cold&&co.newSeen)||(!co.cold&&co.continueSeen))co_stop(88,p,w,h);
    c->runFrame(c);co.frames++;co.phaseFrames++;
    unsigned after=(c->busRead8(c,co.a.main+0x439)&2)!=0;
    co_capture_frame(p,w,h,after); // Preserve the first violating frame too.
    if(before||after) {
        if(co.cold)co_stop(89,p,w,h);
        const unsigned phases[]={CO_TRIAL,CO_GUARD,CO_HOWLER,CO_BOSS};
        const unsigned trainers[]={855,856,857,858};unsigned i=0;
        while(i<4&&phases[i]!=co.kind)i++;
        if(i==4||c->busRead16(c,co.a.trainer)!=trainers[i])co_stop(89,p,w,h);
        if(!before&&after){if(co.attempts!=i)co_stop(89,p,w,h);co.attempts++;co.combatLoaded=0;}
        if(co.encounterFrames[i]>=(i==3?30000u:36000u))co_stop(87,p,w,h);
        co.encounterFrames[i]++;
        unsigned meta[16]={co.frames,co.kind,c->busRead8(c,co.a.turn),c->busRead16(c,co.a.move),c->busRead16(c,co.a.power),
            c->busRead8(c,co.a.crit),c->busRead8(c,co.a.attacker),c->busRead8(c,co.a.target),before,after,c->busRead8(c,co.a.outcome),i,
            c->busRead8(c,co.a.moveResults),c->busRead32(c,co.a.damage),0,0};
        unsigned char raw[976];co_bytes(c,co.a.party,raw,600);co_bytes(c,co.a.mons,raw+600,352);co_bytes(c,co.a.controls,raw+952,16);co_bytes(c,co.a.chosen,raw+968,8);
        if(fwrite(meta,1,sizeof meta,co.battleTrace)!=sizeof meta||fwrite(raw,1,sizeof raw,co.battleTrace)!=sizeof raw)co_stop(84,p,w,h);
        if(after&&(c->busRead32(c,co.a.main+4)&~1u)==(co.a.battleMain&~1u)) {
            unsigned alive=c->busRead16(c,co.a.mons+0x28)&&c->busRead16(c,co.a.mons+2*0x58+0x28);
            if(co.combatLoaded&&!alive)co_stop(90,p,w,h);
            if(alive)co.combatLoaded=1;
        }
        if(before&&!after&&c->busRead8(c,co.a.outcome)!=1)co_stop(90,p,w,h);
    }
    co.battleWas=after;
    if(co_phase(c)) {
        struct CoSnapshot s={0};unsigned error=co_read(c,&s);if(error){co_dump(&s,"first-invalid-or-partial");co_stop(error,p,w,h);}
        error=co_field_validate(&s);if(error){co_dump(&s,"first-invalid");co_stop(error,p,w,h);}
        unsigned hdr[4]={co.frames,co.kind,sizeof s,0};
        if(fwrite(hdr,1,sizeof hdr,co.trace)!=sizeof hdr||fwrite(&s,1,sizeof s,co.trace)!=sizeof s)co_stop(84,p,w,h);
        co.valid++;
    }else co.deferred++;
}
