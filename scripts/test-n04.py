#!/usr/bin/env python3
"""Normal-input victories from exact accepted defeat saves; no engine/state edits."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,tempfile
from PIL import Image
root=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
assert not git('status','--porcelain'), 'Commit changes first'
revision=git('rev-parse','HEAD');base=Path(os.environ['DCC_RECOVERY_BASE_RUN']).resolve()
tested=(base/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',tested,revision,'--','engine','scripts/playtest.c','scripts/battle-input-symbols.py'],cwd=root,check=True)
summary=json.loads((base/'validation-summary.json').read_text());shape=(len(summary),sum(x['assertions'] for x in summary))
assert shape in [(76,1303),(78,1315),(84,1393),(86,1399)], 'Require full N03, N05, F1-T01 or F1-A01 acceptance coverage'
assert len({x['route'] for x in summary})==len(summary), 'Duplicate session names'
assert sum(x['assertions'] for x in summary if x['fixture'])==({(84,1393):220,(86,1399):226}.get(shape,193))
if len(summary)>=78:
 assert {x['route']:x['assertions'] for x in summary if x['route'].startswith('guide-')}=={'guide-after-trial':6,'guide-before-trial':6}
if shape in [(84,1393),(86,1399)]:
 counts={x['route']:x['assertions'] for x in summary}
 assert {name:counts[name] for name in ['text-state','text-return-cold','text-return-reentry','text-complete','tag-fixture-full','tag-fixture-cold','quest-fixture-capacity','quest-fixture-reload','wire-pair','wire-cold']}=={'text-state':25,'text-return-cold':5,'text-return-reentry':11,'text-complete':7,'tag-fixture-full':14,'tag-fixture-cold':7,'quest-fixture-capacity':25,'quest-fixture-reload':11,'wire-pair':23,'wire-cold':7}
 if shape==(86,1399):
  assert counts['membership-fixture-policy']==counts['membership-extended-fixture-policy']==3
for entry in summary:
 errors=base/entry['route']/'errors.log'
 assert errors.is_file() and not errors.stat().st_size, errors
 assert (base/entry['route']/'replay.log').read_text().endswith(f"result=0 assertions={entry['assertions']}\n"), entry['route']
rom=base/'production.gba';digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(rom)==(base/'rom.sha256').read_text().split()[0]
parent=root/'artifacts/n04';parent.mkdir(exist_ok=True);out=Path(tempfile.mkdtemp(prefix='run-',dir=parent));print('Evidence:',out,flush=True)
(out/'tested-commit.txt').write_text(revision+'\n')
config=json.loads(git('show',revision+':scripts/contracts/n04-recovery.json'))
identity={'source_test_commit':revision,'unchanged_engine_compiled_commit':tested,'base_run':str(base),'production_sha256':digest(rom),'harness_sha256':digest(base/'playtest'),'symbols_sha256':digest(base/'game.sym'),'method':'Verified unchanged engine/harness source; reuse accepted clean production build. No engine rebuild claimed. Normal save copies and read-only RAM assertions.'}
(out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');results=[]
def run(name,route,save,expected):
 d=out/name;d.mkdir();(d/'input.route').write_text(route)
 with (d/'input.route').open() as src,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as errors:
  subprocess.run([str(base/'playtest'),str(rom),str(save),str(base/'game.sym')],cwd=d,stdin=src,stdout=log,stderr=errors,check=True)
 log=(d/'replay.log').read_text();assert log.endswith(f'result=0 assertions={expected}\n') and not (d/'errors.log').stat().st_size
 for p in d.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
 results.append({'route':name,'assertions':expected});print(name,'PASS',expected,flush=True);return log
for c in config:
 save=out/c['input_save'];shutil.copyfile(base/c['input_save'],save)
 (out/(c['name']+'-input.sha256')).write_text(digest(save)+'  '+c['input_save']+'\n')
 route=git('show',revision+':'+c['route'])+'\n';original=git('show',revision+':'+c['original_retry_route']).removesuffix('quit')
 assert route.startswith(original),'original retry checks must stay intact'
 log=run(c['name']+'-win',route,save,c['assertions'])
 # Snapshot actual persistent values before reset, then compare after cold load.
 # These are assertions only: no game RAM, save bytes or outcome flags are written.
 hp=re.findall(r'party=2 HP=(\d+)/\d+,(\d+)/\d+',log)[-1]
 pp=re.findall(r'persistent PP=(\d+),(\d+) status=(\d+),(\d+)',log)[-1]
 growth=re.findall(r'growth level/xp/item=(\d+)/(\d+)/(\d+),(\d+)/(\d+)/(\d+)',log)[-1]
 uses=re.findall(r'party action uses=(\d+),(\d+) / (\d+),(\d+)',log)[-1]
 (out/(c['name']+'-victory-state.json')).write_text(json.dumps({'hp':hp,'pp_and_status':pp,'growth':growth,'uses':uses},indent=2)+'\n')
 cold=c['cold_prefix']+'roster '+' '.join(hp+pp)+'\nuses '+' '.join(uses)+'\nquit\n'
 run(c['name']+'-cold',cold,save,c['cold_assertions'])
assert len(results)==12 and sum(x['assertions'] for x in results)==216,(len(results),results)
(out/'validation-summary.json').write_text(json.dumps(results,indent=2)+'\n')
assert git('rev-parse','HEAD')==revision and not git('status','--porcelain')
print('PASS 12 production sessions / 216 assertions; inspect actual recovery/victory/cold frames before acceptance.',flush=True)
