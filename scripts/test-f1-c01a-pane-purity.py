"""Execute extracted native pane functions in ordinary host C; synthetic/offline only."""
from pathlib import Path
import subprocess,tempfile,json
ROOT=Path(__file__).resolve().parents[1]
def run():
    source=(ROOT/'engine/src/battle_controller_player.c').read_text()
    funcs=[]
    for ret,name in [('const u8 *','MoveSelectionGetHint'),('void ','MoveSelectionDisplayPPString'),('void ','MoveSelectionDisplayMoveType')]:
        begin=source.index('static '+ret+name+'('+('u16 move' if name=='MoveSelectionGetHint' else 'void')+')\n{');end=source.index('\n}',begin)+2;funcs.append(source[begin:end])
    pre=r'''
#include <assert.h>
#include <stdint.h>
#include <string.h>
typedef uint8_t u8;typedef uint16_t u16;
#define MOVE_DCC_STRIKE 355
#define MOVE_DCC_BRACE 356
#define MOVE_DCC_SPARK 357
#define MOVE_DCC_WEAKEN 358
#define B_WIN_PP 5
#define B_WIN_MOVE_TYPE 7
#define EXT_CTRL_CODE_BEGIN 0xfc
#define EXT_CTRL_CODE_FONT 6
#define FONT_NORMAL 2
struct ChooseMoveStruct {u16 moves[4];u8 currentPP[4],maxPP[4];u16 species;u8 monTypes[2];};
static u8 gBattleBufferA[4][512],gMoveSelectionCursor[4],gActiveBattler,gDisplayedStringBattle[128];
static const u8 gText_DccStrikeHint[]="ONE FOE",gText_DccBraceHint[]="SELF DEF+",gText_DccSparkHint[]="BOTH FOES",gText_DccWeakenHint[]="ALL FOES ATK-",gText_MoveInterfaceUses[]="USES",gText_MoveInterfacePP[]="PP",gText_MoveInterfaceType[]="TYPE/";
static const u8 *gTypeNames[]={ (const u8 *)"NORMAL"};
static struct {unsigned type;}gBattleMoves[65536];
static u8 rendered[128];static unsigned window,calls;
static u8 *StringCopy(u8 *d,const u8 *s){while((*d=*s)){d++;s++;}return d;}
static void BattlePutTextOnWindow(u8 *s,unsigned w){strcpy((char *)rendered,(char *)s);window=w;calls++;}
'''
    post=r'''
int main(void){
    for(unsigned n=0;n<65536;n++)assert((MoveSelectionGetHint(n)!=NULL)==(n>=355 && n<=358));
    const char *expected[]={"ONE FOE","SELF DEF+","BOTH FOES","ALL FOES ATK-"};
    for(unsigned actor=0;actor<4;actor++)for(unsigned cursor=0;cursor<4;cursor++)for(unsigned zero=0;zero<2;zero++){
        gActiveBattler=actor;gMoveSelectionCursor[actor]=cursor;
        struct ChooseMoveStruct *m=(struct ChooseMoveStruct *)&gBattleBufferA[actor][4];
        for(unsigned n=0;n<4;n++){m->moves[n]=355+n;m->currentPP[n]=zero?0:8;m->maxPP[n]=40;}
        unsigned char before[sizeof gBattleBufferA],cursors[4];memcpy(before,gBattleBufferA,sizeof before);memcpy(cursors,gMoveSelectionCursor,4);
        unsigned count=calls;MoveSelectionDisplayPPString();assert(window==5 && !strcmp((char *)rendered,"USES"));MoveSelectionDisplayMoveType();assert(window==7 && !strcmp((char *)rendered,expected[cursor]) && calls==count+2);
        assert(!memcmp(before,gBattleBufferA,sizeof before) && !memcmp(cursors,gMoveSelectionCursor,4) && actor==gActiveBattler);
        m->moves[cursor]=33;memcpy(before,gBattleBufferA,sizeof before);MoveSelectionDisplayPPString();assert(window==5 && !strcmp((char *)rendered,"PP"));MoveSelectionDisplayMoveType();assert(window==7 && !strcmp((char *)rendered,"TYPE/\xfc\x06\x02NORMAL"));assert(!memcmp(before,gBattleBufferA,sizeof before));
    }
    return 0;
}
'''
    with tempfile.TemporaryDirectory(prefix='c01a-pane-') as tmp:
        p=Path(tmp);(p/'test.c').write_text(pre+'\n'.join(funcs)+post)
        subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True,capture_output=True)
        subprocess.run([str(p/'test')],check=True,capture_output=True)
    return dict(PASS=True,scope='Offline extracted native function execution with synthetic inputs; not gameplay',helper_inputs=65536,actor_cursor_zero_cases=32,authored_and_native_panes=64,input_buffer_cursor_actor_mutations=0,no_extra_draw_calls=True)
if __name__=='__main__':print(json.dumps(run(),indent=2))
