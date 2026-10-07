#!/usr/bin/env python3
"""Focused full-walk scene occupancy measurement on the accepted diagnostic ROM."""
from pathlib import Path
from PIL import Image
import hashlib,json,os,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
assert not git('status','--porcelain')
head=git('rev-parse','HEAD');base=Path(os.environ['DCC_G01_BASE_RUN']).resolve();observer=Path(os.environ['DCC_G01_OBSERVER_RUN']).resolve()
identity=json.loads((observer/'identity.json').read_text());assert (identity['observer_sessions'],identity['observer_assertions'])==(3,6203)
subprocess.run(['git','diff','--quiet',identity['observer_source'],head,'--','engine','scripts/playtest.c','scripts/contracts/f1-g01-opening.json','scripts/floor1/opening-graybox.py','scripts/test-f1-g01-observe.py'],cwd=root,check=True)
out=Path(tempfile.mkdtemp(prefix='scene-',dir=root/'artifacts/floor1/g01'));print('Evidence:',out,flush=True)
d=base/'open';rom=d/'diagnostic.gba';assert hashlib.sha256(rom.read_bytes()).hexdigest()==(d/'rom.sha256').read_text().split()[0]
route=d/'guard-first/input.route'
with route.open() as inputs,(out/'replay.log').open('w') as log,(out/'errors.log').open('w') as errors:
    subprocess.run([str(observer/'playtest'),str(rom),str(out/'scene.sav'),str(d/'game.sym')],cwd=out,stdin=inputs,stdout=log,stderr=errors,check=True)
assert (out/'replay.log').read_text().endswith('result=0 assertions=155\n') and not (out/'errors.log').stat().st_size
for p in out.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
(out/'identity.json').write_text(json.dumps({'measurement_runner_source':head,'diagnostic_source':identity['diagnostic_game_source'],'observer_source':identity['observer_source'],'observer_harness_sha256':hashlib.sha256((observer/'playtest-observe.c').read_bytes()).hexdigest(),'route':str(route),'assertions':155,'diagnostic':True,'scope':'Readonly arrays sampled on every ordinary step frame whose loaded map extent is79x62. All candidate anchors/lane samples visited; not a whole-floor or hardware performance budget.'},indent=2)+'\n')
assert not git('status','--porcelain') and git('rev-parse','HEAD')==head
print('PASS155 scene route; '+(out/'replay.log').read_text().splitlines()[-2],flush=True)
