#!/usr/bin/env python3
"""One parent-authorised fresh-input patrol replay, then persistence/idempotence."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, importlib.util, json, re, shutil, subprocess

ROOT=Path(__file__).resolve().parents[1]
GAME='c643f01c11ec68119b0347b107ee20115131debc'
ROM='b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a'
BASE='b36f750c689029e4fcc9f0a43b73c0c3dca7dccf'
SEED='c11c64559f38680dd21afe693327e703fd4b452776ace69f8e7f1e0b1f3bc67f'

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser=argparse.ArgumentParser()
parser.add_argument('--build',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--seed',type=Path,required=True)
parser.add_argument('--stage',choices=['prepare','patrol','cold'],required=True)
args=parser.parse_args()
assert not git('status','--porcelain'),'Commit contract/source before execution'
head=git('rev-parse','HEAD')
build=args.build.resolve();out=args.output.resolve();seed=args.seed.resolve()
assert sha(seed)==SEED
assert (build/'tested-commit.txt').read_text().strip()==GAME
subprocess.run(['git','diff','--quiet',GAME,head,'--','engine'],cwd=ROOT,check=True)
subprocess.run(['git','diff','--quiet',BASE,head,'--','scripts/test-f1-g01e-recovery.py',
    'scripts/test-f1-g01e-current-patrol.py','scripts/floor1/recovery-host.py',
    'scripts/floor1/potion-menu-readiness.h','docs/floor1/g01e-recovery-contract.md',
    'docs/floor1/g01e-current-patrol-contract.md','docs/evidence/floor1/g01e/recovery'],cwd=ROOT,check=True)
engine=build/'source/engine';rom=engine/'pokeemerald.gba'
assert sha(rom)==ROM
out.mkdir(parents=True,exist_ok=True)
if args.stage=='prepare':
    assert not (out/'identity.json').exists(),'Preserve prepared host and executions'
    host=module('new_save_host',ROOT/'scripts/floor1/new-save-recovery-host.py')
    code,base=host.generate(git)
    (out/'observer.c').write_text(code)
    with (out/'host-build.log').open('w') as log:
        subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],stdout=log,stderr=subprocess.STDOUT,check=True)
    with (out/'game.sym').open('w') as symbols:
        subprocess.run(['arm-none-eabi-nm','--defined-only',str(engine/'pokeemerald.elf')],stdout=symbols,check=True)
    with (out/'game.sym').open('a') as symbols:
        subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)],stdout=symbols,check=True)
    (out/'identity.json').write_text(json.dumps(dict(runner=head,base=BASE,game=GAME,rom=ROM,
        seed_sha256=SEED,host_sha256=sha(out/'observer.c'),reconstructed_base_observer=base,
        method='Separate parent-reviewed fresh-save contract; no historical-input equivalence'),indent=2)+'\n')
    print('PASS prepared/compiled; no emulator execution');raise SystemExit(0)

identity=json.loads((out/'identity.json').read_text())
assert identity['host_sha256']==sha(out/'observer.c')
subprocess.run(['git','diff','--quiet',identity['runner'],head,'--','engine',
    'scripts/test-f1-g01e-new-save-recovery.py','scripts/floor1/new-save-recovery-host.py',
    'scripts/floor1/new-save-potion-state.h','scripts/floor1/recovery-field-readiness.h',
    'scripts/floor1/live-save-observer.py','scripts/floor1/walking-harness.py'],cwd=ROOT,check=True)
assert not (out/'STOP.json').exists(),'Stop on failure; further execution needs parent review'
summary_path=out/'summary.json'
summary=json.loads(summary_path.read_text()) if summary_path.exists() else []
assert [x['stage'] for x in summary]==([] if args.stage=='patrol' else ['patrol'])
d=out/args.stage;d.mkdir()
pending=['flag 46 0','flag 47 0','flag 48 0','flag 49 0','flag 2138 0','flag 2139 0']
target=['expect 35 0 37 31 7','levels 11 10','growth 11 748 0 10 1058 0',
    'duo healthy','uses 8 40 2 40','item 13 0','item 378 2','flag 2135 1','flag 2136 1','flag 2137 1']+pending
save=out/(args.stage+'.sav')
if args.stage=='patrol':
    shutil.copyfile(seed,save)
    # Exact published patrol route plus existing recovery target assertions.
    lines=git('show',BASE+':docs/evidence/floor1/g01e/attempts/patrol-single-weaken/input.route').splitlines()
    lines=[x for x in lines if x not in ['snapshot','quit']]
    assert lines.count('pilot offensive 36000')==1
    lines[lines.index('pilot offensive 36000')]='pilot potion-once 36000'
    lines[9:9]=['item 13 1','item 378 2','growth 9 495 0 9 805 0','money remember']+pending
    i=lines.index('flag 2137 1')
    lines[i+1:i+1]=['growth 10 616 0 9 926 0','item 13 1','item 378 2','flag 2136 0','money gain 360']+pending
    i=lines.index('flag 2136 1')
    lines[i+1:i+1]=['growth 11 748 0 10 1058 0','item 13 0','item 378 2','money gain 680','money remember','xp remember']+pending
    i=lines.index('step 1 8 -',i)
    lines[i:i]=['xp same','money same','no-battle start','step 1 1 -','step 400 0 guard-resolved.ppm',
        'dialog 3600','ready','step 40 0 -']+target+['xp same','money same','no-battle end']
    lines+=target+['xp same','money same']
else:
    shutil.copyfile(out/'patrol.sav',save)
    lines=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -',
        'step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 cold.ppm','ready']+target
    lines+=['xp remember','money remember','no-battle start','step 1 1 -','step 400 0 cold-guard-resolved.ppm',
        'dialog 3600','ready','step 40 0 -']+target+['xp same','money same']
    geometry=module('new_save_geometry',ROOT/'scripts/floor1/relocation-graybox.py')
    routes=module('new_save_routes',ROOT/'scripts/floor1/live-route.py')
    spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
    r=routes.Route(spec,geometry,'field',(37,31),1,7)
    r.anchor('howler');r.talk(128,'cold-howler-resolved')
    r.lines+=['flag 2137 1','growth 11 748 0 10 1058 0','duo healthy','uses 8 40 2 40',
        'item 13 0','item 378 2','xp same','money same']+pending
    r.anchor('guard')
    lines+=r.lines+target+['xp same','money same','no-battle end']
route=d/'input.route';route.write_text('\n'.join(lines+['quit'])+'\n')
before=sha(save)
with (d/'execution-claim.json').open('x') as claim:
    json.dump(dict(runner=head,stage=args.stage,route_sha256=sha(route),input_save_sha256=before),claim,indent=2)
with route.open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
    result=subprocess.run([str(out/'playtest'),str(rom),str(save),str(out/'game.sym')],cwd=d,stdin=inp,stdout=log,stderr=err)
for frame in d.glob('*.ppm'):
    im=Image.open(frame);assert im.size==(240,160);im.save(frame.with_suffix('.png'))
log=(d/'replay.log').read_text()
verdict=dict(stage=args.stage,runner=head,host_runner=identity['runner'],exit=result.returncode,
    errors_bytes=(d/'errors.log').stat().st_size,assertions=int(re.search(r'assertions=(\d+)\n$',log)[1]),
    input_save_sha256=before,output_save_sha256=sha(save),route_sha256=sha(route),reconstructed_input=True)
summary.append(verdict);summary_path.write_text(json.dumps(summary,indent=2)+'\n')
if result.returncode or verdict['errors_bytes']:
    (out/'STOP.json').write_text(json.dumps(verdict,indent=2)+'\n')
    raise SystemExit('STOP: failure retained; no further execution')
assert sha(rom)==ROM and sha(seed)==SEED
if args.stage=='cold':
    assert before==sha(save)==sha(out/'patrol.sav'),'Cold/repeats must not write save'
print('PASS',args.stage,verdict['assertions'],'assertions; save',sha(save),flush=True)
