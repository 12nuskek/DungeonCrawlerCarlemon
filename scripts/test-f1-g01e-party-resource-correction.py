#!/usr/bin/env python3
"""One exclusive ordinary noncombat probe; capture private fields at strict stop."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, shutil, subprocess
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BASE='531276ae7ee4e238ed804cff4c5d970d32d63ff0'
GAME='5084a1814904f1a43fd999fddf770b221bb53653'
ROM='23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167'
SAVE='6ab1357be75bcf4f41fe8064e8df590876348e28fe78e557f28ff90648246386'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

parser=argparse.ArgumentParser()
parser.add_argument('--stage',choices=['prepare','probe'],required=True)
parser.add_argument('--output',type=Path,default=ROOT/'artifacts/floor1/party-resource-correction/runtime')
args=parser.parse_args();out=args.output.resolve()
assert not git('status','--porcelain'),'Commit diagnostic contract and tools before prepare/execution'
head=git('rev-parse','HEAD')
subprocess.run(['git','diff','--quiet',BASE,head,'--','engine','scripts/floor1/warden-first-clear-host.py',
    'scripts/floor1/warden-fairness-host.py','scripts/test-f1-g01e-warden-fairness.py','docs/evidence/floor1/g01e/warden-fairness',
    'scripts/floor1/party-preservation-observer.h','scripts/floor1/party-preservation-host.py',
    'scripts/test-f1-g01e-party-preservation.py','docs/evidence/floor1/g01e/party-preservation-diagnosis',
    'docs/floor1/accepted-plan.md','docs/floor1/g01e-warden-fairness-contract.md'],cwd=ROOT,check=True)
build=ROOT/'artifacts/floor1/warden-fairness/build';engine=build/'source/engine';rom=engine/'pokeemerald.gba'
seed=ROOT/'artifacts/floor1/warden-fairness/runtime/offensive/first-clear.sav'
assert sha(rom)==ROM and sha(seed)==SAVE and (build/'tested-commit.txt').read_text().strip()==GAME
fields=module('probe_fields',ROOT/'scripts/floor1/party-fields.py');saved=fields.saved_party(seed)
assert saved['latest_sector_checksums_valid'] and saved['friendship_counter']==66
spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
geometry=module('probe_geometry',ROOT/'scripts/floor1/relocation-graybox.py')
routes=module('probe_routes',ROOT/'scripts/floor1/live-route.py')
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 cold.ppm','ready']
state=['levels 12 10','growth 12 974 0 10 1284 0','vitals 18 24 0 0 3 40 0 37',
       'flag 2135 1','flag 2136 1','flag 2137 1','flag 46 0','flag 49 0','flag 47 1','flag 48 1','flag 2138 1','flag 2139 0',
       'item 13 0','item 378 2','item 22 0','item 379 0','item 380 0']
def route():
    r=routes.Route(spec,geometry,'checkpoint',(8,6),1,7);r.expect();r.lines+=state
    r.lines+=['xp remember','money remember','preserve start','no-battle start','probe arm']
    r.anchor('arrival');r.anchor('stairs')
    if r.face!=128:r.step(1,128);r.face=128;r.step(40)
    r.step(1,1);r.step(400)
    r.lines+=['pages stairs-no DCC_F1D1Warden_StairsText','choice-ready'];r.step(40,0,'stairs-no-choice.ppm')
    r.step(1,128);r.step(20);r.step(1,1);r.step(400)
    r.lines+=['pages stairs-no-cancelled DCC_Boss_Text_StairsCancel','dialog 3600','ready'];r.step(40);r.expect()
    r.lines+=['choice-result 0']+state+['xp same','money same','preserve check']
    r.step(40,0,'stairs-no-passed.ppm')
    legal=geometry.cells(spec['maps']['boss'],False)
    assert all((x,10) in legal for x in range(4,13))
    for _ in range(4):
        r.follow((4,10));r.lines+=['ready','preserve check']
        r.follow((12,10));r.lines+=['ready','preserve check']
    r.lines+=state+['xp same','money same','preserve check','no-battle end','probe finish','quit']
    lines=boot+r.lines
    assert not any(x.startswith(('pilot ','engage ','candidate ','snapshot','recover','save','restore')) for x in lines)
    assert sum(int(x.split()[1]) for x in lines if x.startswith('step '))+10800<24000
    return '\n'.join(lines)+'\n'

if args.stage=='prepare':
    assert not out.exists(),'Preserve existing prepared probe identity'
    out.mkdir(parents=True)
    code,base=module('probe_host',ROOT/'scripts/floor1/party-resource-host.py').generate(git)
    (out/'observer.c').write_text(code)
    with (out/'host-build.log').open('w') as log:
        subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],stdout=log,stderr=subprocess.STDOUT,check=True)
    shutil.copyfile(ROOT/'artifacts/floor1/warden-fairness/runtime/offensive/game.sym',out/'game.sym')
    (out/'planned.route').write_text(route())
    assert sha(out/'planned.route')=='efad1580ea49f49bd215868aec53f4f9313face05ef6d563bf32856d779a0f69'
    identity=dict(runner=head,base=BASE,game=GAME,rom_SHA256=ROM,input_save_SHA256=SAVE,
        host_SHA256=sha(out/'observer.c'),route_SHA256=sha(out/'planned.route'),frame_limit=24000,execution_limit=1,
        seed_method='controller-authored completed offensive unprepared Save; no synthetic state',old_base_observer=base)
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');print('PASS fresh host compiled and one noncombat route frozen; no emulator');raise SystemExit(0)

identity=json.loads((out/'identity.json').read_text())
assert identity['host_SHA256']==sha(out/'observer.c') and identity['route_SHA256']==sha(out/'planned.route')
subprocess.run(['git','diff','--quiet',identity['runner'],head,'--','scripts/floor1/party-resource-observer.h',
 'scripts/floor1/party-resource-canonical.h','scripts/floor1/party-resource-host.py',
 'scripts/floor1/party-fields.py','scripts/test-f1-g01e-party-resource-correction.py'],cwd=ROOT,check=True)
assert not (out/'execution-claim.json').exists() and not (out/'STOP.json').exists()
save=out/'input-copy.sav';shutil.copyfile(seed,save)
with (out/'execution-claim.json').open('x') as f:
    json.dump(dict(identity,execution_runner=head,method='one fixed walking/staircase-NO route; strict first-mismatch stop'),f,indent=2)
with (out/'planned.route').open() as inp,(out/'replay.log').open('w') as log,(out/'errors.log').open('w') as err:
    result=subprocess.run([str(out/'playtest'),str(rom),str(save),str(out/'game.sym')],cwd=out,stdin=inp,stdout=log,stderr=err)
for p in out.glob('*.ppm'):
    im=Image.open(p);assert im.size==(240,160);im.save(p.with_suffix('.png'))
log=(out/'replay.log').read_text();counter=re.search(r'DIAGNOSTIC frames=(\d+) battles=(\d+) armed_checks=(\d+) reason=(\d+)',log)
footer=re.search(r'result=(\d+) assertions=(\d+)\n$',log)
verdict=dict(identity,execution_runner=head,exit=result.returncode,assertions=int(footer[2]) if footer else None,
    frames=int(counter[1]) if counter else None,battle_frames=int(counter[2]) if counter else None,
    armed_strict_frame_checks=int(counter[3]) if counter else None,reason=int(counter[4]) if counter else None,
    input_copy_unchanged=sha(save)==SAVE,errors_bytes=(out/'errors.log').stat().st_size)
(out/'summary.json').write_text(json.dumps(verdict,indent=2)+'\n')
if result.returncode:
    (out/'STOP.json').write_text(json.dumps(verdict,indent=2)+'\n')
    print('STOP preserved; no further execution. Read-only decoding next.');raise SystemExit(result.returncode)
assert counter and footer and verdict['frames']<=24000 and verdict['battle_frames']==0 and verdict['input_copy_unchanged']
print('Probe completed without mismatch; no retry or mechanism claim')
