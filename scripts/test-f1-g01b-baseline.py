#!/usr/bin/env python3
"""Ordinary production recovery roundtrips from immutable copied saves."""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json,os,re,shlex,shutil,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
assert not git('status','--porcelain'),'Commit first'
head=git('rev-parse','HEAD');base=Path(os.environ['DCC_A01_BASE_RUN']).resolve()
subprocess.run(['git','diff','--quiet','abb77feb',head,'--','engine','scripts/playtest.c'],cwd=root,check=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base/'production.gba')=='5c4f865a95c0b9e4c65f13d86c8ba44c9082599432b387f6fc350c0bd99b7230'
original={n:digest(base/n) for n in ['howler-pending.sav','boss-loss.sav']}
out=Path(tempfile.mkdtemp(prefix='baseline-',dir=root/'artifacts/floor1/g01b'));print('Evidence:',out,flush=True)
loader=importlib.util.spec_from_file_location('walking',root/'scripts/floor1/walking-harness.py');m=importlib.util.module_from_spec(loader);loader.loader.exec_module(m)
code=m.instrument(git('show',head+':scripts/playtest.c')+'\n');(out/'walking.c').write_text(code)
subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',*shlex.split(os.environ.get('DCC_TEST_CFLAGS','')),str(out/'walking.c'),*shlex.split(os.environ.get('DCC_TEST_LDFLAGS','')),'-lmgba','-o',str(out/'playtest')],check=True)
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 start.ppm']
summary=[]
def run(name,seed,lines):
    save=out/(name+'.sav');shutil.copyfile(seed,save);d=out/name;d.mkdir();(d/'input.route').write_text('\n'.join(lines)+'\n')
    with (d/'input.route').open() as inputs,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as errors:
        subprocess.run([str(out/'playtest'),str(base/'production.gba'),str(save),str(base/'game.sym')],cwd=d,stdin=inputs,stdout=log,stderr=errors,check=True)
    assert not (d/'errors.log').stat().st_size
    checks=sum(line.startswith(('expect ','flag ','duo ','uses ','growth ','roster ')) for line in lines)
    assert (d/'replay.log').read_text().endswith(f'result=0 assertions={checks}\n')
    for p in d.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
    measures=[dict(name=match[0],frames=int(match[1]),walking_frames=int(match[2]),engine_tile_changes=int(match[3]),map_changes=int(match[4]),walking_seconds=int(match[2])/59.7275005696) for match in re.findall(r'MEASURE name=(\S+) frames=(\d+) walking=(\d+) tiles=(\d+) warps=(\d+)',(d/'replay.log').read_text())]
    summary.append({'route':name,'assertions':checks,'production':True,'measurements':measures});print(name,'PASS',checks,measures,flush=True);return save
calibration=boot+['expect 34 3 5 5 7','flag 2136 1','flag 2137 0','measure start one-tile-north','step 16 64 -','step 40 0 north.ppm','expect 34 3 5 4 7','measure stop','measure start one-tile-south','step 16 128 -','step 40 0 south.ppm','expect 34 3 5 5 7','measure stop','quit']
run('calibration',base/'howler-pending.sav',calibration)
# Seed Howler point entirely through normal navigation; no modified save/RAM.
seed=boot+['expect 34 4 8 5 7','flag 2136 1','flag 2137 1','duo healthy','step 16 64 -','step 40 0 -','step 96 32 -','step 220 0 -','expect 34 3 12 4 7','step 32 32 -','step 40 0 -','step 16 128 -','step 40 0 howler-point.ppm','expect 34 3 10 5 7','step 1 8 -','step 120 0 -','step 1 128 -','step 20 0 -','step 1 128 -','step 20 0 -','step 1 1 -','step 160 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 saved.ppm','step 1 1 -','step 600 0 seed-done.ppm','expect 34 3 10 5 7','quit']
howlerSave=run('howler-ordinary-seed',base/'boss-loss.sav',seed)
for name,x,save,guardFlag,howlerFlag in [('guard',5,base/'howler-pending.sav',1,0),('howler',10,howlerSave,1,1)]:
    # Reuse validated original outbound/recovery controls, but return to SAME starting encounter.
    originalRoute=(root/('docs/evidence/s03/guard-rest.route' if name=='guard' else 'docs/evidence/s03/boss-rest.route')).read_text().splitlines()
    start=originalRoute.index('step 20 64 -');end=originalRoute.index('step 20 32 -',start)
    outbound=originalRoute[start:end]
    healStart=outbound.index('step 1 1 -');walking=outbound[:healStart];healing=outbound[healStart:]
    lines=boot+[f'expect 34 3 {x} 5 7',f'flag 2136 {guardFlag}',f'flag 2137 {howlerFlag}','measure start '+name+'-out']+walking+['expect 34 1 4 7 7','measure stop']+healing+['duo healthy','uses 8 40 2 40','measure start '+name+'-back']
    lines+=['step 20 32 -','step 40 0 -','step 52 64 -','step 40 0 -','step 20 32 -','step 220 0 -','expect 34 2 2 4 7','step 84 128 -','step 220 0 -','expect 34 3 2 4 7',f'step {16*(x-2)+4} 16 -','step 40 0 -','step 20 128 -','step 40 0 returned.ppm',f'expect 34 3 {x} 5 7','measure stop',f'flag 2136 {guardFlag}',f'flag 2137 {howlerFlag}','duo healthy','uses 8 40 2 40','quit']
    # Full-health Howler seed legitimately differs from old damaged roster; omit only exact old HP check.
    lines=[line for line in lines if not line.startswith('roster ')]
    run(name+'-roundtrip',save,lines)
assert all(digest(base/n)==h for n,h in original.items())
(out/'identity.json').write_text(json.dumps({'runner_source':head,'production_compiled_source':(base/'tested-commit.txt').read_text().strip(),'production_sha256':digest(base/'production.gba'),'source_save_sha256':original,'method':'Copied ordinary saves, controller navigation/recovery only; read-only callback/avatar/position frame sampling. Active walking requires CB2_Overworld, nonforced avatar, no active palette fade, MOVING and nonzero tile transition. Menu/dialogue/idle/other callbacks excluded. No human pacing claim.'},indent=2)+'\n')
(out/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
assert not git('status','--porcelain') and git('rev-parse','HEAD')==head
print('PASS production baseline sessions',len(summary),flush=True)
