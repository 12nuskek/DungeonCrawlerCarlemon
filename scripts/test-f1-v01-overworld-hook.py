"""Compile the actual visual hook against a controlled native-interface fixture."""
from pathlib import Path
import argparse,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);(out/'constants').mkdir(exist_ok=True)
    headers={
      'global.h':'''#ifndef MOCK_GLOBAL
#define MOCK_GLOBAL
#include <stddef.h>
#include <string.h>
#include <assert.h>
typedef unsigned char u8;
#define EWRAM_DATA
#define TRUE 1
#define FALSE 0
#define OBJECT_EVENTS_COUNT 16
#define DIR_SOUTH 1
#define DIR_NORTH 2
#define DIR_WEST 3
#define DIR_EAST 4
struct ObjectEvent {u8 active,graphicsId,mapGroup,mapNum,localId,heldMovementFinished,facingDirection,frozen,spriteAnimPausedBackup;};
struct Sprite {u8 animPaused,animNum;};
extern struct ObjectEvent gObjectEvents[16];
extern u8 gSelectedObjectEvent;
#endif
''',
      'event_object_movement.h':'#include "global.h"\nu8 GetOppositeDirection(u8);\nu8 GetFaceDirectionAnimNum(u8);\n',
      'field_player_avatar.h':'#include "global.h"\nu8 GetPlayerFacingDirection(void);\n',
      'script.h':'#include "global.h"\nu8 ScriptContext_IsEnabled(void);\n',
      'sprite.h':'#include "global.h"\nvoid StartSpriteAnim(struct Sprite *,u8);\n',
      'constants/event_objects.h':'#define OBJ_EVENT_GFX_SKITTY 203\n',
    }
    for name,text in headers.items():(out/name).write_text(text)
    # dcc_overworld.h resolves after the mock directory through actual engine/include.
    code=r'''
#include "global.h"
#include "dcc_overworld.h"
#include <stdio.h>
struct ObjectEvent gObjectEvents[16];u8 gSelectedObjectEvent;
const u8 DCC_Donut_Talk[8]={0};static u8 facing=4,enabled=1;static unsigned starts;
u8 GetOppositeDirection(u8 d){return d==1?2:d==2?1:d==3?4:3;}
u8 GetFaceDirectionAnimNum(u8 d){return d-1;}
u8 GetPlayerFacingDirection(void){return facing;}
u8 ScriptContext_IsEnabled(void){return enabled;}
void StartSpriteAnim(struct Sprite *s,u8 a){s->animNum=a;starts++;}
static void setup(struct Sprite *s){memset(gObjectEvents,0,sizeof gObjectEvents);gSelectedObjectEvent=5;gObjectEvents[5]=(struct ObjectEvent){1,203,35,1,5,1,3,1,0};*s=(struct Sprite){1,2};facing=4;enabled=1;starts=0;}
int main(void){
 struct Sprite s;struct ObjectEvent *o=gObjectEvents+5,before;
 setup(&s);DccDonutAttentionTryStart(DCC_Donut_Talk+1);DccDonutAttentionUpdate(o,&s);assert(!starts&&s.animPaused==1);
 setup(&s);o->mapNum=2;DccDonutAttentionTryStart(DCC_Donut_Talk+2);DccDonutAttentionUpdate(o,&s);assert(!starts);
 setup(&s);o->graphicsId=202;DccDonutAttentionTryStart(DCC_Donut_Talk+2);DccDonutAttentionUpdate(o,&s);assert(!starts);
 setup(&s);facing=1;DccDonutAttentionTryStart(DCC_Donut_Talk+2);DccDonutAttentionUpdate(o,&s);assert(!starts);
 setup(&s);o->heldMovementFinished=0;DccDonutAttentionTryStart(DCC_Donut_Talk+2);DccDonutAttentionUpdate(o,&s);assert(!starts&&s.animPaused);o->heldMovementFinished=1;before=*o;
 for(unsigned i=0;i<24;i++){DccDonutAttentionUpdate(o,&s);assert(s.animNum==20&&!s.animPaused&&!memcmp(o,&before,sizeof before));}
 DccDonutAttentionUpdate(o,&s);assert(s.animNum==2&&s.animPaused&&starts==2&&!memcmp(o,&before,sizeof before));
 setup(&s);facing=3;o->facingDirection=4;DccDonutAttentionTryStart(DCC_Donut_Talk+2);DccDonutAttentionUpdate(o,&s);assert(s.animNum==21);enabled=0;DccDonutAttentionUpdate(o,&s);assert(s.animNum==3&&s.animPaused);
 setup(&s);DccDonutAttentionTryStart(DCC_Donut_Talk+2);DccDonutAttentionUpdate(o,&s);o->frozen=0;o->spriteAnimPausedBackup=0;enabled=0;DccDonutAttentionUpdate(o,&s);assert(s.animNum==2&&!s.animPaused);
 setup(&s);DccDonutAttentionTryStart(DCC_Donut_Talk+2);o->heldMovementFinished=0;enabled=0;DccDonutAttentionUpdate(o,&s);assert(!starts&&s.animPaused);
 setup(&s);DccDonutAttentionTryStart(DCC_Donut_Talk+2);o->facingDirection=2;DccDonutAttentionUpdate(o,&s);assert(!starts&&s.animPaused);
 setup(&s);DccDonutAttentionTryStart(DCC_Donut_Talk+2);DccDonutAttentionUpdate(o,&s);o->active=0;DccDonutAttentionUpdate(o,&s);o->active=1;starts=0;DccDonutAttentionUpdate(o,&s);assert(!starts);
 puts("PASS 10 actual-source visual-hook lifecycle/negative cases;24-frame hold; object fields untouched");
}
'''
    (out/'hook-cases.c').write_text(code)
    subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-I'+str(out),'-I'+str(ROOT/'engine/include'),str(out/'hook-cases.c'),str(ROOT/'engine/src/dcc_overworld.c'),'-o',str(out/'hook-cases')],check=True)
    subprocess.run([str(out/'hook-cases')],check=True)
if __name__=='__main__':main()
