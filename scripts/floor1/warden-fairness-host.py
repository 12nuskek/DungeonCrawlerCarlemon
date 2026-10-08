"""Read-only bounded candidate observer; inherited two frozen ordinary policies."""
from pathlib import Path
import importlib.util, hashlib
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    def module(name,path):
        spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    prior=module('fairness_prior',ROOT/'scripts/floor1/warden-first-clear-host.py')
    helper=module('fairness_replace',ROOT/'scripts/floor1/recovery-host.py')
    code,base=prior.generate(git);assert hashlib.sha256(code.encode()).hexdigest()=='a2f44379112d4fd06107b13862f403ddb6fd9f8566ffac39a33c944e05f5aee0'
    replace=helper.replace_once
    code=replace(code,'unsigned wardenFrames=0, attemptUsed=0,', 'unsigned candidateTrainer=0, candidateFortify=0, motionCount=0, cueCount=0, powerAddress=0;\n    unsigned wardenFrames=0, attemptUsed=0,')
    code=replace(code,'unsigned attacker=0, defender=0, currentMove=0, critical=0, moveDamage=0,', 'unsigned battlePower=0, attacker=0, defender=0, currentMove=0, critical=0, moveDamage=0,')
    code=replace(code,'        if (!strcmp(symbol,"gTasks")) tasks=addr;', '        if (!strcmp(symbol,"gBattleMovePower")) battlePower=addr;\n        if (!strcmp(symbol,"gTasks")) tasks=addr;')
    code=replace(code,'    yesNoTask=yesNoAddress;choiceResult=choiceAddress;', '    powerAddress=battlePower;\n    yesNoTask=yesNoAddress;choiceResult=choiceAddress;')
    point='        if (!strcmp(line,"quit\\n")) break;'
    code=replace(code,point,point+r'''
        if (!strncmp(line,"candidate ",10)) {
            char policyName[32];unsigned trainerId;
            if (sscanf(line,"candidate %u %31s %c",&trainerId,policyName,&extra)!=2 || attemptUsed
                || (trainerId!=858 && trainerId!=859) || (strcmp(policyName,"offensive") && strcmp(policyName,"fortify"))) {result=54;break;}
            candidateTrainer=trainerId;candidateFortify=!strcmp(policyName,"fortify");
            checks++;printf("PASS frozen candidate trainer=%u policy=%s\n",trainerId,policyName);continue;
        }
''')
    start=code.index('            if (strcmp(line,"pilot fortify 30000\\n")')
    finish=code.index('            char policy[32], limitText[32];',start)
    code=code[:start]+r'''
            if (!candidateTrainer || !powerAddress || attemptUsed
                || strcmp(line,candidateFortify?"pilot fortify 30000\n":"pilot offensive 30000\n")
                || core->busRead16(core,trainer)!=candidateTrainer
                || core->busRead8(core,mons+0x2A+0x58)!=(candidateTrainer==858?12:10)
                || core->busRead8(core,mons+0x2A+3*0x58)!=(candidateTrainer==858?9:8)
                || core->busRead8(core,results+0x13)!=0 || core->busRead8(core,outcome)!=0) {
                result=54;fprintf(stderr,"Candidate frozen identity/one-attempt gate failed; STOP\n");break;
            }
            attemptUsed=1;checks++;printf("PASS exact candidate trainer=%u attempts=1\n",candidateTrainer);
''' +code[finish:]
    point='                    observedHp[b]=hp;'
    code=replace(code,point,r'''
                    if (hp!=observedHp[b] && core->busRead8(core,attacker)==1 && core->busRead16(core,currentMove)==360
                        && (core->busRead8(core,critical)!=1 || core->busRead16(core,powerAddress)!=45)) {
                        result=55;fprintf(stderr,"Authored SLAM power/critical mismatch; STOP\n");break;
                    }
                    if (hp!=observedHp[b] && core->busRead8(core,attacker)==3
                        && (core->busRead8(core,defender)!=2 || core->busRead16(core,currentMove)!=33 || core->busRead8(core,results+0x13)%4)) {
                        result=55;fprintf(stderr,"Helper target/cadence mismatch; STOP\n");break;
                    }
''' +point)
    point='                    lastTurn=turn;'
    code=replace(code,point,r'''
                    printf("CANDIDATE turn=%u CarlDEF=%u WardenATK=%u helperATK=%u helperPP=%u helperHP=%u duoPP=%u,%u,%u,%u power=%u\n",turn,
                        core->busRead8(core,mons+0x1A),core->busRead8(core,mons+0x58+0x19),core->busRead8(core,mons+3*0x58+0x19),
                        core->busRead8(core,mons+3*0x58+0x24),core->busRead16(core,mons+3*0x58+0x28),
                        party_pp(core,party,0),party_pp(core,party,1),party_pp(core,party+100,0),party_pp(core,party+100,1),core->busRead16(core,powerAddress));
                    if (core->busRead16(core,mons+3*0x58+0x28)) {
                        unsigned expectedPP=35-(turn+3)/4;
                        if (core->busRead8(core,mons+3*0x58+0x24)!=expectedPP) {result=55;fprintf(stderr,"Helper rest PP/cadence mismatch; STOP\n");break;}
                        for (unsigned stat=2;stat<8;stat++) if (core->busRead8(core,mons+3*0x58+0x18+stat)!=6) {
                            result=55;fprintf(stderr,"Helper incidental stat change; STOP\n");break;
                        }
                    }
                    if (candidateFortify && turn==3 && core->busRead8(core,mons+0x1A)!=9) {result=55;fprintf(stderr,"BRACE contribution absent; STOP\n");break;}
                    char frameName[64];snprintf(frameName,sizeof frameName,"turn-%02u.ppm",turn);
                    result=capture(frameName,pixels,width,height);if (result) break;
''' +point)
    point='                elapsed++;total++;\n                if (turn!=lastTurn) {'
    code=replace(code,point,r'''
                elapsed++;total++;
                if (turn<2 && elapsed%120==0 && motionCount<64) {
                    char frameName[64];snprintf(frameName,sizeof frameName,"motion-%03u.ppm",motionCount++);
                    result=capture(frameName,pixels,width,height);if (result) break;
                    printf("MOTION frame=%u turn=%u file=%s\n",total,turn,frameName);
                }
                if (turn!=lastTurn) {''')
    point='                WARDEN_FRAME(); if (noBattleMonitoring && (core->busRead8(core,mainstate+0x439)&2)) sawBattle=1;elapsed++;total++;'
    code=replace(code,point,point+r'''
                if (elapsed%120==0 && cueCount<40) {
                    char frameName[64];snprintf(frameName,sizeof frameName,"cue-%03u.ppm",cueCount++);
                    result=capture(frameName,pixels,width,height);if (result) break;
                }
''')
    assert not any(x in code for x in ['snapshot','STATE {','encryption_key','busWrite'])
    return code,base
