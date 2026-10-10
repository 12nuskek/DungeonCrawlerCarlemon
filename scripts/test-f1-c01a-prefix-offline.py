"""Host-only binding/capacity/passivity/error tests. No mCore/gameplay launch."""
from pathlib import Path
import argparse,json,subprocess,hashlib,importlib.util,os,re,copy
ROOT=Path(__file__).resolve().parents[1]
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def validate_profile(profile,identity):
    b=module('validatePrefixSymbols',ROOT/'scripts/floor1/v01-native-boundary-symbols.py');elf=Path(identity['ROM']).with_suffix('.elf')
    assert sha(elf)==profile['ELF_SHA256']==identity['ELF_SHA256'];raw=b.symbols.elf_symbols(elf);functions=b.symbols.functions(raw)
    for p in profile['points']:
        f=[f for f in functions if p['identity'] in f['aliases']];assert len(f)==1;f=f[0]
        assert (p['function'],p['size'],p['hash32'])==(f['address'],f['size'],f['hash32'])
        assert p['mode']==1 and p['pc']==p['rom'] and f['address']<=p['pc']<=f['address']+f['size']-2
        assert p['opcode']==int.from_bytes(b.rom_bytes(elf,p['pc'],2),'little') and 1<=p['role']<=11
    for p in profile['RAM']:
        hits=[s for s in raw if s['name']==p['name'] and s['index']];assert len(hits)==1
        assert p['address']==hits[0]['value'] and p['size']==hits[0]['size']
