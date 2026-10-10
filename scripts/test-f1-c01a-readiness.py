"""Offline synthetic checks of the new source-bound receiving menu guards."""
from pathlib import Path
import subprocess,tempfile,json
ROOT=Path(__file__).resolve().parents[1]
def run():
    s=(ROOT/'scripts/floor1/c01a-ui-observer.h').read_text();s=s[:s.index('static unsigned ui_sample')]
    pre='''#include <stdint.h>\n#include <stdio.h>\n#include <string.h>\n#include <assert.h>\nstruct mCore {unsigned (*busRead8)(struct mCore *,unsigned);unsigned (*busRead32)(struct mCore *,unsigned);};\nstatic unsigned char ram[4096];\nstatic unsigned r8(struct mCore *c,unsigned a){(void)c;assert(a<4096);return ram[a];}\nstatic unsigned r32(struct mCore *c,unsigned a){(void)c;assert(a+3<4096);unsigned x;memcpy(&x,ram+a,4);return x;}\nstatic void w32(unsigned a,unsigned v){memcpy(ram+a,&v,4);}\n'''+(ROOT/'scripts/floor1/potion-menu-readiness.h').read_text()
    post='''int main(void){(void)menu_ready;(void)acknowledged_stage;struct mCore c={r8,r32};ui.mainstate=0x100;ui.battleCB2=0xabc;ui.exec=0x40;unsigned controls=0x20,tasks=0x600,fade=0x80;ram[ui.mainstate+0x439]=2;w32(ui.mainstate+4,ui.battleCB2|1);unsigned passed=0;for(unsigned kind=1;kind<=7;kind++){ui.a[8+kind]=0x800+kind*4;if(kind<=3){w32(controls,ui.a[8+kind]|1);w32(ui.exec,1);}else{w32(tasks,ui.a[8+kind]|1);ram[tasks+4]=1;}assert(ui_ready(&c,&ui,controls,tasks,fade,0,kind));passed++;ram[fade+7]=128;assert(!ui_ready(&c,&ui,controls,tasks,fade,0,kind));passed++;ram[fade+7]=0;if(kind<=3){w32(ui.exec,0);assert(!ui_ready(&c,&ui,controls,tasks,fade,0,kind));w32(ui.exec,1);w32(ui.mainstate+4,0);assert(!ui_ready(&c,&ui,controls,tasks,fade,0,kind));w32(ui.mainstate+4,ui.battleCB2|1);}else{ram[tasks+4]=0;assert(!ui_ready(&c,&ui,controls,tasks,fade,0,kind));ram[tasks+4]=1;w32(tasks,0);assert(!ui_ready(&c,&ui,controls,tasks,fade,0,kind));}passed+=2;}assert(!ui_kind("invalid"));assert(passed==28);return 0;}'''
    with tempfile.TemporaryDirectory(prefix='c01a-readiness-') as tmp:
        p=Path(tmp);(p/'test.c').write_text(pre+s+post)
        result=subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],capture_output=True)
        assert result.returncode==0,result.stderr.decode()
        subprocess.run([str(p/'test')],check=True)
    return dict(PASS=True,scope='Synthetic/offline receiving callback/fade/exec guard tests; not emulator',cases=28,unknown_kind_rejected=True)
if __name__=='__main__':print(json.dumps(run(),indent=2))
