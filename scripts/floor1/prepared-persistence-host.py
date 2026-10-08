"""Separate source-valid walking contract on the frozen prepared candidate host."""
from pathlib import Path
import hashlib,importlib.util,re
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    def module(name,path):
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    replace=module('prepared_replace',ROOT/'scripts/floor1/recovery-host.py').replace_once
    code,base=module('prepared_old',ROOT/'scripts/floor1/warden-fairness-host.py').generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='b2030b4da242f14d9993cbb00493dd9bb02c746fc12ce75cd994b11b760f0c71'
    source=(ROOT/'engine/src/pokemon.c').read_text()
    orders=[tuple(map(int,row)) for row in re.findall(r'SUBSTRUCT_CASE\(\s*(\d+),(\d+),(\d+),(\d+),(\d+)\)',source)]
    header=(ROOT/'scripts/floor1/walking-preservation.h').read_text()
    table=[tuple(map(int,row.split(','))) for row in re.findall(r'\{([0-3],[0-3],[0-3],[0-3])\}',header)]
    assert [x[1:] for x in sorted(orders)]==table and len(table)==24
    assert '[FRIENDSHIP_EVENT_WALKING]         = { 1,  1,  1}' in source
    assert 'mod = (150 * mod) / 100;' in source and 'friendship = MAX_FRIENDSHIP;' in source
    addition='\n'.join((ROOT/p).read_text() for p in ['scripts/floor1/party-resource-canonical.h','scripts/floor1/walking-preservation.h','scripts/floor1/prepared-preservation-observer.h'])
    code=replace(code,'int main(int argc, char **argv)',addition+'\nint main(int argc, char **argv)')
    code=replace(code,'unsigned animationActive=0,','unsigned mapgroups=0;\n    unsigned animationActive=0,')
    code=replace(code,'        if (!strcmp(symbol,"gMain")) mainstate=addr;','        if (!strcmp(symbol,"gMapGroups")) mapgroups=addr;\n        if (!strcmp(symbol,"gMain")) mainstate=addr;')
    point='    powerAddress=battlePower;'
    code=replace(code,point,'''    struct WalkPreservation walking={0};unsigned walkKeys=0;
    struct WalkAddresses walkAddresses={party,saveptr,save2ptr,mapgroups,mainstate,objects,avatar,choiceAddress};
    if(!mapgroups || !save2ptr || !choiceAddress) return 4;
''' +point)
    point='#define WARDEN_FRAME() do {'
    code=replace(code,point,r'''#define WALK_STOP(reason) do { \
    walk_snapshot(core,walkAddresses,"stop");walk_write("stop-last-party.bin",walking.last,600); \
    capture("walking-preservation-stop.ppm",pixels,width,height); \
    fprintf(stderr,"Narrow walking preservation stop reason=%u; no further frames\n",reason); \
    printf("WARDEN battle_frames=%u attempts=%u\nresult=%u assertions=%u\n",wardenFrames,attemptUsed,reason,checks);exit(reason); \
} while(0)
#define WARDEN_FRAME() do {''')
    point='    core->runFrame(core); \\\n'
    code=replace(code,point,r'''    if(walking.armed && (walkKeys&1) && active_task(core,tasks,yesNoTask)) { \
        unsigned sb=core->busRead32(core,saveptr),obj=objects+core->busRead8(core,avatar+5)*0x24; \
        if(core->busRead8(core,sb+4)==35 && core->busRead8(core,sb+5)==3 \
           && (short)core->busRead16(core,obj+0x10)-7==12 && (short)core->busRead16(core,obj+0x12)-7==10) walking.pendingStairs=1; \
    } \
''' +point+r'''    if(walking.pendingStairs && !active_task(core,tasks,yesNoTask)) { \
        if(core->busRead16(core,choiceResult)==1) {walking.actualYes=1;} walking.pendingStairs=0; \
    } \
    unsigned walkReason=walk_frame_check(core,&walking,walkAddresses,total+1);if(walkReason) WALK_STOP(walkReason); \
''')
    # Track the exact already-prescribed ordinary keys; no input/cadence changes.
    code=code.replace('core->setKeys(core,','WALK_KEYS(')
    point='    while (fgets(line,sizeof(line),stdin)) {'
    code=replace(code,point,'#define WALK_KEYS(k) do {walkKeys=(k);core->setKeys(core,walkKeys);} while(0)\n'+point)
    point='        if (!strcmp(line,"quit\\n")) break;'
    code=replace(code,point,r'''        if (!strcmp(line,"quit\n")) {
            unsigned reason=walk_stable_check(core,&walking,walkAddresses,total);if(reason) WALK_STOP(reason);
            walk_snapshot(core,walkAddresses,"final");
            printf("WALKING frame_checks=%u boundary_events=%u resource_checks=%u total_frames=%u\n",walking.checks,walking.events,walking.snapshots,total);break;
        }
        if (!strcmp(line,"preserve start\n") || !strcmp(line,"preserve check\n")) {
            if(!fieldLock || !fieldCallback || !scriptStatus || core->busRead8(core,fieldLock) || core->busRead8(core,scriptStatus)!=2
                || (core->busRead32(core,mainstate+4)&~1u)!=(fieldCallback&~1u)) WALK_STOP(40);
            unsigned reason=!strcmp(line,"preserve start\n")?walk_arm(core,&walking,walkAddresses,total):walk_stable_check(core,&walking,walkAddresses,total);
            if(reason) WALK_STOP(reason);
            if(!strcmp(line,"preserve check\n")) {checks+=2;printf("PASS exact source-valid post-victory party and logical resources\n");}continue;
        }
''')
    # Historical preservation block remains verbatim but the separate handler above
    # handles preservation commands; its inventory-only behavior is unchanged.
    code=replace(code,'            checks++;printf("PASS ready\\n");continue;',r'''            unsigned reason=walk_stable_check(core,&walking,walkAddresses,total);if(reason) WALK_STOP(reason);
            checks++;printf("PASS ready\n");continue;''')
    assert code.count('core->runFrame(core);')==1 and 'busWrite' not in code
    return code,base
