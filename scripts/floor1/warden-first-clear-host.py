"""Read-only first-clear observer, existing fortify choices, whole-battle bound."""
from pathlib import Path
import importlib.util,hashlib

ROOT=Path(__file__).resolve().parents[2]

def generate(git):
    def module(name,path):
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    prior=module('reviewed_new_save_host',ROOT/'scripts/floor1/new-save-recovery-host.py')
    native=module('warden_native',ROOT/'scripts/floor1/native-text-observer.py')
    helpers=module('warden_replacement_helpers',ROOT/'scripts/floor1/recovery-host.py')
    code,base=prior.generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='a3af0f882d95912304e5c3c8d537449f8b335930bf6a806244358fa395af2a12'
    replace=helpers.replace_once
    code=native.instrument(code)
    code=replace(code,'int main(int argc, char **argv)',
        (ROOT/'scripts/floor1/warden-attempt-bound.h').read_text()+'\nint main(int argc, char **argv)')
    code=replace(code,'unsigned potionHp=0,',
        'unsigned wardenFrames=0, attemptUsed=0, yesNoTask=0, choiceResult=0;\n    unsigned potionHp=0,')
    # Symbol variables precede symbol parsing; attempt counters precede all frames.
    code=replace(code,'unsigned attacker=0, defender=0, currentMove=0, critical=0, moveDamage=0;',
        'unsigned attacker=0, defender=0, currentMove=0, critical=0, moveDamage=0, yesNoAddress=0, choiceAddress=0;')
    code=replace(code,'        if (!strcmp(symbol,"gTasks")) tasks=addr;',
        '        if (!strcmp(symbol,"Task_HandleYesNoInput")) yesNoAddress=addr;\n        if (!strcmp(symbol,"gSpecialVar_Result")) choiceAddress=addr;\n        if (!strcmp(symbol,"gTasks")) tasks=addr;')
    point='    while (fgets(line,sizeof(line),stdin)) {'
    assert code.count(point)==1
    code=replace(code,point,r'''
    yesNoTask=yesNoAddress;choiceResult=choiceAddress;
#define WARDEN_STOP_BOUND() do { \
    capture("warden-budget-stop.ppm",pixels,width,height); \
    fprintf(stderr,"Warden whole-battle bound reached: frames=%u limit=30000; STOP\n",wardenFrames); \
    printf("WARDEN battle_frames=%u attempts=%u\nresult=51 assertions=%u\n",wardenFrames,attemptUsed,checks); \
    exit(51); \
} while (0)
#define WARDEN_FRAME() do { \
    unsigned wasBattle=(core->busRead8(core,mainstate+0x439)&2)!=0; \
    if (!warden_before_frame(wardenFrames,wasBattle)) WARDEN_STOP_BOUND(); \
    core->runFrame(core); \
    unsigned isBattle=(core->busRead8(core,mainstate+0x439)&2)!=0; \
    if (wasBattle || isBattle) wardenFrames++; \
    if (noBattleMonitoring && (wasBattle || isBattle)) sawBattle=1; \
    if (!warden_after_frame(wardenFrames,isBattle)) WARDEN_STOP_BOUND(); \
} while (0)
''' +point)
    # Frame wrapper includes native pages and every ready/text/save/walking loop.
    begin=code.index('    while (fgets(line,sizeof(line),stdin)) {')
    code=code[:begin]+code[begin:].replace('core->runFrame(core);','WARDEN_FRAME();')
    point='        if (!strcmp(line,"quit\\n")) break;'
    code=replace(code,point,point+r'''
        if (!strcmp(line,"choice-ready\n")) {
            unsigned elapsed=0;
            if (!yesNoTask || !choiceResult) {result=52;break;}
            core->setKeys(core,0);
            while (elapsed<3600 && !menu_ready(core,tasks,fade,yesNoTask)) {WARDEN_FRAME();elapsed++;total++;}
            if (!menu_ready(core,tasks,fade,yesNoTask)) {result=52;fprintf(stderr,"Staircase choice not ready; STOP\n");break;}
            checks++;printf("PASS actual staircase Yes/No task ready frames=%u\n",elapsed);continue;
        }
        if (!strncmp(line,"choice-result ",14)) {
            unsigned wanted;
            if (!choiceResult || sscanf(line,"choice-result %u %c",&wanted,&extra)!=1 || wanted>1
                || core->busRead16(core,choiceResult)!=wanted) {result=52;fprintf(stderr,"Staircase acknowledgement mismatch; STOP\n");break;}
            checks++;printf("PASS %s",line);continue;
        }
        if (!strcmp(line,"vitals record\n") || !strncmp(line,"vitals ",7)) {
            unsigned actual[]={core->busRead16(core,party+0x56),core->busRead16(core,party+100+0x56),
                core->busRead32(core,party+0x50),core->busRead32(core,party+100+0x50),
                party_pp(core,party,0),party_pp(core,party,1),party_pp(core,party+100,0),party_pp(core,party+100,1)};
            if (!strcmp(line,"vitals record\n")) {
                printf("VITALS %u %u %u %u %u %u %u %u\n",actual[0],actual[1],actual[2],actual[3],actual[4],actual[5],actual[6],actual[7]);continue;
            }
            unsigned wanted[8];
            if (sscanf(line,"vitals %u %u %u %u %u %u %u %u %c",wanted,wanted+1,wanted+2,wanted+3,wanted+4,wanted+5,wanted+6,wanted+7,&extra)!=8
                || memcmp(actual,wanted,sizeof actual)) {result=53;fprintf(stderr,"Saved HP/status/PP differs; STOP\n");break;}
            checks++;printf("PASS %s",line);continue;
        }
        if (!strcmp(line,"preserve start\n") || !strcmp(line,"preserve check\n")
            || !strcmp(line,"inventory start\n") || !strcmp(line,"inventory check\n")) {
            static unsigned char savedDuo[200];
            static unsigned short savedBag[512];
            static unsigned initialized=0,savedSlots=0;
            unsigned short bagValues[512];unsigned slots=0;
            if (!pockets || !save2ptr) {result=53;break;}
            unsigned key=core->busRead16(core,core->busRead32(core,save2ptr)+0xAC);
            for (unsigned p=0;p<5;p++) {
                unsigned data=core->busRead32(core,pockets+8*p),capacity=core->busRead8(core,pockets+8*p+4);
                if (!data || slots+capacity>256) {result=53;break;}
                for (unsigned i=0;i<capacity;i++,slots++) {
                    bagValues[2*slots]=core->busRead16(core,data+4*i);
                    bagValues[2*slots+1]=core->busRead16(core,data+4*i+2)^key;
                }
            }
            if (result) break;
            if (!strcmp(line,"preserve start\n") || !strcmp(line,"inventory start\n")) {
                if (!strcmp(line,"preserve start\n"))
                    for (unsigned i=0;i<200;i++) savedDuo[i]=core->busRead8(core,party+i);
                memcpy(savedBag,bagValues,2*slots*sizeof(*bagValues));savedSlots=slots;initialized=1;continue;
            }
            if (!initialized || savedSlots!=slots || memcmp(savedBag,bagValues,2*slots*sizeof(*bagValues))) {
                result=53;fprintf(stderr,"Full owned inventory changed; STOP\n");break;
            }
            if (!strcmp(line,"inventory check\n")) {checks++;printf("PASS full owned inventory unchanged across first battle\n");continue;}
            for (unsigned i=0;i<200;i++) if (savedDuo[i]!=core->busRead8(core,party+i)) {result=53;break;}
            if (result) {fprintf(stderr,"Post-victory duo/inventory changed; STOP\n");break;}
            checks+=2;printf("PASS unchanged post-victory duo and full inventory\n");continue;
        }
''')
    point='        if (!strncmp(line,"pilot ",6)) {'
    code=replace(code,point,point+r'''
            if (strcmp(line,"pilot fortify 30000\n") || attemptUsed || core->busRead16(core,trainer)!=858
                || core->busRead8(core,mons+0x2A+0x58)!=12 || core->busRead8(core,mons+0x2A+3*0x58)!=9
                || core->busRead8(core,results+0x13)!=0 || core->busRead8(core,outcome)!=0) {
                result=54;fprintf(stderr,"Pinned unprepared Warden start/one-attempt contract mismatch; STOP\n");break;
            }
            attemptUsed=1;checks++;printf("PASS actual first trainer858, foes levels12/9, fortify30000, attempts=1\n");
''')
    # Keep the exact inherited fortify controller and victory/no-incapacity checks.
    code=code.replace('Patrol victory/no-incapacity assertion failed','Warden victory/no-incapacity assertion failed')
    code=replace(code,'    printf("result=%d assertions=%u\\n",result,checks);',
        '    printf("WARDEN battle_frames=%u attempts=%u\\n",wardenFrames,attemptUsed);\n    printf("result=%d assertions=%u\\n",result,checks);')
    assert not any(x in code for x in ['snapshot','STATE {','encryption_key','busWrite'])
    return code,base
