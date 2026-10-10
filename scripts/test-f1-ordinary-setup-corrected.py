#!/usr/bin/env python3
"""Reviewed zero-frame observation relocation. Reuse actual trial Save/host; no retry."""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
BASE='030e4d19b1bdc928237f3596041379a5f279dacf'
TRIAL='f866e7c61a7bb91333822d435a3ad9f395ec62839bf5c4dc7c939b15b48c8281'
PRIOR_ID='e2447f13519b6352f907559c3c57556a2f387ceaf765660503cbcb344125ec05'
STAGES=['setup','patrol','cold']
SCOPED=['scripts/test-f1-ordinary-setup-corrected.py','scripts/test-f1-ordinary-recovery.py',
        'scripts/test-ordinary-setup-relocation.py',
        'scripts/floor1','scripts/contracts','docs/floor1/ordinary-setup-corrected-20261010-contract.md']


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


shared=module('ordinary_shared',ROOT/'scripts/test-f1-ordinary-recovery.py')
sha=shared.sha
git=shared.git


def corrected_route(text,code):
    before=text.splitlines()
    old=['item 13 1','uses 3 40 0 37','return-field','ready']
    new=['return-field','ready','item 13 1','uses 3 40 0 37']
    positions=[i for i in range(len(before)-3) if before[i:i+4]==old]
    assert len(positions)==1,'Exactly one reviewed assertion group'
    index=positions[0];after=before[:index]+new+before[index+4:]
    observed={'item 13 1','uses 3 40 0 37'}
    assert [x for x in before if x not in observed]==[x for x in after if x not in observed]
    assert all(before.count(x)==after.count(x)>=1 for x in observed)
    # Inspect each actual compiled host command block; neither advances a frame/input.
    for command in ['item','uses']:
        handlers=list(re.finditer(r'(?m)^\s*if\s*\(!strncmp\(line,"'+command+r' ",5\)[^\n]*\{',code))
        assert len(handlers)==1,('actual command handler',command)
        start=handlers[0].end()-1;depth=1;end=start+1
        while depth:
            depth+=(code[end]=='{')-(code[end]=='}');end+=1
        block=code[start:end]
        assert 'runFrame' not in block and 'setKeys' not in block,command
    return '\n'.join(after)+'\n',dict(relocated_lines_1_based=[index+1,index+2],
        identical_all_other_commands=True,identical_frame_and_input_commands=True,
        both_exact_assertions_retained=True,compiled_handlers_advance_no_frames_or_inputs=True)


def verify_artifacts(build,out,identity):
    source=build/'source';engine=source/'engine'
    for path,key in [(engine/'pokeemerald.gba','ROM_SHA256'),(engine/'pokeemerald.elf','ELF_SHA256'),
                     (out/'observer.c','host_SHA256'),(out/'playtest','binary_SHA256'),(out/'game.sym','symbols_SHA256'),
                     (out/'source-manifest.json','source_manifest_SHA256')]:
        assert sha(path)==identity[key],('frozen identity',path)
    for path,record in json.loads((out/'source-manifest.json').read_text()).items():
        assert sha(source/path)==record['archive_SHA256'],('frozen archived source',path)
    assert sha(Path(shutil.which('ffmpeg')))==identity['ffmpeg_SHA256']
    assert sha(Path(identity['mgba']['path']))==identity['mgba']['SHA256']
    for record in identity['mgba']['resolved_dependency_hashes']:
        assert sha(Path(record['path']))==record['SHA256'],('native dependency',record['path'])


