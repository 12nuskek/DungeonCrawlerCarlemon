"""Minimal native-context resource correction on pinned PR101 generated host."""
from pathlib import Path
import hashlib, importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    def module(name,path):
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    old=module('resource_old',ROOT/'scripts/floor1/party-preservation-host.py')
    replace=module('resource_replace',ROOT/'scripts/floor1/recovery-host.py').replace_once
    code,base=old.generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='5fb1277ec61c000eccf901fb029871c62f6415f88d3fe685d0e8e5f984dc6354'
    code=replace(code,(ROOT/'scripts/floor1/party-preservation-observer.h').read_text(),
        (ROOT/'scripts/floor1/party-resource-canonical.h').read_text()+'\n'+(ROOT/'scripts/floor1/party-resource-observer.h').read_text())
    code=code.replace('probe_dump(core,&partyProbe,party,saveptr,objects,avatar,','probe_dump(core,&partyProbe,party,saveptr,save2ptr,objects,avatar,')
    code=replace(code,'probe_arm(core,&partyProbe,party,saveptr,probeFrames);','probe_arm(core,&partyProbe,party,saveptr,save2ptr,probeFrames);')
    point='        if (!strcmp(line,"quit\\n")) break;'
    code=replace(code,point,r'''
        if(partyProbe.armed && (!strcmp(line,"ready\n") || !strcmp(line,"preserve check\n") || !strcmp(line,"probe finish\n"))) {
            if(!fieldLock || !fieldCallback || !scriptStatus || core->busRead8(core,fieldLock) || core->busRead8(core,scriptStatus)!=2
                || (core->busRead32(core,mainstate+4)&~1u)!=(fieldCallback&~1u)) PROBE_STOP(40);
            unsigned reason=probe_resources_ready(core,&partyProbe,party,saveptr,save2ptr,probeFrames);
            if(reason) PROBE_STOP(reason);
        }
''' +point)
    start=code.index('        if (!strcmp(line,"preserve start\\n")');end=code.index('        if (!strncmp(line,"pilot ",6)) {',start)
    previous=old.generate(git)[0];a=previous.index('        if (!strcmp(line,"preserve start\\n")');b=previous.index('        if (!strncmp(line,"pilot ",6)) {',a)
    assert code[start:end]==previous[a:b], 'Historical strict gate remains verbatim'
    assert code.count('core->runFrame(core);')==1 and 'busWrite' not in code
    return code,base
