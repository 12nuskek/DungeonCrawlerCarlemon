/* Bounded native-source logic and actual host closure; no emulator created.
 * Pixels, bus memory, registers and scheduling below are explicitly synthetic. */
#include <mgba/core/core.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <unistd.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int32_t s32;
typedef u8 bool8;
typedef u16 bool16;
typedef u32 bool32;
#include "native-types.inc"
#include "characters.inc"
#define TRUE 1
#define FALSE 0
#define A_BUTTON 1
#define B_BUTTON 2
#define SE_SELECT 1
#define TEXT_SKIP_DRAW 255
#define BATTLE_TYPE_RECORDED (1u<<24)
#define COPYWIN_GFX 2
#define WINDOWS_MAX 32
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
#define JOY_NEW(k) (gMain.newKeys&(k))
#define JOY_HELD(k) (gMain.heldKeys&(k))
#define PIXEL_FILL(c) ((c)|((c)<<4))
static struct {u16 newKeys,heldKeys;} gMain;
static struct {u8 canABSpeedUpPrint,autoScroll;} gTextFlags;
static u32 gBattleTypeFlags;
static struct {u8 width;} gCurGlyph;
static int gMPlayInfo_BGM;
static struct TextPrinter sTempTextPrinter,sTextPrinters[WINDOWS_MAX];
static bool8 gDisableTextPrinters;
static const u8 sWindowVerticalScrollSpeeds[]={1,2,4};
static const struct FontInfo *gFonts;
static u16 RenderText(struct TextPrinter *p);
static u32 RenderFont(struct TextPrinter *p);
static void CopyWindowToVram(u8 w,u8 m){(void)w;(void)m;}
static void TextPrinterDrawDownArrow(struct TextPrinter*p){(void)p;}
static void TextPrinterClearDownArrow(struct TextPrinter*p){(void)p;}
static void PlaySE(unsigned s){(void)s;}
static void PlayBGM(unsigned s){(void)s;}
static void m4aMPlayStop(int*p){(void)p;}
static void m4aMPlayContinue(int*p){(void)p;}
static bool8 IsSEPlaying(void){return FALSE;}
static int GetPlayerTextSpeed(void){return 0;}
static void FillWindowPixelBuffer(u8 w,u8 p){(void)w;(void)p;}
static void ScrollWindow(u8 w,u8 d,u8 s,u8 p){(void)w;(void)d;(void)s;(void)p;}
static void ClearTextSpan(struct TextPrinter*p,s32 w){(void)p;(void)w;}
static u8 DrawKeypadIcon(u8 w,u8 c,u8 x,u8 y){(void)w;(void)c;(void)x;(void)y;return 1;}
static void GenerateFontHalfRowLookupTable(u8 f,u8 b,u8 s){(void)f;(void)b;(void)s;}
static void DecompressGlyph_Small(u16 c,bool32 j){(void)c;(void)j;gCurGlyph.width=1;}
static void DecompressGlyph_Normal(u16 c,bool32 j){(void)c;(void)j;gCurGlyph.width=1;}
static void DecompressGlyph_Short(u16 c,bool32 j){(void)c;(void)j;gCurGlyph.width=1;}
static void DecompressGlyph_Narrow(u16 c,bool32 j){(void)c;(void)j;gCurGlyph.width=1;}
static void DecompressGlyph_SmallNarrow(u16 c,bool32 j){(void)c;(void)j;gCurGlyph.width=1;}
static void CopyGlyphToWindow(struct TextPrinter*p){(void)p;}
#include "native-render.inc"
#include "compiled-text.inc"
static const struct FontInfo fonts[10]={[FONT_NORMAL]={.fontFunction=FontFunc_Normal,.maxLetterHeight=15}};
static void stale_callback(struct TextPrinterTemplate*p,u16 c){(void)p;(void)c;}
static void partial_copy_checks(void){
    unsigned snapshots=0,mixed=0;
    const unsigned states[]={0,2,3};
    for(unsigned active=0;active<2;active++)for(unsigned state=0;state<3;state++){
        unsigned char old[36]={0},fresh[36]={0};
        old[1]=0x50;old[16]=1;old[19]=0xDE;old[27]=(u8)active;old[28]=(u8)states[state];
        fresh[1]=0x60;fresh[27]=1; /* Exact completed temp state=0/callback=NULL. */
        for(unsigned stage=0;stage<4;stage++){
            unsigned char observed[36];memcpy(observed,old,sizeof observed);
            memcpy(observed,fresh,stage*12);snapshots++;
            unsigned accepted=observed[27]&&(observed[28]==2||observed[28]==3);
            if(!active||stage==3)assert(!accepted);
            if(stage==1){assert(observed[1]==0x60&&observed[19]==0xDE);}
            if(stage>=2){assert(observed[1]==0x60&&observed[16]==0&&observed[19]==0);}
            if(accepted&&stage>0)mixed++;
        }
    }
    assert(snapshots==24&&mixed==4);
    puts("PARTIAL_COPY snapshots=24 mixed_owner_pauses=4; instruction-cut countermodels, native host-cut reachability unresolved");
}
static unsigned local_checks(void){
    unsigned cases=0;
    const unsigned speeds[]={0,1,255},delays[]={0,1,255};
    for(unsigned text=0;text<4;text++){
        for(unsigned cursor=0;cursor<lengths[text];cursor++)
        for(unsigned speed=0;speed<3;speed++)for(unsigned delay=0;delay<3;delay++)
        for(unsigned keys=0;keys<4;keys++)for(unsigned automatic=0;automatic<2;automatic++)
        for(unsigned sped=0;sped<2;sped++){
            struct TextPrinter p={0};p.state=RENDER_STATE_HANDLE_CHAR;p.active=TRUE;
            p.printerTemplate.currentChar=texts[text]+cursor;p.printerTemplate.fontId=FONT_NORMAL;
            p.textSpeed=(u8)speeds[speed];p.delayCounter=(u8)delays[delay];
            struct TextPrinterSubStruct*sub=(void*)p.subStructFields;sub->hasPrintBeenSpedUp=sped;
            gMain.newKeys=gMain.heldKeys=(u16)keys;gTextFlags.autoScroll=(u8)automatic;
            gTextFlags.canABSpeedUpPrint=TRUE;gFonts=fonts;
            (void)FontFunc_Normal(&p);
            assert(p.state==RENDER_STATE_HANDLE_CHAR);
            assert(p.printerTemplate.currentChar>=texts[text]&&p.printerTemplate.currentChar<=texts[text]+lengths[text]);cases++;
        }
        for(unsigned speed=0;speed<256;speed++){
            memset(sTextPrinters,0,sizeof sTextPrinters);sTextPrinters[0].state=RENDER_STATE_CLEAR;
            sTextPrinters[0].callback=stale_callback;
            struct TextPrinterTemplate t={.currentChar=texts[text],.fontId=FONT_NORMAL};
            gFonts=fonts;gMain.newKeys=gMain.heldKeys=0;gTextFlags.autoScroll=FALSE;
            assert(AddTextPrinter(&t,(u8)speed,NULL));
            if(speed&&speed!=TEXT_SKIP_DRAW){assert(sTextPrinters[0].active&&sTextPrinters[0].state==0);
                assert(sTextPrinters[0].printerTemplate.currentChar==texts[text]&&!sTextPrinters[0].callback);
            }else {assert(!IsTextPrinterActive(0));}
            cases++;
        }
        /* Early return is a real native branch; this old owner is a countermodel,
         * not asserted to be reachable on the unchanged gameplay route. */
        struct TextPrinterTemplate t={.currentChar=texts[text],.fontId=FONT_NORMAL};
        gFonts=NULL;sTextPrinters[0].active=1;sTextPrinters[0].state=2;
        sTextPrinters[0].callback=stale_callback;
        assert(!AddTextPrinter(&t,1,NULL)&&sTextPrinters[0].active&&sTextPrinters[0].state==2);cases++;
    }
    gFonts=fonts;memset(sTextPrinters,0,sizeof sTextPrinters);
    sTextPrinters[0].active=1;sTextPrinters[0].state=0;
    sTextPrinters[0].printerTemplate.currentChar=texts[0]+lengths[0]-1;
    sTextPrinters[0].printerTemplate.fontId=FONT_NORMAL;gDisableTextPrinters=FALSE;
    RunTextPrinters();assert(!sTextPrinters[0].active);cases++;
    printf("LOCAL cases=%u conditional owned HANDLE_CHAR invariant; no timing bound\n",cases);return cases;
}
/* Exact production PPM writer, snapshot writer, stop function and outer closure. */
static unsigned co_capture_absolute;
#include "host-types.inc"
static struct CoGuard co;
#include "host-stop.inc"
static unsigned char memory[65536];
static unsigned advances,keyChanges;
static color_t pixels[240*160];
static uint32_t read8(struct mCore*c,uint32_t a){(void)c;assert(a<sizeof memory);return memory[a];}
static void setKeys(struct mCore*c,uint32_t k){(void)c;assert(k<=1);keyChanges++;}
static bool readRegister(const struct mCore*c,const char*n,void*out){
    (void)c;unsigned v=0xB0000000u;
    if(n[0]=='r')v+=(unsigned)strtoul(n+1,NULL,10);
    else if(!strcmp(n,"cpsr"))v+=16;else if(!strcmp(n,"spsr"))v+=17;else return false;
    memcpy(out,&v,4);return true;
}
static struct mCore mock={.busRead8=read8,.setKeys=setKeys,.readRegister=readRegister};
static void co_run(struct mCore*c,const color_t*p,unsigned w,unsigned h){
    (void)c;(void)p;assert(w==240&&h==160);advances++;co.frames++;co_capture_absolute=co.frames;
    pixels[0]=(color_t)(co.frames&0xFFFFFFu);
    /* Tag every synthetic frame; refresh its full flat image at each exact
     * command-cycle boundary, including the final failing frame. */
    if(co.frames%401==0){for(unsigned i=0;i<w*h;i++)pixels[i]=pixels[0];}
    /* Complete synthetic frame/index admission coverage, including final frame. */
    unsigned row[2]={co.frames,(unsigned)pixels[0]};assert(fwrite(row,1,sizeof row,co.index)==sizeof row);
}
static int closure(const char*table,unsigned which,unsigned active,unsigned state){
    unsigned total=0,checks=0,addr=0;int result=0;char extra=0,type=0;
    const unsigned width=240,height=160,string4=0x6000,printers=0x7000,mainstate=0x8000;
    struct mCore*core=&mock;char*argv[4]={NULL,NULL,NULL,(char*)table};char line[2048];
    memset(memory,0,sizeof memory);memset(&co,0,sizeof co);memset(pixels,0,sizeof pixels);
    advances=keyChanges=co_capture_absolute=0;co.core=core;co.armed=1;
    memset(&co.last,0xA6,sizeof co.last);co.index=fopen("synthetic-frame-index.bin","wb");assert(co.index);
    memcpy(memory+string4,texts[which],lengths[which]);
    for(unsigned i=0;i<5;i++)memcpy(memory+0x1000+0x400*i,texts[i],lengths[i]);
    memory[printers+27]=(u8)active;memory[printers+28]=(u8)state;
    FILE*commands=tmpfile();assert(commands);
    fprintf(commands,"pages synthetic %s\n",labels[which]);rewind(commands);
    /* fgets and the terminal line are literal retained outer-loop boundaries.
     * The interior contains only the exact pages branch under test. */
    while (fgets(line,sizeof(line),commands)) {
#include "pages-command.inc"
        assert(!"unhandled fixture command");
    }
#include "outer-closure.inc"
    assert(!result&&total==advances&&!advances&&checks==1);assert(!fclose(co.index)&&!fclose(commands));return 0;
}
static void must_close(const char*table,unsigned which,unsigned active,unsigned state){
    char name[80];snprintf(name,sizeof name,"closure-%u-%u-%u",which,active,state);
    assert(!mkdir(name,0700));fflush(NULL);pid_t child=fork();assert(child>=0);
    if(!child){assert(!chdir(name));int result=closure(table,which,active,state);exit(result);}
    int status;assert(waitpid(child,&status,0)==child&&WIFEXITED(status));
    unsigned wanted=active?41:0;assert(WEXITSTATUS(status)==(int)wanted);
    char path[200];snprintf(path,sizeof path,"%s/synthetic-frame-index.bin",name);
    FILE*f=fopen(path,"rb");assert(f);unsigned row[2],last[2]={0},count=0;
    while(fread(row,1,sizeof row,f)==sizeof row){count++;assert(row[0]==count&&row[1]==count);memcpy(last,row,sizeof last);}assert(feof(f)&&!fclose(f));
    unsigned frames=active&&(state==2||state==3)?12832:0;assert(count==frames);
    if(wanted){
        snprintf(path,sizeof path,"%s/first-failure-CPU-context-private.bin",name);
        unsigned regs[24];f=fopen(path,"rb");assert(f&&fread(regs,1,sizeof regs,f)==sizeof regs&&fgetc(f)==EOF&&!fclose(f));
        assert(regs[0]==frames&&regs[1]==41&&regs[2]==65535&&regs[20]==1&&regs[21]==1);
        for(unsigned i=0;i<16;i++)assert(regs[4+i]==0xB0000000u+i);
        assert(regs[22]==0xB0000010u&&regs[23]==0xB0000011u);
        snprintf(path,sizeof path,"%s/first-failure.ppm",name);f=fopen(path,"rb");assert(f);
        char header[16];assert(fread(header,1,15,f)==15&&!memcmp(header,"P6\n240 160\n255\n",15));
        for(unsigned i=0;i<240*160;i++){unsigned char rgb[3];assert(fread(rgb,1,3,f)==3);
            assert(rgb[0]==(frames&255)&&rgb[1]==((frames>>8)&255)&&rgb[2]==0);}assert(fgetc(f)==EOF&&!fclose(f));
        snprintf(path,sizeof path,"%s/last-accepted-state.bin",name);f=fopen(path,"rb");assert(f);
        for(unsigned i=0;i<sizeof(struct CoSnapshot);i++){assert(fgetc(f)==0xA6);}
        assert(fgetc(f)==EOF&&!fclose(f));
        if(frames){
            snprintf(path,sizeof path,"%s/synthetic-00-31.ppm",name);f=fopen(path,"rb");assert(f);
            unsigned char rgb[3];assert(fread(header,1,15,f)==15&&!memcmp(header,"P6\n240 160\n255\n",15));
            assert(fread(rgb,1,3,f)==3&&rgb[0]==(12431&255)&&rgb[1]==(12431>>8)&&rgb[2]==0);
            assert(!fclose(f));
        }
    }
    printf("CLOSURE text=%u active=%u state=%u result=%u frames=%u terminal=%u\n",which,active,state,wanted,frames,wanted!=0);
}
int main(int argc,char**argv){
    assert(argc==2);partial_copy_checks();unsigned local=local_checks(),closures=0;
    for(unsigned text=0;text<4;text++){
        must_close(argv[1],text,0,2);closures++;
        must_close(argv[1],text,1,0);closures++;
        must_close(argv[1],text,1,2);closures++;
        must_close(argv[1],text,1,3);closures++;
    }
    must_close(argv[1],4,1,2);closures++;
    printf("PASS native-state local_cases=%u outer_closure_cases=%u checkpoint_failure=12832 final_frame_included=1 emulators=0\n",local,closures);
    return 0;
}
