#!/usr/bin/env python3
"""One exclusive unchanged dependent cold route; no battle or Save controls."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,importlib.util,json,re,shutil,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='84cbb196b52db3330e39ec793828ee2d06c63f2b'
GAME='5084a1814904f1a43fd999fddf770b221bb53653'
ROM='23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167'
SEED='dbaaf7312ed6100b780811cd9b71c627ba42c6100bf318071b8cd1616a62ccd7'
ROUTE='b3e46bacbbd903d674a8329dafc78a6ccb1ceee3ed6d34508613a3fc0c572427'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
parser=argparse.ArgumentParser();parser.add_argument('--build',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--seed',type=Path,required=True);parser.add_argument('--stage',choices=['prepare','cold'],required=True);args=parser.parse_args()
assert not git('status','--porcelain'),'Freeze separate source and contract before execution'
head=git('rev-parse','HEAD');build=args.build.resolve();out=args.output.resolve();seed=args.seed.resolve();engine=build/'source/engine'
assert sha(seed)==SEED and (build/'tested-commit.txt').read_text().strip()==GAME and sha(engine/'pokeemerald.gba')==ROM
subprocess.run(['git','diff','--quiet',GAME,head,'--','engine'],cwd=ROOT,check=True)
subprocess.run(['git','diff','--quiet',BASE,head,'--','scripts/test-f1-g01e-prepared-persistence.py',
    'scripts/floor1/prepared-persistence-host.py','scripts/floor1/prepared-preservation-observer.h',
    'scripts/floor1/walking-preservation.h','scripts/floor1/party-resource-canonical.h',
    'docs/evidence/floor1/g01e/prepared-persistence','docs/floor1/g01e-prepared-persistence-contract.md',
    'docs/floor1/accepted-plan.md'],cwd=ROOT,check=True)
route=ROOT/'scripts/contracts/f1-g01e-prepared-cold.route';assert sha(route)==ROUTE
lines=route.read_text();assert not any(x.startswith(('pilot ','engage ','measure ','inventory ','recover ','restore ')) for x in lines.splitlines())
assert not (out/'STOP.json').exists(),'Retain STOP; no retry'
prior=ROOT/'artifacts/floor1/prepared-persistence/runtime/prepared';expected=prior/'first-clear'
native=module('cold_native_validation',ROOT/'scripts/floor1/prepared-save-validation.py');validation=native.validate(seed,expected)
if args.stage=='prepare':
    assert not out.exists(),'Preserve any existing host/claim/outputs'
    out.mkdir(parents=True);code,base=module('cold_phase_host',ROOT/'scripts/floor1/prepared-cold-phase-host.py').generate(git)
    (out/'observer.c').write_text(code)
    with (out/'host-build.log').open('w') as log:
        subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],stdout=log,stderr=subprocess.STDOUT,check=True)
    shutil.copyfile(prior/'game.sym',out/'game.sym');shutil.copyfile(route,out/'planned.route')
    identity={'runner':head,'base':BASE,'game':GAME,'ROM_SHA256':ROM,'seed_SHA256':SEED,'route_SHA256':ROUTE,
        'host_SHA256':sha(out/'observer.c'),'historical_generated_host_SHA256':'a15f03615c01b463388b0dd8f17a9239050bedaf16f701e60588b701bdb7100b',
        'frame_limit':24000,'execution_limit':1,'battle_attempt_limit':0,'reconstructed_base_observer':base,
        'method':'One separately authorised cold-only dependent route from actual normal prepared Save; unchanged inputs/cadence, native phase gate and absolute clock'}
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');(out/'native-save-validation.json').write_text(json.dumps(validation,indent=2)+'\n')
    print('PASS fresh host compiled and cold route/input identities frozen; no emulator');raise SystemExit(0)
identity=json.loads((out/'identity.json').read_text());assert sha(out/'observer.c')==identity['host_SHA256'] and sha(out/'planned.route')==ROUTE
subprocess.run(['git','diff','--quiet',identity['runner'],head,'--','engine','scripts/test-f1-g01e-prepared-cold-phase.py',
    'scripts/floor1/prepared-cold-phase-host.py','scripts/floor1/cold-phase-guard.h','scripts/floor1/cold-phase-observer.h',
    'scripts/floor1/prepared-save-validation.py','scripts/floor1/walking-preservation.h','scripts/floor1/party-resource-canonical.h',
    'scripts/contracts/f1-g01e-prepared-cold.route','docs/floor1/g01e-prepared-cold-phase-contract.md'],cwd=ROOT,check=True)
assert not (out/'summary.json').exists(),'Exactly one new exclusive claim, no retry'
d=out/'cold';d.mkdir();save=out/'cold.sav';shutil.copyfile(seed,save)
for kind in ['party','flags','owned','context']:shutil.copyfile(expected/('final-'+kind+'.bin'),d/('expected-'+kind+'.bin'))
meta=json.loads((expected/'final-metadata.json').read_text());(d/'expected-counter.bin').write_bytes(struct.pack('<H',meta['counter']))
shutil.copyfile(out/'planned.route',d/'input.route')
with (d/'execution-claim.json').open('x') as f:json.dump({'execution_source':head,'host_runner':identity['runner'],'input_Save_SHA256':SEED,'route_SHA256':ROUTE,'execution_limit':1,'frame_limit':24000,'battle_attempt_limit':0},f,indent=2)
with (d/'input.route').open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
    result=subprocess.run([str(out/'playtest'),str(engine/'pokeemerald.gba'),str(save),str(out/'game.sym')],cwd=d,stdin=inp,stdout=log,stderr=err)
for f in d.glob('*.ppm'):
    im=Image.open(f);assert im.size==(240,160);im.save(f.with_suffix('.png'))
log=(d/'replay.log').read_text();footer=re.search(r'assertions=(\d+)\n$',log);battle=re.search(r'WARDEN battle_frames=(\d+) attempts=(\d+)\n',log)
clock=re.search(r'COLD_CLOCK absolute_frames=(\d+) valid_frame_samples=(\d+) deferred_frame_samples=(\d+) explicit_checkpoints=(\d+) reentry_comparisons=(\d+) boundary_events=(\d+) armed_frame=(\d+)\n',log)
verdict={'execution_source':head,'host_runner':identity['runner'],'exit':result.returncode,'errors_bytes':(d/'errors.log').stat().st_size,
    'assertions':int(footer[1]) if footer else None,'battle_frames':int(battle[1]) if battle else None,'battle_attempts':int(battle[2]) if battle else None,
    'clock':dict(zip(['absolute_frames','valid_frame_samples','deferred_frame_samples','explicit_checkpoints','reentry_comparisons','boundary_events','armed_frame'],map(int,clock.groups()))) if clock else None,
    'input_Save_SHA256':SEED,'output_Save_SHA256':sha(save),'route_SHA256':ROUTE}
(out/'summary.json').write_text(json.dumps(verdict,indent=2)+'\n')
if result.returncode or verdict['errors_bytes'] or not footer or not clock or not battle or verdict['battle_frames'] or verdict['battle_attempts'] or sha(save)!=SEED:
    (out/'STOP.json').write_text(json.dumps(verdict,indent=2)+'\n');raise SystemExit('STOP: preserve failure; no further emulator execution')
c=verdict['clock'];assert c['absolute_frames']<=24000 and c['valid_frame_samples']+c['deferred_frame_samples']==c['absolute_frames']-c['armed_frame']
assert sha(seed)==SEED and sha(engine/'pokeemerald.gba')==ROM
print('PASS one cold-only route',verdict['assertions'],'assertions;',c['absolute_frames'],'exact frames;zero battles;unchanged Save',SEED)
