"""Separate pinned noncombat diagnostic; historical controllers/gate untouched."""
from pathlib import Path
import hashlib, importlib.util

ROOT=Path(__file__).resolve().parents[2]


def generate(git):
    def module(name,path):
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    prior=module('party_probe_prior',ROOT/'scripts/floor1/warden-fairness-host.py')
    replace=module('party_probe_replace',ROOT/'scripts/floor1/recovery-host.py').replace_once
    code,base=prior.generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='b2030b4da242f14d9993cbb00493dd9bb02c746fc12ce75cd994b11b760f0c71'
    start=code.index('        if (!strcmp(line,"preserve start\\n")')
    end=code.index('        if (!strncmp(line,"pilot ",6)) {',start)
    strict=code[start:end]
    code=replace(code,(ROOT/'scripts/floor1/warden-attempt-bound.h').read_text(),'')
    code=replace(code,'int main(int argc, char **argv)',(ROOT/'scripts/floor1/party-preservation-observer.h').read_text()+'\nint main(int argc, char **argv)')
    code=replace(code,'unsigned potionHp=0,','struct PartyProbe probe={0};unsigned probeFrames=0;\n    unsigned potionHp=0,')
    start=code.index('#define WARDEN_FRAME() do {')
    end=code.index('} while (0)',start)+len('} while (0)')
    code=code[:start]+r'''
#define PROBE_STOP(reason) do { \
    if(probe.armed) probe_dump(core,&probe,party,saveptr,objects,avatar,probeFrames,(reason)); \
    capture("probe-stop.ppm",pixels,width,height); \
    fprintf(stderr,"Probe strict stop reason=%u; no further frames\n",(unsigned)(reason)); \
    printf("DIAGNOSTIC frames=%u battles=%u armed_checks=%u reason=%u\n",probeFrames,wardenFrames,probe.checks,(unsigned)(reason)); \
    printf("WARDEN battle_frames=%u attempts=%u\nresult=%u assertions=%u\n",wardenFrames,attemptUsed,(unsigned)(reason),checks); \
    exit(reason); \
} while (0)
#define WARDEN_FRAME() do { \
    if(probeFrames>=24000) PROBE_STOP(59); \
    if(core->busRead8(core,mainstate+0x439)&2) PROBE_STOP(58); \
    core->runFrame(core);probeFrames++; \
    if(core->busRead8(core,mainstate+0x439)&2) {wardenFrames++;PROBE_STOP(58);} \
    unsigned probeReason=probe_check(core,&probe,party,saveptr,probeFrames); \
    if(probeReason) PROBE_STOP(probeReason); \
} while (0)
''' +code[end:]
    point='        if (!strcmp(line,"quit\\n")) break;'
    code=replace(code,point,point+r'''
        if(!strcmp(line,"probe arm\n")) {
            probe_arm(core,&probe,party,saveptr,probeFrames);checks++;
            result=capture("probe-anchor.ppm",pixels,width,height);if(result) break;continue;
        }
        if(!strcmp(line,"probe finish\n")) {
            if(!probe.armed) {result=54;break;}
            probe_dump(core,&probe,party,saveptr,objects,avatar,probeFrames,0);
            printf("DIAGNOSTIC frames=%u battles=%u armed_checks=%u reason=0\n",probeFrames,wardenFrames,probe.checks);
            checks++;continue;
        }
''')
    assert strict in code, 'Historical200-byte gate must be verbatim'
    assert code.count('core->runFrame(core);')==1
    assert 'busWrite' not in code and 'encryption_key' not in code and 'STATE {' not in code
    return code,base
