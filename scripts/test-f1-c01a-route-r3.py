"""Offline route proof using extracted native input handlers, never an emulator.

Native action/move/target/context/Summary handlers execute with rendering/audio
stubs. Asynchronous battle/menu returns are source-guarded explicit transitions;
round resolution/PP spending is an expectation, not simulated combat or timing.
"""
from pathlib import Path
import ctypes,hashlib,json,re,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'scripts/contracts/f1-c01a-ui.route'
ROUTE=ROOT/'scripts/contracts/f1-c01a-ui-r3.route'
OUT=Path('/workspace/scratch/c01a-action-hints-r3-20261010')
CHANGES={24:('ui wait action 0 900','ui next action 0 900'),38:('step 1 32 -','step 1 16 -'),41:('step 1 64 -','step 1 32 -'),47:('step 1 32 -','step 1 16 -'),56:('step 1 64 -','step 1 32 -'),84:('step 1 16 -','step 1 0 -'),91:('step 1 32 -','step 1 16 -'),101:('step 1 32 -','step 1 16 -'),104:('step 1 64 -','step 1 32 -'),149:('step 1 32 -','step 1 16 -')}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def function(text,name):
    m=re.search(r'^(?:static )?(?:void|u8|s8|bool8) '+re.escape(name)+r'\([^;\n]*\)\n\{',text,re.M);assert m,name
    start=m.start();at=m.end();depth=1
    while depth:
        depth+=(text[at]=='{')-(text[at]=='}');at+=1
    return text[start:at]
