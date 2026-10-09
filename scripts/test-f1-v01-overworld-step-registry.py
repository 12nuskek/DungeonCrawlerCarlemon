"""Reproduce stale native face seek and verify the actual corrected registry."""
from pathlib import Path
import argparse,subprocess,re
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    src=(ROOT/'engine/src/event_object_movement.c').read_text()
    def function(needle):
        start=src.index(needle);return src[start:src.index('\n}',start)+2]
    functions=function('static const struct StepAnimTable *GetStepAnimTable(')+'\n'+function('void SetStepAnim(struct ObjectEvent *objectEvent, struct Sprite *sprite, u8 animNum)\n{')
    header='''#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
typedef unsigned char u8;
union AnimCmd {int value;};
struct ObjectEvent {u8 inanimate;};
struct Sprite {const union AnimCmd *const *anims;u8 animNum,animCmdIndex;};
struct StepAnimTable {const union AnimCmd *const *anims;u8 animPos[4];};
static unsigned seeks,last;
static void SeekSpriteAnim(struct Sprite *s,u8 index){seeks++;last=index;s->animCmdIndex=index;}
'''
    for label,text,registered in [('original',subprocess.check_output(['git','show','2a76829f:engine/src/data/object_events/object_event_anims.h'],cwd=ROOT,text=True),False),('corrected',(ROOT/'engine/src/data/object_events/object_event_anims.h').read_text(),True)]:
        start=text.index('static const struct StepAnimTable sStepAnimTables[] = {');table=text[start:text.index('\n};',start)+3];names=sorted(set(re.findall(r'\.anims = (sAnimTable_\w+)',table))|{'sAnimTable_DccDonut'})
        arrays='static const union AnimCmd unique[8]={{0},{1},{2},{3},{4},{5},{6},{7}};\n'+''.join(f'static const union AnimCmd *const {name}[]={{&unique[{i}]}};\n' for i,name in enumerate(names))
        cases='''int main(void){struct ObjectEvent o={0};struct Sprite s={sAnimTable_DccDonut,0,0};
'''
        if registered:
            cases+='''assert(GetStepAnimTable(s.anims));assert(!memcmp(GetStepAnimTable(s.anims)->animPos,GetStepAnimTable(sAnimTable_Standard)->animPos,4));
for(unsigned index=0;index<4;index++){s.animCmdIndex=index;seeks=0;SetStepAnim(&o,&s,9);assert(seeks==1&&last==(index<=1?1:3)&&s.animNum==9);}
o.inanimate=1;seeks=0;SetStepAnim(&o,&s,8);assert(!seeks);
puts("PASS corrected actual registry and native SetStepAnim:4 starting indices, unchanged standard metadata, inanimate guard");}
'''
        else:
            cases+='''assert(!GetStepAnimTable(s.anims));SetStepAnim(&o,&s,9);assert(!seeks&&s.animNum==9&&s.animCmdIndex==0);
puts("REPRODUCED original native defect:custom table absent, animNum changes but SeekSpriteAnim never runs");}
'''
        f=out/(label+'.c');f.write_text(header+arrays+table+'\n'+functions+'\n'+cases);binary=out/label
        subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(f),'-o',str(binary)],check=True);subprocess.run([str(binary)],check=True)
if __name__=='__main__':main()
