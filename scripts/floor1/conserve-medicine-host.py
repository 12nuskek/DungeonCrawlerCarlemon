"""Separately named two-foe policy; unchanged r3 transaction/key/route machinery."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
NAMES=['boot','note','supply','guide-initial','trial','scrap','guide-posttrial','guard','guide-guard','save']
KINDS=['BOOT','NOTE','SUPPLY','GUIDE','TRIAL','SCRAP','GUIDE','GUARD','GUIDE','SAVE']
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def generate(git):
    old=module('conserve_r3_host',ROOT/'scripts/floor1/guard-choice-r3-host.py');code,base=old.generate(git)
    def once(a,b):
        nonlocal code
        assert code.count(a)==1,(a[:100],code.count(a));code=code.replace(a,b)
    start=code.index('static unsigned gc_choice(');end=code.index('\n}',start)+2
    policy=(ROOT/'scripts/floor1/conserve-medicine-policy.h').read_text()
    split=policy.index('struct GcFoeAddresses')
    code=code[:start]+policy[:split]+code[end:]
    once('static unsigned gc_remove(',policy[split:]+'\nstatic unsigned gc_remove(')
    start=code.index('                    gc.choice=gc_choice(');end=code.index('                    if(gc.choice>2)',start)
    code=code[:start]+'''                    unsigned guardAlive=0,scuttlerAlive=0;
                    gc.choice=gc_decision(core,&guardAlive,&scuttlerAlive);
                    gc.turn=turn;gc.decided=1;
                    printf("GUARD_CHOICE absolute=%u turn=%u CarlHP=%u DonutHP=%u GuardAlive=%u ScuttlerAlive=%u Potion=%u choice=%u\\n",co.frames,turn,
                        core->busRead16(core,mons+40),core->busRead16(core,mons+2*88+40),guardAlive,scuttlerAlive,gc_quantity(gc.owned),gc.choice);
'''+code[end:]
    once('        if (!strcmp(symbol,"gTasks")) tasks=addr;','''        if(!strcmp(symbol,"gBattlersCount"))gcf.count=addr;
        if(!strcmp(symbol,"gBattlerPositions"))gcf.positions=addr;
        if(!strcmp(symbol,"gAbsentBattlerFlags"))gcf.absent=addr;
        if (!strcmp(symbol,"gTasks")) tasks=addr;''')
    once('    co.core=core;co.pending=!co.cold;', '    if(!gcf.count||!gcf.positions||!gcf.absent)return 4;\n    co.core=core;co.pending=!co.cold;')
    assert code.count('->runFrame(')==code.count('core->reset(')==1
    assert not any(x in code for x in ('busWrite','loadState','RNG_SEED'))
    return code,base