def prepare(build,prior,out):
    assert not out.exists(),'Separate empty claim only'
    out.mkdir(parents=True)
    with (out/'prepare-claim.json').open('x') as f:
        json.dump(dict(source=git('rev-parse','HEAD'),base=BASE,output=str(out),prior=str(prior),
                       preparation_attempt=3,prior_ordinary_processes=2,next_ordinary_process=3,
                       next_setup_attempt=2,execution_limit=1),f,indent=2)
    assert sha(prior/'fresh.sav')==TRIAL and sha(prior/'identity.json')==PRIOR_ID
    history=json.loads((prior/'summary.json').read_text());failure=json.loads((prior/'STOP.json').read_text())
    assert [x['stage'] for x in history]==['fresh','seed'] and [x['exit'] for x in history]==[0,40]
    assert failure['stage']=='seed' and failure['exit']==40 and history[0]['native_manual_Save_exact']
    assert failure['input_Save_SHA256']==failure['output_Save_SHA256']==TRIAL
    assert 'absolute_frame=3040' in (prior/'seed/errors.log').read_text()
    identity=json.loads((prior/'identity.json').read_text());verify_artifacts(build,prior,identity)
    before=(prior/'seed.route').read_text();assert sha(prior/'seed.route')==identity['routes']['seed']
    route,proof=corrected_route(before,(prior/'observer.c').read_text())
    for name in ['observer.c','playtest','game.sym','source-manifest.json']:shutil.copy2(prior/name,out/name)
    shutil.copyfile(prior/'fresh.sav',out/'trial.sav');assert sha(out/'trial.sav')==TRIAL
    (out/'setup.route').write_text(route)
    for stage in ('patrol','cold'):shutil.copyfile(prior/(stage+'.route'),out/(stage+'.route'))
    (out/'prior-history.json').write_text(json.dumps(dict(summary=history,STOP=failure),indent=2)+'\n')
    identity.update(publication_base=BASE,claim_source=git('rev-parse','HEAD'),prior_identity_SHA256=PRIOR_ID,
        trial_Save_SHA256=TRIAL,prior_STOP_SHA256=sha(prior/'STOP.json'),prior_summary_SHA256=sha(prior/'summary.json'),
        prior_root=str(prior),prior_ordinary_processes=2,process_ordinals=dict(setup=3,patrol=4,cold=5),
        setup_attempt_ordinal=2,routes={s:sha(out/(s+'.route')) for s in STAGES},
        route_correction_proof=proof,observer_compile_attempts_this_claim=0,game_builds_this_claim=0,
        prepare_claim_SHA256=sha(out/'prepare-claim.json'))
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    print('PASS separate host-free preparation: actual trial Save, unchanged host/build/native identities and zero-frame route relocation verified')


