"""Compile-only Warden observer proposal. Its entry point refuses all execution."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
NAMES=['boss','boss-repeat','stairs-no','stairs-yes','checkpoint','save']
KINDS=['BOSS','STABLE','STABLE','STAIRS','STABLE','SAVE']
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def generate(git):
    parent=module('wc_parent',ROOT/'scripts/floor1/continuous-opening-host.py')
    route=module('wc_route',ROOT/'scripts/floor1/warden-continuation-route.py')
    proposal=route.routes();limit=route.budget(proposal['continuation'])['total']
    cold_limit=route.budget(proposal['cold'])['total']
    code,base=parent.generate(git)
    def once(old,new):
        nonlocal code
        assert code.count(old)==1,(old[:90],code.count(old));code=code.replace(old,new)
    once('int main(int argc, char **argv)',(ROOT/'scripts/floor1/howler-continuation-save.h').read_text()+'\nint main(int argc, char **argv)')
    once('    if(argc!=5||(strcmp(argv[4],"opening")&&strcmp(argv[4],"cold")))return 2;',
         '    return 101; /* CLOSED: offline-only; no core, ROM, Save, reset or frames. */\n'
         '    if(argc!=5||(strcmp(argv[4],"warden-continuation")&&strcmp(argv[4],"warden-new-save-cold")))return 2;')
    once('co.cold=!strcmp(argv[4],"cold");co.limit=co.cold?6000:100000;co.kind=co.cold?CO_COLD:CO_BOOT;',
         f'co.cold=!strcmp(argv[4],"warden-new-save-cold");co.limit=co.cold?{cold_limit}:{limit};co.kind=CO_COLD;')
    once('co.core=core;co.pending=!co.cold;','co.core=core;co.pending=0;')
    once('if((co.cold&&co.newSeen)||(!co.cold&&co.continueSeen))','if(co.newSeen)')
    once('if(i==4||c->busRead16(c,co.a.trainer)!=trainers[i])','if(i!=3||c->busRead16(c,co.a.trainer)!=trainers[i])')
    once('if(co.attempts!=i)','if(co.attempts!=0)')
    once('const char *phaseNames[]={'+','.join('"'+n+'"' for n in parent.NAMES)+'};const unsigned phaseKinds[]={'+','.join('CO_'+n for n in parent.KINDS)+'};',
         'const char *phaseNames[]={'+','.join('"'+n+'"' for n in NAMES)+'};const unsigned phaseKinds[]={'+','.join('CO_'+n for n in KINDS)+'};')
    once('phaseSeq>=18','phaseSeq>=6')
    once('                if(phaseSeq==0)co_dump(&current,"before");','')
    once('if(co.cold||sscanf(line+(begin?12:10)','if(co.cold||!hc.anchored||sscanf(line+(begin?12:10)')
    once('if((co.cold&&(!co.continueSeen||co.attempts))||(!co.cold&&(!co.newSeen||phaseSeq!=18||co.attempts!=4)))',
         'if(!co.continueSeen||co.newSeen||(co.cold?co.attempts!=0:(!hc.anchored||phaseSeq!=6||co.attempts!=1||hc.saveStage!=3)))')
    once('            core->setKeys(core,keys);','            if(co.kind==CO_SAVE){result=hc_save_key(keys,frames);if(result)break;}\n            core->setKeys(core,keys);')
    once('        if (!strcmp(symbol,"gTasks")) tasks=addr;',
         '        if(!strcmp(symbol,"SaveOverwriteInputCallback"))hc.overwrite=addr;\n'
         '        if(!strcmp(symbol,"gDifferentSaveFile"))hc.different=addr;\n        if (!strcmp(symbol,"gTasks")) tasks=addr;')
    once('if(!cb1||!vblank','if(!hc.overwrite||!hc.different||!cb1||!vblank')
    # Reuse precisely the reviewed native three-stage Save helper and Continue
    # handoff, not the Howler policy, foe model, healing or historical gates.
    howler=module('wc_save_parent',ROOT/'scripts/floor1/howler-continuation-host.py').generate(git)[0]
    a=howler.index('        if(!strcmp(line,"co save-ready\\n")')
    b=howler.index('        if(!strcmp(line,"co potion-recipient\\n")',a)
    save=howler[a:b].replace('HOWLER_VALIDATOR','WARDEN_VALIDATOR').replace(
         str(ROOT/'scripts/floor1/howler-continuation-state.py'),str(ROOT/'scripts/floor1/warden-continuation-state.py'))
    a=code.index('        if(!strcmp(line,"co save-ready\\n")');b=code.index('        if(!strcmp(line,"co potion-recipient\\n")',a)
    code=code[:a]+save+code[b:]
    code=code.replace(str(ROOT/'scripts/floor1/continuous-opening-state.py'),str(ROOT/'scripts/floor1/warden-continuation-state.py'))
    assert code.index('return 101;')<code.index('mCoreFind')
    assert code.count('->runFrame(')==code.count('core->reset(')==1
    assert not any(s in code for s in ('busWrite','loadState','RNG_SEED','pilot donut-heal'))
    return code,base
