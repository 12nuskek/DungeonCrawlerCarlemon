"""One normal New Game driver; separate read-only cold mode, no old runner calls."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
NAMES=['boot','note','supply','guide-initial','trial','scrap','potion','guide-posttrial','guard','guide-guard','howler','guide-howler','guide-preboss','boss','boss-repeat','stairs-no','stairs-yes','save']
KINDS=['BOOT','NOTE','SUPPLY','GUIDE','TRIAL','SCRAP','POTION','GUIDE','GUARD','GUIDE','HOWLER','GUIDE','GUIDE','BOSS','STABLE','STABLE','STAIRS','SAVE']
def generate(git):
    code,base=module('co_inherited',ROOT/'scripts/floor1/recovery-host.py').generate(git)
    # Replace the complete old rescue/controller parser with precisely the
    # original offensive/fortify buttons. No new combat decision or fallback.
    start=code.index('        if (!strncmp(line,"pilot ",6)) {');end=code.index('        if (sscanf(line,"step ',start)
    original=(ROOT/'scripts/playtest.c').read_text();a=original.index('        if (!strncmp(line,"pilot ",6)) {');b=original.index('        if (sscanf(line,"step ',a)
    pilot=original[a:b]
    pilot=pilot.replace('            unsigned elapsed=0, lastTurn=UINT_MAX, capturedIncap=0;',r'''
            if((co.kind==CO_BOSS?strcmp(line,"pilot fortify 30000\n"):strcmp(line,"pilot offensive 36000\n"))
                || !co.pending || co.cold || !battleMain
                || (core->busRead32(core,mainstate+4)&~1u)!=(battleMain&~1u)) {result=91;break;}
            unsigned elapsed=0, lastTurn=UINT_MAX, capturedIncap=0;
''')
    needle='                            unsigned cursor=core->busRead8(core,moveCursor+b);'
    assert pilot.count(needle)==1
    pilot=pilot.replace(needle,r'''
                            if(b==0&&desired==0&&!core->busRead8(core,mons+0x24)&&core->busRead8(core,mons+0x25)) {
                                fprintf(stderr,"Existing controller exhausted Carl STRIKE while BRACE remains; no invented fallback\n");result=92;break;
                            }
''' +needle)
    pilot=pilot.replace('                if (result) break;\n                core->setKeys(core,key);',r'''
                if(result)break;
                printf("TURN_METRIC absolute=%u encounter=%u turn=%u actor=%u menu=%u selection=%u key=%u HP=%u,%u,%u,%u PP=%u,%u,%u,%u stages=%u,%u,%u\n",
                    co.frames,core->busRead16(core,trainer),turn,actor,menu,selection,key,
                    core->busRead16(core,mons+0x28),core->busRead16(core,mons+0x58+0x28),core->busRead16(core,mons+2*0x58+0x28),core->busRead16(core,mons+3*0x58+0x28),
                    core->busRead8(core,mons+0x24),core->busRead8(core,mons+0x25),core->busRead8(core,mons+2*0x58+0x24),core->busRead8(core,mons+2*0x58+0x25),
                    core->busRead8(core,mons+0x1a),core->busRead8(core,mons+0x58+0x19),core->busRead8(core,mons+3*0x58+0x19));
                core->setKeys(core,key);
''',1)
    pilot=pilot.replace('            checks++;\n            continue;',r'''
            if(core->busRead8(core,outcome)!=1||lastPilotIncap){result=90;break;}
            checks++;
            continue;''')
    pilot=pilot.replace('                if (!chp && dhp) lastPilotIncap|=1;',r'''
                if(!chp||!dhp||!core->busRead16(core,mons+0x28)||!core->busRead16(core,mons+2*0x58+0x28)) {
                    result=90;break; // First observed incapacitation; no further input/frame.
                }
                if (!chp && dhp) lastPilotIncap|=1;''')
    code=code[:start]+pilot+code[end:]
    a=code.index('static unsigned acknowledged_stage(');b=code.index('\n#endif',a);code=code[:a]+code[b:]
    code=code.replace('potionStage=0, pendingContext=0, pendingRecipient=0, healed=0, ','')
    code=code.replace('contextInput=0, ','').replace('        if (!strcmp(symbol,"Task_ItemContext_SingleRow")) contextInput=addr;\n','')
    code=module('co_native_pages',ROOT/'scripts/floor1/native-text-observer.py').instrument(code)
    def once(old,new):
        nonlocal code
        assert code.count(old)==1,(old[:80],code.count(old));code=code.replace(old,new)
    once('static int capture(const char *name, const color_t *pixels, unsigned width, unsigned height)',
         'static unsigned co_capture_absolute;\nstatic int capture(const char *name, const color_t *pixels, unsigned width, unsigned height)')
    once('    if (fclose(out)) result=12;','    if (fclose(out)) result=12;\n    if(!result)printf("CAPTURE name=%s absolute=%u width=%u height=%u\\n",name,co_capture_absolute,width,height);')
    once('int main(int argc, char **argv)',(ROOT/'scripts/floor1/party-resource-canonical.h').read_text()+'\n'+(ROOT/'scripts/floor1/walking-preservation.h').read_text()+'\n'+(ROOT/'scripts/floor1/continuous-opening-guard.h').read_text()+'\nint main(int argc, char **argv)')
    once('    if (argc != 4) return 2;', '    if(argc!=5||(strcmp(argv[4],"opening")&&strcmp(argv[4],"cold")))return 2;\n    co.cold=!strcmp(argv[4],"cold");co.limit=co.cold?6000:100000;co.kind=co.cold?CO_COLD:CO_BOOT;')
    once('    FILE *symbols=fopen(argv[3], "r");','    unsigned cb1=0,vblank=0,maps=0,newGame=0,continueGame=0,yesno=0,startTask=0,startInput=0,startCursor=0,menuFn=0,answer=0,saveFn=0,confirmSave=0,saveSuccess=0,saveReturn=0,grid=0,currentMove=0,movePower=0,critical=0,attacker=0,target=0,menuState=0,bagPosition=0,chosen=0,moveResults=0,damage=0;\n    FILE *symbols=fopen(argv[3], "r");')
    symbols={'CB1_Overworld':'cb1','VBlankCB_Field':'vblank','gMapGroups':'maps','CB2_NewGame':'newGame','CB2_ContinueSavedGame':'continueGame','coYesNo':'yesno','coStartTask':'startTask','coStartInput':'startInput','coStartCursor':'startCursor','gMenuCallback':'menuFn','gSpecialVar_Result':'answer','coSaveFn':'saveFn','coConfirmSave':'confirmSave','coSaveSuccess':'saveSuccess','coSaveReturn':'saveReturn'}
    symbols.update({'gBackupMapLayout':'grid','gCurrentMove':'currentMove','gBattleMovePower':'movePower','gCritMultiplier':'critical','gBattlerAttacker':'attacker','gBattlerTarget':'target'})
    symbols.update({'coMenu':'menuState','gBagPosition':'bagPosition','gChosenMoveByBattler':'chosen','gMoveResultFlags':'moveResults','gBattleMoveDamage':'damage'})
    once('        if (!strcmp(symbol,"gTasks")) tasks=addr;', ''.join(f'        if(!strcmp(symbol,"{n}")){v}=addr;\n' for n,v in symbols.items())+'        if (!strcmp(symbol,"gTasks")) tasks=addr;')
    init=r'''
    co.a=(struct CoAddresses){party,count,saveptr,save2ptr,mainstate,cb1,fieldCallback,vblank,objects,avatar,maps,trainer,outcome,newGame,continueGame,grid,mons,results+0x13,currentMove,movePower,critical,attacker,target,controls,chosen,moveResults,damage,battleMain};
    if(!cb1||!vblank||!maps||!newGame||!continueGame||!yesno||!startTask||!startInput||!startCursor||!menuFn||!answer||!saveFn||!confirmSave||!saveSuccess||!saveReturn)return 4;
    co.trace=fopen("complete-field-trace-private.bin","wb");co.index=fopen("frame-index.bin","wb");if(!co.trace||!co.index)return 84;
    if(!grid||!currentMove||!movePower||!critical||!attacker||!target||!mons||!results||!controls||!menuState||!bagPosition||!chosen||!moveResults||!damage)return 4;
    co.battleTrace=fopen("complete-battle-trace-private.bin","wb");if(!co.battleTrace)return 84;
    unsigned phaseSeq=0;const char *phaseNames[]={NAMES};const unsigned phaseKinds[]={KINDS};
    co.pending=!co.cold;
    setvbuf(stdout,NULL,_IOLBF,0);
'''.replace('NAMES',','.join('"'+n+'"' for n in NAMES)).replace('KINDS',','.join('CO_'+n for n in KINDS))
    once('    while (fgets(line,sizeof(line),stdin)) {',init+'    while (fgets(line,sizeof(line),stdin)) {')
    commands=r'''
        if(!strncmp(line,"phase begin ",12)||!strncmp(line,"phase end ",10)) {
            char label[40];unsigned begin=!strncmp(line,"phase begin ",12);
            if(co.cold||sscanf(line+(begin?12:10),"%39s %c",label,&extra)!=1||phaseSeq>=18||strcmp(label,phaseNames[phaseSeq])||!co_phase(core)
                ||core->busRead8(core,fieldLock)||core->busRead8(core,scriptStatus)!=2||(core->busRead8(core,fade+7)&128)) {result=93;break;}
            struct CoSnapshot current={0};result=co_read(core,&current);if(result)break;
            if(begin){if(co.pending){result=93;break;}co.before=current;co.kind=phaseKinds[phaseSeq];co.pending=1;co.phaseFrames=0;co_dump(&current,"before");
                if(co.kind==CO_POTION&&(owned_potions(core,pockets,save2ptr)!=2||core->busRead16(core,party+100+0x56)>=core->busRead16(core,party+100+0x58))){result=96;break;}}
            else {
                if(!co.pending){result=93;break;}co_dump(&current,"current");
                if(phaseSeq==0)co_dump(&current,"before");
                char command[512];snprintf(command,sizeof command,"python3 STATE_VALIDATOR %s",label);
                if(system(command)){result=94;break;}
                char prefix[64];snprintf(prefix,sizeof prefix,"phase-%02u",phaseSeq);co_dump(&current,prefix);
                printf("PASS CONTINUOUS phase=%s frame=%u count=%u savedCount=%u counter=%u map=%u,%u pos=%u,%u facing=%u\n",label,co.frames,current.count,current.savedCount,current.counter,current.group,current.map,current.x,current.y,current.facing);
                co.last=current;co.kind=CO_STABLE;co.pending=0;phaseSeq++;checks++;
            }continue;
        }
        if(!strcmp(line,"co yesno\n")) {
            if(!co_task_state(core,tasks,yesno,2,5,65535)||(core->busRead8(core,fade+7)&128)){result=95;break;}checks++;continue;
        }
        if(!strncmp(line,"co answer ",10)) {
            unsigned want;if(sscanf(line,"co answer %u %c",&want,&extra)!=1||want>1||core->busRead16(core,answer)!=want){result=95;break;}checks++;continue;
        }
        if(!strncmp(line,"co choice ",10)) {
            unsigned want;if(sscanf(line,"co choice %u %c",&want,&extra)!=1||want>1||core->busRead8(core,menuState+2)!=want||!menu_ready(core,tasks,fade,yesno)){result=95;break;}checks++;continue;
        }
        if(!strcmp(line,"co bag-item\n")) {
            if(co.kind!=CO_POTION||!recovery_field_ready(core,mainstate,bagMain,tasks,fade,bagInput)
                ||core->busRead8(core,bagPosition+4)||core->busRead8(core,bagPosition+5)
                ||core->busRead16(core,bagPosition+8)||core->busRead16(core,bagPosition+18)){result=95;break;}checks++;continue;
        }
        if(!strcmp(line,"co potion-use\n")) {
            if(co.kind!=CO_POTION||!recovery_field_ready(core,mainstate,bagMain,tasks,fade,fieldContext)
                ||core->busRead16(core,selectedItem)!=13||core->busRead8(core,menuState+2)){result=95;break;}checks++;continue;
        }
        if(!strcmp(line,"co boss-start\n")) {
            if(co.kind!=CO_BOSS||core->busRead16(core,trainer)!=858||core->busRead8(core,outcome)
                ||core->busRead8(core,results+0x13)||core->busRead8(core,mons+0x58+0x2a)!=12||core->busRead8(core,mons+3*0x58+0x2a)!=9
                ||core->busRead16(core,mons+0x58+0x28)!=42||core->busRead16(core,mons+3*0x58+0x28)!=30){result=95;break;}checks++;continue;
        }
        if(!strncmp(line,"co start ",9)) {
            unsigned cursor;
            if(sscanf(line,"co start %u %c",&cursor,&extra)!=1||cursor>4||!co_task_state(core,tasks,startTask,0,1,1)||core->busRead8(core,startCursor)!=cursor||!menu_ready(core,tasks,fade,startTask)||(core->busRead32(core,menuFn)&~1u)!=(startInput&~1u)){result=95;break;}checks++;continue;
        }
        if(!strcmp(line,"co save-ready\n")||!strcmp(line,"co save-success\n")) {
            unsigned success=!strcmp(line,"co save-success\n"),elapsed=0;
            if(co.cold||co.kind!=CO_SAVE){result=95;break;}
            core->setKeys(core,0);
            while(elapsed<3600){
                unsigned cb=core->busRead32(core,saveFn)&~1u;
                if((success?(cb==(saveSuccess&~1u)||cb==(saveReturn&~1u)):(cb==(confirmSave&~1u)))
                    && !(core->busRead8(core,fade+7)&128)&&!core->busRead8(core,printers+0x1b))break;
                co_run(core,pixels,width,height);elapsed++;total++;
            }
            if(elapsed==3600||(!success&&core->busRead8(core,menuState+2))){result=95;break;}checks++;continue;
        }
        if(!strcmp(line,"co potion-recipient\n")) {
            if(co.kind!=CO_POTION||core->busRead16(core,selectedItem)!=13||core->busRead8(core,partyMenu+9)!=1||!recovery_field_ready(core,mainstate,partyMain,tasks,fade,partyInput)){result=95;break;}checks++;continue;
        }
        if(!strcmp(line,"co potion-healed\n")) {
            if(co.kind!=CO_POTION||(core->busRead32(core,mainstate+4)&~1u)!=(partyMain&~1u)||(!menu_ready(core,tasks,fade,restoredText)&&!menu_ready(core,tasks,fade,closeText))){result=95;break;}checks++;continue;
        }
        if(!strcmp(line,"co cold-verify\n")) {
            if(!co.cold||!co_phase(core)){result=96;break;}
            struct CoSnapshot current={0};result=co_read(core,&current);if(result)break;co_dump(&current,"current");
            if(system("python3 STATE_VALIDATOR cold")){result=96;break;}checks++;continue;
        }
'''.replace('STATE_VALIDATOR',str(ROOT/'scripts/floor1/continuous-opening-state.py'))
    allow=r'''        if(strncmp(line,"phase ",6)&&strncmp(line,"co ",3)&&strncmp(line,"step ",5)&&strncmp(line,"engage ",7)&&strncmp(line,"pilot ",6)&&strncmp(line,"expect ",7)&&strncmp(line,"item ",5)&&strncmp(line,"flag ",5)&&strncmp(line,"uses ",5)&&strncmp(line,"pages ",6)&&strncmp(line,"wait-task ",10)&&strncmp(line,"dialog ",7)&&strncmp(line,"measure start ",14)&&strcmp(line,"measure stop\n")&&strcmp(line,"ready\n")&&strcmp(line,"return-field\n")&&strcmp(line,"duo healthy\n")&&strcmp(line,"quit\n")){result=97;break;}
'''
    once('        if (!strcmp(line,"quit\\n")) break;',allow+commands+'        if (!strcmp(line,"quit\\n")) break;')
    # Field-only inventory/flag/assertion/telemetry is gated before SaveBlock reads.
    once('        unsigned sb=core->busRead32(core,saveptr);',r'''
        if(!co_phase(core)){if(strncmp(line,"step ",5)){result=80;break;}continue;}
        unsigned sb=core->busRead32(core,saveptr);''')
    needle='            unsigned sb=core->busRead32(core,saveptr), obj=objects+core->busRead8(core,avatar+5)*0x24;'
    assert code.count(needle)==2 # measure-start and actual motion sample
    code=code.replace(needle,'            if(!co_phase(core)){result=80;break;}\n'+needle)
    once('                if (measuring) {','                if (measuring) {\n                    if(!co_phase(core)){measured++;motion=0;continue;}')
    # Prepared rescue interfaces are unreachable; no policy/resource injection.
    code=code.replace('core->runFrame(core);','co_run(core,pixels,width,height);')
    code=code.replace('c->runFrame(c);co.frames++;co.phaseFrames++;','c->runFrame(c);co.frames++;co.phaseFrames++;co_capture_absolute=co.frames;')
    once("    fputc('\\n', stderr);","    fputc('\\n', stderr);\n    exit(98); // First mGBA ERROR/FATAL stops, never continues.")
    once('    if (ferror(stdin)) result=15;',r'''
    if(result)co_stop(result,pixels,width,height);
    if((co.cold&&(!co.continueSeen||co.attempts))||(!co.cold&&(!co.newSeen||phaseSeq!=18||co.attempts!=4)))co_stop(99,pixels,width,height);
    if(co.motion&&fclose(co.motion))return 84;
    if(fclose(co.trace)||fclose(co.index)||fclose(co.battleTrace))return 84;
    printf("CONTINUOUS frames=%u valid=%u deferred=%u attempts=%u per-encounter=%u,%u,%u,%u\n",co.frames,co.valid,co.deferred,co.attempts,co.encounterFrames[0],co.encounterFrames[1],co.encounterFrames[2],co.encounterFrames[3]);
    if (ferror(stdin)) result=15;''')
    code=code.replace(r'\\n',r'\n').replace('static unsigned walk_flags_equal','static inline unsigned walk_flags_equal')
    assert code.count('->runFrame(')==1 and code.count('core->reset(')==1
    assert 'ordinary_initial' not in code and 'PatrolGuard' not in code and 'busWrite' not in code and 'loadState' not in code
    return code,base
