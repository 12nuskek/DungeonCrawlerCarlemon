"""Compile/run host-only fake-memory fixtures. Never load a ROM or run mCore."""
from pathlib import Path
import importlib.util,subprocess,json,hashlib,argparse,os,re
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    m=module('terminal',ROOT/'scripts/floor1/c01a-ui-host-terminal.py')
    pre=r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <assert.h>
#include <sys/stat.h>
#include <unistd.h>
enum {REG_KEYINPUT=0,ARM_PC=15,MODE_THUMB=1};
struct ARMCore {unsigned gprs[16],executionMode;};
struct GBA {struct {unsigned short io[8];unsigned romSize;void *rom;} memory;};
struct mCore {void *board;struct ARMCore *cpu;};
struct BattleVisual {unsigned frames;};
static struct {unsigned mainstate,a[16],link[4];} ui;
static unsigned bv_tl_read(const struct GBA *g,unsigned a,unsigned n){(void)g;(void)a;(void)n;return 0;}
static unsigned bv_callback(struct BattleVisual *v,unsigned a){(void)v;return a;}
static unsigned bv_tl_valid_ram(unsigned a,unsigned n){(void)a;(void)n;return 1;}
static void bv_ts_pack(unsigned char *b,const unsigned *w,unsigned n){for(unsigned i=0;i<n;i++)for(unsigned j=0;j<4;j++)b[4*i+j]=w[i]>>(8*j);}
'''
    post=r'''
int main(int argc,char **argv){
 assert(argc==3);unsigned mode=atoi(argv[1]);
 static struct GBA gba;static struct ARMCore cpu;static struct mCore core;static struct BattleVisual visual;
 cpu.gprs[0]=0x12345678;core.board=&gba;core.cpu=&cpu;visual.frames=3171;
 edge.core=&core;edge.visual=&visual;edge.active=1;edge.command=26;edge.epoch=5216;
 edge.file=fopen(mode==4?"/dev/full":argv[2],"wb");assert(edge.file);
 edge.used=2;edge.buffer[0][0]=3;edge.buffer[0][30]=77;edge.buffer[1][0]=4;edge.buffer[1][30]=88;
 if(mode==2)edge.reason=125;
 if(mode==3)edge.rows=C01_EDGE_MAX_ROWS;
 if(mode==5){edge.rows=C01_EDGE_MAX_ROWS-2;edge.used=3;edge.buffer[2][0]=5;}
 if(mode==1){unsigned r=c01_edge_close(0);assert(!r&&!edge.file&&!edge.active&&cpu.gprs[0]==0x12345678);return 0;}
 c01_edge_terminal_exit(mode==6?51:mode==7?109:124);
}
'''
    # Compare normal success bytes with the unchanged old close implementation.
    old=(ROOT/'scripts/floor1/c01a-ui-edge-r4.h').read_text()
    old_terminal='static void c01_edge_terminal_exit(unsigned r){(void)c01_edge_close(r);exit(r);}'
    binaries={};fixtures={}
    for name,header in [('old',old+'\n'+old_terminal),('new',m.edge_header())]:
        c=out/(name+'.c');c.write_text(pre+header+post);binary=out/name
        subprocess.run(['gcc','-std=c11','-D_POSIX_C_SOURCE=200809L','-Wall','-Wextra','-Werror','-Wno-unused-function',str(c),'-o',str(binary)],check=True)
        binaries[name]=binary
    for mode in range(8):
        dest=out/('mode'+str(mode)+'.bin');r=subprocess.run([str(binaries['new']),str(mode),str(dest)],capture_output=True)
        expected=0 if mode==1 else 51 if mode==6 else 109 if mode==7 else 124
        assert r.returncode==expected,(mode,r)
        data=dest.read_bytes() if dest.exists() else b''
        rows=[list(__import__('struct').unpack('<40I',data[i:i+160])) for i in range(0,len(data),160)]
        if mode in [0,1,2,6,7]:
            assert [w[0] for w in rows]==[3,4,11] and [w[30] for w in rows]==[77,88,expected]
            assert rows[-1][1:4]==[26,5216,3171]
        if mode==3:assert not rows
        if mode==4:assert b'Terminal edge retention failed=125; original STOP=124 preserved' in r.stderr
        if mode==5:assert [w[0] for w in rows]==[3,4] and len(data)==320
        fixtures[str(mode)]={'exit':r.returncode,'tags':[w[0] for w in rows],'bytes':len(data),'stderr':r.stderr.decode()}
    old_dest=out/'old-success.bin';subprocess.run([str(binaries['old']),'1',str(old_dest)],check=True)
    assert old_dest.read_bytes()==(out/'mode1.bin').read_bytes()
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    prior=module('terminal_original_generator',ROOT/'scripts/floor1/c01a-ui-host-r4.py')
    historical=prior.generate(git);generated=m.generate(git)
    assert hashlib.sha256(historical.encode()).hexdigest()=='564c8b04c4ab6e8ef1efb9a5d846ff1934525f9b64e647b0c0db69b23ecf8732'
    back=generated.replace(m.edge_header(),old)
    for expression in ['51','109','vr']:back=back.replace('c01_edge_terminal_exit('+expression+');','exit('+expression+');')
    assert back==historical
    assert re.findall(r'core->setKeys\(core,([^;]+)\);',generated)==re.findall(r'core->setKeys\(core,([^;]+)\);',historical)
    tool=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root');host_c=out/'observer-terminal.c';host_c.write_text(generated)
    host=out/'observer-terminal';command=['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(tool/'usr/include'),str(host_c),'-L'+str(tool/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(host)]
    env=dict(os.environ,LD_LIBRARY_PATH=str(tool/'usr/lib/x86_64-linux-gnu'))
    subprocess.run(command,env=env,check=True) # Compile/link only. Never launch host.
    # Recover neither historical missing bytes nor unrecorded controller state.
    result={'PASS':True,'scope':'Host-only fake-memory error/success fixtures; no gameplay process, ROM load, CPU step, frame, input or game call',
      'fixtures':fixtures,'success_footer_bytes_identical_to_old':True,'original_STOP_preserved_on_IO_and_capacity_error':True,
      'historical_unflushed_observations_not_recovered':True,'source_SHA256':hashlib.sha256((ROOT/'scripts/floor1/c01a-ui-host-terminal.py').read_bytes()).hexdigest(),
      'exact_generated_historical_C_restored_by_reversing_scoped_edits':True,'all15_original_key_expressions_identical':True,'compiled_host_never_launched':True,
      'new_generated_source_SHA256':hashlib.sha256(generated.encode()).hexdigest(),'new_host_binary_SHA256':hashlib.sha256(host.read_bytes()).hexdigest(),'host_compile_command':command}
    (out/'terminal-retention-proof.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS terminal host retention: eight cases + old success byte equality; no emulator')
if __name__=='__main__':main()
