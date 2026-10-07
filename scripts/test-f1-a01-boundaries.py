#!/usr/bin/env python3
"""Focused boundary fixtures, retaining the exact accepted A01 production build."""
from pathlib import Path
from PIL import Image
import hashlib,json,os,shutil,subprocess,tempfile

root=Path(__file__).resolve().parents[1]
def git(*args):
    return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
assert not git('status','--porcelain'), 'Commit changes first'
revision=git('rev-parse','HEAD');base=Path(os.environ['DCC_A01_BASE_RUN']).resolve()
tested=(base/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',tested,revision,'--','engine','scripts/playtest.c','scripts/battle-input-symbols.py'],cwd=root,check=True)
summary=json.loads((base/'validation-summary.json').read_text())
assert (len(summary),sum(x['assertions'] for x in summary))==(86,1399)
assert all((base/x['route']/'errors.log').is_file() and not (base/x['route']/'errors.log').stat().st_size for x in summary)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base/'production.gba')==(base/'rom.sha256').read_text().split()[0]
out=Path(tempfile.mkdtemp(prefix='boundaries-',dir=root/'artifacts/floor1/a01'));print('Evidence:',out,flush=True)
source=out/'source';source.mkdir();shutil.copytree(base/'source/engine',source/'engine',symlinks=True)
identity={'fixture_test_source':revision,'production_compiled_source':tested,'production_sha256':digest(base/'production.gba'),'base_run':str(base),'method':'Incremental isolated diagnostic builds from committed engine sources using accepted build cache; no new production rebuild or stock-map playthrough claimed.'}
(out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');results=[]
route=git('show',revision+':scripts/routes/f1-a01/boundaries.route')+'\n'
for name,mode in [('membership-boundary-fixture',''),('membership-extended-boundary-fixture','extended')]:
    for path in ['engine/src/crawler.c','engine/src/crawler_identity.c','engine/src/battle_script_commands.c','engine/data/maps/DCC_Entrance/scripts.inc','engine/src/fieldmap.c','engine/src/overworld.c','engine/src/event_object_movement.c','engine/src/battle_setup.c']:
        (source/path).write_bytes(subprocess.check_output(['git','show',tested+':'+path],cwd=root))
    subprocess.run(['python3',str(root/'scripts/floor1/membership-boundary-fixture.py'),str(source),mode],check=True)
    with (out/(name+'-build.log')).open('w') as log:
        subprocess.run(['make','-C',str(source/'engine'),'-j2'],stdout=log,stderr=subprocess.STDOUT,check=True)
    rom=out/(name+'.gba');shutil.copyfile(source/'engine/pokeemerald.gba',rom)
    (out/(name+'-rom.sha256')).write_text(digest(rom)+'  '+rom.name+'\n')
    sym=out/(name+'.sym')
    with sym.open('w') as output:
        subprocess.run(['arm-none-eabi-nm','-g','--defined-only',str(source/'engine/pokeemerald.elf')],stdout=output,check=True)
        subprocess.run(['python3',str(root/'scripts/battle-input-symbols.py'),str(source/'engine')],stdout=output,check=True)
    d=out/(name+'-policy');d.mkdir();(d/'input.route').write_text(route)
    with (d/'input.route').open() as inputs,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as errors:
        subprocess.run([str(base/'playtest'),str(rom),str(out/(name+'.sav')),str(sym)],cwd=d,stdin=inputs,stdout=log,stderr=errors,check=True)
    assert (d/'replay.log').read_text().endswith('result=0 assertions=3\n') and not (d/'errors.log').stat().st_size
    for p in d.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
    results.append({'route':d.name,'assertions':3,'fixture':True});print(d.name,'PASS3 / mask255',flush=True)
assert len(results)==2 and sum(x['assertions'] for x in results)==6
(out/'validation-summary.json').write_text(json.dumps(results,indent=2)+'\n')
assert git('rev-parse','HEAD')==revision and not git('status','--porcelain')
print('PASS two isolated boundary sessions /6 assertions; direct API dispatch only, no synthetic trainer battle.',flush=True)