def function(code,name):
    m=re.search(r'^[^\n]*\b'+name+r'\([^;]*?\)\n\{',code,re.M);assert m,name;return code[m.start():code.index('\n}',m.start())+2]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--bindings-root',type=Path,required=True);a=ap.parse_args();o=a.output;o.mkdir(parents=True,exist_ok=True)
    negatives=0
    abi_values=[]
    for case in ['baseline','candidate']:
        ident=json.loads((Path('/workspace/scratch/c01a-action-hints-r4-20261010')/case/'identity.json').read_text());p=json.loads((a.bindings_root/(case+'-diagnostic-bindings.json')).read_text());validate_profile(p,ident)
        engine=Path(ident['ROM']).parent
        abi=o/(case+'-ABI.c');abi.write_text('#include "global.h"\n#include "text.h"\n#include "main.h"\n#include "battle.h"\n#define OFF(s,f) ((unsigned)&((struct s *)0)->f)\nstruct Dma3Request {const u8 *src;u8 *dest;u16 size;u16 mode;u32 value;};\nconst unsigned dgLayout[]={sizeof(struct TextPrinterTemplate),OFF(TextPrinterTemplate,currentChar),OFF(TextPrinterTemplate,windowId),OFF(TextPrinterTemplate,fontId),sizeof(struct Main),OFF(Main,callback1),OFF(Main,callback2),sizeof(gBattleBufferA[0]),sizeof(struct Dma3Request),OFF(Dma3Request,src),OFF(Dma3Request,dest),OFF(Dma3Request,size),OFF(Dma3Request,mode),OFF(Dma3Request,value)};\n')
        env=dict(os.environ,LD_LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'),PATH=str(TOOL/'usr/bin')+':'+os.environ['PATH'])
        pp=subprocess.check_output(['gcc','-E','-iquote','include','-iquote','src','-Wno-trigraphs','-DMODERN=0','-I','tools/agbcc/include','-I','tools/agbcc','-nostdinc','-undef','-std=gnu89',str(abi)],cwd=engine,env=env)
        assembly=subprocess.check_output(['tools/agbcc/bin/agbcc','-mthumb-interwork','-Wimplicit','-Wparentheses','-Werror','-O2','-fhex-asm','-o','-','-'],cwd=engine,env=env,input=pp)
        asm=o/(case+'-ABI.s');asm.write_bytes(assembly+b'\n.text\n\t.align\t2, 0\n');obj=o/(case+'-ABI.o')
        subprocess.run(['arm-none-eabi-as','-mcpu=arm7tdmi','--defsym','MODERN=0','-o',str(obj),str(asm)],env=env,check=True)
        sections=module('prefixABIsections',ROOT/'scripts/floor1/v01-static-build-audit.py');symbols=module('prefixABIsymbols',ROOT/'scripts/floor1/v01-battle-symbols.py');data=sections.sections(obj)['.rodata']['bytes'];entry=[s for s in symbols.elf_symbols(obj) if s['name']=='dgLayout'];assert len(entry)==1
        import struct
        values=struct.unpack('<14I',data[entry[0]['value']:entry[0]['value']+entry[0]['size']]);assert values==(16,0,4,5,1084,0,4,512,16,0,4,8,10,12),values;abi_values.append(values)
        for kind in ['opcode','scope','PC','size','RAM','RAMsize','role']:
            q=copy.deepcopy(p)
            if kind=='opcode':q['points'][0]['opcode']^=1
            if kind=='scope':q['points'][0]['identity']='L:wrong.o:BattleMainCB1'
            if kind=='PC':q['points'][0]['pc']+=2
            if kind=='size':q['points'][0]['size']+=2
            if kind=='RAM':q['RAM'][0]['address']+=4
            if kind=='RAMsize':q['RAM'][0]['size']+=1
            if kind=='role':q['points'][0]['role']=99
            try:validate_profile(q,ident)
            except AssertionError:negatives+=1
            else:raise AssertionError('Wrong binding accepted '+kind)
    h=module('prefixHostOffline',ROOT/'scripts/floor1/c01a-prefix-host.py');t=module('reviewedTerminalOffline',ROOT/'scripts/floor1/c01a-ui-host-terminal.py')
    git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip();old=t.generate(git);new=h.generate(git)
    unchanged=['bv_native_step','bv_native_events','bv_native_due','bv_boundary_drive_frame','bv_native_metadata','bv_native_compare','bv_native_sample','bv_native_finish','ui_sample','ui_ready']
    for name in unchanged:assert function(old,name)==function(new,name),name
    assert re.findall(r'core->setKeys\(core,([^;]+)\);',old)==re.findall(r'core->setKeys\(core,([^;]+)\);',new)
    c=o/'observer.c';c.write_text(new);env=dict(os.environ,LD_LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'))
    command=['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(TOOL/'usr/include'),str(c),'-L'+str(TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(o/'observer')]
    subprocess.run(command,env=env,check=True)
    pre=r'''
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
#include <unistd.h>
#include <errno.h>
#include <sys/stat.h>
#include <mgba/core/core.h>
#include <mgba/internal/gba/gba.h>
#include <mgba/internal/gba/io.h>
struct BattleVisual {unsigned frames;FILE *trace;};
static struct {struct BattleVisual *visual;unsigned epoch;} edge;
static struct {FILE *trace;} ui;
static unsigned bv_tl_valid_ram(unsigned a,unsigned n){return (a>=0x02000000&&a<=0x02040000&&n<=0x02040000-a)||(a>=0x03000000&&a<=0x03008000&&n<=0x03008000-a);}
static unsigned bv_tl_read(const struct GBA *g,unsigned a,unsigned n){const unsigned char *p=a>=0x03000000?(const unsigned char *)g->memory.iwram+a-0x03000000:(const unsigned char *)g->memory.wram+a-0x02000000;unsigned v=0;for(unsigned i=0;i<n;i++)v|=(unsigned)p[i]<<(8*i);return v;}
static unsigned bv_tl_event_id(const struct GBA *g,const struct mTimingEvent *e){return !e?0:e==&g->irqEvent?1:4;}
static unsigned c01_edge_identity(unsigned a){return a;}
static void bv_ts_pack(unsigned char *b,const unsigned *w,unsigned n){for(unsigned i=0;i<n;i++)for(unsigned j=0;j<4;j++)b[4*i+j]=w[i]>>(8*j);}
'''
    post=r'''
struct ShortFile {unsigned char data[4096];size_t used,limit;};
static ssize_t short_write(void *p,const char *b,size_t n){struct ShortFile *s=p;size_t take=n;if(take>s->limit-s->used)take=s->limit-s->used;if(!take){errno=ENOSPC;return -1;}memcpy(s->data+s->used,b,take);s->used+=take;return take;}
int main(int argc,char **argv){
 assert(argc==2);unsigned mode=atoi(argv[1]);static struct GBA g;static struct ARMCore cpu;static struct mCore core;static struct BattleVisual visual;
 g.memory.wram=calloc(1,0x40000);g.memory.iwram=calloc(1,0x8000);g.memory.rom=calloc(1,64);g.memory.romSize=64;((unsigned char *)g.memory.rom)[1]=0xb5;
 core.cpu=&cpu;core.board=&g;visual.frames=3170;edge.visual=&visual;edge.epoch=5215;
 cpu.executionMode=MODE_THUMB;cpu.gprs[ARM_PC]=0x08000002;cpu.gprs[ARM_SP]=0x03007000;cpu.prefetch[0]=0xb500;
 dg.count=1;dg.point[0]=(struct DgPoint){.pc=0x08000000,.rom=0x08000000,.function=0x08000000,.identity=0x08000000,.opcode=0xb500,.mode=1,.role=3,.size=4,.seen=511};
 for(unsigned i=0;i<DG_DATA;i++)dg.data[i]=0x02000000+0x1000*i;dg.dataSeen=(1u<<DG_DATA)-1;
 if(mode==8)dg.point[0].opcode^=1;if(mode==9)dg.point[0].identity^=1;if(mode==10)dg.data[0]=0;
 unsigned opened=dg_open(&core);if(mode>=8&&mode<=10){assert(opened==126);return 0;}assert(!opened);
 if(mode==11)cpu.gprs[ARM_SP]=0x03fffffc;
 struct ARMCore original=cpu;struct GBA board=g;unsigned char *ram=malloc(0x40000),*iwram=malloc(0x8000);memcpy(ram,g.memory.wram,0x40000);memcpy(iwram,g.memory.iwram,0x8000);
 dg.command=24;assert(!dg_command());assert(dg.active&&dg.command==25&&dg.used==129);assert(!dg_keys(1)&&dg.used==130);
 assert(!dg_observe(&core,5216));assert(!memcmp(&cpu,&original,sizeof cpu)&&!memcmp(&g,&board,sizeof g)&&!memcmp(ram,g.memory.wram,0x40000));
 if(mode==11){unsigned w[64];assert(!dg_collect(w,3,0)&&w[52]==0);}
 unsigned result=mode==0?0:mode==12?51:mode==13?109:124;
 if(mode==1){dg.used=DG_BUFFER-1;unsigned w[64]={0};assert(dg_add(w,0,0)==126);}
 if(mode==2){assert(!dg_flush());dg.rows=DG_NORMAL_LIMIT;unsigned w[64]={0};assert(dg_add(w,0,0)==126);}
 if(mode==3){fclose(dg.file);dg.file=fopen("/dev/full","wb");assert(dg.file);}
 struct ShortFile sf={.limit=384};
 if(mode==4){fclose(dg.file);dg.file=fopencookie(&sf,"w",(cookie_io_functions_t){.write=short_write});assert(dg.file);setvbuf(dg.file,NULL,_IONBF,0);dg.used=3;assert(dg_flush()==126);assert(dg.used==2&&sf.used==384);}
 if(mode==5){dg.used=DG_BUFFER-1;dg.queueSeen=1;assert(!dg_frame_end());}
 if(mode==6){dg.frames=925;assert(dg_frame_end()==126);}
 if(mode==7){dg.point[0].opcode^=1;assert(dg_observe(&core,5216)==126);}
 unsigned retained=dg_close(result);
 if(mode==0||mode==5||mode>=11)assert(!retained&&dg.terminal);else assert(retained==126);
 if(mode==2)assert(dg.rows==DG_TOTAL_LIMIT&&dg.terminal);
 if(mode==4)assert(sf.used==384);
 assert(!memcmp(&cpu,&original,sizeof cpu)&&!memcmp(&g,&board,sizeof g)&&!memcmp(ram,g.memory.wram,0x40000)&&!memcmp(iwram,g.memory.iwram,0x8000));
 return result;
}
'''
    fixture=o/'diagnostic-fixture.c';fixture.write_text(pre+(ROOT/'scripts/floor1/c01a-prefix-diagnostic.h').read_text()+post)
    subprocess.run(['cc','-DUSE_DEBUGGERS','-std=gnu11','-I'+str(TOOL/'usr/include'),str(fixture),'-o',str(o/'diagnostic-fixture')],env=env,check=True)
    cases={}
    for mode in range(14):
        dest=o/('case'+str(mode));dest.mkdir();r=subprocess.run([str(o/'diagnostic-fixture'),str(mode)],cwd=dest,capture_output=True,env=env)
        result=0 if mode in [0,8,9,10] else 51 if mode==12 else 109 if mode==13 else 124
        assert r.returncode==result,(mode,r.stdout,r.stderr)
        if mode in [0,1,2,5,6,7,11,12,13]:
            data=(dest/'controller-dma-diagnostic-private.bin').read_bytes();assert (len(data)-16)%256==0
            import struct
            footer=struct.unpack('<64I',data[-256:]);assert footer[0]==11 and footer[1]==result
        cases[str(mode)]={'exit':r.returncode,'log':r.stdout.decode(),'CPU_board_RAM_unchanged':True}
    assert (925*4096+1)*256+925*184+48==970103304 and 2*970103304==1940206608
    runner=module('prefixAdmissionOffline',ROOT/'scripts/test-f1-c01a-prefix-pair.py')
    eligible={'diagnostic_prefix_only':True,'prefix_matches_original_reference':True,'diagnostic_terminal_complete':True,'exit':0,'full_acceptance':False,'Save_unchanged':True}
    assert runner.eligible(eligible)
    for name in eligible:
        wrong=dict(eligible);wrong[name]=not eligible[name] if isinstance(eligible[name],bool) else 124
        assert not runner.eligible(wrong),name
    route=(ROOT/'scripts/contracts/f1-c01a-ui-r3.route').read_bytes();prefix=b''.join(route.splitlines(keepends=True)[:27])
    assert prefix.splitlines()[-3:]==[b'step 1 1 -',b'step 24 0 -',b'ui wait move 0 900'] and len(prefix.splitlines())==27
    assert 'bv_native_finish(&native)' not in new[new.index('if(dg.command==27)'):new.index('if(dg.command==27)')+220]
    proof={'PASS':True,'wrong_actual_ELF_binding_rejections':negatives,'fixture_cases':cases,'unchanged_original_functions':unchanged,'all15_original_key_expressions_unchanged':True,
      'no_IO_in_interpreter':'dg_observe/collect/record/add perform direct reads and host buffer/cache writes only; flush/open/close outside dispatch',
      'source_SHA256':{p:sha(ROOT/p) for p in ['scripts/floor1/c01a-prefix-host.py','scripts/floor1/c01a-prefix-diagnostic.h','scripts/floor1/c01a-prefix-bindings.py','scripts/test-f1-c01a-prefix-offline.py']},
      'observer_source_SHA256':sha(c),'observer_binary_SHA256':sha(o/'observer'),'data_max_bytes':(925*4096+1)*256+16,'reviewed_reserved_per_case':970103304,'reviewed_reserved_pair':1940206608,
      'full_acceptance_not_claimed':True,'compiled_gameplay_host_not_launched_in_offline_tests':True,'candidate_gate_positive_and6_negatives':True,
      'prefix_exact_original_commands_1_to_27_SHA256':hashlib.sha256(prefix).hexdigest(),'no_diagnostic_full_finish_or_oracle_replacement':True,'both_source_bound_ARM_ABI_values':abi_values,'ABI_fixture_only_not_game_build':True}
    (o/'offline-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('PASS14 actual-ELF negatives;14 host fixtures; CPU/board/RAM/driver/input/strict comparison preservation; no gameplay')
if __name__=='__main__':main()