PRE=r'''
#include <stdint.h>
#include <string.h>
typedef uint8_t u8;typedef uint16_t u16;typedef int32_t s32;typedef int8_t s8;typedef unsigned bool32;
#define TRUE 1
#define FALSE 0
#define MAX_BATTLERS_COUNT 4
#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))
#define JOY_NEW(a) (key&(a))
#define JOY_HELD(a) JOY_NEW(a)
#define JOY_REPEAT(a) JOY_NEW(a)
#define BOUNCE_HEALTHBOX 0
#define BOUNCE_MON 1
#define SE_SELECT 0
#define B_WIN_SWITCH_PROMPT 0
#define OPTIONS_BUTTON_MODE_L_EQUALS_A 2
#define B_COMM_TO_ENGINE 0
#define B_POSITION_PLAYER_LEFT 0
#define B_POSITION_OPPONENT_LEFT 1
#define B_POSITION_PLAYER_RIGHT 2
#define B_POSITION_OPPONENT_RIGHT 3
#define LAST_BALL 12
#define BATTLE_OPPOSITE(a) ((a)^1)
#define GET_BATTLER_SIDE(a) ((a)&1)
#define BATTLE_ALIVE_EXCEPT_ACTIVE 0
#define TYPE_GHOST 7
#define MON_DATA_MOVE1 0
#define MENU_NOTHING_CHOSEN -2
#define MENU_B_PRESSED -1
#define PSS_PAGE_INFO 0
#define PSS_PAGE_SKILLS 1
#define MENU_L_PRESSED 1
#define MENU_R_PRESSED 2
static unsigned key;static int event,value,closed;
static u8 gActiveBattler,gMoveSelectionCursor[4],gActionSelectionCursor[4],gMultiUsePlayerCursor,gNumberOfMovesToChoose=2,gBattlersCount=4,gAbsentBattlerFlags,gBattlerSpriteIds[4],gBattlerPartyIndexes[4];
static unsigned gBattleTypeFlags=BATTLE_TYPE_DOUBLE,gPlayerDpadHoldFrames,gBitTable[]={1,2,4,8};
static u8 gBattleBufferA[4][512];
struct ChooseMoveStruct {u16 moves[4];u8 currentPP[4],maxPP[4],monTypes[2];};
static struct {u8 target;} gBattleMoves[400];
static struct {unsigned optionsButtonMode;} save,*gSaveBlock2Ptr=&save;
static struct {void (*callback)(void);} gSprites[4];
static void (*gBattlerControllerFuncs[4])(void);
static const u8 sTargetIdentities[]={0,2,3,1};
static unsigned gPlayerParty[2];
static struct {u8 cursorPos,minCursorPos,maxCursorPos,APressMuted;} sMenu;
static struct {unsigned active;} gPaletteFade;
static struct {unsigned currPageIndex;} summary,*sMonSummaryScreen=&summary;
static void HandleInputChooseAction(void),HandleInputChooseMove(void),HandleInputChooseTarget(void);
static void HandleMoveSwitching(void){}
static void SpriteCB_HideAsMoveTarget(void){}
static void SpriteCB_ShowAsMoveTarget(void){}
static void PlaySE(unsigned n){(void)n;}
static void DoBounceEffect(unsigned a,unsigned b,unsigned c,unsigned d){(void)a;(void)b;(void)c;(void)d;}
static void EndBounceEffect(unsigned a,unsigned b){(void)a;(void)b;}
static void ActionSelectionDestroyCursorAt(unsigned a){(void)a;}
static void ActionSelectionCreateCursorAt(unsigned a,unsigned b){(void)a;(void)b;}
static void MoveSelectionDestroyCursorAt(unsigned a){(void)a;}
static void MoveSelectionCreateCursorAt(unsigned a,unsigned b){(void)a;(void)b;}
static void __attribute__((unused)) MoveSelectionDisplayPPString(void){}
static void MoveSelectionDisplayPPNumber(void){}
static void MoveSelectionDisplayMoveType(void){}
static __attribute__((unused)) const u8 *MoveSelectionGetHint(unsigned a){(void)a;return (const u8*)"authored";}
static const u8 gText_BattleSwitchWhich[]={0};
static void BattlePutTextOnWindow(const u8 *a,unsigned b){(void)a;(void)b;}
static void SwapHpBarsWithHpText(void){}
static unsigned GetBattlerPosition(unsigned a){return a;}
static unsigned GetBattlerAtPosition(unsigned a){return a;}
static unsigned CountAliveMonsInBattle(unsigned a){(void)a;return 3;}
static unsigned GetDefaultMoveTarget(unsigned a){(void)a;return 1;}
static unsigned GetMonData(unsigned *p,unsigned n){(void)p;return n?356:355;}
static void AddBagItem(unsigned a,unsigned b){(void)a;(void)b;}
static void BtlController_EmitTwoReturnValues(unsigned a,unsigned b,unsigned c){(void)a;event=b;value=c;}
static void PlayerBufferExecCompleted(void){}
static void RedrawMenuCursor(unsigned a,unsigned b){(void)a;(void)b;}
static unsigned MenuHelpers_ShouldWaitForLinkRecv(void){return 0;}
static unsigned GetLRKeysPressed(void){return 0;}
static void ChangeSummaryPokemon(unsigned a,int b){(void)a;(void)b;}
static void ChangePage(unsigned a,int b){(void)a;(void)b;}
static void StopPokemonAnimations(void){}
static void BeginCloseSummaryScreen(unsigned a){(void)a;closed=1;}
static void SwitchToMoveSelection(unsigned a){(void)a;}
'''
POST=r'''
void reset(void){memset(gMoveSelectionCursor,0,4);memset(gActionSelectionCursor,0,4);memset(gBattleBufferA,0,sizeof gBattleBufferA);sMenu.cursorPos=0;sMenu.minCursorPos=0;sMenu.maxCursorPos=2;closed=0;for(unsigned a=0;a<4;a++){struct ChooseMoveStruct *m=(void*)&gBattleBufferA[a][4];gBattleBufferA[a][1]=1;m->moves[0]=a==2?357:355;m->moves[1]=a==2?358:356;m->currentPP[0]=a==2?2:8;m->currentPP[1]=40;}}
int press(unsigned kind,unsigned actor,unsigned keys){key=keys;gActiveBattler=actor;event=-1;value=-1;gBattlerControllerFuncs[actor]=kind==1?HandleInputChooseAction:kind==2?HandleInputChooseMove:HandleInputChooseTarget;if(kind<=3)gBattlerControllerFuncs[actor]();else if(kind==6){event=Menu_ProcessInputNoWrapAround_other();value=sMenu.cursorPos;}else if(kind==7){closed=0;Task_HandleInput(0);event=closed;}return event;}
unsigned peek(unsigned kind,unsigned actor){if(kind==1)return gActionSelectionCursor[actor];if(kind==2)return gMoveSelectionCursor[actor];if(kind==6)return sMenu.cursorPos;if(kind==3)return gBattlerControllerFuncs[actor]==HandleInputChooseTarget;return 999;}
int emitted(void){return value;}
unsigned pp(unsigned actor,unsigned slot){struct ChooseMoveStruct *m=(void*)&gBattleBufferA[actor][4];return m->currentPP[slot];}
void spend(unsigned actor,unsigned slot){struct ChooseMoveStruct *m=(void*)&gBattleBufferA[actor][4];if(m->currentPP[slot])m->currentPP[slot]--;}
void context_reset(void){sMenu.cursorPos=0;}
'''
def compile_native(engine,tmp):
    paths=['src/battle_controller_player.c','src/menu.c','src/party_menu.c','src/data/party_menu.h','src/pokemon_summary_screen.c','src/item_menu.c','src/data/battle_moves.h','src/text.c','include/gba/io_reg.h','include/battle.h','include/constants/battle.h','include/constants/moves.h']
    source={n:(engine/n).read_text() for n in paths}
    defs=[]
    for n in ['include/gba/io_reg.h','include/battle.h','include/constants/battle.h','include/constants/moves.h']:
        for line in source[n].splitlines():
            if re.match(r'#define (A_BUTTON|B_BUTTON|SELECT_BUTTON|START_BUTTON|DPAD_(RIGHT|LEFT|UP|DOWN|ANY)|B_ACTION_(USE_MOVE|USE_ITEM|SWITCH|RUN|EXEC_SCRIPT|CANCEL_PARTNER)|MOVE_TARGET_[A-Z_]+|BATTLE_TYPE_(DOUBLE|MULTI|LINK)|MOVE_CURSE)\s',line):defs.append(line)
    assert all(re.search(r'#define '+n+r'\s+0x'+v,source['include/gba/io_reg.h']) for n,v in [('DPAD_RIGHT','0010'),('DPAD_LEFT','0020'),('DPAD_UP','0040'),('DPAD_DOWN','0080')])
    funcs=[function(source['src/battle_controller_player.c'],n) for n in ['HandleInputChooseAction','HandleInputChooseMove','HandleInputChooseTarget']]
    funcs += [function(source['src/menu.c'],n) for n in ['Menu_MoveCursorNoWrapAround','Menu_ProcessInputNoWrapAround_other']]
    funcs += [function(source['src/pokemon_summary_screen.c'],'Task_HandleInput')]
    # Guard asynchronous returns against exact current native source. They are
    # modeled below; no timing, callback activation, battle outcome or RNG proof.
    anchors={
      'src/data/party_menu.h':['sPartyMenuAction_SendOutSummaryCancel[] = {MENU_SEND_OUT, MENU_SUMMARY, MENU_CANCEL1}', '[ACTIONS_SEND_OUT]      = sPartyMenuAction_SendOutSummaryCancel'],
      'src/party_menu.c':['input = Menu_ProcessInputNoWrapAround_other();','sCursorOptions[sPartyMenuInternal->actions[input]].func(taskId);','sCursorOptions[sPartyMenuInternal->actions[sPartyMenuInternal->numActions - 1]].func(taskId);','PARTY_MSG_DO_WHAT_WITH_MON, Task_TryCreateSelectionWindow, gPartyMenu.exitCallback);'],
      'src/item_menu.c':['case LIST_CANCEL:', 'gSpecialVar_ItemId = ITEM_NONE;', 'gTasks[taskId].func = Task_FadeAndCloseBagMenu;'],
      'src/battle_controller_player.c':['gActionSelectionCursor[gActiveBattler] = 0;', 'gMoveSelectionCursor[gActiveBattler] = 0;'],
      'src/text.c':['JOY_NEW(A_BUTTON | B_BUTTON)'],
    }
    for n,needles in anchors.items():
        for needle in needles:assert needle in source[n],(n,needle)
    assert 'gTasks[taskId].func = Task_HandleChooseMonInput;' in function(source['src/party_menu.c'],'CursorCb_Cancel1')
    assert 'Task_ClosePartyMenu(taskId);' in function(source['src/party_menu.c'],'HandleChooseMonCancel')
    assert 'sPartyMenuInternal->exitCallback = CB2_ShowPokemonSummaryScreen;' in function(source['src/party_menu.c'],'CursorCb_Summary')
    init='static void setup_targets(void){'+''.join(f'gBattleMoves[{i}].target={target};' for i,target in [(355,'MOVE_TARGET_SELECTED'),(356,'MOVE_TARGET_USER'),(357,'MOVE_TARGET_BOTH'),(358,'MOVE_TARGET_BOTH')])+'}\n'
    for name,target in [('STRIKE','SELECTED'),('BRACE','USER'),('SPARK','BOTH'),('WEAKEN','BOTH')]:
        block=re.search(r'\[MOVE_DCC_'+name+r'\] =\s*\{(.*?)\}',source['src/data/battle_moves.h'],re.S)[1];assert '.target = MOVE_TARGET_'+target+',' in block
    code='\n'.join(defs)+'\n'+PRE+'\n'+'\n'.join(funcs)+'\n'+init+POST+'\nvoid init(void){setup_targets();reset();}\n'
    c=tmp/'native.c';so=tmp/'native.so';c.write_text(code)
    result=subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC',str(c),'-o',str(so)],capture_output=True)
    assert result.returncode==0,result.stderr.decode()
    lib=ctypes.CDLL(str(so));lib.init()
    return lib,dict(source_SHA256={n:sha(engine/n) for n in paths},extracted_handlers_SHA256=hashlib.sha256('\n'.join(funcs).encode()).hexdigest(),native_C_SHA256=sha(c),native_compilation_PASS=True)
