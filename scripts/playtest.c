/* Real mGBA input-driven gameplay testing; RAM reads only, never RAM patches.
 * Commands: step FRAMES KEYS CAPTURE.ppm (or -), expect GROUP MAP X Y FLAGS,
 * battle IN_BATTLE BATTLERS OUTCOME CARL_PP DONUT_PP TRIAL_WON DONUT_ABILITY, duo healthy,
 * roster CARL_HP DONUT_HP CARL_PP DONUT_PP CARL_STATUS DONUT_STATUS,
 * quit. Flags are the low three bits (E01 intro/crate and E02 guide) of save byte 0x1274.
 * RAM offsets match the pinned Emerald structs; update when their layouts change.
 * Supply ROM SAVE and `arm-none-eabi-nm -g --defined-only` output paths.
 */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/core/version.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <limits.h>

static int number(const char *text, unsigned limit, unsigned *out)
{
    char *end;
    unsigned long value;
    if (*text < '0' || *text > '9') return 0;
    errno=0;
    value=strtoul(text,&end,10);
    if (errno || *end || value>limit) return 0;
    *out=(unsigned)value;
    return 1;
}

// Decode only the saved party attack block; never decrypt or write game RAM in place.
static unsigned party_pp(struct mCore *core, unsigned mon)
{
    static const unsigned char attacksSlot[24]={1,1,2,3,2,3,0,0,0,0,0,0,2,3,1,1,3,2,2,3,1,1,3,2};
    unsigned personality=core->busRead32(core,mon);
    unsigned key=personality^core->busRead32(core,mon+4);
    return (core->busRead32(core,mon+0x20+12*attacksSlot[personality%24]+8)^key)&255;
}

