/* Read-only actual allocation and hardware checks for the environment pilot. */
struct V01Addresses {unsigned sprites,tiles,palettes,heapStart,heapSize,layout;};
struct V01Peak {unsigned samples,objects,sprites,objTiles,objPalettes,heapUsed,heapFreeMin;};
static unsigned v01_sample(struct mCore *core,struct V01Addresses a,struct WalkAddresses w,struct V01Peak *peaks)
{
    if(!cold_phase_ready(core,w))return 0;
    unsigned sb=core->busRead32(core,w.saveptr),map=core->busRead8(core,sb+5);
    if(core->busRead8(core,sb+4)!=35 || map>4)return 80;
    struct V01Peak *p=peaks+map;unsigned objects=0,sprites=0,tiles=0,palettes=0;
    for(unsigned i=0;i<16;i++)objects+=core->busRead8(core,w.objects+36*i)&1;
    for(unsigned i=0;i<64;i++)sprites+=core->busRead8(core,a.sprites+68*i+62)&1;
    for(unsigned i=0;i<128;i++){unsigned b=core->busRead8(core,a.tiles+i);for(unsigned j=0;j<8;j++)tiles+=(b>>j)&1;}
    for(unsigned i=0;i<16;i++)palettes+=core->busRead16(core,a.palettes+2*i)!=65535;
    unsigned start=core->busRead32(core,a.heapStart),size=core->busRead32(core,a.heapSize),at=start,used=0,free=0,n=0;
    if(!start || size!=0x1c000)return 81;
    do {
        if(at<start || at+16>start+size || ++n>2048 || core->busRead16(core,at+2)!=0xa3a3)return 81;
        unsigned amount=core->busRead32(core,at+4),flag=core->busRead16(core,at);
        if(flag>1 || amount>size || at+16+amount>start+size)return 81;
        if(flag)used+=amount;else free+=amount;
        at=core->busRead32(core,at+12);
    }while(at!=start);
    if(used+free+16*n!=size)return 81;
#define V01_MAX(field,value) do {if((value)>p->field)p->field=(value);}while(0)
    V01_MAX(objects,objects);V01_MAX(sprites,sprites);V01_MAX(objTiles,tiles);V01_MAX(objPalettes,palettes);V01_MAX(heapUsed,used);
#undef V01_MAX
    if(!p->samples || free<p->heapFreeMin)p->heapFreeMin=free;
    p->samples++;return 0;
}
static unsigned v01_file_match(struct mCore *core,const char *file,unsigned address,unsigned limit)
{
    FILE *f=fopen(file,"rb");if(!f)return 82;unsigned n=0;int b;
    while((b=fgetc(f))!=EOF){if(n>=limit || core->busRead8(core,address+n)!=(unsigned)b){fclose(f);return 82;}n++;}
    if(ferror(f) || fclose(f) || !n)return 82;
    printf("PASS hardware bytes file=%s address=%08x bytes=%u\n",file,address,n);return 0;
}
static unsigned v01_scene(struct mCore *core,struct V01Addresses a,struct WalkAddresses w,const char *label)
{
    if(!cold_phase_ready(core,w))return 40;
    unsigned sb=core->busRead32(core,w.saveptr),map=core->busRead8(core,sb+5),width=core->busRead32(core,a.layout),height=core->busRead32(core,a.layout+4),buffer=core->busRead32(core,a.layout+8);
    char file[128];snprintf(file,sizeof file,"expected-map-%u.bin",map);FILE *f=fopen(file,"rb");if(!f || !buffer || width*height>10240)return 83;
    /* Actual connected-map buffer includes the engine's seven-cell border. */
    unsigned mw=map==0?64:16,mh=map==0?48:14;
    if(width!=mw+15 || height!=mh+14){fclose(f);return 83;}
    for(unsigned y=0;y<mh;y++)for(unsigned x=0;x<mw;x++){
        int lo=fgetc(f),hi=fgetc(f);if(lo<0 || hi<0 || core->busRead16(core,buffer+2*((y+7)*width+x+7))!=(unsigned)(lo|(hi<<8))){fclose(f);return 83;}
    }
    if(fgetc(f)!=EOF || fclose(f))return 83;
    unsigned reason=v01_file_match(core,"expected-atlas.bin",0x06004000,16384);if(reason)return reason;
    reason=v01_file_match(core,"expected-palettes.bin",0x050000c0,96);if(reason)return reason;
    unsigned used[1024]={0},mask=0,maximum=0,count=0;
    for(unsigned bg=1;bg<4;bg++){
        unsigned control=core->busRead16(core,0x04000008+2*bg),base=(control>>8)&31;
        if(((control>>2)&3)!=0 || (control&0x80) || (control>>14))return 84;
        for(unsigned i=0;i<1024;i++){
            unsigned entry=core->busRead16(core,0x06000000+2048*base+2*i),tile=entry&1023;
            used[tile]=1;mask|=1u<<(entry>>12);if(tile>maximum)maximum=tile;
        }
        printf("BG label=%s bg=%u control=%04x char_base=0 screen_base=%u screen_bytes=2048\n",label,bg,control,base);
    }
    for(unsigned i=0;i<1024;i++)count+=used[i];
    printf("SCENE_VIEW label=%s map=%u bg_referenced_unique_tiles=%u bg_max_tile=%u bg_palette_mask=%04x loaded_secondary_bytes_verified=1 palettes6_7_8_verified=1 exact_interior_words=%u\n",label,map,count,maximum,mask,mw*mh);
    return 0;
}
