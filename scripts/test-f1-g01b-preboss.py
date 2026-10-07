#!/usr/bin/env python3
"""Measure the original Howler→guide→Warden preparation route without resaving."""
from pathlib import Path
from PIL import Image
import hashlib,json,os,re,shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=root,text=True).strip()
assert not git('status','--porcelain')
head=git('rev-parse','HEAD');base=Path(os.environ['DCC_A01_BASE_RUN']).resolve();baseline=Path(os.environ['DCC_G01B_BASELINE']).resolve()
identity=json.loads((baseline/'identity.json').read_text());summary=json.loads((baseline/'validation-summary.json').read_text());assert len(summary)==4 and sum(r['assertions'] for r in summary)==44
subprocess.run(['git','diff','--quiet',identity['runner_source'],head,'--','engine','scripts/playtest.c','scripts/floor1/walking-harness.py'],cwd=root,check=True)
assert hashlib.sha256((base/'production.gba').read_bytes()).hexdigest()==identity['production_sha256']
lines=(root/'docs/evidence/s03/boss-rest.route').read_text().splitlines();lines=lines[:lines.index('step 1 8 -',10)]
lines=[v for v in lines if not v.startswith('roster ')]
lines.insert(lines.index('step 20 64 -'),'measure start preboss-out')
a=lines.index('step 1 1 -',10);lines.insert(a,'measure stop')
a=lines.index('step 20 32 -',10);lines.insert(a,'measure start preboss-back')
a=lines.index('expect 34 4 8 5 7')+1;lines.insert(a,'measure stop');lines+=['duo healthy','uses 8 40 2 40','quit']
out=Path(tempfile.mkdtemp(prefix='preboss-',dir=root/'artifacts/floor1/g01b'));print('Evidence:',out,flush=True)
seed=baseline/'howler-ordinary-seed.sav';digest=hashlib.sha256(seed.read_bytes()).hexdigest();save=out/'copied.sav';shutil.copyfile(seed,save);(out/'input.route').write_text('\n'.join(lines)+'\n')
with (out/'input.route').open() as inputs,(out/'replay.log').open('w') as log,(out/'errors.log').open('w') as errors:
 subprocess.run([str(baseline/'playtest'),str(base/'production.gba'),str(save),str(base/'game.sym')],cwd=out,stdin=inputs,stdout=log,stderr=errors,check=True)
assert not (out/'errors.log').stat().st_size
checks=sum(v.startswith(('expect ','flag ','duo ','uses ','growth ')) for v in lines);assert (out/'replay.log').read_text().endswith(f'result=0 assertions={checks}\n')
measures=[{'name':m[0],'frames':int(m[1]),'walking_frames':int(m[2]),'engine_tile_changes':int(m[3]),'map_changes':int(m[4])} for m in re.findall(r'MEASURE name=(\S+) frames=(\d+) walking=(\d+) tiles=(\d+) warps=(\d+)',(out/'replay.log').read_text())]
assert [(v['engine_tile_changes'],v['walking_frames']) for v in measures]==[(19,304),(27,431)]
assert hashlib.sha256(seed.read_bytes()).hexdigest()==digest
for p in out.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
(out/'result.json').write_text(json.dumps({'runner_source':head,'measurement_source':identity['runner_source'],'production_sha256':identity['production_sha256'],'seed_sha256':digest,'assertions':checks,'measurements':measures,'total_steps':46,'walking_frames':735,'walking_seconds':735/59.7275005696,'scope':'Ordinary copied production save; menu/dialogue/idle/fades/loaded-center state excluded. Seed HP is fully healthy; no balance or battle outcome claim.'},indent=2)+'\n')
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
print('PASS preboss',checks,'assertions;46steps/735walking frames',flush=True)