def walk(lines,lib):
    lib.reset();kind='intro';actor=0;rounds=0;history=[];cancel=[];shots={};moves=[];pending={};assertions=0
    kinds={'action':1,'move':2,'target':3,'bag':4,'party':5,'context':6,'summary':7}
    for index,line in enumerate(lines,1):
        try:
            p=line.split()
            if p[:2]==['ui','start']:kind='intro'
            elif p[:2] in (['ui','wait'],['ui','next']):
                requested,who=p[2],int(p[3])
                if kind=='intro' and p[1]=='next':kind='action';actor=0
                elif kind=='round' and p[1]=='next':
                    assert requested=='action' and who==0 and set(pending)=={0,2}
                    for a,slot in pending.items():lib.spend(a,slot)
                    pending.clear();rounds+=1;kind='action';actor=0
                elif kind=='empty' and p[1]=='next':assert requested=='move' and who==2;kind='move';actor=2
                assert (kind,actor)==(requested,who),('readiness',kind,actor,requested,who)
                assertions+=1
            elif p[:2]==['ui','move']:
                a,c,pp=map(int,p[2:]);assert kind=='move' and actor==a
                assert lib.peek(2,a)==c and lib.pp(a,c)==pp,('cursor/PP',a,c,pp,lib.peek(2,a),lib.pp(a,c))
                moves.append([index,a,c,pp]);assertions+=1
            elif p[0]=='step' and index>=24:
                key=int(p[2]);before=kind
                if key and kind in kinds:
                    k=kinds[kind]
                    if kind=='bag':assert key==2;kind='action';cancel.append('Bag')
                    elif kind=='party':
                        assert key in (1,2)
                        if key==1:kind='context';lib.context_reset()
                        else:kind='action';cancel.append('Party')
                    else:
                        event=lib.press(k,actor,key);value=lib.emitted()
                        if before=='action' and event>=0:
                            assert event in (0,1,2),('unexpected action',event)
                            kind={0:'move',1:'bag',2:'party'}[event]
                        elif before=='move':
                            if lib.peek(3,actor):kind='target'
                            elif event==10:
                                if value==65535:kind='action';cancel.append('Move'+str(actor))
                                elif lib.pp(actor,value&255)==0:kind='empty'
                                else:
                                    pending[actor]=value&255
                                    kind='action' if actor==0 else 'round';actor=2 if actor==0 else 0
                        elif before=='target' and key==2:assert not lib.peek(3,actor);kind='move';cancel.append('Target')
                        elif before=='context':
                            if event==-1:kind='party';cancel.append('Context')
                            elif event>=0:assert event==1,('must choose Summary, not Send Out',event);kind='summary'
                        elif before=='summary':assert event==1 and key==2;kind='context';lib.context_reset();cancel.append('Summary')
                    history.append(dict(command=index,key=key,before=before,after=kind,actor=actor,action_cursors=[lib.peek(1,a) for a in (0,2)],move_cursors=[lib.peek(2,a) for a in (0,2)]))
                if p[3]!='-':shots[p[3]]=dict(command=index,kind=kind,actor=actor,move=lib.peek(2,actor),action=lib.peek(1,actor))
            elif p[:2]==['ui','finish']:assert kind=='move' and actor==2 and lib.peek(2,2)==1 and rounds==2 and pending=={0:1},(kind,actor,rounds,pending)
        except AssertionError as e:raise AssertionError(f'command{index}: {line}: {e}') from e
    required={'carl-strike.ppm':('move',0,0),'carl-brace.ppm':('move',0,1),'strike-target.ppm':('target',0,0),'bag.ppm':('bag',0,0),'party.ppm':('party',0,0),'summary.ppm':('summary',0,0),'carl-return.ppm':('move',0,0),'donut-spark.ppm':('move',2,0),'donut-weaken.ppm':('move',2,1),'donut-return.ppm':('move',2,0),'spark-one.ppm':('move',2,0),'spark-empty.ppm':('move',2,0),'spark-rejected.ppm':('empty',2,0),'spark-empty-return.ppm':('move',2,0),'weaken-after-empty.ppm':('move',2,1)}
    for name,want in required.items():r=shots[name];assert (r['kind'],r['actor'],r['move'])==want,(name,r,want)
    assert cancel==['Target','Move0','Bag','Summary','Context','Party','Move2'],cancel
    assert {(a,c) for _,a,c,_ in moves}=={(0,0),(0,1),(2,0),(2,1)}
    return dict(commands=156,modeled_readiness_and_move_assertions=assertions,native_transitions=history,cancellation_path=cancel,move_assertions=moves,capture_path=shots,expected_rounds=rounds,scope='Offline exact compiled input handlers plus source-guarded asynchronous return and PP expectations; no timing/RNG/battle-survival/runtime acceptance')
