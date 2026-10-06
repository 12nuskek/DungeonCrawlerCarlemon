/* Real mGBA input-driven gameplay testing; RAM reads only, never RAM patches.
 * Commands: step FRAMES KEYS CAPTURE.ppm (or -), expect GROUP MAP X Y FLAGS,
 * quit. Flags are the low two bits at the existing save flag byte for E01.
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
    unsigned saveptr=0, objects=0, avatar=0, addr;
    char type, symbol[128];
    FILE *symbols=fopen(argv[3], "r");
    if (!symbols) return 3;
    while (fscanf(symbols, "%x %c %127s", &addr, &type, symbol)==3) {
        if (!strcmp(symbol,"gSaveBlock1Ptr")) saveptr=addr;
        if (!strcmp(symbol,"gObjectEvents")) objects=addr;
        if (!strcmp(symbol,"gPlayerAvatar")) avatar=addr;
    }
    fclose(symbols);
    if (!saveptr || !objects || !avatar) return 4;
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
        } else if (strncmp(line,"expect ",7)) {result=13;break;}
        unsigned sb=core->busRead32(core,saveptr);
        unsigned object=objects+core->busRead8(core,avatar+5)*0x24;
        int group=core->busRead8(core,sb+4),map=core->busRead8(core,sb+5);
        int x=(short)core->busRead16(core,object+0x10)-7;
        int y=(short)core->busRead16(core,object+0x12)-7;
        int flags=core->busRead8(core,sb+0x1274)&3;
        printf("frame=%u map=%d.%d pos=%d,%d flags=%d\n",total,group,map,x,y,flags);
        if (!strncmp(line,"expect ",7)) {
            char values[5][32];
            unsigned eg,em,ex,ey,ef;
            if (sscanf(line,"expect %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],&extra)!=5 ||
                !number(values[0],255,&eg) || !number(values[1],255,&em) ||
                !number(values[2],2047,&ex) || !number(values[3],2047,&ey) || !number(values[4],3,&ef) ||
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
