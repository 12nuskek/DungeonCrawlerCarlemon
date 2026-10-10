"""Separate diagnostic prefix host; original full-route finish guards untouched."""
from pathlib import Path
import importlib.util,re
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    s=importlib.util.spec_from_file_location('prefixTerminal',ROOT/'scripts/floor1/c01a-ui-host-terminal.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    original=m.generate(git);code=original
    def replace(a,b):
        nonlocal code
        assert code.count(a)==1,(a,code.count(a));code=code.replace(a,b)
    replace('static unsigned c01_edge_observe(struct mCore *,unsigned);','static unsigned dg_observe(struct mCore *,unsigned);\nstatic unsigned c01_edge_observe(struct mCore *,unsigned);')
    replace('unsigned edgeReason=c01_edge_observe(r->core,r->inputEpoch);','unsigned edgeReason=dg_observe(r->core,r->inputEpoch);if(!edgeReason)edgeReason=c01_edge_observe(r->core,r->inputEpoch);')
    header=(ROOT/'scripts/floor1/c01a-prefix-diagnostic.h').read_text()
    replace('static void c01_edge_terminal_exit(unsigned result)',header+'\nstatic void c01_edge_terminal_exit(unsigned result)')
    replace('    unsigned retention=c01_edge_close(result);','    unsigned diagnostic=dg_close(result);\n    if(diagnostic)fprintf(stderr,"Terminal diagnostic retention=%u original STOP=%u preserved\\n",diagnostic,result);\n    unsigned retention=c01_edge_close(result);')
    anchor='        bv_tl_symbol(&timelineConfig,addr,symbol);'
    assignments='''
        if(!strcmp(symbol,"dg_count"))dg.count=addr;
        unsigned dgIndex;char dgExtra;
        if(sscanf(symbol,"dg_data%u%c",&dgIndex,&dgExtra)==1 && dgIndex<DG_DATA){dg.data[dgIndex]=addr;dg.dataSeen|=1u<<dgIndex;}
'''
    for name,field,bit in [('pc','pc',1),('rom','rom',2),('op','opcode',4),('mode','mode',8),('fn','function',16),('id','identity',32),('role','role',64),('size','size',128)]:
        assignments+=f'        if(sscanf(symbol,"dg_{name}%u%c",&dgIndex,&dgExtra)==1 && dgIndex<DG_POINTS){{dg.point[dgIndex].{field}=addr;dg.point[dgIndex].seen|={bit};}}\n'
    assignments+='        if(sscanf(symbol,"dg_scope%u%c",&dgIndex,&dgExtra)==1 && dgIndex<DG_POINTS && addr==1)dg.point[dgIndex].seen|=256;\n'
    replace(anchor,anchor+assignments)
    replace('        if(c01_edge_command()){result=125;break;}','        if(c01_edge_command()){result=125;break;}\n        if(dg_command()){result=126;break;}')
    replace('            visual.candidate=mode;ui.candidate=mode;','            unsigned diagnosticOpen=dg_open(core);if(diagnosticOpen){result=diagnosticOpen;break;}\n            visual.candidate=mode;ui.candidate=mode;')
    replace('        if(!vr)vr=ui_sample(core,&ui,&snapshot,mainstate,tasks,pixels,width,height); \\','        if(!vr)vr=ui_sample(core,&ui,&snapshot,mainstate,tasks,pixels,width,height); \\\n        if(!vr)vr=dg_frame_end(); \\')
    # No added command/input. Stop immediately after original command27 succeeds.
    replace('printf("UI_READY %s actor=%u visual=%u waited=%u\\n",name,keys,visual.frames,elapsed);checks++;continue;','printf("UI_READY %s actor=%u visual=%u waited=%u\\n",name,keys,visual.frames,elapsed);checks++;\n            if(dg.command==27){if(kind!=2 || keys!=0){result=126;break;}printf("DIAGNOSTIC_PREFIX_END command=27 frames=%u full_acceptance=0\\n",visual.frames);break;}\n            continue;')
    replace('    unsigned edgeClose=c01_edge_close(result);','    unsigned diagnosticClose=dg_close(result);if(!result)result=diagnosticClose;\n    unsigned edgeClose=c01_edge_close(result);')
    # Append host key records before original setKeys; expressions stay exact.
    code=re.sub(r'core->setKeys\(core,([^;]+)\);',lambda x:'if(dg_keys('+x[1]+')){result=126;goto c01_cleanup;}'+x[0],code)
    assert re.findall(r'core->setKeys\(core,([^;]+)\);',code)==re.findall(r'core->setKeys\(core,([^;]+)\);',original)
    assert code.count('ARMRun(cpu);')==original.count('ARMRun(cpu);')==1
    assert code.count('bv_native_frame(&native,')==original.count('bv_native_frame(&native,')==1
    return code