def execute(build,out,stage):
    identity=json.loads((out/'identity.json').read_text());head=git('rev-parse','HEAD')
    assert not (out/'STOP.json').exists(),'First actual failure terminal'
    subprocess.run(['git','diff','--quiet',identity['claim_source'],head,'--',*SCOPED],cwd=ROOT,check=True)
    prior=Path(identity['prior_root'])
    assert sha(prior/'fresh.sav')==TRIAL and sha(prior/'STOP.json')==identity['prior_STOP_SHA256']
    assert sha(prior/'summary.json')==identity['prior_summary_SHA256'] and sha(out/'trial.sav')==TRIAL
    verify_artifacts(build,out,identity)
    assert sha(out/(stage+'.route'))==identity['routes'][stage]
    summaryfile=out/'summary.json';summary=json.loads(summaryfile.read_text()) if summaryfile.exists() else []
    assert [x['stage'] for x in summary]==STAGES[:STAGES.index(stage)]
    assert shutil.disk_usage(out).free>=7000000000
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<13000000000
    d=out/stage;d.mkdir();save=out/(stage+'.sav');assert not save.exists()
    input_save=out/('trial.sav' if stage=='setup' else STAGES[STAGES.index(stage)-1]+'.sav')
    shutil.copyfile(input_save,save);before=sha(save)
    source=build/'source';engine=source/'engine';state=module('corrected_state',source/'scripts/floor1/guard-first-state.py')
    if stage in ('patrol','cold'):state.seed_snapshot(save,d/'expected')
    shutil.copyfile(out/(stage+'.route'),d/'input.route')
    claim=dict(execution_source=head,host_source=identity['host_source'],claim_source=identity['claim_source'],
        stage=stage,ordinary_process_ordinal=identity['process_ordinals'][stage],
        setup_attempt_ordinal=2 if stage=='setup' else None,execution_limit=1,
        identity_SHA256=sha(out/'identity.json'),input_Save_SHA256=before,route_SHA256=sha(d/'input.route'),
        battles=2 if stage=='patrol' else 0,prior_ordinary_processes=2)
    with (d/'execution-claim.json').open('x') as f:json.dump(claim,f,indent=2)
    verdict=dict(claim)
    try:
        with (d/'input.route').open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
            result=subprocess.run([str(out/'playtest'),str(engine/'pokeemerald.gba'),str(save),str(out/'game.sym'),
                'seed' if stage=='setup' else stage],cwd=d,stdin=inp,stdout=log,stderr=err,timeout=600)
        verdict.update(exit=result.returncode,errors_bytes=(d/'errors.log').stat().st_size,output_Save_SHA256=sha(save))
        verdict['captures']=shared.captures(d)
        text=(d/'replay.log').read_text();footer=re.search(r'assertions=(\d+)\n$',text)
        verdict['assertions']=int(footer[1]) if footer else None
        assert result.returncode==0 and not verdict['errors_bytes'] and footer,'first native failure'
        clock=re.search(r'PATROL_CLOCK absolute_frames=(\d+) valid_samples=(\d+) deferred_samples=(\d+) reentries=(\d+) unarmed_frames=(\d+) mutation_frames=(\d+) checkpoints=(\d+) battle_frames=(\d+) battle_attempts=(\d+) stage=(\d+)',text)
        assert clock
        c=dict(zip(['frames','valid','deferred','reentries','unarmed','mutation','checkpoints','battle_frames','battle_attempts','stage'],map(int,clock.groups())))
        verdict['clock']=c
        assert c['frames']==c['valid']+c['deferred']+c['unarmed']+c['mutation']<=100000
        if stage!='cold':
            state.seed_snapshot(save,d/'disk');disk=state.snapshot(d/'disk')
            live=state.snapshot(d/('seed-saved' if stage=='setup' else 'saved'))
            for k in ('party','flags','logical','count','saved_count','counter','map','position'):
                assert disk[k]==live[k],('complete manual Save persistence',k)
            assert disk['count']==2 and 0<=disk['counter']<128
            for i in range(2):
                decoded=state.fields.decode(disk['party'][i*100:(i+1)*100])
                assert decoded['checksum_valid'] and decoded['reencoding_exact'] and not decoded['bad_egg'] and not decoded['egg']
            verdict['native_manual_Save_exact']=True
        if stage=='setup':
            assert c['battle_attempts']==c['battle_frames']==0 and disk['map']==[35,0] and disk['position']==[37,31]
        elif stage=='patrol':
            assert c['battle_attempts']==2 and c['stage']==4
            reviewed=module('corrected_travel',source/'scripts/test-f1-g01e-guard-first-current.py')
            verdict['travel']=reviewed.travel(text)
            assert disk['map']==[35,3] and disk['position']==[8,7]
        else:
            assert c['battle_attempts']==c['battle_frames']==0 and sha(save)==before==sha(out/'patrol.sav')
            for k in ('party','flags','logical','count','saved_count','counter','map','position'):
                assert state.snapshot(d/'cold')[k]==state.snapshot(d/'expected')[k],('independent full cold',k)
            verdict['native_cold_exact']=True
        verdict['facing']=re.findall(r'FIELD_FACING checkpoint=(\S+) facing=(\d+)',text)
    except BaseException as e:
        verdict['validation_failure']=str(e)
        if save.exists():verdict['output_Save_SHA256']=sha(save)
        (out/'STOP.json').write_text(json.dumps(verdict,indent=2)+'\n')
        summary.append(verdict);summaryfile.write_text(json.dumps(summary,indent=2)+'\n')
        raise SystemExit('STOP: first failure retained; no dependent emulator execution')
    summary.append(verdict);summaryfile.write_text(json.dumps(summary,indent=2)+'\n')
    print('PASS',stage,'ordinary process',claim['ordinary_process_ordinal'],verdict['assertions'],'assertions; Save',sha(save))


def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--prior',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--stage',choices=['prepare']+STAGES,required=True);a=p.parse_args()
    assert not git('status','--porcelain'),'Commit source freeze first'
    if a.stage=='prepare':prepare(a.build.resolve(),a.prior.resolve(),a.output.resolve())
    else:execute(a.build.resolve(),a.output.resolve(),a.stage)


if __name__=='__main__':main()
