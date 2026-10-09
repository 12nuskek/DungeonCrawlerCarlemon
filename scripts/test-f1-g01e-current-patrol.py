#!/usr/bin/env python3
"""One fixed current-candidate patrol validation; no historical pass transfer or retry."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, json, os, re, shlex, shutil, subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]
IDENTITIES = {
    'rom': 'b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a',
    'save': 'ea719ffb76f510eabac88cbd345c87d7e21ce009dde0bfca9418ca0a1d3babc8',
    'route': '008761831f2c3ab45e91d9b1ab3304aec76a5202ff43aac4ce60695c2a68d3be',
    'observer': '897d1d698ea33aee7d7bcf6cd77475dc1a8b6ae562c92376103fdef6ef7c5e1c',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def replace_once(code, old, new):
    assert code.count(old) == 1, ('instrumentation anchor', old[:80], code.count(old))
    return code.replace(old, new)

p = argparse.ArgumentParser()
p.add_argument('--retained', type=Path, required=True, help='Preserved private route/observer inputs only')
p.add_argument('--build',type=Path,required=True,help='Verified current isolated build/symbol inputs')
p.add_argument('--original-save', type=Path, required=True)
p.add_argument('--prepare-only', action='store_true', help='Compile host without emulator/save-copy execution')
a = p.parse_args()
assert not git('status', '--porcelain'), 'Commit verification source before execution'
head = git('rev-parse', 'HEAD')
retained = a.retained.resolve()
build=a.build.resolve()
compiled=(build/'tested-commit.txt').read_text().strip()
assert compiled=='c643f01c11ec68119b0347b107ee20115131debc'
subprocess.run(['git','diff','--quiet',compiled,head,'--','engine'],cwd=ROOT,check=True)
engine=build/'source/engine'
diag = retained / 'guard-diagnosis-a9buq1t_/howler-first'
files = dict(rom=engine / 'pokeemerald.gba', save=a.original_save.resolve(), route=diag / 'input.route', observer=retained / 'ordinary-24wjwxed/observer.c')
for name, path in files.items(): assert sha(path) == IDENTITIES[name], ('identity', name)
parent = ROOT / 'artifacts/floor1/current-patrol'
subprocess.run(['python3',str(ROOT/'scripts/test-potion-menu-readiness.py')],check=True)
parent.mkdir(parents=True, exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='prepare-' if a.prepare_only else 'runtime-', dir=parent))
print('Evidence:', out, flush=True)
# Claim the one actual execution before constructing the host. A failure never permits a retry.
if not a.prepare_only:
    with (parent / 'one-current-execution-claimed.json').open('x') as f:
        json.dump(dict(runner=head, output=str(out), identities=IDENTITIES), f, indent=2)
sym = out / 'game.sym'
with sym.open('w') as f:
    subprocess.run(['arm-none-eabi-nm', '--defined-only', str(engine / 'pokeemerald.elf')], stdout=f, check=True)
with sym.open('a') as f:
    subprocess.run(['python3', str(ROOT / 'scripts/battle-input-symbols.py'), str(engine)], stdout=f, check=True)
code = files['observer'].read_text()
# Remove the previously denied private dump capability entirely; retain all normal controllers.
begin = code.index('        if (!strcmp(line,"snapshot\\n")) {')
end = code.index('        if (!strncmp(line,"measure start ",14)) {', begin)
code = code[:begin] + code[end:]
assert not any(x in code for x in ['STATE {', 'encryption_key', 'busWrite'])
code = replace_once(code, 'int main(int argc, char **argv)', r'''
static unsigned owned_potions(struct mCore *core, unsigned pockets, unsigned save2ptr)
{
    unsigned quantity=0, key=core->busRead16(core,core->busRead32(core,save2ptr)+0xAC);
    for (unsigned p=0;p<5;p++) {
        unsigned slots=core->busRead32(core,pockets+8*p), capacity=core->busRead8(core,pockets+8*p+4);
        for (unsigned i=0;i<capacity;i++)
            if (core->busRead16(core,slots+4*i)==13)
                quantity+=core->busRead16(core,slots+4*i+2)^key;
    }
    return quantity;
}
''' + (ROOT/'scripts/floor1/potion-menu-readiness.h').read_text() + r'''
int main(int argc, char **argv)''')
code = replace_once(code, '    char type, symbol[128];', '    unsigned tasks=0, partyMenu=0, bagInput=0, contextInput=0, partyInput=0, restoredText=0, closeText=0, battleMain=0, selectedItem=0;\n    char type, symbol[128];')
code = replace_once(code, '        if (!strcmp(symbol,"CB2_Overworld")) overworld=addr;', '''        if (!strcmp(symbol,"gTasks")) tasks=addr;
        if (!strcmp(symbol,"gPartyMenu")) partyMenu=addr;
        if (!strcmp(symbol,"Task_BagMenu_HandleInput")) bagInput=addr;
        if (!strcmp(symbol,"Task_ItemContext_SingleRow")) contextInput=addr;
        if (!strcmp(symbol,"Task_HandleChooseMonInput")) partyInput=addr;
        if (!strcmp(symbol,"Task_DisplayHPRestoredMessage")) restoredText=addr;
        if (!strcmp(symbol,"Task_ClosePartyMenuAfterText")) closeText=addr;
        if (!strcmp(symbol,"BattleMainCB2")) battleMain=addr;
        if (!strcmp(symbol,"gSpecialVar_ItemId")) selectedItem=addr;
        if (!strcmp(symbol,"CB2_Overworld")) overworld=addr;''')
code = replace_once(code, '    int result=0;\n    unsigned measuring=', '    int result=0;\n    unsigned potionStage=0, pendingContext=0, pendingRecipient=0, healed=0, noBattleMonitoring=0, sawBattle=0, xpAnchor[6]={0}, haveXp=0;\n    unsigned measuring=')
point = '        if (!strcmp(line,"quit\\n")) break;'
code = replace_once(code, point, point + r'''
        if (!strcmp(line,"xp remember\n") || !strcmp(line,"xp same\n")) {
            unsigned now[]={core->busRead8(core,party+0x54),growth_word(core,party,1),growth_word(core,party,0)>>16,
                core->busRead8(core,party+100+0x54),growth_word(core,party+100,1),growth_word(core,party+100,0)>>16};
            if (!strcmp(line,"xp remember\n")) {
                memcpy(xpAnchor,now,sizeof now);haveXp=1;
                printf("XP anchor %u %u %u %u %u %u\n",now[0],now[1],now[2],now[3],now[4],now[5]);
            } else {
                if (!haveXp || memcmp(xpAnchor,now,sizeof now)) {result=45;fprintf(stderr,"XP/level/equipment changed after victory\n");break;}
                checks++;printf("PASS unchanged XP level equipment\n");
            }
            continue;
        }
        if (!strcmp(line,"no-battle start\n")) {noBattleMonitoring=1;sawBattle=0;continue;}
        if (!strcmp(line,"no-battle end\n")) {
            if (!noBattleMonitoring || sawBattle) {result=45;fprintf(stderr,"Repeated encounter restarted a battle\n");break;}
            noBattleMonitoring=0;checks++;printf("PASS repeat encounter no battle\n");continue;
        }
''')
code = replace_once(code, '            char policy[32], limitText[32]; unsigned limit;', '''            char policy[32], limitText[32]; unsigned limit;
            unsigned rescue=!strncmp(line,"pilot potion-once ",18);
            if (rescue) {
                if (potionStage || !tasks || !partyMenu || !bagInput || !contextInput || !partyInput || !restoredText || !closeText || !battleMain || !selectedItem) {result=44;break;}
                strcpy(line,"pilot offensive 36000\\n");
            }''')

# A missing live Carl action at the prescribed turn is divergence, not permission to continue.
code = replace_once(code, '                unsigned turn=core->busRead8(core,results+0x13);', r'''
                unsigned turn=core->busRead8(core,results+0x13);
                if (rescue && potionStage==0 && (turn>4 || (turn==4 && !chp))) {
                    capture("decision-blocked.ppm",pixels,width,height);
                    printf("CANDIDATE blocked decision frame=%u turn=%u CarlHP=%u DonutHP=%u\n",total,turn,chp,dhp);
                    result=44;fprintf(stderr,"Prespecified live Carl turn4 action unavailable; STOP\n");break;
                }
''')
anchor = '                    if (actor!=UINT_MAX)\n                        printf("pilot frame=%u turn=%u actor=%u menu=%u selection=%u key=%u\\n",total,turn,actor,menu,selection,key);'
code = replace_once(code, anchor, r'''
                    if (rescue && potionStage==0 && actor==0 && menu==1 && turn==4) {

                        result=capture("decision-observed.ppm",pixels,width,height);if (result) break;
                        printf("CANDIDATE decision frame=%u trainer=%u turn=%u HP=%u/%u,%u/%u PP=%u,%u,%u,%u foesHP=%u,%u owned=%u cursor=%u\n",
                            total,core->busRead16(core,trainer),turn,chp,core->busRead16(core,party+0x58),dhp,core->busRead16(core,party+100+0x58),
                            party_pp(core,party,0),party_pp(core,party,1),party_pp(core,party+100,0),party_pp(core,party+100,1),
                            core->busRead16(core,mons+0x58+0x28),core->busRead16(core,mons+3*0x58+0x28),owned_potions(core,pockets,save2ptr),core->busRead8(core,actionCursor));
                        if (core->busRead16(core,trainer)!=856 || chp!=3 || dhp!=30
                            || core->busRead16(core,party+0x58)!=36 || core->busRead16(core,party+100+0x58)!=30
                            || party_pp(core,party,0)!=4 || party_pp(core,party,1)!=40
                            || party_pp(core,party+100,0)!=0 || party_pp(core,party+100,1)!=38
                            || core->busRead16(core,mons+0x58+0x28)!=0 || core->busRead16(core,mons+3*0x58+0x28)!=18
                            || core->busRead8(core,actionCursor)!=0 || owned_potions(core,pockets,save2ptr)!=1) {
                            result=44;fprintf(stderr,"Current decision diverged from prespecified semantic state; STOP\n");break;
                        }
                        result=capture("decision-before.ppm",pixels,width,height);if (result) break;
                        checks++;printf("PASS current Potion decision frame=%u turn=4 CarlHP=3 DonutHP=30 PP=4,40,0,38 foesHP=0,18 owned=1\n",total);
                        potionStage=1;
                    }

                    if (rescue && potionStage>0 && potionStage<7) {
                        actor=UINT_MAX;key=0;
                        if (potionStage==2 && pendingContext) {
                            unsigned next=acknowledged_stage(potionStage,pendingContext,
                                menu_ready(core,tasks,fade,contextInput),0,core->busRead16(core,selectedItem),0);
                            if (next==3) {potionStage=next;printf("PASS actual Potion context acknowledged frame=%u\n",total);checks++;}
                        }
                        if (potionStage==3 && pendingRecipient) {
                            unsigned next=acknowledged_stage(potionStage,pendingRecipient,0,
                                menu_ready(core,tasks,fade,partyInput),core->busRead16(core,selectedItem),core->busRead8(core,partyMenu+9));
                            if (next==4) {potionStage=next;printf("PASS actual Carl recipient acknowledged frame=%u\n",total);checks++;}
                        }
                        if (potionStage==1 && (core->busRead32(core,controls)&~1u)==inputAction) {
                            unsigned cursor=core->busRead8(core,actionCursor);
                            if (cursor>1) {result=44;fprintf(stderr,"Unexpected Bag action cursor\n");break;}
                            key=cursor==1?1:16;
                            if (cursor==1) potionStage=2;
                        } else if (potionStage==2 && !pendingContext && menu_ready(core,tasks,fade,bagInput)) {
                            if (core->busRead8(core,bag+5)!=0 || core->busRead16(core,bag+8)!=0 || core->busRead16(core,bag+18)!=0
                                || core->busRead16(core,core->busRead32(core,pockets))!=13) {
                                result=44;fprintf(stderr,"Expected first owned Potion in Items pocket\n");break;
                            }
                            result=capture("owned-potion-bag.ppm",pixels,width,height);if (result) break;
                            key=1;pendingContext=1;
                            printf("PASS Bag selection ready fade=0 expected_task=1 frame=%u\n",total);checks++;
                        } else if (potionStage==3 && !pendingRecipient && menu_ready(core,tasks,fade,contextInput)) {
                            if (core->busRead16(core,selectedItem)!=13) {result=44;break;}
                            key=1;pendingRecipient=1;
                        } else if (potionStage==4 && menu_ready(core,tasks,fade,partyInput)) {
                            if (core->busRead8(core,partyMenu+9)!=0 || core->busRead16(core,selectedItem)!=13) {result=44;fprintf(stderr,"Potion recipient is not Carl\n");break;}
                            result=capture("potion-recipient.ppm",pixels,width,height);if (result) break;
                            key=1;potionStage=5;
                        } else if (potionStage==5 || potionStage==6) {
                            key=1;
                            if (potionStage==6 && (core->busRead32(core,mainstate+4)&~1u)==battleMain
                                && (core->busRead32(core,controls+8)&~1u)==inputAction) {
                                if (core->busRead16(core,party+0x56)!=23 || core->busRead16(core,mons+0x28)!=23
                                    || owned_potions(core,pockets,save2ptr)!=0 || party_pp(core,party,0)!=4
                                    || party_pp(core,party,1)!=40 || party_pp(core,party+100,0)!=0 || party_pp(core,party+100,1)!=38) {result=44;fprintf(stderr,"Battle heal/consumption/action PP mismatch\n");break;}
                                result=capture("healed-battle.ppm",pixels,width,height);if (result) break;
                                checks++;printf("PASS Potion battle return HP=23 quantity=0 PP=4,40,0,38\n");
                                potionStage=7; // A is the original Donut Fight selection. Original policy resumes next pulse.
                            }
                        }
                        printf("potion controller frame=%u stage=%u key=%u\n",total,potionStage,key);
                    }
                    if (actor!=UINT_MAX)
                        printf("pilot frame=%u turn=%u actor=%u menu=%u selection=%u key=%u\n",total,turn,actor,menu,selection,key);
''')
anchor = '                if (result) break;\n                core->setKeys(core,key);'
code = replace_once(code, anchor, r'''
                if (rescue && potionStage==5 && (active_task(core,tasks,restoredText) || active_task(core,tasks,closeText))) {
                    if (chp!=23 || dhp!=30 || owned_potions(core,pockets,save2ptr)!=0
                        || party_pp(core,party,0)!=4 || party_pp(core,party,1)!=40
                        || party_pp(core,party+100,0)!=0 || party_pp(core,party+100,1)!=38) {result=44;fprintf(stderr,"Potion did not heal20HP/consume exactly one/preserve PP\n");break;}
                    result=capture("healed-party.ppm",pixels,width,height);if (result) break;
                    checks++;printf("PASS Potion healed20HP Carl=3->23 inventory=1->0 PP unchanged\n");
                    healed=1;potionStage=6;
                }
                if (result) break;
                core->setKeys(core,key);''')
code = replace_once(code, '            checks++;\n            continue;\n        }\n        if (sscanf(line,"step', '''            if (rescue && (!healed || potionStage!=7 || core->busRead8(core,outcome)!=1)) {result=44;fprintf(stderr,"Potion hypothesis did not yield verified victory\\n");break;}
            checks++;
            continue;
        }
        if (sscanf(line,"step''')
# Read-only battle latch adds no frames and covers repeated NPC interaction.
code = code.replace('core->runFrame(core);', 'core->runFrame(core); if (noBattleMonitoring && (core->busRead8(core,mainstate+0x439)&2)) sawBattle=1;')
assert not any(x in code for x in ['STATE {', 'encryption_key', 'busWrite', 'snapshot'])
(out / 'observer.c').write_text(code)
with (out / 'host-build.log').open('w') as f:
    subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', *shlex.split(os.environ.get('DCC_TEST_CFLAGS','')), str(out/'observer.c'), *shlex.split(os.environ.get('DCC_TEST_LDFLAGS','')), '-lmgba', '-o', str(out/'playtest')], stdout=f, stderr=subprocess.STDOUT, check=True)
if a.prepare_only:
    print('PASS static host compilation; no emulator or save copy', flush=True)
    raise SystemExit(0)
lines = files['route'].read_text().splitlines()
assert lines.count('pilot offensive 36000')==1 and lines.count('snapshot')==1
lines.remove('snapshot')
# Extra zero-frame initial ownership assertion, no input change.
lines.insert(lines.index('flag 2137 0')+1,'item 13 1')
i=lines.index('pilot offensive 36000')
assert 'flag 2137 1' in lines[:i]
lines[i]='pilot potion-once 36000'
# Capture filenames and zero-frame read-only checks never retime the preserved inputs.
lines[i+1]='step 600 0 guard-result.ppm'
j=lines.index('flag 2136 1', i)
lines[j+1:j+1]=['flag 2137 1','item 13 0','xp remember']
k=lines.index('flag 2136 1', j+4)
lines[k:k]=['xp same']
# Retain every original Save input. Add one ordinary resolved-NPC interaction before Save.
k=lines.index('step 1 8 -', k)
repeat=['no-battle start','step 1 1 -','step 400 0 guard-resolved.ppm','dialog 3600','ready','step 40 0 -','expect 35 0 37 31 7','flag 2136 1','flag 2137 1','item 13 0','xp same','no-battle end']
lines[k:k]=repeat
lines.insert(lines.index('quit'), 'xp same')
original_log=(diag/'replay.log').read_text()
old_prefix=[s for s in original_log.splitlines() if s.startswith('pilot frame=') and int(re.search(r'frame=(\d+)',s)[1])<24673]
summary=[]
def run(name, save, commands):
    d=out/name;d.mkdir();(d/'input.route').write_text('\n'.join(commands)+'\n')
    with (d/'input.route').open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
        result=subprocess.run([str(out/'playtest'),str(files['rom']),str(save),str(sym)],cwd=d,stdin=inp,stdout=log,stderr=err)
    for image in d.glob('*.ppm'):
        frame=Image.open(image);assert frame.size==(240,160);frame.save(image.with_suffix('.png'))
    log=(d/'replay.log').read_text()
    verdict=dict(route=name,exit=result.returncode,errors_bytes=(d/'errors.log').stat().st_size)
    if name=='howler-first-potion':
        observed=re.search(r'CANDIDATE decision frame=(\d+)',log)
        cutoff=int(observed[1]) if observed else 2**32
        prefix=[s for s in log.splitlines() if s.startswith('pilot frame=') and int(re.search(r'frame=(\d+)',s)[1])<cutoff]
        verdict['decision_observed']=bool(observed)
        verdict.update(current_prefix_actions=len(prefix), historical_prefix_actions=len(old_prefix), historical_timestamps_equal=prefix==old_prefix, historical_normalized_prefix_equal=[re.sub(r'frame=\d+ ', '',x) for x in prefix]==[re.sub(r'frame=\d+ ', '',x) for x in old_prefix])
    summary.append(verdict);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert result.returncode==0 and not verdict['errors_bytes'], ('STOP; no retry',name,d,result.returncode)
    # Historical prefix is descriptive only; current semantic decision/readiness/behavior assertions govern.
    verdict['assertions']=int(re.search(r'result=0 assertions=(\d+)\n$',log)[1])
    print('PASS',name,verdict['assertions'],flush=True)
    return log
save=out/'ordinary-copy.sav';shutil.copyfile(files['save'],save)
log=run('howler-first-potion',save,lines)
anchor=re.search(r'^XP anchor (\d+ \d+ \d+ \d+ \d+ \d+)$',log,re.M)[1]
cold_save=out/'cold-copy.sav';shutil.copyfile(save,cold_save);cold_before=sha(cold_save)
boot=files['route'].read_text().splitlines()[:9]
cold=boot+['ready','expect 35 0 37 31 7','flag 2136 1','flag 2137 1','flag 49 0','item 13 0','duo healthy','uses 8 40 2 40','growth '+anchor,'xp remember']+repeat+['growth '+anchor,'quit']
run('cold-potion-victories',cold_save,cold)
assert sha(files['save'])==IDENTITIES['save'] and sha(cold_save)==cold_before
assert sha(files['rom'])==IDENTITIES['rom']
(out/'summary.json').write_text(json.dumps(dict(runner=head,compiled=compiled,rom=IDENTITIES['rom'],sessions=summary,original_save_unchanged=True,cold_save_unchanged=True,game_changes=False,current_candidate_patrol_gate='verified_scoped',full_route_gate='pending'),indent=2)+'\n')
print('PASS one current-candidate patrol intervention and cold verification; full route gate pending',flush=True)
