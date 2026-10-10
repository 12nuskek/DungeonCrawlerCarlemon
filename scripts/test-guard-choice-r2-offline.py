#!/usr/bin/env python3
"""Comprehensive inert admission, no emulator initialization or gameplay claim."""
from pathlib import Path
import argparse,hashlib,importlib.util,itertools,json,os,shutil,stat,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--artifacts',type=Path,required=True);args=parser.parse_args();d=args.artifacts;d.mkdir()
    runner=module('gc_runner',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
    host=module('gc_host',ROOT/'scripts/floor1/guard-choice-r2-host.py');route=module('gc_route',ROOT/'scripts/floor1/guard-choice-route.py')
    model=module('gc_state',ROOT/'scripts/floor1/guard-choice-r2-state.py');medicine=model.medicine
    oldtest=module('gc_retained_fixtures',ROOT/'scripts/test-continuous-opening-offline.py')
    code,base=host.generate(git);plans=route.routes()
    assert [x[10:] for x in plans['opening'].splitlines() if x.startswith('phase end ')]==host.NAMES
    assert plans['opening'].count('pilot offensive 36000')==plans['opening'].count('pilot donut-heal 36000')==1
    assert all(x not in plans['opening'] for x in ('phase begin potion','phase begin howler','phase begin boss','phase begin stairs','item 13 1'))
    assert plans['opening'].count('co save-ready')==plans['opening'].count('co save-success')==1
    assert 'expect 35 1 4 5 7' in plans['cold'] and 'co start 0' in plans['opening']
    for name,text in plans.items():assert text==(ROOT/f'scripts/contracts/f1-c01-guard-choice-{name}.route').read_text()
    assert code.count('->runFrame(')==code.count('core->reset(')==1 and not any(x in code for x in ('busWrite','loadState','RNG_SEED'))
    (d/'observer.c').write_text(code)
    command=['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(runner.TOOL/'usr/include')]
    subprocess.run(command+[str(d/'observer.c'),'-L'+str(runner.TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(d/'observer')],check=True)
    (d/'inert-observer.c').write_text(code.replace('int main(int argc','int continuous_host_main(int argc'))
    inert=(ROOT/'scripts/floor1/guard-choice-r2-inert.c').read_text().replace('OBSERVER',str(d/'inert-observer.c'))
    (d/'inert.c').write_text(inert)
    subprocess.run(command+['-fsanitize=undefined',str(d/'inert.c'),'-L'+str(runner.TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(d/'inert')],check=True)
    extra=module('gc_full_native',ROOT/'scripts/floor1/guard-choice-offline.py')
    (d/'fixture.bin').write_bytes(extra.pack(oldtest.fixtures(model)))
    subprocess.run([str(d/'inert')],cwd=d,env=runner.ENV,check=True)
    subprocess.run([str(d/'inert'),'--medicine'],cwd=d,env=runner.ENV,check=True)
    comprehensive=extra.run(model,d,d/'inert',runner.ENV,host.NAMES,host.KINDS,plans['opening'])
    vectors=[]
    for alive,cm,dm,n,s,b in itertools.product((False,True),(33,36),(28,),range(3),(0,1,8),(0,40)):
        for c,dh in itertools.product(range(cm+1),range(dm+1)):vectors.append((c,cm,dh,dm,alive,n,s,b))
    (d/'choice-vectors.txt').write_text(''.join(' '.join(str(int(x)) for x in v)+'\n' for v in vectors))
    outputs=list(map(int,subprocess.check_output([str(d/'inert'),'--choices',str(d/'choice-vectors.txt')],env=runner.ENV,text=True).splitlines()))
    assert outputs==[medicine.choice(*v) for v in vectors]
    assert medicine.choice(22,33,28,28,True,2,6,40)==1 and min(22+20,33)-22==11
    for v in ((37,36,28,28,True,2,8,40),(28,33,29,28,True,2,8,40),(28,33,28,28,True,3,8,40),(28,33,28,28,True,2,9,40)):
        try:medicine.choice(*v)
        except AssertionError:pass
        else:raise AssertionError('corrupt policy input accepted')
    logical=bytearray(1272);struct.pack_into('<HHHH',logical,0xd0,13,2,378,2)
    removal_checks=0
    for qty in (2,1):
        struct.pack_into('<HH',logical,0xd0,13,qty);(d/'owned.bin').write_bytes(logical)
        subprocess.run([str(d/'inert'),'--remove',str(d/'owned.bin'),str(d/'removed.bin')],env=runner.ENV,check=True)
        native=medicine.remove(bytes(logical));assert native==(d/'removed.bin').read_bytes()
        assert struct.unpack_from('<HH',native,0xd0)==(13,1) if qty==2 else struct.unpack_from('<HH',native,0xd0)==(0,0)
        assert native[0xd4:0xd8]==bytes(logical[0xd4:0xd8]);(d/'owned.bin').write_bytes(native)
        subprocess.run([str(d/'inert'),'--compact',str(d/'owned.bin'),str(d/'compacted.bin')],env=runner.ENV,check=True)
        assert medicine.compact(native)==(d/'compacted.bin').read_bytes();removal_checks+=2
    # Every complete byte remains observed, including unused slots and Bag holes.
    for raw in (bytes((0x01,0x23,0x45)),bytes((0x10,0x23,0x45))):
        order=medicine.order(raw);party=oldtest.fixtures(model)['party'];assert medicine.to_field(medicine.to_ui(party,order),order)==party
    for raw in (b'\x00\x23\x45',b'\x16\x23\x45',b'\x23\x01\x45'):
        try:medicine.order(raw)
        except AssertionError:pass
        else:raise AssertionError('invalid party mapping accepted')
    print("PASS inherited full native phase/resource/Save guards",json.dumps(comprehensive,sort_keys=True),flush=True)
    good='MEDICINE_HEAL absolute=10 turn=2 rest\nMEDICINE_ACK absolute=11 turn=2 use=1 WAIT=1 owner=2 fresh_A=1 full_state_exact=1\nMEDICINE_RETURN absolute=40 turn=2 uses=1 full_state_exact=1 ack_frame=11 released=1 printer_done=1 print_task_destroyed=1 party_fade=1 field_order=1 exit=1 setup=1 reshow_entry=1 reshow=1\n'
    assert model.acknowledgement_audit(good,1)['single_fresh_A_each']
    negatives=[good.replace('WAIT=1','WAIT=0'),good.replace('owner=2','owner=0'),good.replace('fresh_A=1','fresh_A=0'),good.replace('ack_frame=11','ack_frame=12'),good.replace('absolute=11','absolute=9'),good.replace('released=1','released=0'),good.replace('printer_done=1','printer_done=0'),good.replace('print_task_destroyed=1','print_task_destroyed=0'),good.replace('party_fade=1','party_fade=0'),good.replace('reshow=1','reshow=0'),good+good.splitlines()[1]+'\n']
    for bad in negatives:
        try:model.acknowledgement_audit(bad,1)
        except AssertionError:pass
        else:raise AssertionError('invalid acknowledgement receipt accepted')
    native=runner.abi(d);binding=runner.binding_table(code,d);game=runner.verify_game()
    # Native source chain: exact tree/build binding plus substantive medicine assertions.
    item=(ROOT/'engine/src/item.c').read_text();party=(ROOT/'engine/src/party_menu.c').read_text();pokemon=(ROOT/'engine/src/pokemon.c').read_text();script=(ROOT/'engine/data/battle_scripts_2.s').read_text()
    start=item.index('bool8 RemoveBagItem(');end=item.index('\n}',start)+2
    assert 'CompactItemsInBagPocket' not in item[start:end]
    for token in ('RemoveBagItem(item, 1);','ResetHPTaskData(taskId, 0, hp);','sPartyMenuInternal->exitCallback = CB2_SetUpExitToBattleScreen;','UpdatePartyToFieldOrder();','GetPartyIdFromBattleSlot(partyMonIndex)'):
        assert token in party
    assert 'gBattleMons[battler].hp = dataUnsigned;' in pokemon and 'if (gBattlerPartyIndexes[i] == partyIndex)' in pokemon
    effect=(ROOT/'engine/src/data/pokemon/item_effects.h').read_text().split('const u8 gItemEffect_Potion[7] = {',1)[1].split('};',1)[0]
    assert effect.strip()=='[4] = ITEM4_HEAL_HP,\n    [6] = 20, // Amount of HP to recover'
    assert '.battleUseFunc = ItemUseInBattle_Medicine,' in (ROOT/'engine/src/data/items.h').read_text()
    assert 'gItemUseCB = ItemUseCB_Medicine;' in (ROOT/'engine/src/item_use.c').read_text()
    assert script.split('BattleScript_PlayerUsesItem::')[1].split('BattleScript_OpponentUsesHealItem::')[0].strip()=='moveendcase MOVEEND_MIRROR_MOVE\n\tend'
    text=(ROOT/'engine/src/text.c').read_text();helpers=(ROOT/'engine/src/menu_helpers.c').read_text();reshow=(ROOT/'engine/src/reshow_battle_screen.c').read_text()
    assert 'WIN_MSG = PARTY_SIZE,' in party and '#define WINDOWS_MAX  32' in (ROOT/'engine/include/window.h').read_text()
    assert 'CreateTask(Task_PrintAndWaitForText, 1)' in party and 'RunTextPrintersRetIsActive(WIN_MSG) != TRUE' in party
    assert 'gTasks[taskId].func = Task_ClosePartyMenuAfterText;' in party and 'gTasks[taskId].func = Task_ClosePartyMenuAndSetCB2;' in party
    assert 'SetMainCallback2(CB2_SetUpReshowBattleScreenAfterMenu);' in party
    assert 'SetMainCallback2(ReshowBattleScreenAfterMenu);' in (ROOT/'engine/src/battle_controller_player.c').read_text()
    assert 'SetMainCallback2(CB2_ReshowBattleScreenAfterMenu);' in reshow and 'SetMainCallback2(BattleMainCB2);' in reshow
    assert 'if (JOY_NEW(A_BUTTON | B_BUTTON))' in text and 'sTextPrinters[i].active = FALSE;' in text
    assert 'textPrinter->state = RENDER_STATE_WAIT;' in text and 'RunTextPrinters();' in helpers
    assert 'point(s).{PAUSE_UNTIL_PRESS}' in (ROOT/'engine/src/strings.c').read_text()
    prior=module('gc_original_storage',ROOT/'scripts/test-f1-c01-guard-choice-r1.py')
    assert runner.storage()==prior.storage() and runner.reservation()==prior.reservation()==10000408128
    # Only read retained STOP104 bytes; never restore them into a runtime process.
    retained=Path('/workspace/scratch/c01-guard-choice-r1-20261010/opening')
    healed=retained/'medicine-01-healed-state.bin';terminal=retained/'first-invalid-or-partial-medicine-state.bin'
    assert healed.read_bytes()==terminal.read_bytes() and len(healed.read_bytes())==3324
    retained_heal={'healed_snapshot_SHA256':runner.sha(healed),'terminal_snapshot_SHA256':runner.sha(terminal),'full_3324_bytes_equal':True}
    old=json.loads(Path('/workspace/scratch/c01a-journal-admission-r3-20261010/freeze.json').read_text());tools=old['tool_files']
    for path,h in tools.items():assert runner.sha(path)==h
    assert runner.sha(runner.TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5')=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
    os.chmod(d/'observer',0o700);fs=(d/'observer').stat();identity={'SHA256':runner.sha(d/'observer'),'owner_uid':fs.st_uid,'mode':stat.S_IMODE(fs.st_mode),'device':fs.st_dev,'inode':fs.st_ino}
    checker=module('gc_exec',ROOT/'scripts/floor1/c01a-prefix-execfile.py');checker.verify_executable(d/'observer',identity)
    for k,v in [('SHA256','0'*64),('owner_uid',fs.st_uid+1),('mode',0o755),('inode',fs.st_ino+1)]:
        try:checker.verify_executable(d/'observer',dict(identity,**{k:v}))
        except AssertionError:pass
        else:raise AssertionError(('unsafe executable',k))
    (d/'observer-symlink').symlink_to(d/'observer')
    try:checker.verify_executable(d/'observer-symlink',identity)
    except AssertionError:pass
    else:raise AssertionError('symlink executable admitted')
    reservation=runner.reservation();free=shutil.disk_usage(d).free
    receipt={'PASS':True,'full_aggregate':True,'gameplay_processes':0,'generated_host_SHA256':runner.sha(d/'observer.c'),'observer_executable_SHA256':runner.sha(d/'observer'),
      'inherited_generated_base_SHA256':base,'dependencies':runner.dependencies(),'native_ABI':native,'binding_count':len(binding),'source_verification':game,
      'retained_STOP104_read_only':retained_heal,'native_complete_state':comprehensive,'medicine_policy_vectors':len(vectors),'native_removal_compaction_cases':removal_checks,
      'medicine_UI_animation_mock_cases':8,'stateful_successive_Potion_uses':2,'native_acknowledgement_lifecycle':True,'medicine_full_snapshot_byte_corruptions':10*3288*2,'medicine_snapshot_corruptions_by_stage':{'native_HP_animation':32880,'native_WAIT':32880},'readiness_or_lifecycle_negative_cases':210,'premature_printing_no_input_cases':10,'duplicate_ack_no_input_cases':10,'executable_negatives':5,'acknowledgement_audit_negatives':len(negatives),'storage':runner.storage(),'reservation_bytes':reservation,'available_bytes':free,'runtime_storage_admitted':free>=reservation,'storage_shortfall_bytes':max(0,reservation-free),
      'artifacts':{p.name:runner.sha(p) for p in d.iterdir() if p.is_file() and not p.is_symlink()}}
    runner.write(d/'admission-receipt.json',receipt);print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
