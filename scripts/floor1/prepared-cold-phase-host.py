"""Minimal separate phase adapter/clock on immutable PR105 generated host."""
from pathlib import Path
import hashlib,importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    def module(name,path):
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    replace=module('cold_replace',ROOT/'scripts/floor1/recovery-host.py').replace_once
    code,base=module('cold_prior',ROOT/'scripts/floor1/prepared-persistence-host.py').generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='a15f03615c01b463388b0dd8f17a9239050bedaf16f701e60588b701bdb7100b'
    main=(ROOT/'engine/include/main.h').read_text();source=(ROOT/'engine/src/overworld.c').read_text();save=(ROOT/'engine/src/load_save.c').read_text()
    assert '/*0x00C*/ IntrCallback vblankCallback;' in main
    assert 'SetMainCallback1(CB1_Overworld);' in source and 'SetMainCallback2(CB2_Overworld);' in source
    assert 'SetVBlankCallback(VBlankCB_Field);' in source and 'gMain.vblankCallback = NULL;' in save
    addition=(ROOT/'scripts/floor1/cold-phase-guard.h').read_text()+'\n'+(ROOT/'scripts/floor1/cold-phase-observer.h').read_text()
    code=replace(code,(ROOT/'scripts/floor1/prepared-preservation-observer.h').read_text(),addition)
    code=replace(code,'unsigned mapgroups=0;','unsigned mapgroups=0,nativeCB1=0,nativeVBlank=0;')
    code=replace(code,'        if (!strcmp(symbol,"gMapGroups")) mapgroups=addr;',
        '        if (!strcmp(symbol,"CB1_Overworld")) nativeCB1=addr;\n        if (!strcmp(symbol,"VBlankCB_Field")) nativeVBlank=addr;\n        if (!strcmp(symbol,"gMapGroups")) mapgroups=addr;')
    code=replace(code,'walkAddresses={party,saveptr,save2ptr,mapgroups,mainstate,objects,avatar,choiceAddress};',
        'walkAddresses={party,saveptr,save2ptr,mapgroups,mainstate,objects,avatar,choiceAddress,count,nativeCB1,fieldCallback,nativeVBlank};')
    code=replace(code,'if(!mapgroups || !save2ptr || !choiceAddress) return 4;',
        'if(!mapgroups || !save2ptr || !choiceAddress || !nativeCB1 || !nativeVBlank || !fieldCallback) return 4;')
    start=code.index('#define WALK_STOP(reason)');end=code.index('#define WALK_KEYS(k)',start)
    code=code[:start]+r'''#define WALK_STOP(reason) do { \
    cold_stop_snapshot(core,&walking,walkAddresses); \
    capture("cold-phase-stop.ppm",pixels,width,height); \
    fprintf(stderr,"Cold phase stop reason=%u absolute_frame=%u; no further frames\n",reason,walking.guard.frames); \
    printf("WARDEN battle_frames=%u attempts=%u\nresult=%u assertions=%u\n",wardenFrames,attemptUsed,reason,checks);exit(reason); \
} while(0)
#define WARDEN_FRAME() do { \
    unsigned wasBattle=(core->busRead8(core,mainstate+0x439)&2)!=0; \
    unsigned reason=cold_before_frame(&walking.guard,wasBattle);if(reason) WALK_STOP(reason); \
    if(!warden_before_frame(wardenFrames,wasBattle)) WARDEN_STOP_BOUND(); \
    if(walking.armed && cold_phase_ready(core,walkAddresses) && (walkKeys&1) && active_task(core,tasks,yesNoTask)) { \
        unsigned sb=core->busRead32(core,saveptr),obj=objects+core->busRead8(core,avatar+5)*0x24; \
        if(core->busRead8(core,sb+4)==35 && core->busRead8(core,sb+5)==3 \
           && (short)core->busRead16(core,obj+0x10)-7==12 && (short)core->busRead16(core,obj+0x12)-7==10) walking.pendingStairs=1; \
    } \
    core->runFrame(core); \
    unsigned isBattle=(core->busRead8(core,mainstate+0x439)&2)!=0; \
    reason=cold_after_frame(&walking.guard,isBattle); \
    if(wasBattle || isBattle) wardenFrames++; \
    if(noBattleMonitoring && (wasBattle || isBattle)) sawBattle=1; \
    if(reason) WALK_STOP(reason); \
    if(walking.pendingStairs && !active_task(core,tasks,yesNoTask)) { \
        if(core->busRead16(core,choiceResult)==1) {walking.actualYes=1;} walking.pendingStairs=0; \
    } \
    unsigned walkReason=walk_frame_check(core,&walking,walkAddresses,walking.guard.frames);if(walkReason) WALK_STOP(walkReason); \
    if(!warden_after_frame(wardenFrames,isBattle)) WARDEN_STOP_BOUND(); \
} while(0)
''' +code[end:]
    code=replace(code,'    while (fgets(line,sizeof(line),stdin)) {',r'''    while (fgets(line,sizeof(line),stdin)) {
        if(!strncmp(line,"pilot ",6) || !strncmp(line,"engage ",7) || !strncmp(line,"measure ",8) || !strncmp(line,"inventory ",10)) WALK_STOP(70);
        if(strncmp(line,"step ",5) && !cold_phase_ready(core,walkAddresses)) WALK_STOP(40);''')
    code=replace(code,'            walk_snapshot(core,walkAddresses,"final");',
        '            cold_dump(&walking.guard.last,"final",walking.guard.frames,1);')
    code=replace(code,'            printf("WALKING frame_checks=%u boundary_events=%u resource_checks=%u total_frames=%u\\n",walking.checks,walking.events,walking.snapshots,total);break;',
        '            printf("COLD_CLOCK absolute_frames=%u valid_frame_samples=%u deferred_frame_samples=%u explicit_checkpoints=%u reentry_comparisons=%u boundary_events=%u armed_frame=%u\\n",walking.guard.frames,walking.guard.validFrames,walking.guard.deferredFrames,walking.guard.checkpoints,walking.guard.reentries,walking.guard.events,walking.guard.armedFrame);break;')
    code=code.replace('walk_arm(core,&walking,walkAddresses,total)','walk_arm(core,&walking,walkAddresses,walking.guard.frames)')
    code=code.replace('walk_stable_check(core,&walking,walkAddresses,total)','walk_stable_check(core,&walking,walkAddresses,walking.guard.frames)')
    # Legacy telemetry may read map/flags only under the same central native gate.
    code=replace(code,'        unsigned sb=core->busRead32(core,saveptr);',r'''        if(!cold_phase_ready(core,walkAddresses)) {printf("PHASE telemetry deferred absolute_frame=%u\n",walking.guard.frames);continue;}
        unsigned sb=core->busRead32(core,saveptr);''')
    code=replace(code,'printf("frame=%u map=%d.%d pos=%d,%d flags=%d\\n",total,group,map,x,y,flags);',
        'printf("frame=%u map=%d.%d pos=%d,%d flags=%d\\n",walking.guard.frames,group,map,x,y,flags);')
    assert code.count('core->runFrame(core);')==1 and 'busWrite' not in code
    return code,base
