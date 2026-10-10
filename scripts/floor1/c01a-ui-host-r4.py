"""Separately frozen all-menu readiness and passive native receiving context."""
from pathlib import Path
import importlib.util,re
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    s=importlib.util.spec_from_file_location('c01r4prior',ROOT/'scripts/floor1/c01a-ui-host.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);code=m.generate(git)
    def replace(a,b):
        nonlocal code
        assert code.count(a)==1,(a,code.count(a));code=code.replace(a,b)
    declarations='static unsigned c01_edge_observe(struct mCore *,unsigned);\nstatic unsigned c01_edge_frame_begin(unsigned);\n'
    replace('static inline unsigned bv_native_observe(void *p)',declarations+'static inline unsigned bv_native_observe(void *p)')
    replace('struct ARMCore original=*cpu;r->debugger.platform->checkBreakpoints(r->debugger.platform);','struct ARMCore original=*cpu;unsigned edgeReason=c01_edge_observe(r->core,r->inputEpoch);\n    if(edgeReason)return edgeReason;\n    r->debugger.platform->checkBreakpoints(r->debugger.platform);')
    replace('r->lastInput=r->core->getKeys(r->core);r->inputEpoch++;','r->lastInput=r->core->getKeys(r->core);r->inputEpoch++;\n    unsigned edgeReason=c01_edge_frame_begin(r->inputEpoch);if(edgeReason)return bv_native_fail(r,edgeReason);')
    old=(ROOT/'scripts/floor1/c01a-ui-observer.h').read_text();new=(ROOT/'scripts/floor1/c01a-ui-observer-r4.h').read_text()
    replace(old,'static unsigned c01_edge_frame_end(struct mCore *);\n'+new+'\n'+(ROOT/'scripts/floor1/c01a-ui-edge-r4.h').read_text())
    anchor='        bv_tl_symbol(&timelineConfig,addr,symbol);'
    assignments=''
    for i,n in enumerate(['uiBagCB2','uiPartyCB2','uiSummaryCB2']):assignments+=f'        if(!strcmp(symbol,"{n}"))ui.cb2[{i}]=addr;\n'
    for i,n in enumerate(['uiWireless','uiWiredCount','uiRfuCount','uiRemotePlayers']):assignments+=f'        if(!strcmp(symbol,"{n}"))ui.link[{i}]=addr;\n'
    assignments+='''        unsigned edgeIndex;char edgeExtra;
        if(sscanf(symbol,"ce_pc%u%c",&edgeIndex,&edgeExtra)==1 && edgeIndex<C01_EDGE_POINTS){edge.point[edgeIndex].pc=addr;edge.point[edgeIndex].seen|=1;}
        if(sscanf(symbol,"ce_op%u%c",&edgeIndex,&edgeExtra)==1 && edgeIndex<C01_EDGE_POINTS){edge.point[edgeIndex].opcode=addr;edge.point[edgeIndex].seen|=2;}
        if(sscanf(symbol,"ce_fn%u%c",&edgeIndex,&edgeExtra)==1 && edgeIndex<C01_EDGE_POINTS){edge.point[edgeIndex].function=addr;edge.point[edgeIndex].seen|=4;}
        if(sscanf(symbol,"ce_role%u%c",&edgeIndex,&edgeExtra)==1 && edgeIndex<C01_EDGE_POINTS){edge.point[edgeIndex].role=addr;edge.point[edgeIndex].seen|=8;}
        if(sscanf(symbol,"ce_kind%u%c",&edgeIndex,&edgeExtra)==1 && edgeIndex<C01_EDGE_POINTS){edge.point[edgeIndex].kind=addr;edge.point[edgeIndex].seen|=16;}
        if(sscanf(symbol,"ce_scope%u%c",&edgeIndex,&edgeExtra)==1 && edgeIndex<C01_EDGE_POINTS){edge.point[edgeIndex].seen|=addr==1?32:0;}
'''
    replace(anchor,anchor+'\n'+assignments)
    replace('            if(result)break;','            for(unsigned z=0;z<3;z++)if(!ui.cb2[z]){result=121;break;}\n            for(unsigned z=0;z<4;z++)if(!ui.link[z]){result=121;break;}\n            if(result)break;\n            unsigned edgeOpen=c01_edge_open(core,&visual,tasks,fade);if(edgeOpen){result=edgeOpen;break;}')
    replace('    while (fgets(line,sizeof(line),stdin)) {','    while (fgets(line,sizeof(line),stdin)) {\n        if(c01_edge_command()){result=125;break;}')
    replace('            unsigned kind=ui_kind(name),elapsed=0,advance=!strncmp(line,"ui next",7);','            unsigned kind=ui_kind(name),elapsed=0,advance=!strncmp(line,"ui next",7);\n            edge.desiredKind=kind;edge.desiredActor=keys;')
    replace('            printf("UI_READY %s actor=%u visual=%u waited=%u\\n",name,keys,visual.frames,elapsed);checks++;continue;','            if(c01_edge_record(9,C01_EDGE_POINTS,0,0)){result=125;break;}\n            printf("UI_READY %s actor=%u visual=%u waited=%u\\n",name,keys,visual.frames,elapsed);checks++;continue;')
    # Retain every original key expression/call. Recording does not send keys,
    # invoke native functions, schedule events or execute another instruction.
    calls=re.findall(r'core->setKeys\(core,([^;]+)\);',code);assert len(calls)==15
    code=re.sub(r'core->setKeys\(core,([^;]+)\);',lambda x:'if(c01_edge_keys('+x[1]+')){result=125;goto c01_cleanup;}'+x[0],code)
    replace('    if (ferror(stdin)) result=15;','c01_cleanup:\n    if (ferror(stdin)) result=15;')
    replace('    mCoreConfigDeinit(&core->config);','    unsigned edgeClose=c01_edge_close(result);if(!result)result=edgeClose;\n    mCoreConfigDeinit(&core->config);')
    assert 'busWrite' not in code and code.count('bv_native_frame(&native,')==1
    assert re.findall(r'core->setKeys\(core,([^;]+)\);',code)==calls
    return code
