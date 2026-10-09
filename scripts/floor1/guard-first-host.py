"""New phase-aware adapter; historical offensive decision code stays unchanged."""
from pathlib import Path
import importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    s=importlib.util.spec_from_file_location('gf_prior',ROOT/'scripts/floor1/new-save-recovery-host.py');prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
    code,base=prior.generate(git);assert hashlib.sha256(code.encode()).hexdigest()=='a3af0f882d95912304e5c3c8d537449f8b335930bf6a806244358fa395af2a12'
    def once(old,new):
        nonlocal code
        assert code.count(old)==1,(old[:80],code.count(old));code=code.replace(old,new)
    once('int main(int argc, char **argv)',(ROOT/'scripts/floor1/party-resource-canonical.h').read_text()+'\n'+(ROOT/'scripts/floor1/walking-preservation.h').read_text()+'\n'+(ROOT/'scripts/floor1/guard-first-observer.h').read_text()+'\nint main(int argc, char **argv)')
    once('    FILE *symbols=fopen(argv[3], "r");','    unsigned cb1=0,vblank=0,mapgroups=0;\n    FILE *symbols=fopen(argv[3], "r");')
    once('        if (!strcmp(symbol,"gTasks")) tasks=addr;', '''        if (!strcmp(symbol,"CB1_Overworld")) cb1=addr;
        if (!strcmp(symbol,"VBlankCB_Field")) vblank=addr;
        if (!strcmp(symbol,"gMapGroups")) mapgroups=addr;
        if (!strcmp(symbol,"gTasks")) tasks=addr;''')
    once('    while (fgets(line,sizeof(line),stdin)) {','''    setvbuf(stdout,NULL,_IOLBF,0);
    struct PatrolGuard pg={0};
    struct PatrolAddresses pa={party,saveptr,save2ptr,mapgroups,mainstate,objects,avatar,count,cb1,fieldCallback,vblank,trainer};
    if(!cb1||!vblank||!mapgroups||!fieldCallback||!trainer)return 4;
    while (fgets(line,sizeof(line),stdin)) {''')
    once('        if (!strcmp(line,"quit\\n")) break;',r'''
        if (!strcmp(line,"quit\n")) break;
        if (!strcmp(line,"cold-approach\n")) {if(pg.armed||pg.frames){result=70;break;}pg.approach=1;pg.stage=4;continue;}
        if (!strcmp(line,"approach\n")) {if(!pg.armed||pg.pending||pg.stage!=4){result=70;break;}pg.approach=1;continue;}
        if (!strncmp(line,"mutation ",9)) {
            unsigned pending=0;
            if(!strcmp(line,"mutation guard\n")&&pg.stage==0)pending=1;
            if(!strcmp(line,"mutation howler\n")&&pg.stage==2)pending=2;
            if(!strcmp(line,"mutation heal\n")&&(pg.stage==1||pg.stage==3||pg.stage==4))pending=3;
            if(!pg.armed||pg.pending||!pending){result=70;break;}
            result=patrol_sample(core,&pg,pa,1);if(result)break;
            patrol_dump(&pg.last,"before",pg.frames);
            patrol_dump(&pg.last,pending==1?"guard-before":pending==2?"howler-before":pg.stage==1?"guide-guard-before":pg.stage==3?"guide-howler-before":"guide-preboss-before",pg.frames);pg.pending=pending;continue;
        }
        if (!strncmp(line,"checkpoint ",11)) {
            char label[32];unsigned mutation=pg.pending;
            if(sscanf(line,"checkpoint %31s %c",label,&extra)!=1){result=70;break;}
            if(!strcmp(label,"boot")) {if(pg.armed){result=70;break;}}
            else if(!strcmp(label,"guard-win")) {if(mutation!=1||pg.stage!=0){result=70;break;}pg.stage=1;}
            else if(!strcmp(label,"howler-win")) {if(mutation!=2||pg.stage!=2){result=70;break;}pg.stage=3;}
            else if(!strcmp(label,"guide-guard")) {if(mutation!=3||pg.stage!=1){result=70;break;}pg.stage=2;}
            else if(!strcmp(label,"guide-howler")) {if(mutation!=3||pg.stage!=3){result=70;break;}pg.stage=4;}
            else if(!strcmp(label,"guide-preboss")) {if(mutation!=3||pg.stage!=4){result=70;break;}}
            else if(strcmp(label,"guard-repeat")&&strcmp(label,"howler-repeat")&&strcmp(label,"final")&&strcmp(label,"saved")&&strcmp(label,"cold")){result=70;break;}
            else if(mutation||!pg.armed){result=70;break;}
            struct PatrolSnapshot current=pg.last;result=patrol_read(core,pa,&current,1,pg.approach);if(result)break;
            unsigned w=core->busRead32(core,maplayout),h=core->busRead32(core,maplayout+4),tiles=core->busRead32(core,maplayout+8);
            if(!tiles||current.x+7>=w||current.y+7>=h||(core->busRead16(core,tiles+2*((current.y+7)*w+current.x+7))&0xC00)){result=57;break;}
            patrol_dump(&current,"current",pg.frames);
            if(!pg.armed||mutation){
                char command[512];snprintf(command,sizeof command,"python3 /workspace/DungeonCrawlerCarlemon/scripts/floor1/guard-first-state.py %s",label);
                if(system(command)){result=71;break;}
                pg.last=current;pg.lastAccepted=pg.frames;pg.armed=1;pg.pending=0;pg.wasDeferred=0;
            }else{result=patrol_sample(core,&pg,pa,1);if(result)break;}
            patrol_dump(&current,label,pg.frames);pg.checkpoints++;checks++;printf("PASS checkpoint %s absolute_frame=%u\n",label,pg.frames);continue;
        }
        if(!strncmp(line,"pilot ",6)&&strcmp(line,"pilot offensive 36000\n")){result=70;break;}
''')
    # Only this wrapper advances the emulator: first failing frame returns to STOP.
    code=code.replace('core->runFrame(core);','if((result=patrol_frame(core,&pg,pa))){goto patrol_stop;}')
    # Gate measurement before SaveBlock reads, retain original active-frame latch.
    once('\n            unsigned sb=core->busRead32(core,saveptr), obj=objects+core->busRead8(core,avatar+5)*0x24;',
         '            if(!patrol_phase(core,pa)){result=40;break;}\n            unsigned sb=core->busRead32(core,saveptr), obj=objects+core->busRead8(core,avatar+5)*0x24;')
    once('                if (measuring) {','                if (measuring) {\n                    measured++;\n                    if(!patrol_phase(core,pa)){motion=0;continue;}')
    once('                    measured++;\n                    unsigned delta=', '                    unsigned delta=')
    once('            total+=frames;', '            total=pg.frames;\n            if(result)break;')
    # Safe deferred telemetry for fixed boot/battle/menu steps. Assertions cannot defer.
    once('\n        unsigned sb=core->busRead32(core,saveptr);','''        if(!patrol_phase(core,pa)) {
            if(strncmp(line,"step ",5)){result=40;break;}
            printf("TELEMETRY deferred absolute_frame=%u\\n",pg.frames);continue;
        }
        unsigned sb=core->busRead32(core,saveptr);''')
    once('\n        if (!strcmp(line,"money remember\\n")', '        if ((!strcmp(line,"money remember\\n") || !strcmp(line,"money same\\n") || !strncmp(line,"money gain ",11)) && !patrol_phase(core,pa)) {result=40;break;}\n        if (!strcmp(line,"money remember\\n")')
    # Labels use the exact wrapper clock; no alteration to policy choices/cadence.
    code=code.replace('                        total,b,observedHp[b]', '                        pg.frames,b,observedHp[b]')
    once('    if (ferror(stdin)) result=15;', '''patrol_stop:
    if(result){
        if(pg.armed)patrol_dump(&pg.last,"stop-last-accepted",pg.lastAccepted);
        struct PatrolSnapshot live=pg.last;if(!patrol_read(core,pa,&live,1,pg.approach))patrol_dump(&live,"stop-live",pg.frames);
        capture("stop.ppm",pixels,width,height);
        fprintf(stderr,"Guard-first STOP reason=%d absolute_frame=%u last_accepted=%u pending=%u stage=%u\\n",result,pg.frames,pg.lastAccepted,pg.pending,pg.stage);
    }
    printf("PATROL_CLOCK absolute_frames=%u valid_samples=%u deferred_samples=%u reentries=%u unarmed_frames=%u mutation_frames=%u checkpoints=%u battle_frames=%u battle_attempts=%u stage=%u\\n",pg.frames,pg.valid,pg.deferred,pg.reentries,pg.unarmedFrames,pg.mutationFrames,pg.checkpoints,pg.battleFrames,pg.battleAttempts,pg.stage);
    if (ferror(stdin)) result=15;''')
    assert 'busWrite' not in code and code.count('runFrame(')==1
    return code,base
