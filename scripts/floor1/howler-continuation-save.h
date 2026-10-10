/* Shared production/inert native same-file Save handoff. No paragraph advance. */
static struct {unsigned anchored,saveStage,overwrite,different,presses,keys,resolved;} hc;
static unsigned hc_text_exact(struct mCore*c,unsigned buffer,unsigned expected) {
    for(unsigned i=0;i<1024;i++) {
        unsigned byte=c->busRead8(c,expected+i);
        if(c->busRead8(c,buffer+i)!=byte)return 0;
        if(byte==255)return 1;
    }
    return 0;
}
static unsigned hc_save_key(unsigned keys,unsigned frames) {
    if(keys&1) {
        if(keys!=1||frames!=1||(hc.keys&1)||hc.saveStage>2||hc.presses!=hc.saveStage)return 95;
        hc.presses++;
    }
    hc.keys=keys;return 0;
}
static unsigned hc_save_ready(struct mCore*c,unsigned stage,unsigned saveFn,unsigned confirm,
                             unsigned success,unsigned done,unsigned fade,unsigned printers,unsigned menu) {
    if(stage>2||hc.saveStage!=stage||hc.presses!=stage+1||c->busRead8(c,hc.different))return 95;
    unsigned cb=c->busRead32(c,saveFn)&~1u;
    unsigned ready=stage==0?cb==(confirm&~1u):stage==1?cb==(hc.overwrite&~1u):(cb==(success&~1u)||cb==(done&~1u));
    if(!ready||(c->busRead8(c,fade+7)&128)||c->busRead8(c,printers+0x1b))return 1;
    if(stage<2&&c->busRead8(c,menu+2))return 95;
    return 0;
}
