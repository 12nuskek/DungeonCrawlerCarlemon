/* Read-only actual OBJ pixels/palettes/poses on the existing native object slots. */
struct CharacterState {
    unsigned observing,candidate,talkDirection,talkFrames,talkReactions;
    unsigned carlSeen[2],donutSeen[2],reactionFrames[2],lastFrame[2],lastFlip[2],samples;
    unsigned char carl[9][256],donut[4][128],palettes[64];
};
static unsigned character_load(const char *name,unsigned char *data,unsigned length)
{
    FILE *f=fopen(name,"rb");if(!f)return 90;
    if(fread(data,1,length,f)!=length || fgetc(f)!=EOF || fclose(f))return 90;
    return 0;
}
static unsigned character_sprite(struct mCore *core,struct V01Addresses a,unsigned objectBase,unsigned object,
                                 struct CharacterState *s,unsigned which,unsigned frame,unsigned *pose,unsigned *flip)
{
    unsigned id=core->busRead8(core,object+4),graphics=core->busRead8(core,object+5);
    if(id>=64 || graphics!=(which?203:0))return 91;
    unsigned sprite=a.sprites+68*id,attr0=core->busRead16(core,sprite),attr1=core->busRead16(core,sprite+2),attr2=core->busRead16(core,sprite+4);
    unsigned shape=attr0>>14,size=attr1>>14,tile=attr2&1023,palette=attr2>>12,count=which?(s->candidate?4:3):9,bytes=which?128:256;
    if(!(core->busRead8(core,sprite+62)&1) || shape!=(which?0:2) || size!=(which?1:2)
        || (signed char)core->busRead8(core,sprite+40)!=-8 || (signed char)core->busRead8(core,sprite+41)!=(which?-8:-16)
        || tile*32+bytes>32768)return 91;
    unsigned found=count;
    for(unsigned n=0;n<count;n++){
        unsigned equal=1;for(unsigned i=0;i<bytes;i++){
            unsigned expected=which?s->donut[n][i]:s->carl[n][i];
            if(core->busRead8(core,0x06010000+tile*32+i)!=expected){equal=0;break;}
        }
        if(equal){found=n;break;}
    }
    if(found==count)return 92;
    for(unsigned i=0;i<32;i++)if(core->busRead8(core,0x05000200+32*palette+i)!=s->palettes[32*which+i])return 93;
    *pose=found;*flip=(core->busRead8(core,sprite+63)&1);
    if(s->lastFrame[which]!=found || s->lastFlip[which]!=*flip){
        printf("CHAR_POSE absolute_frame=%u actor=%u object=%u sprite=%u gfx=%u pose=%u flip=%u facing=%u anim=%u tile=%u palette=%u pivot=%d,%d obj_bytes=%u verified=1\n",
            frame,which,(object-objectBase)/36,id,graphics,found,*flip,core->busRead8(core,object+24)&15,core->busRead8(core,sprite+42),tile,palette,
            (signed char)core->busRead8(core,sprite+40),(signed char)core->busRead8(core,sprite+41),bytes);
        s->lastFrame[which]=found;s->lastFlip[which]=*flip;
    }
    return 0;
}
static unsigned character_sample(struct mCore *core,struct V01Addresses a,struct WalkAddresses w,
                                  struct CharacterState *s,unsigned frame,const color_t *pixels,unsigned width,unsigned height)
{
    if(!s->observing || !cold_phase_ready(core,w))return 0;
    unsigned sb=core->busRead32(core,w.saveptr),player=core->busRead8(core,w.avatar+5);
    if(core->busRead8(core,sb+4)!=35 || core->busRead8(core,sb+5)!=1 || player>=16)return 94;
    unsigned pose,flip,reason=character_sprite(core,a,w.objects,w.objects+36*player,s,0,frame,&pose,&flip);if(reason)return reason;
    if(!(s->carlSeen[flip]&(1u<<pose))){char name[80];snprintf(name,sizeof name,"carl-pose-%u-flip-%u.ppm",pose,flip);if(capture(name,pixels,width,height))return 95;}
    s->carlSeen[flip]|=1u<<pose;
    unsigned donut=16;
    for(unsigned i=0;i<16;i++)if((core->busRead8(core,w.objects+36*i)&1) && core->busRead8(core,w.objects+36*i+8)==5){if(donut!=16)return 94;donut=i;}
    if(donut==16)return 94;
    unsigned object=w.objects+36*donut;
    if(core->busRead16(core,object+16)!=15 || core->busRead16(core,object+18)!=15)return 94;
    reason=character_sprite(core,a,w.objects,object,s,1,frame,&pose,&flip);if(reason)return reason;
    s->donutSeen[flip]|=1u<<pose;
    if(pose==3){
        if(!s->candidate || (s->talkDirection!=3 && s->talkDirection!=4)
            || (core->busRead8(core,object+24)&15)!=s->talkDirection || flip!=(s->talkDirection==4))return 96;
        s->reactionFrames[flip]++;s->talkReactions++;
        if(s->talkReactions==2){char name[80];snprintf(name,sizeof name,"donut-reaction-%u.ppm",s->talkDirection);if(capture(name,pixels,width,height))return 95;}
    }
    if(s->talkDirection)s->talkFrames++;
    s->samples++;return 0;
}