def run():
    old=OLD.read_text().splitlines();new=ROUTE.read_text().splitlines();assert len(old)==len(new)==156
    assert sha(OLD)=='7105211cf9560d981f78f630962f49d1a3b5ea599c03784760ece71dfd2ff1c0'
    actual={i:(a,b) for i,(a,b) in enumerate(zip(old,new),1) if a!=b};assert actual==CHANGES,actual
    cases={}
    for case in ['baseline','candidate']:
        ident=json.loads((Path('/workspace/scratch/c01a-action-hints-r2-20261010')/case/'identity.json').read_text());engine=Path(ident['ROM']).parent
        with tempfile.TemporaryDirectory(prefix='c01a-r3-native-') as d:
            lib,proof=compile_native(engine,Path(d));proof['path']=walk(new,lib);rejected={}
            for command,(original,_) in CHANGES.items():
                mutant=new.copy();mutant[command-1]=original
                try:walk(mutant,lib)
                except AssertionError as e:rejected[str(command)]=str(e)
                else:raise AssertionError(('original mistake accepted',case,command))
            proof['original_mistakes_rejected']=rejected;assert len(rejected)==10
            cases[case]=proof
    return dict(PASS=True,old_route_SHA256=sha(OLD),corrected_route_SHA256=sha(ROUTE),commands=156,reviewed_changes={str(k):list(v) for k,v in CHANGES.items()},preserved_commands=146,preserved_assertions_captures_bounds=True,original_mistakes_rejected=20,cases=cases)
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);result=run();(OUT/'offline-route-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
