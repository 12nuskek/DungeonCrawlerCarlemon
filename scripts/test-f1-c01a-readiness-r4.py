"""Source-bound offline readiness, handoffs and native fresh-key edge proof."""
from pathlib import Path
import importlib.util,json,hashlib,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-action-hints-r4-20261010')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def native_function(source,name):
    m=re.search(r'^(?:static )?void '+name+r'\([^;\n]*\)\n\{',source,re.M);assert m,name
    at=m.end();depth=1
    while depth:depth+=(source[at]=='{')-(source[at]=='}');at+=1
    return source[m.start():at]
def run():
    layout=json.loads((OUT/'native-edge-layout-proof.json').read_text());assert layout['PASS']
    h=(ROOT/'scripts/floor1/c01a-ui-observer-r4.h').read_text();h=h[:h.index('static unsigned ui_sample')]
    assert 'a[16]' in h and 'cb2[3],link[4]' in h and 'u->a[8+kind]' in h
    pre=r'''
#include <stdio.h>
#include <string.h>
#include <assert.h>
struct mCore {unsigned (*busRead8)(struct mCore*,unsigned);unsigned (*busRead32)(struct mCore*,unsigned);void (*setKeys)(struct mCore*,unsigned);};
static unsigned char ram[65536];static unsigned calls,framesPassed,readyAfter,keyHistory[1000];
static unsigned r8(struct mCore*c,unsigned a){(void)c;assert(a<sizeof ram);return ram[a];}
static unsigned r32(struct mCore*c,unsigned a){(void)c;unsigned v;assert(a+4<=sizeof ram);memcpy(&v,ram+a,4);return v;}
static void w32(unsigned a,unsigned v){memcpy(ram+a,&v,4);}
static void setKeys(struct mCore*c,unsigned v){(void)c;assert(calls<1000);keyHistory[calls++]=v;}
static unsigned c01_edge_keys(unsigned v){(void)v;return 0;}
static void frame_step(void){framesPassed++;if(framesPassed>=readyAfter)ram[0x2007]=0;}
#define WARDEN_FRAME() frame_step()
'''+(ROOT/'scripts/floor1/potion-menu-readiness.h').read_text()
    spec=importlib.util.spec_from_file_location('r4gen',ROOT/'scripts/floor1/c01a-ui-host-r4.py');gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
    def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
    generated=gen.generate(git);start=generated.index('            while(elapsed<frames && !ui_ready');end=generated.index('            if(!ui_ready',start);loop=generated[start:end]
    wait='static unsigned wait_ready(struct mCore *core,unsigned advance,unsigned ready,unsigned bound){unsigned result=0,kind=4,keys=0,frames=bound,elapsed=0,total=0,controls=0,tasks=0x4000,fade=0x2000;calls=framesPassed=0;readyAfter=ready;ram[0x2007]=ready?128:0;'+loop+'\nc01_cleanup:return result?9999:total;}\n'
    post=r'''
int main(void){(void)menu_ready;(void)acknowledged_stage;assert(ui_kind("bag")==4&&ui_kind("summary")==7);struct mCore c={r8,r32,setKeys};ui.mainstate=0x1000;ui.battleCB2=0x7010;ui.exec=0x3100;for(unsigned i=0;i<16;i++)ui.a[i]=0x8000+4*i;for(unsigned i=0;i<3;i++)ui.cb2[i]=0x9000+4*i;for(unsigned i=0;i<4;i++)ui.link[i]=0x3000+i;unsigned checked=0;
for(unsigned kind=4;kind<=7;kind++){
 unsigned cb=ui.cb2[kind==4?0:kind==7?2:1],fn=ui.a[8+kind];memset(ram,0,sizeof ram);w32(0x4000,fn|1);ram[0x4004]=1;w32(0x1004,cb|1);assert(ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;
 w32(0x1004,0x999c);assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;w32(0x1004,0);assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;w32(0x1004,cb|1);
 ram[0x4004]=0;assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;ram[0x4004]=1;w32(0x4000,0xdead);assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;w32(0x4000,0);assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;w32(0x4000,fn|1);
 unsigned index=kind==4?0:kind==7?2:1;ui.cb2[index]=0;assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;ui.cb2[index]=cb;
 ram[0x2007]=128;assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;ram[0x200a]=2;ram[0x2009]=64;assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;ram[0x2007]=0;assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));checked++;ram[0x200a]=ram[0x2009]=0;
 for(unsigned j=0;j<4;j++){unsigned save=ui.link[j];ui.link[j]=0;assert(!ui_ready(&c,&ui,0,0x4000,0x2000,0,kind));ui.link[j]=save;checked++;}
 for(unsigned wireless=0;wireless<=1;wireless++)for(unsigned count=0;count<256;count++){ram[0x3000]=wireless;ram[0x3001]=ram[0x3002]=0;ram[wireless?0x3002:0x3001]=count;assert(ui_ready(&c,&ui,0,0x4000,0x2000,0,kind)==(count<3));checked++;}
}
/* Both menu return paths, exact receiving task distinct despite shared Party CB2. */
unsigned path[]={4,1,5,6,7,6,5,1};memset(ram,0,sizeof ram);ram[0x1439]=2;w32(ui.exec,1);
for(unsigned i=0;i<8;i++){unsigned kind=path[i];memset(ram+0x4000,0,640);if(kind>=4){w32(0x1004,ui.cb2[kind==4?0:kind==7?2:1]|1);w32(0x4000,ui.a[8+kind]|1);ram[0x4004]=1;}else{w32(0x1004,ui.battleCB2|1);w32(0x3200,ui.a[9]|1);}assert(ui_ready(&c,&ui,0x3200,0x4000,0x2000,0,kind));checked++;}
/* Exact generated wait loop: initial ready returns/release with zero frames;
 * eventual ready takes precisely65 frames, A only at0/60, no extra frame. */
w32(0x1004,ui.cb2[0]|1);w32(0x4000,ui.a[12]|1);ram[0x4004]=1;
assert(wait_ready(&c,1,0,900)==0&&framesPassed==0&&calls==1&&keyHistory[0]==0);
assert(wait_ready(&c,1,65,900)==65&&framesPassed==65&&calls==66&&keyHistory[0]==1&&keyHistory[60]==1&&keyHistory[65]==0);
for(unsigned i=1;i<65;i++)if(i!=60)assert(keyHistory[i]==0);
assert(wait_ready(&c,0,2,900)==2&&calls==3&&keyHistory[0]==0&&keyHistory[1]==0&&keyHistory[2]==0);
printf("guard_cases=%u generated_wait_release_cases=3\n",checked);return 0;}
'''
    native=(ROOT/'engine/src/main.c').read_text();readkeys=native_function(native,'ReadKeys')
    keys=r'''
#include <assert.h>
#include <stdio.h>
typedef unsigned short u16;
#define KEYS_MASK 0x3ff
#define A_BUTTON 1
#define B_BUTTON 2
#define L_BUTTON 256
#define TRUE 1
#define OPTIONS_BUTTON_MODE_L_EQUALS_A 2
#define JOY_NEW(a) (gMain.newKeys&(a))
#define JOY_HELD(a) (gMain.heldKeys&(a))
static u16 hardware;
#define REG_KEYINPUT hardware
static struct {u16 heldKeysRaw,newKeysRaw,heldKeys,newKeys,newAndRepeatedKeys,keyRepeatCounter,watchedKeysMask,watchedKeysPressed;} gMain;
static struct {unsigned optionsButtonMode;} save,*gSaveBlock2Ptr=&save;
static unsigned gKeyRepeatContinueDelay=5,gKeyRepeatStartDelay=30;
'''+readkeys+r'''
static void apply(unsigned keys){hardware=keys^KEYS_MASK;ReadKeys();}
int main(void){apply(0);apply(A_BUTTON);assert(gMain.newKeysRaw==1&&gMain.newKeys==1&&gMain.heldKeys==1&&gMain.newAndRepeatedKeys==1);apply(A_BUTTON);assert(!gMain.newKeys&&!gMain.newKeysRaw);apply(0);assert(!gMain.heldKeys&&!gMain.newKeys);apply(B_BUTTON);assert(gMain.newKeys==2&&gMain.newKeysRaw==2);apply(B_BUTTON);assert(!gMain.newKeys);apply(0);apply(A_BUTTON);assert(gMain.newKeys==1);apply(0);save.optionsButtonMode=2;apply(L_BUTTON);assert(gMain.newKeysRaw==256&&gMain.heldKeysRaw==256&&gMain.newKeys==257&&gMain.heldKeys==257&&gMain.newAndRepeatedKeys==256);apply(0);assert(!gMain.heldKeys&&!gMain.newKeys);return 0;}
'''
    with tempfile.TemporaryDirectory(prefix='c01r4-readiness-') as tmp:
        tmp=Path(tmp)
        for name,code in [('guards',pre+h+wait+post),('keys',keys)]:
            c=tmp/(name+'.c');exe=tmp/name;c.write_text(code);result=subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(c),'-o',str(exe)],capture_output=True);assert result.returncode==0,result.stderr.decode();result=subprocess.run([str(exe)],capture_output=True);assert result.returncode==0,result.stderr.decode()
            if name=='guards':summary=result.stdout.decode().strip()
    assert sha(ROOT/'scripts/contracts/f1-c01a-ui-r3.route')=='f03cae6c47e866b49209f1a78f6fd2ca34e1653084422b5bab7c3c1e7175b3fa'
    cases={}
    for case in ['baseline','candidate']:
        ident=json.loads((Path('/workspace/scratch/c01a-action-hints-r3-20261010')/case/'identity.json').read_text());engine=Path(ident['ROM']).parent
        main=(engine/'src/main.c').read_text();assert native_function(main,'ReadKeys')==readkeys
        sources={n:(engine/n).read_text() for n in ['src/item_menu.c','src/party_menu.c','src/pokemon_summary_screen.c','src/menu_helpers.c','src/link.c','src/link_rfu_2.c','src/overworld.c','src/palette.c']}
        assert sources['src/item_menu.c'].index('taskId = CreateBagInputHandlerTask')<sources['src/item_menu.c'].index('SetMainCallback2(CB2_BagMenuRun)')
        assert 'SetMainCallback2(CB2_UpdatePartyMenu)' in sources['src/party_menu.c'] and 'CreateTask(Task_HandleInput, 0)' in sources['src/pokemon_summary_screen.c']
        assert 'SetMainCallback2(MainCB2)' in sources['src/pokemon_summary_screen.c']
        assert 'return gRfu.recvQueue.count;' in sources['src/link_rfu_2.c'] and 'return gLink.recvQueue.count;' in sources['src/link.c']
        assert 'GetLinkRecvQueueLength() >= OVERWORLD_RECV_QUEUE_MAX' in sources['src/link.c']
        assert 'gPaletteFade.softwareFadeFinishingCounter == 4' in sources['src/palette.c']
        cases[case]={n:sha(engine/n) for n in sources}
    return dict(PASS=True,scope='Source-bound offline guards/native ReadKeys/generated release loop; no emulator',guard_summary=summary,task_based_kinds=[4,5,6,7],transition_path=['Bag','battle','Party','context','Summary','context','Party','battle'],native_key_edges_and_L_remapping=True,ready_without_extra_frame=True,all_ten_route_corrections_and156_commands_unchanged=True,source_hashes=cases,ABI_proof_SHA256=sha(OUT/'native-edge-layout-proof.json'),observer_array_slots=16,separately_mandatory_running_CB2_bindings=3)
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);r=run();(OUT/'readiness-proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='source_hashes'},indent=2))
