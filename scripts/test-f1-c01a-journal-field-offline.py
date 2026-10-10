"""Inert host guards only: no ROM, mGBA core, Save, CPU or gameplay load."""
from pathlib import Path
import importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-journal-field-offline-20261010')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
host=module('fieldInertHost',ROOT/'scripts/floor1/c01a-journal-field-host.py');route=module('fieldInertRoute',ROOT/'scripts/floor1/c01a-journal-field-route.py')
OUT.mkdir();generated=host.generate();(OUT/'generated-field-host.c').write_text(generated);commands=route.generate().splitlines()
assert all(line.split()[0] in ('step','ready','expect','duo','uses','item','flag','jf','snapshot','pages','quit') for line in commands)
assert sum(line=='jf yesno' for line in commands)==4 and sum(line=='jf start 4' for line in commands)==4
assert sum(line.startswith('pages ') for line in commands)==6
assert generated.count('->runFrame(')==1 and 'busWrite' not in generated
mock=r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned color_t;
struct mCore {unsigned char (*busRead8)(struct mCore*,unsigned);unsigned short (*busRead16)(struct mCore*,unsigned);unsigned (*busRead32)(struct mCore*,unsigned);void (*runFrame)(struct mCore*);};
static unsigned char memory[2048];static unsigned steps,captures,after,before,ioerror;
static unsigned char r8(struct mCore*c,unsigned p){(void)c;return p==0x439?(steps?after:before):memory[p];}
static unsigned short r16(struct mCore*c,unsigned p){return r8(c,p)|(r8(c,p+1)<<8);}
static unsigned r32(struct mCore*c,unsigned p){return r16(c,p)|(r16(c,p+2)<<16);}
static void step(struct mCore*c){(void)c;steps++;}
static int capture(const char*n,const color_t*p,unsigned w,unsigned h){(void)n;(void)p;(void)w;(void)h;captures++;return ioerror;}
static void done(void){fprintf(stdout,"steps=%u captures=%u\n",steps,captures);}
'''+host.GUARD+r'''
int main(int argc,char**argv){
 struct mCore c={r8,r16,r32,step};color_t pixel=0;unsigned mode=argc>1?atoi(argv[1]):0;atexit(done);
 if(mode<6){if(mode==1)before=2;if(mode==2)after=2;if(mode==4)jf_frames=18000;if(mode==5)ioerror=1;jf_run(&c,0,&pixel,mode==3?239:240,160);return 0;}
 unsigned fn=0x08004001,base=128;
 memcpy(memory+base,&fn,4);memory[base+4]=1;memory[base+12]=5;
 if(mode==7)memory[base+12]=4;
 if(mode==8){memcpy(memory+base+40,&fn,4);memory[base+44]=1;memory[base+52]=5;}
 if(mode==9)memory[base+4]=0;
 if(mode==10){memory[base+12]=0;memory[base+8]=5;}
 unsigned ready=jf_task(&c,base,fn,12,5);printf("ready=%u\n",ready);return ready==(mode==6)?0:2;
}
'''
(OUT/'guard-fixture.c').write_text(mock);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(OUT/'guard-fixture.c'),'-o',str(OUT/'guard-fixture')],check=True)
results={}
for mode in range(11):
    p=subprocess.run([str(OUT/'guard-fixture'),str(mode)],capture_output=True,text=True);expected=61 if mode in range(1,6) else 0;assert p.returncode==expected,(mode,p.returncode,p.stdout,p.stderr)
    if mode in (1,3,4):assert 'steps=0 ' in p.stdout
    if mode in (2,5):assert 'steps=1 ' in p.stdout
    results[str(mode)]={'exit':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip()}
proof={'PASS':True,'no_ROM_Save_mGBA_or_gameplay':True,'route_commands':len(commands),'four_native_YesNo_tasks_and_reopens':True,'single_guarded_frame_driver':True,'inert_cases':results}
(OUT/'field-offline-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('PASS11 inert field-only frame/task guards; fixed ordinary route; no emulator')
