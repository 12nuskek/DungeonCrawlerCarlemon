"""One separate Guard choice observer. Never run a historical wrapper."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
NAMES=['boot','note','supply','guide-initial','trial','scrap','guide-posttrial','guard','guide-guard','save']
KINDS=['BOOT','NOTE','SUPPLY','GUIDE','TRIAL','SCRAP','GUIDE','GUARD','GUIDE','SAVE']
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def generate(git):
    inherited=module('gc_inherited_host',ROOT/'scripts/floor1/continuous-opening-host.py')
    inherited.NAMES=NAMES;inherited.KINDS=KINDS
    code,base=inherited.generate(git)
    def once(old,new):
        nonlocal code
        assert code.count(old)==1,(old[:100],code.count(old));code=code.replace(old,new)
    code=code.replace('co.cold?6000:100000','co.cold?6000:72000').replace('phaseSeq>=18','phaseSeq>=10').replace('phaseSeq!=18||co.attempts!=4','phaseSeq!=10||co.attempts!=2')
    once('co.kind==CO_BOSS?strcmp(line,"pilot fortify 30000\\n"):strcmp(line,"pilot offensive 36000\\n")',
         'co.kind==CO_GUARD?strcmp(line,"pilot donut-heal 36000\\n"):strcmp(line,"pilot offensive 36000\\n")')
    once('(strcmp(policy,"defensive") &&','(strcmp(policy,"donut-heal") && strcmp(policy,"defensive") &&')
    medicine=(ROOT/'scripts/floor1/guard-choice-r2-medicine.h').read_text()
    split=medicine.index('static unsigned gc_choice(')
    once('static unsigned co_owned_valid(struct CoSnapshot*s) {',medicine[:split]+'\nstatic unsigned gc_owned_exact(struct CoSnapshot*s);\nstatic unsigned co_owned_valid(struct CoSnapshot*s) {\n    if(co.kind==CO_GUARD)return gc_owned_exact(s);')
    guard=(ROOT/'scripts/floor1/continuous-opening-guard.h').read_text()
    a=guard.index('static unsigned co_read(');b=guard.index('static void co_dump(',a)
    read=guard[a:b].replace('co_read(', 'gc_read(').replace('    if(!co_phase(c))return 80;\n','')
    once('int main(int argc, char **argv)',medicine[split:]+read+'\nint main(int argc, char **argv)')
    bindings={'Task_ItemContext_SingleRow':'context','gBattlerInMenuId':'owner','gBattlePartyCurrentOrder':'order',
      'gBattlerPartyIndexes':'indexes','gChosenActionByBattler':'actions','gItemUseCB':'itemCB','ItemUseCB_Medicine':'medicine',
      'gPartyMenuUseExitCallback':'useExit','gcInternal':'internal','gcExitBattle':'exitBattle','gcCompleteItem':'completeItem',
      'gcBufferRun':'bufferRun','gcHPTask':'hpTask','gcReturnBag':'returnBag',
      'gcMessagePrinters':'messagePrinters','gcPrintWait':'printWait','gcCloseFade':'closeFade',
      'gcSetupReshow':'setupReshow','gcReshowEntry':'reshowEntry','gcReshow':'reshow',
      'gTextFlags':'textFlags','gDisableTextPrinters':'disablePrinters','gStringVar4':'string4'}
    once('        if (!strcmp(symbol,"gTasks")) tasks=addr;',
      ''.join('        if(!strcmp(symbol,"'+k+'"))gc.a.'+v+'=addr;\n' for k,v in bindings.items())+'        if (!strcmp(symbol,"gTasks")) tasks=addr;')
    once('    co.core=core;co.pending=!co.cold;',r'''
    gc.a.tasks=tasks;gc.a.fade=fade;gc.a.bagMain=bagMain;gc.a.bagInput=bagInput;gc.a.partyMain=partyMain;gc.a.partyInput=partyInput;
    gc.a.partyMenu=partyMenu;gc.a.bagPosition=bagPosition;gc.a.menu=menuState;gc.a.selected=selectedItem;gc.a.restored=restoredText;gc.a.closeText=closeText;
    const unsigned *gcAddresses=(const unsigned*)&gc.a;for(unsigned i=0;i<sizeof gc.a/sizeof *gcAddresses;i++)if(!gcAddresses[i])return 4;
    co.core=core;co.pending=!co.cold;''')
    once('co.pending=1;co.phaseFrames=0;co_dump(&current,"before");',
      'co.pending=1;co.phaseFrames=0;co_dump(&current,"before");if(co.kind==CO_GUARD){resource_canonical(gc.owned,current.owned,current.context);gc.decided=0;}')
    once('                unsigned turn=core->busRead8(core,results+0x13);',r'''
                unsigned turn=core->busRead8(core,results+0x13);
                result=gc_observe(core,pixels,width,height);if(result)break;
                if(co.kind==CO_GUARD&&!gc.stage&&(core->busRead32(core,controls)&~1u)==inputAction
                    &&(!gc.decided||gc.turn!=turn)) {
                    struct CoSnapshot choiceState={0};result=gc_read(core,&choiceState);if(result)break;
                    if(!gc_owned_exact(&choiceState)){result=106;break;}
                    gc.choice=gc_choice(core->busRead16(core,mons+40),core->busRead16(core,mons+44),
                        core->busRead16(core,mons+2*88+40),core->busRead16(core,mons+2*88+44),
                        core->busRead16(core,mons+88+40)!=0,gc_quantity(gc.owned),core->busRead8(core,mons+36),core->busRead8(core,mons+37));
                    gc.turn=turn;gc.decided=1;
                    printf("GUARD_CHOICE absolute=%u turn=%u CarlHP=%u DonutHP=%u GuardAlive=%u Potion=%u choice=%u\n",co.frames,turn,
                        core->busRead16(core,mons+40),core->busRead16(core,mons+2*88+40),core->busRead16(core,mons+88+40)!=0,gc_quantity(gc.owned),gc.choice);
                    if(gc.choice>2){result=gc.choice;break;}
                }
''')
    once('                    for (unsigned b=0;b<=2;b+=2) {',r'''
                    if(gc.stage){result=gc_buttons(core,&key,pixels,width,height);actor=2;menu=4;selection=gc.recipient;}
                    else for (unsigned b=0;b<=2;b+=2) {''')
    once('                            key=(cursor&1)?32:(cursor&2)?64:1;',r'''
                            if(co.kind==CO_GUARD&&b==2&&gc.choice) {
                                if(!gc.decided||gc.turn!=turn||gc.uses>=2){result=103;break;}
                                key=(cursor&2)?64:cursor==1?1:16;actor=2;menu=1;selection=1;
                                if(key==1){result=gc_read(core,&gc.before);if(result)break;gc_dump(&gc.before,"field");gc.recipient=gc.choice-1;gc.start=co.frames;gc.stage=1;}
                                break;
                            }
                            key=(cursor&1)?32:(cursor&2)?64:1;''')
    code=code.replace(str(ROOT/'scripts/floor1/continuous-opening-state.py'),str(ROOT/'scripts/floor1/guard-choice-r2-state.py'))
    assert code.count('s->map>4||s->map==2')==2
    code=code.replace('s->map>4||s->map==2','s->map>1')
    code=code.replace('35,40,41,42,43,44,45,46,49,2139','35,40,41,42,43,44,45,46,47,48,49,2137,2138,2139')
    once('    if(result)co_stop(result,pixels,width,height);',
      '    if(result){if(co.kind==CO_GUARD){struct CoSnapshot failed={0};(void)gc_read(core,&failed);co_dump(&failed,"first-invalid-or-partial-medicine");}co_stop(result,pixels,width,height);}')
    # Old later encounter branches remain inert source history, but admission is restricted.
    once('    unsigned before=(c->busRead8(c,co.a.main+0x439)&2)!=0;',
      '    unsigned before=(c->busRead8(c,co.a.main+0x439)&2)!=0;\n    if(before&&co.kind!=CO_TRIAL&&co.kind!=CO_GUARD)co_stop(89,p,w,h);')
    once('                core->setKeys(core,key);', '                gc.keys=key;core->setKeys(core,key);')
    assert code.count('->runFrame(')==1 and code.count('core->reset(')==1
    assert not any(x in code for x in ('busWrite','loadState','RNG_SEED'))
    return code,base
