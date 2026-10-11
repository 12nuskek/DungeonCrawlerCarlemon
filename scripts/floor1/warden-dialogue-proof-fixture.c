/* Inert command/control-flow proof. Counters are synthetic, never game frames. */
#include <mgba/core/core.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint8_t bool8;
typedef uint16_t bool16;
#include "native-types.inc"
enum {WINDOWS_MAX=32,COPYWIN_GFX=2};
enum {RENDER_PRINT,RENDER_FINISH,RENDER_REPEAT,RENDER_UPDATE};
#define A_BUTTON 1
#define B_BUTTON 2
#define TRUE 1
#define FALSE 0
#define SE_SELECT 1
#define TEST_BUTTON(field,button) ((field)&(button))
#define JOY_NEW(button) TEST_BUTTON(gMain.newKeys,button)
static struct {u16 newKeysRaw,newKeys,heldKeysRaw;} gMain;
static struct {u8 autoScroll;} gTextFlags;
static struct TextPrinter sTextPrinters[WINDOWS_MAX];
static bool8 gDisableTextPrinters;
static unsigned renderCalls,callbackCalls,copyCalls,arrowCalls,soundCalls;
static unsigned renderCommand=RENDER_UPDATE;
static u16 RenderFont(struct TextPrinter *p){(void)p;renderCalls++;return renderCommand;}
static void CopyWindowToVram(u8 id,u8 mode){(void)id;(void)mode;copyCalls++;}
static void TextPrinterDrawDownArrow(struct TextPrinter*p){(void)p;arrowCalls++;}
static void PlaySE(unsigned se){(void)se;soundCalls++;}
#include "native-printer.inc"
static struct {int16_t data[16];} gTasks[16];
static u16 gSpecialVar_Result;
static unsigned destroyed,enabled;
static int selected;
#define tRight data[2]
#define MENU_NOTHING_CHOSEN -2
#define MENU_B_PRESSED -1
static int Menu_ProcessInputNoWrapClearOnChoose(void){return selected;}
static void DestroyTask(u8 id){(void)id;destroyed++;}
static void ScriptContext_Enable(void){enabled++;}
#include "native-completion.inc"
#include "compiled-text.inc"
static void callback(struct TextPrinterTemplate*p,u16 command){(void)p;(void)command;callbackCalls++;}
static unsigned char memory[65536];
static unsigned frames,keys,pulses,fresh,captures,lastCapture,covered,commandCalls;
static unsigned finishAfter,initialHeld,printerState,activeStart,wrongText,battle;
static const unsigned string4=0x6000,printers=0x7000,mainstate=0x8000;
static uint32_t read8(struct mCore*c,uint32_t a){(void)c;assert(a<sizeof memory);return memory[a];}
static uint32_t read16(struct mCore*c,uint32_t a){return read8(c,a)|(read8(c,a+1)<<8);}
static uint32_t read32(struct mCore*c,uint32_t a){return read16(c,a)|(read16(c,a+2)<<16);}
static void setKeys(struct mCore*c,uint32_t k){(void)c;keys=k;if(k==1)pulses++;}
static struct mCore mock={.busRead8=read8,.busRead16=read16,.busRead32=read32,.setKeys=setKeys};
#include "native-task-ready.inc"
static void co_run(struct mCore*c,const color_t*p,unsigned w,unsigned h){
    (void)c;(void)p;assert(w==240&&h==160);
    u16 keyInput=(u16)keys;
    /* Exact native recognition assignments, not key-repeat or held-A credit. */
#include "native-key-edge.inc"
    if(gMain.newKeys&A_BUTTON)fresh++;
    RunTextPrinters();
    frames++;covered++; /* One indexed complete mock frame, including failure. */
    if(finishAfter&&pulses>=finishAfter&&frames%401==0)memory[printers+0x1b]=0;
}
static int capture(const char*name,const color_t*p,unsigned w,unsigned h){
    (void)name;(void)p;assert(w==240&&h==160);captures++;lastCapture=frames;return 0;
}
static void prepare(unsigned which){
    memset(memory,0,sizeof memory);memset(sTextPrinters,0,sizeof sTextPrinters);
    for(unsigned i=0;i<5;i++)memcpy(memory+0x1000+0x400*i,texts[i],lengths[i]);
    memcpy(memory+string4,texts[which],lengths[which]);if(wrongText)memory[string4]^=1;
    memory[printers+0x1b]=(u8)activeStart;memory[printers+0x1c]=(u8)printerState;
    memory[mainstate+0x439]=(u8)(battle?2:0);
    /* Deliberately unrelated cursor/callback: the exact helper never reads them. */
    memset(memory+printers,0xA5,0x18);
    sTextPrinters[0].active=1;sTextPrinters[0].state=(u8)printerState;
    gDisableTextPrinters=1;keys=0;pulses=0;gMain.heldKeysRaw=(u16)initialHeld;
}
static int sequence(const char*table,unsigned commands,unsigned timeoutAt){
    unsigned result=0,total=0,checks=0,addr=0;char extra=0,type=0;
    const color_t pixels[1]={0};const unsigned width=240,height=160;
    struct mCore*core=&mock;char*argv[4]={NULL,NULL,NULL,(char*)table};
    char line[2048];frames=covered=captures=fresh=lastCapture=commandCalls=0;
    for(unsigned cmd=0;cmd<commands;cmd++){
        prepare(cmd);finishAfter=cmd==timeoutAt?0:finishAfter;commandCalls++;
        snprintf(line,sizeof line,"pages inert-%u %s\n",cmd,labels[cmd]);
#include "pages-command.inc"
    }
    assert(total==frames&&covered==frames);(void)checks;return (int)result;
}
static void native_wait_checks(void){
    struct TextPrinter p={0};gTextFlags.autoScroll=0;gMain.newKeys=0;
    assert(!TextPrinterWait(&p)&&!TextPrinterWaitWithDownArrow(&p));
    gMain.newKeys=1;assert(TextPrinterWait(&p)&&TextPrinterWaitWithDownArrow(&p));
    gMain.newKeys=2;assert(TextPrinterWait(&p)&&TextPrinterWaitWithDownArrow(&p));
    gTextFlags.autoScroll=1;
    for(unsigned i=0;i<49;i++)assert(!TextPrinterWaitAutoMode(&p));
    assert(TextPrinterWaitAutoMode(&p));
    memset(sTextPrinters,0,sizeof sTextPrinters);sTextPrinters[0].active=1;
    sTextPrinters[0].callback=callback;gDisableTextPrinters=1;renderCalls=0;
    RunTextPrinters();assert(renderCalls==0&&sTextPrinters[0].active);
    gDisableTextPrinters=0;renderCommand=RENDER_UPDATE;RunTextPrinters();assert(renderCalls==1&&callbackCalls==1);
    renderCommand=RENDER_PRINT;RunTextPrinters();assert(copyCalls==1&&callbackCalls==2);
    renderCommand=RENDER_FINISH;RunTextPrinters();assert(!sTextPrinters[0].active&&callbackCalls==2);
    printf("PASS exact native waits/key consumers and disabled/update/print/finish/callback branches\n");
}
static void native_completion_checks(void){
    gMain.newKeys=0;assert(!WaitForAorBPress());
    gMain.newKeys=1;assert(WaitForAorBPress());gMain.newKeys=2;assert(WaitForAorBPress());
    for(unsigned i=0;i<5;i++){Task_HandleYesNoInput(0);assert(gTasks[0].data[2]==(int)i+1&&!destroyed&&!enabled);}
    selected=MENU_NOTHING_CHOSEN;Task_HandleYesNoInput(0);assert(!destroyed&&!enabled);
    for(int choice=-1;choice<=1;choice++){
        selected=choice;gSpecialVar_Result=255;Task_HandleYesNoInput(0);
        assert(gSpecialVar_Result==(choice==0)&&destroyed==(unsigned)(choice+2)&&enabled==destroyed);
    }
    memset(memory,0,sizeof memory);memory[0x9000]=0x01;memory[0x9001]=0x01;memory[0x9004]=1;
    memory[0x900c]=4;assert(!co_task_state(&mock,0x9000,0x100,2,5,65535));
    memory[0x900c]=5;assert(co_task_state(&mock,0x9000,0x100,2,5,65535));
    memory[0x9028]=0x01;memory[0x9029]=0x01;memory[0x902c]=1;
    assert(!co_task_state(&mock,0x9000,0x100,2,5,65535));memory[0x902c]=0;
    memory[0x9000]=0x03;assert(!co_task_state(&mock,0x9000,0x100,2,5,65535));memory[0x9000]=0x01;
    memory[0x9307]=128;
    assert(!co_task_state(&mock,0x9000,0x100,2,5,65535)||(read8(&mock,0x9307)&128));
    puts("PASS native Default fresh-A/B completion, YesNo delay/no-choice/B/No/Yes, destruction/script-enable and exact task admission negatives");
}
int main(int argc,char**argv){
    assert(argc==2);native_wait_checks();native_completion_checks();unsigned cases=0;
    for(unsigned text=0;text<5;text++){
        /* Rotate each actual compiled text into the one-command fixture. */
        const unsigned char*t=texts[0];unsigned n=lengths[0];const char*l=labels[0];
        texts[0]=texts[text];lengths[0]=lengths[text];labels[0]=labels[text];
        activeStart=0;printerState=2;finishAfter=0;initialHeld=wrongText=battle=0;
        assert(sequence(argv[1],1,99)==0&&frames==0&&captures==1);cases++;
        activeStart=1;
        for(unsigned state=2;state<=3;state++){
            printerState=state;
            assert(sequence(argv[1],1,0)==41&&frames==12832&&captures==32&&fresh==32&&lastCapture==12431);cases++;
        }
        initialHeld=1;assert(sequence(argv[1],1,0)==41&&frames==12832&&fresh==31);cases++;initialHeld=0;
        printerState=0;assert(sequence(argv[1],1,0)==41&&frames==0&&captures==0);cases++;
        printerState=2;wrongText=1;assert(sequence(argv[1],1,0)==41&&frames==0&&captures==0);cases++;wrongText=0;
        battle=1;assert(sequence(argv[1],1,0)==41&&frames==0&&captures==0);cases++;battle=0;
        texts[0]=t;lengths[0]=n;labels[0]=l;
    }
    activeStart=1;printerState=2;initialHeld=wrongText=battle=0;
    for(unsigned stop=0;stop<5;stop++){
        finishAfter=31;
        assert(sequence(argv[1],5,stop)==41&&frames==stop*12431+12832&&commandCalls==stop+1&&captures==(stop+1)*32);cases++;
    }
    finishAfter=31;assert(sequence(argv[1],5,99)==0&&frames==62155&&captures==160);cases++;
    printf("PASS inert pages cases=%u max_single_timeout=12832 max_single_success=12431 max_five_first_failure=62556 max_five_success=62155; zero emulators\n",cases);
    return 0;
}
