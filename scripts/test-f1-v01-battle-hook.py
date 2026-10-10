"""Exercise actual visual C against native interface fixtures, without a game run."""
from pathlib import Path
import argparse, subprocess
ROOT = Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);(out/'constants').mkdir(exist_ok=True)
    (out/'global.h').write_text('''#ifndef MOCK_GLOBAL
#define MOCK_GLOBAL
#include <stdint.h>
#include <string.h>
#include <assert.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef uint8_t bool8;
#define EWRAM_DATA
#define TRUE 1
#define FALSE 0
#define MAX_BATTLERS_COUNT 4
#define MAX_SPRITES 64
#define MAX_MON_PIC_FRAMES 4
#define MON_PIC_SIZE 2048
#define TILE_SIZE_4BPP 32
#define OBJ_VRAM0 0x06010000
#define B_SIDE_PLAYER 0
#define B_SIDE_OPPONENT 1
#define BATTLE_TYPE_TRAINER 8
#define ARRAY_COUNT(x) (sizeof(x)/sizeof((x)[0]))
#define INCGFX_U32(...) {0}
struct SpriteFrameImage {const void *data;u16 size;};
struct Sprite {u8 inUse;const struct SpriteFrameImage *images;struct {u16 tileNum;} oam;};
struct MonSpritesGfx {union {void *ptr[4];u8 *byte[4];} sprites;struct SpriteFrameImage frameImages[4][4];};
struct BattleMon {u16 species,hp;u8 mechanical[84];};
extern struct BattleMon gBattleMons[4];extern struct Sprite gSprites[64];
extern struct MonSpritesGfx *gMonSpritesGfxPtr;
extern u8 gBattleAnimAttacker,gBattlerAttacker,gBattlersCount,gAbsentBattlerFlags,gAnimScriptActive,gBattlerSpriteIds[4];
extern u16 gTrainerBattleOpponent_A,gCurrentMove;extern u32 gBattleTypeFlags;extern const u32 gBitTable[4];
void CpuCopy32(const void *,void *,unsigned);
void RequestSpriteCopy(const u8 *,u8 *,u16);
u8 GetBattlerSide(u8);u8 GetBattlerPosition(u8);
#endif
''')
    for h in ['battle.h','battle_anim.h','battle_setup.h','battle_util.h','sprite.h','util.h']:(out/h).write_text('#include "global.h"\n')
    for h in ['moves.h','species.h','trainers.h']:(out/'constants'/h).write_text((ROOT/'engine/include/constants'/h).read_text())
    (out/'cases.c').write_text('''#include "global.h"
#include <stdio.h>
#include "dcc_battle_pose.c"
struct BattleMon gBattleMons[4];struct Sprite gSprites[64];struct MonSpritesGfx gfx,*gMonSpritesGfxPtr=&gfx;
u8 gBattleAnimAttacker,gBattlerAttacker,gBattlersCount=4,gAbsentBattlerFlags,gAnimScriptActive,gBattlerSpriteIds[4]={0,1,2,3};
u16 gTrainerBattleOpponent_A=858,gCurrentMove;u32 gBattleTypeFlags=8;const u32 gBitTable[4]={1,2,4,8};
static u8 buffers[4][8192];static unsigned copies,requests;
void CpuCopy32(const void *s,void *d,unsigned n){assert(n==2048);assert((u8 *)d>=buffers[0]&&(u8 *)d<buffers[3]+8192);(void)s;copies++;}
void RequestSpriteCopy(const u8 *s,u8 *d,u16 n){assert(n==2048);assert(s>=buffers[0]&&s<buffers[3]+8192);assert((uintptr_t)d>=OBJ_VRAM0);requests++;}
u8 GetBattlerSide(u8 b){return b&1;}u8 GetBattlerPosition(u8 b){return b;}
static void setup(void){DccBattlePoseReset();memset(gBattleMons,0,sizeof gBattleMons);memset(gSprites,0,sizeof gSprites);memset(&gfx,0,sizeof gfx);gMonSpritesGfxPtr=&gfx;gBattleTypeFlags=8;gTrainerBattleOpponent_A=858;gBattlersCount=4;gAbsentBattlerFlags=0;gAnimScriptActive=1;copies=requests=0;for(unsigned b=0;b<4;b++){gBattleMons[b].hp=30;gSprites[b].inUse=1;gSprites[b].images=gfx.frameImages[b];gfx.sprites.ptr[b]=buffers[b];}gBattleMons[0].species=SPECIES_MACHOP;gBattleMons[1].species=SPECIES_LOUDRED;gBattleMons[2].species=SPECIES_MEOWTH;gBattleMons[3].species=SPECIES_VOLTORB;}
static void start(unsigned b,unsigned move){gBattleAnimAttacker=gBattlerAttacker=b;gCurrentMove=move;gAnimScriptActive=1;DccBattlePoseStart(move);}
static void ticks(unsigned n){while(n--)DccBattlePoseUpdate();}
int main(void){
 setup();ticks(30);assert(!copies);gBattleTypeFlags=0;start(0,355);ticks(10);assert(!copies);
 setup();gTrainerBattleOpponent_A=856;start(0,355);ticks(10);assert(!copies);
 setup();start(3,355);ticks(10);assert(!copies);
 setup();gSprites[0].images=NULL;start(0,355);ticks(10);assert(!copies);
 setup();gMonSpritesGfxPtr=NULL;start(0,355);ticks(10);assert(!copies);
 setup();struct BattleMon unchanged[4];memcpy(unchanged,gBattleMons,sizeof unchanged);start(0,355);ticks(7);assert(sDccBattlePoses[0].applied==2);ticks(1);assert(sDccBattlePoses[0].applied==3);gAnimScriptActive=0;ticks(10);assert(sDccBattlePoses[0].applied==4);ticks(1);assert(sDccBattlePoses[0].applied==1);assert(!memcmp(unchanged,gBattleMons,sizeof unchanged));
 setup();start(0,356);ticks(8);assert(sDccBattlePoses[0].applied==5);ticks(1);assert(sDccBattlePoses[0].applied==6);gAnimScriptActive=0;ticks(7);assert(sDccBattlePoses[0].applied==1);
 setup();start(2,357);ticks(8);assert(sDccBattlePoses[2].applied==8);ticks(1);assert(sDccBattlePoses[2].applied==9);gAnimScriptActive=0;ticks(12);assert(sDccBattlePoses[2].applied==10);ticks(1);assert(sDccBattlePoses[2].applied==7);
 setup();start(2,358);ticks(8);assert(sDccBattlePoses[2].applied==11);ticks(1);assert(sDccBattlePoses[2].applied==12);gAnimScriptActive=0;ticks(11);assert(sDccBattlePoses[2].applied==7);
 setup();start(1,359);ticks(6);assert(sDccBattlePoses[1].applied==13);ticks(10);assert(sDccBattlePoses[1].applied==14);ticks(300);assert(sDccBattlePoses[1].applied==15);start(0,356);ticks(70);assert(sDccBattlePoses[1].applied==15);start(1,360);ticks(30);assert(sDccBattlePoses[1].applied==16);DccBattlePoseImpact();ticks(12);assert(sDccBattlePoses[1].applied==17);ticks(1);assert(sDccBattlePoses[1].applied==13);
 setup();start(1,359);ticks(20);gBattleMons[1].hp=0;DccBattlePoseFaint(1);unsigned old=copies;ticks(30);assert(copies==old&&!sDccBattlePoses[1].action&&!sDccBattlePoses[1].applied);gBattleMons[1].hp=30;ticks(30);assert(copies==old);
 setup();start(0,355);ticks(1);start(0,356);ticks(1);assert(sDccBattlePoses[0].applied==5);gAbsentBattlerFlags=1;ticks(30);assert(!sDccBattlePoses[0].applied);
 setup();start(1,359);ticks(25);DccBattlePoseReset();unsigned old2=copies;ticks(30);assert(copies==old2);
 puts("PASS actual-source lifecycle/negative cases: six action bindings, warning persists across other actors, SLAM real-impact recovery, repeated/interrupted swaps, faint/absence/reset, invalid encounter/species/buffer/sprite; no mechanical writes");
}
''')
    # These fixture assignments stand in for the native event writers, which
    # now notify pending work without copying poses outside the update callback.
    cases = (out/'cases.c').read_text().replace('gAnimScriptActive=0;', 'gAnimScriptActive=0;DccBattlePoseNotify();')
    cases = cases.replace('gAbsentBattlerFlags=1;', 'gAbsentBattlerFlags=1;DccBattlePoseNotify();')
    (out/'cases.c').write_text(cases)
    subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-I'+str(out),'-I'+str(ROOT/'engine/include'),'-I'+str(ROOT/'engine/src'),str(out/'cases.c'),'-o',str(out/'cases')],check=True)
    subprocess.run([str(out/'cases')],check=True)
if __name__=='__main__':main()
