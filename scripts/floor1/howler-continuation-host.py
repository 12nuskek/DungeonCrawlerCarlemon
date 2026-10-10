"""Offline proposal: one native Continue, one Howler, same-file Save, separate cold.

Generation and compilation never initialize a core. Historical generators remain
immutable; every source substitution below must match its exact inherited site.
"""
from pathlib import Path
import importlib.util
ROOT = Path(__file__).resolve().parents[2]
NAMES = ['howler', 'howler-repeat', 'guide-howler', 'save']
KINDS = ['HOWLER', 'STABLE', 'GUIDE', 'SAVE']

def generate(git):
    spec = importlib.util.spec_from_file_location('howler_inherited', ROOT/'scripts/floor1/conserve-medicine-host.py')
    inherited = importlib.util.module_from_spec(spec); spec.loader.exec_module(inherited)
    code, base = inherited.generate(git)
    def once(old, new):
        nonlocal code
        assert code.count(old) == 1, (old[:100], code.count(old))
        code = code.replace(old, new)
    # Keep the native transaction, acknowledgement, Bag and party lifecycles.
    code = code.replace('CO_GUARD', 'CO_HOWLER')
    once('CO_POTION,CO_HOWLER,CO_HOWLER,', 'CO_POTION,CO_GUARD,CO_HOWLER,')
    code=code.replace('phases[]={CO_TRIAL,CO_HOWLER,CO_HOWLER,CO_BOSS}', 'phases[]={CO_TRIAL,CO_GUARD,CO_HOWLER,CO_BOSS}')
    once('if(co.kind==CO_HOWLER)return flag==2136;', 'if(co.kind==CO_GUARD)return flag==2136;')
    once('co.kind==CO_HOWLER?132:co.kind==CO_HOWLER?121', 'co.kind==CO_GUARD?132:co.kind==CO_HOWLER?121')
    once('co.kind==CO_HOWLER?1:co.kind==CO_HOWLER?2', 'co.kind==CO_GUARD?1:co.kind==CO_HOWLER?2')
    once('cm>36||dm>28||n>2', '(cm!=36&&cm!=38)||(dm!=28&&dm!=30)||n>1')
    once('scuttler?21u:15u):12u', 'scuttler?16u:12u):9u')
    once('if(!strike&&brace)return 92;', 'if(strike<=1)return 92; /* retain one STRIKE PP: seven-use contract */')
    once('species[]={66,308,52,288}', 'species[]={66,370,52,288}')
    once('!=29||c->busRead16(c,mons+3*88+44)!=24||gh>29||sh>24', '!=30||c->busRead16(c,mons+3*88+44)!=25||gh>30||sh>25')
    once('money!=initial+320', 'money!=initial+360')
    code = code.replace('gc.uses>=2', 'gc.uses>=1')
    code=code.replace('s->count=c->busRead8(c,co.a.count);s->savedCount=c->busRead32(c,sb+0x234);',
                      's->count=c->busRead8(c,co.a.count);s->savedCount=c->busRead32(c,sb+0x234);if(s->savedCount!=2)return 81;')
    code = code.replace('47,48,49,2137,2138,2139', '47,48,49,2138,2139')
    once('if(before&&co.kind!=CO_TRIAL&&co.kind!=CO_HOWLER)', 'if(before&&co.kind!=CO_HOWLER)')
    once('if(co.attempts!=i)', 'if(co.kind!=CO_HOWLER||co.attempts!=0)')
    # There is no invented New Game or earlier encounter count in this mode.
    once('if((co.cold&&co.newSeen)||(!co.cold&&co.continueSeen))', 'if(co.newSeen)')
    once('if(argc!=5||(strcmp(argv[4],"opening")&&strcmp(argv[4],"cold")))return 2;',
         'if(argc!=5||(strcmp(argv[4],"howler-continuation")&&strcmp(argv[4],"howler-new-save-cold")))return 2;')
    once('co.cold=!strcmp(argv[4],"cold");co.limit=co.cold?6000:72000;co.kind=co.cold?CO_COLD:CO_BOOT;',
         'co.cold=!strcmp(argv[4],"howler-new-save-cold");co.limit=co.cold?6000:72000;co.kind=CO_COLD;')
    once('co.core=core;co.pending=!co.cold;', 'co.core=core;co.pending=0;')
    once('const char *phaseNames[]={'+','.join('"'+n+'"' for n in inherited.NAMES)+'};const unsigned phaseKinds[]={'+','.join('CO_'+n.replace('GUARD','HOWLER') for n in inherited.KINDS)+'};',
         'const char *phaseNames[]={'+','.join('"'+n+'"' for n in NAMES)+'};const unsigned phaseKinds[]={'+','.join('CO_'+n for n in KINDS)+'};')
    code = code.replace('phaseSeq>=10', 'phaseSeq>=4')
    # The historical first phase was boot and deliberately re-anchored before.
    # Here the first phase is earned combat: its immutable pre-battle operand
    # must never be overwritten by the post-win snapshot.
    once('                if(phaseSeq==0)co_dump(&current,"before");', '')
    once('if((co.cold&&(!co.continueSeen||co.attempts))||(!co.cold&&(!co.newSeen||phaseSeq!=10||co.attempts!=2)))',
         'if(!co.continueSeen||co.newSeen||(co.cold?co.attempts!=0:(!hc.anchored||phaseSeq!=4||co.attempts!=1||hc.saveStage!=3)))')
    once('int main(int argc, char **argv)', (ROOT/'scripts/floor1/howler-continuation-save.h').read_text()+'\nint main(int argc, char **argv)')
    once('            core->setKeys(core,keys);',
         '            if(co.kind==CO_SAVE){result=hc_save_key(keys,frames);if(result)break;}\n            core->setKeys(core,keys);')
    once('        if (!strcmp(symbol,"gTasks")) tasks=addr;',
         '        if(!strcmp(symbol,"SaveOverwriteInputCallback"))hc.overwrite=addr;\n        if(!strcmp(symbol,"gDifferentSaveFile"))hc.different=addr;\n        if(!strcmp(symbol,"DCC_Corridor_Text_HowlerClear"))hc.resolved=addr;\n        if (!strcmp(symbol,"gTasks")) tasks=addr;')
    once('if(!cb1||!vblank', 'if(!hc.overwrite||!hc.different||!hc.resolved||!cb1||!vblank')
    once('if(co.cold||sscanf(line+(begin?12:10)', 'if(co.cold||!hc.anchored||sscanf(line+(begin?12:10)')
    # The original default offensive driver is made explicit for native turns.
    once('                            unsigned desired=0;',
         '                            unsigned desired=b==2&&turn>=2;\n                            if(b==0&&core->busRead8(core,mons+36)<=1){result=92;break;}\n                            if(b==2&&turn<2&&!core->busRead8(core,mons+2*88+36)){result=92;break;}\n                            if(b==2&&turn>=2&&!core->busRead8(core,mons+2*88+37)){result=92;break;}')
    once('                            key=(!strcmp(policy,"loss") && b==0\n                                 && core->busRead16(core,party+100+0x56) && target!=2)?16:1;',
         '                            unsigned want=core->busRead16(core,mons+88+40)?1:3;\n                            if(b!=0||(want==3&&!core->busRead16(core,mons+3*88+40))){result=103;break;}\n                            key=target==want?1:16;')
    # Native newline-only same-file warning: no extra paragraph A is admitted.
    a=code.index('        if(!strcmp(line,"co save-ready\\n")'); b=code.index('        if(!strcmp(line,"co potion-recipient\\n")',a)
    code=code[:a]+r'''
        if(!strcmp(line,"co howler-resolved\n")) {
            if(co.kind!=CO_STABLE||!co.pending||phaseSeq!=1||co.attempts!=1||!co_phase(core)
                ||(core->busRead8(core,mainstate+0x439)&2)||!hc_text_exact(core,string4,hc.resolved)){result=95;break;}
            checks++;continue;
        }
        if(!strcmp(line,"co save-ready\n")||!strcmp(line,"co overwrite-ready\n")||!strcmp(line,"co save-success\n")) {
            unsigned stage=!strcmp(line,"co save-ready\n")?0:!strcmp(line,"co overwrite-ready\n")?1:2,elapsed=0;
            if(co.cold||co.kind!=CO_SAVE||hc.saveStage!=stage||core->busRead8(core,hc.different)){result=95;break;}
            core->setKeys(core,0);hc.keys=0;
            while(elapsed<3600) {
                unsigned readiness=hc_save_ready(core,stage,saveFn,confirmSave,saveSuccess,saveReturn,fade,printers,menuState);
                if(readiness==95){result=95;break;}
                if(!readiness)break;
                co_run(core,pixels,width,height);elapsed++;total++;
            }
            if(result||elapsed==3600||(stage<2&&core->busRead8(core,menuState+2))){result=95;break;}
            hc.saveStage++;checks++;continue;
        }
        if(!strcmp(line,"co continue-verify\n")) {
            if(co.cold||hc.anchored||!co.continueSeen||co.newSeen||co.attempts||!co_phase(core)){result=96;break;}
            struct CoSnapshot current={0};result=co_read(core,&current);if(result)break;co_dump(&current,"current");
            if(system("python3 HOWLER_VALIDATOR continue")){result=96;break;}
            hc.anchored=1;co.last=current;co.armed=1;co.kind=CO_STABLE;checks++;continue;
        }
'''.replace('HOWLER_VALIDATOR',str(ROOT/'scripts/floor1/howler-continuation-state.py'))+code[b:]
    code=code.replace(str(ROOT/'scripts/floor1/guard-choice-r2-state.py'),str(ROOT/'scripts/floor1/howler-continuation-state.py'))
    # A second encounter (including a resolved-repeat defect) stops immediately.
    once('if(i==4||c->busRead16(c,co.a.trainer)!=trainers[i])', 'if(i!=2||c->busRead16(c,co.a.trainer)!=857)')
    once('const unsigned trainers[]={855,856,857,858};unsigned i=0;', 'unsigned i=0;')
    assert code.count('->runFrame(')==code.count('core->reset(')==1
    assert not any(x in code for x in ('busWrite','loadState','RNG_SEED'))
    return code,base
