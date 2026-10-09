"""Actual native SetSpriteOamFlipBits against the hardware bitfield layout."""
from pathlib import Path
import argparse,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    src=(ROOT/'engine/src/sprite.c').read_text();start=src.index('void SetSpriteOamFlipBits(struct Sprite *sprite, u8 hFlip, u8 vFlip)\n{');end=src.index('\n}',start)+2;native=src[start:end]
    header='''#include <assert.h>
#include <string.h>
#include <stdio.h>
typedef unsigned char u8;
struct OamData {unsigned short x:9;unsigned short matrixNum:5;unsigned short size:2;};
struct Sprite {struct OamData oam;u8 hFlip,vFlip;};
'''
    cases='''int main(void){
assert(sizeof(struct OamData)==2);
for(unsigned anim=0;anim<2;anim++)for(unsigned base=0;base<2;base++){
struct Sprite s={0};s.oam.x=120;s.oam.size=2;s.oam.matrixNum=7;s.hFlip=base;
SetSpriteOamFlipBits(&s,anim,0);unsigned short attr1;memcpy(&attr1,&s.oam,2);
assert(((attr1>>12)&1)==(anim^base));assert(s.oam.x==120&&s.oam.size==2&&(s.oam.matrixNum&7)==7);
}
puts("PASS 4 actual-native OAM XOR cases; hardware attr1 bit12 is effective flip, Sprite.hFlip is only override");
}
'''
    (out/'native-oam.c').write_text(header+native+'\n'+cases)
    subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(out/'native-oam.c'),'-o',str(out/'native-oam')],check=True);subprocess.run([str(out/'native-oam')],check=True)
if __name__=='__main__':main()
