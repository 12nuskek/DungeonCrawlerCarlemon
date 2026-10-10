"""Separately scoped C01a menu adapter; inherited V01 contracts stay unchanged.

Retains passive native Wait B/F/E/EOF, full 2560-byte snapshots, timeline guards
and first-stop diagnostics. Adds full frame snapshots and RNG/cursor/target/task
callback identities. Does not claim whole-battle pose/retirement acceptance.
"""
from pathlib import Path
import importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def generate(git):
    code,_=module('c01a_v01_host',ROOT/'scripts/floor1/v01-battle-host.py').generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='1647352d92b3fa6f0135cf80f4c48df1c2a8a3818b711fd94651390a6334977f'
    def replace(a,b):
        nonlocal code
        assert code.count(a)==1,(a,code.count(a));code=code.replace(a,b)
    addition=(ROOT/'scripts/floor1/c01a-ui-observer.h').read_text()
    replace('int main(int argc, char **argv)',addition+'\nint main(int argc, char **argv)')
    anchor='        bv_tl_symbol(&timelineConfig,addr,symbol);'
    replace(anchor,anchor+'\n        if(!strcmp(symbol,"gMain"))ui.mainstate=addr;\n        if(!strcmp(symbol,"bv_battleCB2"))ui.battleCB2=addr;\n        if(!strcmp(symbol,"gBattleControllerExecFlags"))ui.exec=addr;')
    fields=['gRngValue','gRng2Value','gMoveSelectionCursor','gActionSelectionCursor','gMultiUsePlayerCursor','gBattlerTarget','gActiveBattler','gBattlerInMenuId','gBattleBufferA','uiAction','uiMove','uiTarget','uiBag','uiParty','uiContext','uiSummary']
    replace(anchor,anchor+'\n'+''.join(f'        if(!strcmp(symbol,"{n}"))ui.a[{i}]=addr;\n' for i,n in enumerate(fields)))
    replace('if(!vr)vr=bv_sample(core,&visual,mainstate,mons,results,animationActive,animationActor,currentMove,pixels,width,height);','if(!vr)vr=ui_sample(core,&ui,&snapshot,mainstate,tasks,pixels,width,height);')
    replace('visual.frames>=36000','visual.frames>=18000')
    anchor='        if (!strcmp(line,"quit\\n")) break;'
    commands=r'''
        if(!strcmp(line,"ui start\n")){
            unsigned char mode;
            (void)bv_sample;
            if(visual.recording || bv_load("visual-mode.bin",&mode,1) || mode>1){result=121;break;}
            for(unsigned z=0;z<16;z++)if(!ui.a[z]){result=121;break;}
            if(result)break;
            visual.candidate=mode;ui.candidate=mode;
            visual.trace=fopen(mode?"expected-native-boundary-trace.bin":"native-boundary-trace.bin",mode?"rb":"wbx");
            ui.trace=fopen(mode?"expected-ui-frame-trace.bin":"ui-frame-trace.bin",mode?"rb":"wbx");
            if(!visual.trace || !ui.trace){result=121;break;}
            if(!mode && (fchmod(fileno(visual.trace),0600)||fchmod(fileno(ui.trace),0600))){result=121;break;}
            visual.recording=1;checks++;continue;
        }
        if(sscanf(line,"ui wait %31s %u %u %c",name,&keys,&frames,&extra)==3 || sscanf(line,"ui next %31s %u %u %c",name,&keys,&frames,&extra)==3){
            unsigned kind=ui_kind(name),elapsed=0,advance=!strncmp(line,"ui next",7);
            if(!kind || keys>3 || frames>6000 || !frames){result=122;break;}
            while(elapsed<frames && !ui_ready(core,&ui,controls,tasks,fade,keys,kind)){
                core->setKeys(core,advance && elapsed%60==0?1:0);WARDEN_FRAME();elapsed++;total++;
            }
            core->setKeys(core,0);
            if(!ui_ready(core,&ui,controls,tasks,fade,keys,kind)){result=122;fprintf(stderr,"UI readiness stop %s actor=%u frame=%u\n",name,keys,visual.frames);capture("ui-readiness-stop.ppm",pixels,width,height);break;}
            printf("UI_READY %s actor=%u visual=%u waited=%u\n",name,keys,visual.frames,elapsed);checks++;continue;
        }
        unsigned uiActor,uiCursor,uiPP;
        if(sscanf(line,"ui move %u %u %u %c",&uiActor,&uiCursor,&uiPP,&extra)==3){
            if(uiActor>3 || uiCursor>1 || !ui_ready(core,&ui,controls,tasks,fade,uiActor,2)
                || core->busRead8(core,ui.a[2]+uiActor)!=uiCursor
                || core->busRead8(core,ui.a[8]+512*uiActor+12+uiCursor)!=uiPP){result=123;break;}
            printf("UI_MOVE actor=%u cursor=%u pp=%u frame=%u\n",uiActor,uiCursor,uiPP,visual.frames);checks++;continue;
        }
        if(!strcmp(line,"ui finish\n")){
            unsigned vr=bv_native_finish(&native);
            if(!vr && ui.candidate && fgetc(ui.trace)!=EOF)vr=124;
            if(!vr && (ferror(ui.trace)||fclose(ui.trace)))vr=124;
            if(!vr && fclose(visual.trace))vr=124;
            if(vr){bv_native_retain_failure(&native);result=vr;break;}
            visual.recording=0;checks++;printf("UI_FINISH frames=%u full_native_BFE_EOF=1 full_frame_state_rng_targets_callbacks_EOF=1\n",visual.frames);continue;
        }
'''
    replace(anchor,anchor+commands)
    assert 'busWrite' not in code and code.count('bv_native_frame(&native,')==1
    return code