static void log_emulator(struct mLogger *logger, int category, enum mLogLevel level,
                         const char *format, va_list args)
{
    (void)logger;
    if (level != mLOG_FATAL && level != mLOG_ERROR) return;
    fprintf(stderr, "%s: ", mLogCategoryName(category));
    vfprintf(stderr, format, args);
    fputc('\n', stderr);
}

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    unsigned saveptr=0, objects=0, avatar=0, party=0, count=0, mons=0, battlers=0, outcome=0, mainstate=0, addr;
    char type, symbol[128];
    FILE *symbols=fopen(argv[3], "r");
    if (!symbols) return 3;
    while (fscanf(symbols, "%x %c %127s", &addr, &type, symbol)==3) {
        if (!strcmp(symbol,"gSaveBlock1Ptr")) saveptr=addr;
        if (!strcmp(symbol,"gObjectEvents")) objects=addr;
        if (!strcmp(symbol,"gPlayerAvatar")) avatar=addr;
        if (!strcmp(symbol,"gPlayerParty")) party=addr;
        if (!strcmp(symbol,"gPlayerPartyCount")) count=addr;
        if (!strcmp(symbol,"gBattleMons")) mons=addr;
        if (!strcmp(symbol,"gBattlersCount")) battlers=addr;
        if (!strcmp(symbol,"gBattleOutcome")) outcome=addr;
        if (!strcmp(symbol,"gMain")) mainstate=addr;
    }
    fclose(symbols);
    if (!saveptr || !objects || !avatar || !party || !count || !mons || !battlers || !outcome || !mainstate) return 4;
    FILE *save=fopen(argv[2], "ab+");
    if (!save) return 5;
    fseek(save,0,SEEK_END);
    if (!ftell(save)) for (unsigned i=0;i<131072;i++) fputc(255,save);
    fclose(save);
    struct mLogger logger={.log=log_emulator,.filter=NULL};
    mLogSetDefaultLogger(&logger);
    struct mCore *core=mCoreFind(argv[1]);
    if (!core || !core->init(core)) return 6;
    mCoreConfigInit(&core->config,NULL);
    unsigned width,height;
    core->desiredVideoDimensions(core,&width,&height);
    color_t *pixels=calloc(width*height,sizeof(*pixels));
    if (!pixels) return 7;
    core->setVideoBuffer(core,pixels,width);
    core->setAudioBufferSize(core,1024);
    if (!mCoreLoadFile(core,argv[1]) || !mCoreLoadSaveFile(core,argv[2],false)) return 8;
    core->reset(core);
    printf("mGBA %s; %ux%u; save=%s; read-only RAM diagnostics\n",projectVersion,width,height,argv[2]);
    fflush(stdout);
    char line[256],name[128],extra,ft[32],kt[32];
    unsigned frames,keys,total=0,checks=0;
    int result=0;
    while (fgets(line,sizeof(line),stdin)) {
        if (!strcmp(line,"quit\n")) break;
        if (sscanf(line,"step %31s %31s %127s %c",ft,kt,name,&extra)==3) {
            if (!number(ft,36000,&frames) || !number(kt,1023,&keys) || !frames ||
                total>UINT_MAX-frames) {result=9;break;}
            core->setKeys(core,keys);
            for (unsigned i=0;i<frames;i++) core->runFrame(core);
            total+=frames;
            if (strcmp(name,"-")) {
                if (strspn(name,"abcdefghijklmnopqrstuvwxyz0123456789-.")!=strlen(name)) {result=10;break;}
                FILE *out=fopen(name,"wb");
                if (!out) {result=11;break;}
                fprintf(out,"P6\n%u %u\n255\n",width,height);
                for (unsigned i=0;i<width*height;i++) {
                    unsigned char rgb[]={pixels[i]&255,(pixels[i]>>8)&255,(pixels[i]>>16)&255};
                    if (fwrite(rgb,1,3,out)!=3) {result=12;break;}
                }
                if (fclose(out)) result=12;
                if (result) break;
            }
        } else if (strncmp(line,"expect ",7) && strncmp(line,"battle ",7) && strncmp(line,"roster ",7) && strcmp(line,"duo healthy\n")) {result=13;break;}
        unsigned sb=core->busRead32(core,saveptr);
        unsigned object=objects+core->busRead8(core,avatar+5)*0x24;
        int group=core->busRead8(core,sb+4),map=core->busRead8(core,sb+5);
        int x=(short)core->busRead16(core,object+0x10)-7;
        int y=(short)core->busRead16(core,object+0x12)-7;
        int flags=core->busRead8(core,sb+0x1274)&7;
        printf("frame=%u map=%d.%d pos=%d,%d flags=%d\n",total,group,map,x,y,flags);
        unsigned hp0=core->busRead16(core,party+0x56), max0=core->busRead16(core,party+0x58);
        unsigned hp1=core->busRead16(core,party+100+0x56), max1=core->busRead16(core,party+100+0x58);
        unsigned state[]={(core->busRead8(core,mainstate+0x439)>>1)&1,
            core->busRead8(core,battlers),core->busRead8(core,outcome),
            core->busRead8(core,mons+0x24),core->busRead8(core,mons+2*0x58+0x24),
            (core->busRead8(core,sb+0x1270+0x857/8)>>(0x857%8))&1,
            core->busRead8(core,mons+2*0x58+0x20)};
        printf("party=%u HP=%u/%u,%u/%u battle=%u battlers=%u outcome=%u PP=%u,%u trial=%u donut-ability=%u\n",
            core->busRead8(core,count),hp0,max0,hp1,max1,state[0],state[1],state[2],state[3],state[4],state[5],state[6]);
        unsigned roster[]={hp0,hp1,party_pp(core,party),party_pp(core,party+100),
            core->busRead32(core,party+0x50),core->busRead32(core,party+100+0x50)};
        printf("persistent PP=%u,%u status=%u,%u\n",roster[2],roster[3],roster[4],roster[5]);
        if (!strncmp(line,"roster ",7)) {
            char values[6][32]; unsigned wanted;
            if (sscanf(line,"roster %31s %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],values[5],&extra)!=6) result=19;
            for (unsigned i=0;i<6 && !result;i++)
                if (!number(values[i],UINT_MAX,&wanted) || wanted!=roster[i]) result=19;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++; printf("PASS %s",line);
        }
        if (!strcmp(line,"duo healthy\n")) {
            const unsigned char names[2][6]={{0xBD,0xBB,0xCC,0xC6,0xFF,0},{0xBE,0xC9,0xC8,0xCF,0xCE,0xFF}};
            if (core->busRead8(core,count)!=2 || !hp0 || hp0!=max0 || !hp1 || hp1!=max1) result=17;
            for (unsigned n=0;n<2;n++) for (unsigned i=0;i<(n?6:5);i++)
                if (core->busRead8(core,party+n*100+8+i)!=names[n][i]) result=17;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++; printf("PASS %s",line);
        }
        if (!strncmp(line,"battle ",7)) {
            char values[7][32]; unsigned wanted;
            if (sscanf(line,"battle %31s %31s %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],values[5],values[6],&extra)!=7) result=18;
            for (unsigned i=0;i<7 && !result;i++)
                if (!number(values[i],255,&wanted) || wanted!=state[i]) result=18;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++; printf("PASS %s",line);
        }
        if (!strncmp(line,"expect ",7)) {
            char values[5][32];
            unsigned eg,em,ex,ey,ef;
            if (sscanf(line,"expect %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],&extra)!=5 ||
                !number(values[0],255,&eg) || !number(values[1],255,&em) ||
                !number(values[2],2047,&ex) || !number(values[3],2047,&ey) || !number(values[4],7,&ef) ||
                (int)eg!=group || (int)em!=map || (int)ex!=x || (int)ey!=y || (int)ef!=flags) {
                fprintf(stderr,"FAILED: %s",line);result=14;break;
            }
            checks++;
            printf("PASS %s",line);
        }
        fflush(stdout);
    }
    if (ferror(stdin)) result=15;
    if (!result && !checks) result=16;
    mCoreConfigDeinit(&core->config);
    core->deinit(core);
    mLogSetDefaultLogger(NULL);
    free(pixels);
    printf("result=%d assertions=%u\n",result,checks);
    return result;
}
