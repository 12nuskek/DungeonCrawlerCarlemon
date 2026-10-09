/* Read-only battle graphics and exact baseline/candidate state comparison. */
struct BattleVisualAddresses {unsigned sprites,ids,healthboxes,tiles,palettes,heapStart,heapSize,poseState,unfaded,gfx,fieldCB2,battleCB2,phase,firstTurn,positions,copyCount,copies,copyArmed;};
struct BattleVisual {
    struct BattleVisualAddresses a;
    unsigned candidate,recording,frames,samples,mask,changes[4],last[4],repeat[4],captured,seenFaint,exitClean;
    unsigned maxSprites,maxTiles,maxPalettes,maxHeap,minFree,heapSamples,paletteChecks,paletteMask,enforced,warningFrames,warningOtherActor;
    unsigned char poses[18][2048],palettes[96];
    FILE *trace;
    unsigned callbackCount,callbackAddresses[20000],callbackNames[20000];
    unsigned readyRequested,readyFrame,transitionFrames,lastPhase,failedActor,failedSprite,failedStage,failedAddress,failedTraceByte;
};
static void bv_symbol(struct BattleVisual *v,unsigned address,char type,const char *name)
{
    if(type!='F')return; // Only preverified ELF STT_FUNC canonical identities.
    if(strncmp(name,"fn_",3) || strlen(name)!=67){fprintf(stderr,"Invalid verified function identity\n");exit(112);}
    unsigned hash=2166136261u;for(const unsigned char *p=(const unsigned char *)name;*p;p++)hash=(hash^*p)*16777619u;
    for(unsigned i=0;i<v->callbackCount;i++){
        if(v->callbackAddresses[i]==(address&~1u)){if(v->callbackNames[i]!=hash)exit(112);return;}
        if(v->callbackNames[i]==hash)exit(112);
    }
    if(v->callbackCount>=20000){fprintf(stderr,"Native callback symbol table overflow\n");exit(112);}
    v->callbackAddresses[v->callbackCount]=address&~1u;v->callbackNames[v->callbackCount++]=hash;
}
static unsigned bv_callback(struct BattleVisual *v,unsigned address)
{
    if(!address)return 0;
    for(unsigned i=0;i<v->callbackCount;i++)if(v->callbackAddresses[i]==(address&~1u))return v->callbackNames[i];
    return 0;
}
static unsigned bv_ram(unsigned address,unsigned size)
{
    return address>=0x02000000 && address<=0x02040000 && size<=0x02040000-address;
}
static unsigned bv_copy_pending(struct mCore *core,struct BattleVisual *v,unsigned dest,unsigned size)
{
    unsigned count=core->busRead8(core,v->a.copyCount),found=0;
    if(count>64)return 65;
    for(unsigned i=0;i<count;i++){
        unsigned at=v->a.copies+12*i,to=core->busRead32(core,at+4),n=core->busRead16(core,at+8);
        if(to<dest+size && to+n>dest)found++;
    }
    return found;
}
static unsigned bv_owned(struct mCore *core,struct BattleVisual *v,unsigned b)
{
    unsigned gfx=core->busRead32(core,v->a.gfx),id=core->busRead8(core,v->a.ids+b),pos=core->busRead8(core,v->a.positions+b);
    if(!bv_ram(gfx,384) || id>=64 || pos>=4)return 0;
    unsigned sprite=v->a.sprites+68*id,images=gfx+116+32*pos,buffer=core->busRead32(core,gfx+4+4*pos),first=core->busRead32(core,gfx);
    if(!(core->busRead8(core,sprite+62)&1) || (core->busRead8(core,sprite+63)&64)
        || core->busRead32(core,sprite+12)!=images || !bv_ram(buffer,8192) || buffer!=first+8192*pos)return 0;
    for(unsigned i=0;i<4;i++)if(core->busRead32(core,images+8*i)!=buffer+2048*i || core->busRead16(core,images+8*i+4)!=2048)return 0;
    return 1;
}
static unsigned bv_first_copy(struct mCore *core,struct BattleVisual *v,unsigned b)
{
    unsigned id=core->busRead8(core,v->a.ids+b),sprite=v->a.sprites+68*id;
    if(id>=64 || (core->busRead8(core,sprite+63)&4))return 0;
    unsigned tile=core->busRead16(core,sprite+4)&1023,dest=0x06010000+32*tile;
    if(tile*32+2048>32768 || bv_copy_pending(core,v,dest,2048))return 0;
    unsigned images=core->busRead32(core,sprite+12),buffer=core->busRead32(core,images);
    for(unsigned i=0;i<2048;i++)if(core->busRead8(core,dest+i)!=core->busRead8(core,buffer+i))return 0;
    return 1;
}
static unsigned bv_readiness(struct mCore *core,struct BattleVisual *v,unsigned mainstate,unsigned mons,unsigned results,unsigned currentMove)
{
    if(v->enforced || !v->readyRequested)return 0;
    if(!(core->busRead8(core,mainstate+0x439)&2))return 0;
    unsigned phase=core->busRead32(core,v->a.phase)&~1u;
    if(core->busRead8(core,results+0x13) || core->busRead16(core,currentMove)){v->failedStage=2;return 110;}
    if(phase!=(v->a.firstTurn&~1u))return 0;
    for(unsigned b=0;b<4;b++){
        unsigned species=core->busRead16(core,mons+88*b);
        unsigned id=core->busRead8(core,v->a.ids+b),sprite=v->a.sprites+68*(id<64?id:0);
        // Scratch data is restored by native send-out before this phase;
        // action animations may reuse it later. Registered picture ownership
        // stays mandatory throughout, not transient scratch values.
        if(!species || !core->busRead16(core,mons+88*b+40) || !bv_owned(core,v,b)
            || core->busRead16(core,sprite+46)!=b || core->busRead16(core,sprite+50)!=species || !bv_first_copy(core,v,b))return 0;
    }
    v->enforced=1;v->readyFrame=v->frames;
    printf("BV_READY frame=%u phase=HandleTurnActionSelectionState turn=0 all4_native_owned_first_pictures_copied=1\n",v->frames);
    return 0;
}
static void bv_diagnose(struct mCore *core,struct BattleVisual *v,unsigned reason,unsigned mons,unsigned mainstate,unsigned currentMove)
{
    unsigned phase=core->busRead32(core,v->a.phase),count=core->busRead8(core,v->a.copyCount);
    FILE *f=fopen("visual-stop.json","w");if(!f)return;
    fprintf(f,"{\"reason\":%u,\"visual_frame\":%u,\"enforced\":%u,\"ready_frame\":%u,\"failed_actor\":%u,\"failed_sprite\":%u,\"stage\":%u,\"unresolved_callback_address\":%u,\"native_phase_address\":%u,\"native_phase_ID\":%u,\"CB2\":%u,\"current_move\":%u,\"copy_count\":%u,\"copy_armed\":%u,\"actors\":[",reason,v->frames,v->enforced,v->readyFrame,v->failedActor,v->failedSprite,v->failedStage,v->failedAddress,phase,bv_callback(v,phase),core->busRead32(core,mainstate+4),core->busRead16(core,currentMove),count,core->busRead8(core,v->a.copyArmed));
    for(unsigned b=0;b<4;b++){
        unsigned id=core->busRead8(core,v->a.ids+b),sp=v->a.sprites+68*(id<64?id:0),tile=core->busRead16(core,sp+4)&1023,species=core->busRead16(core,mons+88*b);
        fprintf(f,"%s{\"actor\":%u,\"sprite\":%u,\"species\":%u,\"HP\":%u,\"position\":%u,\"owned\":%u,\"first_copy_complete\":%u,\"attr0\":%u,\"attr1\":%u,\"attr2\":%u,\"images\":%u,\"flags62\":%u,\"flags63\":%u,\"scratch_data0\":%u,\"scratch_data2\":%u,\"pending_picture_copies\":%u}",b?",":"",b,id,species,core->busRead16(core,mons+88*b+40),core->busRead8(core,v->a.positions+b),bv_owned(core,v,b),id<64&&bv_owned(core,v,b)?bv_first_copy(core,v,b):0,core->busRead16(core,sp),core->busRead16(core,sp+2),core->busRead16(core,sp+4),core->busRead32(core,sp+12),core->busRead8(core,sp+62),core->busRead8(core,sp+63),core->busRead16(core,sp+46),core->busRead16(core,sp+50),bv_copy_pending(core,v,0x06010000+32*tile,2048));
        if(id<64){char name[80];snprintf(name,sizeof name,"visual-stop-actor%u-vram.bin",b);FILE *raw=fopen(name,"wb");if(raw){for(unsigned i=0;i<2048;i++)fputc(core->busRead8(core,0x06010000+32*tile+i),raw);fclose(raw);}}
    }
    fputs("],\"copy_queue\":[",f);
    for(unsigned i=0;i<count && i<64;i++){unsigned at=v->a.copies+12*i;fprintf(f,"%s{\"source\":%u,\"destination\":%u,\"size\":%u}",i?",":"",core->busRead32(core,at),core->busRead32(core,at+4),core->busRead16(core,at+8));}
    fprintf(f,"],\"failed_trace_byte\":%u,\"partial_peaks\":{\"samples\":%u,\"sprites\":%u,\"obj_tiles\":%u,\"obj_palettes\":%u,\"heap_used\":%u,\"heap_free_min\":%u}}\n",v->failedTraceByte,v->heapSamples,v->maxSprites,v->maxTiles,v->maxPalettes,v->maxHeap,v->minFree);fclose(f);
}
static unsigned bv_load(const char *file,void *data,unsigned n)
{
    FILE *f=fopen(file,"rb");if(!f)return 100;
    if(fread(data,1,n,f)!=n || fgetc(f)!=EOF || fclose(f))return 100;
    return 0;
}
static unsigned bv_begin(struct BattleVisual *v)
{
    unsigned char mode;
    if(!v->a.phase || !v->a.positions || !v->a.copyCount || !v->a.copies || !v->a.copyArmed || !bv_callback(v,v->a.firstTurn))return 112;
    if(v->recording || v->frames || bv_load("visual-mode.bin",&mode,1) || mode>1)return 100;
    v->candidate=mode;
    if(bv_load("visual-poses.bin",v->poses,sizeof v->poses) || bv_load("visual-palettes.bin",v->palettes,sizeof v->palettes))return 100;
    for(unsigned b=0;b<4;b++)v->last[b]=255;
    v->trace=fopen(mode?"expected-state-trace.bin":"state-trace.bin",mode?"rb":"wb");
    if(!v->trace)return 100;
    v->recording=1;return 0;
}
static unsigned bv_heap(struct mCore *core,struct BattleVisual *v)
{
    unsigned sprites=0,tiles=0,palettes=0;
    for(unsigned i=0;i<64;i++)sprites+=core->busRead8(core,v->a.sprites+68*i+62)&1;
    for(unsigned i=0;i<128;i++){unsigned b=core->busRead8(core,v->a.tiles+i);for(unsigned j=0;j<8;j++)tiles+=(b>>j)&1;}
    for(unsigned i=0;i<16;i++)palettes+=core->busRead16(core,v->a.palettes+2*i)!=65535;
    unsigned start=core->busRead32(core,v->a.heapStart),size=core->busRead32(core,v->a.heapSize),at=start,used=0,free=0,n=0;
    if(!start || size!=0x1c000)return 101;
    do {
        if(at<start || at+16>start+size || ++n>2048 || core->busRead16(core,at+2)!=0xa3a3)return 101;
        unsigned amount=core->busRead32(core,at+4),flag=core->busRead16(core,at);
        if(flag>1 || amount>size || at+16+amount>start+size)return 101;
        if(flag)used+=amount;else free+=amount;
        at=core->busRead32(core,at+12);
    }while(at!=start);
    if(used+free+16*n!=size)return 101;
#define BV_MAX(field,value) do {if((value)>v->field)v->field=(value);}while(0)
    BV_MAX(maxSprites,sprites);BV_MAX(maxTiles,tiles);BV_MAX(maxPalettes,palettes);BV_MAX(maxHeap,used);
#undef BV_MAX
    if(!v->heapSamples || free<v->minFree)v->minFree=free;
    v->heapSamples++;return 0;
}
static unsigned bv_trace(struct mCore *core,struct BattleVisual *v,unsigned party,unsigned mons,unsigned saveptr,unsigned save2ptr,unsigned mainstate,unsigned results,unsigned currentMove,unsigned attacker,unsigned defender,unsigned outcome,unsigned controls)
{
    /* Private byte record includes full party and resources; never upload it. */
    unsigned char data[2560]={0},expected[2560]={0};unsigned at=0;
    v->failedActor=v->failedSprite=255;v->failedStage=v->failedAddress=0;
    v->failedTraceByte=2560;
#define BV_BYTES(address,n) do {for(unsigned z=0;z<(n);z++)data[at++]=core->busRead8(core,(address)+z);}while(0)
    unsigned sb=core->busRead32(core,saveptr),sb2=core->busRead32(core,save2ptr);
    if(sb<0x02000000 || sb+0x3d88>0x02040000 || sb2<0x02000000 || sb2+0xf2c>0x02040000)return 102;
    BV_BYTES(party,600);BV_BYTES(mons,352);BV_BYTES(sb+0x1270,300);BV_BYTES(sb+0x490,1272);
    BV_BYTES(mainstate+0x439,1);BV_BYTES(results+0x13,1);BV_BYTES(currentMove,2);BV_BYTES(attacker,1);BV_BYTES(defender,1);BV_BYTES(outcome,1);BV_BYTES(0x04000130,2);
#undef BV_BYTES
    // Link addresses differ by build. Compare the native callback's exact symbol identity.
    for(unsigned b=0;b<4;b++){
        unsigned address=core->busRead32(core,controls+4*b)&~1u,id=bv_callback(v,address);
        if(address && !id){v->failedActor=b;v->failedSprite=core->busRead8(core,v->a.ids+b);v->failedStage=1;v->failedAddress=address;return 112;}
        for(unsigned i=0;i<4;i++)data[at++]=(id>>(8*i))&255;
    }
    if(v->candidate){if(fread(expected,1,sizeof expected,v->trace)!=sizeof expected || memcmp(data,expected,sizeof data)){
        unsigned diff=0;while(diff<sizeof data && data[diff]==expected[diff])diff++;
        v->failedStage=8;v->failedTraceByte=diff;
        if(diff<200)v->failedActor=diff<100?0:2;
        else if(diff>=600 && diff<952)v->failedActor=(diff-600)/88;
        else if(diff>=2533 && diff<2549)v->failedActor=(diff-2533)/4;
        if(v->failedActor<4)v->failedSprite=core->busRead8(core,v->a.ids+v->failedActor);
        fprintf(stderr,"Exact battle-state/control divergence visual_frame=%u byte=%u; STOP\n",v->frames,diff);return 103;}}
    else if(fwrite(data,1,sizeof data,v->trace)!=sizeof data)return 103;
    return 0;
}
static unsigned bv_sample(struct mCore *core,struct BattleVisual *v,unsigned mainstate,unsigned mons,unsigned results,unsigned animationActive,unsigned animationActor,unsigned currentMove,unsigned pixels[],unsigned width,unsigned height)
{
    unsigned battle=core->busRead8(core,mainstate+0x439)&2;
    unsigned callback=core->busRead32(core,mainstate+4)&~1u;
    v->failedActor=v->failedSprite=255;v->failedStage=v->failedAddress=0;
    if(core->busRead8(core,v->a.copyCount)>64){v->failedStage=3;return 113;}
    if(callback==(v->a.fieldCB2&~1u) || callback==(v->a.battleCB2&~1u)){unsigned reason=bv_heap(core,v);if(reason)return reason;}
    char name[80];snprintf(name,sizeof name,"battle-%05u.ppm",v->frames);if(capture(name,pixels,width,height))return 104;
    if(!battle){
        if(v->candidate && v->a.poseState)for(unsigned i=0;i<16;i++)if(core->busRead8(core,v->a.poseState+i))return 105;
        v->exitClean++;return 0;
    }
    if(callback!=(v->a.battleCB2&~1u))return 0;
    unsigned phase=core->busRead32(core,v->a.phase);
    if(phase && !bv_callback(v,phase)){v->failedStage=1;v->failedAddress=phase;return 112;}
    if((phase&~1u)!=v->lastPhase){v->lastPhase=phase&~1u;printf("BV_PHASE frame=%u native_ID=%u\n",v->frames,bv_callback(v,phase));}
    unsigned readiness=bv_readiness(core,v,mainstate,mons,results,currentMove);if(readiness)return readiness;
    if(!v->enforced){v->transitionFrames++;return 0;}
    unsigned turn=core->busRead8(core,results+0x13),active=core->busRead8(core,animationActive),actor=core->busRead8(core,animationActor),move=core->busRead16(core,currentMove);
    for(unsigned b=0;b<3;b++){
        unsigned species=core->busRead16(core,mons+88*b),hp=core->busRead16(core,mons+88*b+40),expectedSpecies=b==0?66:b==1?371:52;
        if(species!=expectedSpecies)continue;
        if(!hp){
            if(v->candidate && v->a.poseState && (core->busRead8(core,v->a.poseState+4*b) || core->busRead8(core,v->a.poseState+4*b+3)))return 105;
            if(!(v->seenFaint&(1u<<b))){printf("BV_FAINT frame=%u actor=%u no_pose_state=%u\n",v->frames,b,v->candidate);v->seenFaint|=1u<<b;}
            continue;
        }
        unsigned id=core->busRead8(core,v->a.ids+b);
        if(!bv_owned(core,v,b)){v->failedActor=b;v->failedSprite=id;v->failedStage=3;return 105;}
        unsigned sprite=v->a.sprites+68*id,flags=core->busRead8(core,sprite+62),attr0=core->busRead16(core,sprite),attr1=core->busRead16(core,sprite+2),attr2=core->busRead16(core,sprite+4),tile=attr2&1023,palette=attr2>>12;
        if(!(flags&1) || attr0>>14 || attr1>>14!=3 || tile*32+2048>32768){v->failedActor=b;v->failedSprite=id;v->failedStage=3;return 105;}
        unsigned found=18;
        for(unsigned n=0;n<18;n++){
            if((b==0 && n>5)||(b==2 && (n<6 || n>11))||(b==1 && n<12))continue;
            if(!v->candidate && n!=(b==0?0:b==2?6:17))continue;
            unsigned equal=1;for(unsigned i=0;i<2048;i++)if(core->busRead8(core,0x06010000+32*tile+i)!=v->poses[n][i]){equal=0;break;}
            if(equal){found=n;break;}
        }
        /* Native intro/trainer/form loading is deferred, not treated as a pose. */
        if(found==18){v->failedActor=b;v->failedSprite=id;v->failedStage=4;return 107;}
        if(v->candidate && b==1 && v->a.poseState
            && core->busRead8(core,v->a.poseState+4)==5 && core->busRead8(core,v->a.poseState+5)>=18){
            if(found!=14){v->failedActor=b;v->failedSprite=id;v->failedStage=5;return 108;}
            v->warningFrames++;if(actor!=1 && active)v->warningOtherActor++;
        }
        v->samples++;v->mask|=1u<<found;
        if(v->last[b]!=found){
            v->last[b]=found;v->repeat[b]=0;v->changes[b]++;
            printf("BV_POSE frame=%u turn=%u actor=%u pose=%u sprite=%u tile=%u palette=%u x=%d y=%d x2=%d y2=%d pivot=%d,%d affine=%u active=%u animation_actor=%u move=%u hardware_bytes=2048\n",v->frames,turn,b,found,id,tile,palette,(short)core->busRead16(core,sprite+32),(short)core->busRead16(core,sprite+34),(short)core->busRead16(core,sprite+36),(short)core->busRead16(core,sprite+38),(signed char)core->busRead8(core,sprite+40),(signed char)core->busRead8(core,sprite+41),(attr0>>8)&3,active,actor,move);
        }
        v->repeat[b]++;
        if(v->repeat[b]==3 && !(v->captured&(1u<<found))){snprintf(name,sizeof name,"pose-%02u.ppm",found);if(capture(name,pixels,width,height))return 104;v->captured|=1u<<found;}
        /* Restored, non-effect palette checks: native scripts legitimately blend during actions. */
        if(!active && (found==0 || found==6 || found==12 || found==14 || found==17) && !(flags&4)){
            unsigned ch=b==0?0:b==2?1:2;
            unsigned equal=1;for(unsigned i=0;i<32;i++)if(core->busRead8(core,0x05000200+32*palette+i)!=v->palettes[32*ch+i]){equal=0;break;}
            if(equal){v->paletteChecks++;v->paletteMask|=1u<<ch;}
        }
    }
    return 0;
}
static unsigned bv_finish(struct BattleVisual *v)
{
    if(!v->recording || !v->trace)return 106;
    if(!v->enforced || !v->readyFrame)return 110;
    if(v->candidate && fgetc(v->trace)!=EOF)return 103;
    if(ferror(v->trace) || fclose(v->trace))return 103;
    v->recording=0;
    unsigned needed=v->candidate?131071:((1u<<0)|(1u<<6)|(1u<<17));
    if((v->mask&needed)!=needed || (v->captured&needed)!=needed || v->paletteMask!=7 || !(v->seenFaint&2) || !v->exitClean)return 106;
    if(v->candidate && (!v->warningFrames || !v->warningOtherActor))return 108;
    if(v->candidate && (v->changes[0]<12 || v->changes[1]<12 || v->changes[2]<12))return 106;
    printf("BV_FINISH candidate=%u frames=%u samples=%u pose_mask=%u captures=%u swaps=%u,%u,%u faint_mask=%u exit_clean_frames=%u restored_hardware_palette_checks=%u\n",v->candidate,v->frames,v->samples,v->mask,v->captured,v->changes[0],v->changes[1],v->changes[2],v->seenFaint,v->exitClean,v->paletteChecks);
    printf("BV_PEAK samples=%u sprites=%u obj_tiles=%u obj_palettes=%u heap_used=%u heap_free_min=%u\n",v->heapSamples,v->maxSprites,v->maxTiles,v->maxPalettes,v->maxHeap,v->minFree);
    printf("BV_WARNING held_frames=%u other_actor_animation_frames=%u hardware_palette_mask=%u\n",v->warningFrames,v->warningOtherActor,v->paletteMask);
    return 0;
}
