#!/usr/bin/env python3
"""Finish only missing A01 fixture checks against its unchanged clean production run."""
from pathlib import Path
from PIL import Image
import hashlib,json,os,re,subprocess

root=Path(__file__).resolve().parents[1]
def git(*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
assert not git('status','--porcelain'), 'Commit changes first'
revision=git('rev-parse','HEAD')
base=Path(os.environ['DCC_A01_BASE_RUN']).resolve()
tested=(base/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',tested,revision,'--','engine','scripts/playtest.c','scripts/battle-input-symbols.py'],cwd=root,check=True)
summary=json.loads((base/'partial-validation-summary.json').read_text())['sessions']
assert (len(summary),sum(x['assertions'] for x in summary),sum(x['assertions'] for x in summary if x['fixture']))==(84,1393,220)
for row in summary:
    d=base/row['route']
    assert (d/'replay.log').read_text().endswith(f"result=0 assertions={row['assertions']}\n")
    assert (d/'errors.log').is_file() and not (d/'errors.log').stat().st_size
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base/'production.gba')==(base/'rom.sha256').read_text().split()[0]
source=base/'source'
route=git('show',revision+':scripts/routes/f1-a01/membership.route')+'\n'
identity={'fixture_test_source':revision,'production_compiled_source':tested,'production_sha256':digest(base/'production.gba'),'method':'Retain84 verified sessions and immutable clean production ROM; restore committed engine sources before each isolated corrected fixture build. No production rebuild claimed.'}
(base/'fixture-resume-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
for name,mode in [('membership-fixture',''),('membership-extended-fixture','extended')]:
    d=base/(name+'-policy')
    assert not d.exists(), 'Preserve previous attempt; reconcile it before retrying'
    # The previous run's source is a labeled diagnostic snapshot. Restore every
    # file changed by its fixture pipeline, then apply this committed patcher.
    for path in ['engine/src/crawler.c','engine/src/crawler_identity.c','engine/src/battle_script_commands.c','engine/data/maps/DCC_Entrance/scripts.inc']:
        (source/path).write_bytes(subprocess.check_output(['git','show',tested+':'+path],cwd=root))
    subprocess.run(['python3',str(root/'scripts/floor1/membership-fixture.py'),str(source),mode],check=True)
    with (base/(name+'-resume-build.log')).open('w') as log:
        subprocess.run(['make','-C',str(source/'engine'),'-j2'],stdout=log,stderr=subprocess.STDOUT,check=True)
    rom=base/(name+'.gba');rom.write_bytes((source/'engine/pokeemerald.gba').read_bytes())
    (base/(name+'-rom.sha256')).write_text(digest(rom)+'  '+rom.name+'\n')
    sym=base/(name+'.sym')
    with sym.open('w') as output:
        subprocess.run(['arm-none-eabi-nm','-g','--defined-only',str(source/'engine/pokeemerald.elf')],stdout=output,check=True)
        subprocess.run(['python3',str(root/'scripts/battle-input-symbols.py'),str(source/'engine')],stdout=output,check=True)
    d.mkdir();(d/'input.route').write_text(route)
    with (d/'input.route').open() as inputs,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as errors:
        subprocess.run([str(base/'playtest'),str(rom),str(base/(name+'.sav')),str(sym)],cwd=d,stdin=inputs,stdout=log,stderr=errors,check=True)
    assert (d/'replay.log').read_text().endswith('result=0 assertions=3\n')
    assert not (d/'errors.log').stat().st_size
    summary.append({'route':d.name,'assertions':3,'fixture':True})
    print(d.name,'PASS3 (131072 GBA identity comparisons plus presentation/marker probes)',flush=True)
for p in base.glob('*/*.ppm'):
    if p.parent.name!='movement' or not p.name.startswith('walk-'):
        Image.open(p).save(p.with_suffix('.png'))
with (base/'walking-render.log').open('w') as log:
    subprocess.run(['python3',str(root/'scripts/render-walk.py'),str(base/'movement'),str(base/'walking.gif')],stdout=log,check=True)
for script,out in [('verify-opponent-frames.py','opponent-pixels.json'),('verify-environment-props.py','prop-pixels.json'),('verify-dungeon-presentation.py','presentation-pixels.json')]:
    with (base/out).open('w') as log:
        subprocess.run(['python3',str(root/'scripts'/script),str(base)],stdout=log,check=True)
assert (len(summary),sum(x['assertions'] for x in summary),sum(x['assertions'] for x in summary if x['fixture']))==(86,1399,226)
(base/'validation-summary.json').write_text(json.dumps(sorted(summary,key=lambda r:r['route']),indent=2)+'\n')
assert git('rev-parse','HEAD')==revision and not git('status','--porcelain')
print('PASS86 sessions/1399 assertions;216 recovery and actual visual review still required.',flush=True)
