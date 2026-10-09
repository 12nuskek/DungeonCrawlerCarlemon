#!/usr/bin/env python3
"""ONE frozen current-order/travel claim plus dependent exact native cold. No retry."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,importlib.util,json,re,shutil,subprocess
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
BASE='3e0ace22ce82fcee61a6e945be219dd8849e6ea3';GAME='5084a1814904f1a43fd999fddf770b221bb53653'
ROM='23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167';ELF='cafc512d915d01ff1b598b1a7050261f5990bc50fc0faed533b0ec6d7309336b'
SEED='c11c64559f38680dd21afe693327e703fd4b452776ace69f8e7f1e0b1f3bc67f'
SCOPED=['scripts/test-f1-g01e-guard-first-current.py','scripts/floor1/guard-first-host.py','scripts/floor1/guard-first-observer.h','scripts/floor1/guard-first-state.py','scripts/floor1/guard-first-route.py','scripts/floor1/guard-first-tests.py','scripts/contracts/f1-g01e-guard-first-current.route','scripts/contracts/f1-g01e-guard-first-current-cold.route','docs/floor1/g01e-guard-first-current-contract.md']
PRESERVED=['engine','docs/floor1/accepted-plan.md','scripts/floor1/walking-preservation.h','scripts/floor1/party-resource-canonical.h','scripts/floor1/travel-measurements.py','scripts/floor1/new-save-recovery-host.py','scripts/floor1/recovery-host.py','scripts/floor1/cold-phase-guard.h','scripts/floor1/cold-phase-observer.h']
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
state=module('gf_state',ROOT/'scripts/floor1/guard-first-state.py')
def travel(log):
 rows=[dict(zip(['name','frames','walking_frames','steps','warps'],[m[0]]+list(map(int,m[1:])))) for m in re.findall(r'MEASURE name=(\S+) frames=(\d+) walking=(\d+) tiles=(\d+) warps=(\d+)',log)]
 expected=['guard-out','guard-back','howler-out','howler-back','preboss-out','preboss-back'];assert Counter(x['name'] for x in rows)==Counter(expected),'ALL six exact names required'
 validator=module('gf_travel',ROOT/'scripts/floor1/travel-measurements.py');spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text());ceiling=json.loads((ROOT/'scripts/contracts/f1-g01b-recovery.json').read_text())
 for kind in ('guard-first','preboss'):validator.validate(kind,[x for x in rows if x['name'] in validator.TRAVEL_NAMES[kind]],spec,ceiling)
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=Path,required=True);p.add_argument('--stage',choices=['prepare','patrol','cold'],required=True);a=p.parse_args()
 assert not git('status','--porcelain'),'Freeze all source before execution'
 head=git('rev-parse','HEAD');build=a.build.resolve();out=a.output.resolve();seed=a.seed.resolve();engine=build/'source/engine'
 assert sha(seed)==SEED and (build/'tested-commit.txt').read_text().strip()==GAME and sha(engine/'pokeemerald.gba')==ROM and sha(engine/'pokeemerald.elf')==ELF
 subprocess.run(['git','diff','--quiet',BASE,head,'--',*PRESERVED],cwd=ROOT,check=True)
 routes={kind:ROOT/f'scripts/contracts/f1-g01e-guard-first-current{"-cold" if kind=="cold" else ""}.route' for kind in ('patrol','cold')}
 if a.stage=='prepare':
  assert not out.exists(),'Preserve host/claims/outputs';out.mkdir(parents=True)
  code,base=module('gf_host',ROOT/'scripts/floor1/guard-first-host.py').generate(git);(out/'observer.c').write_text(code)
  with (out/'host-build.log').open('w') as log:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],stdout=log,stderr=subprocess.STDOUT,check=True)
  with (out/'game.sym').open('w') as f:subprocess.run(['arm-none-eabi-nm','--defined-only',str(engine/'pokeemerald.elf')],stdout=f,check=True)
  with (out/'game.sym').open('a') as f:subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)],stdout=f,check=True)
  identity=dict(host_source=head,base=BASE,game_source=GAME,ROM_SHA256=ROM,ELF_SHA256=ELF,input_Save_SHA256=SEED,host_SHA256=sha(out/'observer.c'),binary_SHA256=sha(out/'playtest'),routes={k:sha(v) for k,v in routes.items()},reconstructed_base_observer=base,frame_limit=100000,patrol_battle_frames_each=36000,battle_attempts=2,method='One separately authorised current Guard-first route and exact native cold; approved unchanged game build reused, new host compiled')
  (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');print('PASS frozen host compiled; no emulator');return
 identity=json.loads((out/'identity.json').read_text());assert identity['host_SHA256']==sha(out/'observer.c') and identity['binary_SHA256']==sha(out/'playtest')
 subprocess.run(['git','diff','--quiet',identity['host_source'],head,'--',*SCOPED,*PRESERVED],cwd=ROOT,check=True)
 assert not(out/'STOP.json').exists(),'STOP remains; no retry'
 summaryfile=out/'summary.json';summary=json.loads(summaryfile.read_text()) if summaryfile.exists() else []
 assert [x['stage'] for x in summary]==([] if a.stage=='patrol' else ['patrol']),'Exactly ONE route and dependent cold'
 d=out/a.stage;d.mkdir();save=out/(a.stage+'.sav');shutil.copyfile(seed if a.stage=='patrol' else out/'patrol.sav',save)
 state.seed_snapshot(save,d/'expected');shutil.copyfile(routes[a.stage],d/'input.route');assert sha(d/'input.route')==identity['routes'][a.stage]
 before=sha(save)
 with (d/'execution-claim.json').open('x') as f:json.dump(dict(execution_source=head,host_source=identity['host_source'],stage=a.stage,input_Save_SHA256=before,route_SHA256=sha(d/'input.route'),execution_limit=1,battle_attempts=2 if a.stage=='patrol' else 0),f,indent=2)
 with (d/'input.route').open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
  result=subprocess.run([str(out/'playtest'),str(engine/'pokeemerald.gba'),str(save),str(out/'game.sym')],cwd=d,stdin=inp,stdout=log,stderr=err)
 for f in d.glob('*.ppm'):
  im=Image.open(f);assert im.size==(240,160);im.save(f.with_suffix('.png'))
 log=(d/'replay.log').read_text();footer=re.search(r'assertions=(\d+)\n$',log);clock=re.search(r'PATROL_CLOCK absolute_frames=(\d+) valid_samples=(\d+) deferred_samples=(\d+) reentries=(\d+) unarmed_frames=(\d+) mutation_frames=(\d+) checkpoints=(\d+) battle_frames=(\d+) battle_attempts=(\d+) stage=(\d+)',log)
 verdict=dict(stage=a.stage,execution_source=head,host_source=identity['host_source'],exit=result.returncode,errors_bytes=(d/'errors.log').stat().st_size,assertions=int(footer[1]) if footer else None,input_Save_SHA256=before,output_Save_SHA256=sha(save),route_SHA256=sha(d/'input.route'),clock=dict(zip(['absolute_frames','valid_samples','deferred_samples','reentries','unarmed_frames','mutation_frames','checkpoints','battle_frames','battle_attempts','stage'],map(int,clock.groups()))) if clock else None)
 try:
  assert result.returncode==0 and not verdict['errors_bytes'] and footer and clock,'first native failure'
  c=verdict['clock'];assert c['absolute_frames']==c['valid_samples']+c['deferred_samples']+c['unarmed_frames']+c['mutation_frames']<=100000,'exact frame accounting'
  if a.stage=='patrol':
   assert c['battle_attempts']==2 and c['stage']==4;verdict['measurements']=travel(log)
   state.seed_snapshot(save,d/'disk');disk=state.snapshot(d/'disk');live=state.snapshot(d/'saved')
   for k in ('party','flags','logical','count','saved_count','counter','map','position'):assert disk[k]==live[k],('manual Save exact native persistence',k)
   assert disk['map']==[35,3] and disk['position']==[8,7];verdict['native_manual_Save_exact']=True
  else:
   assert c['battle_attempts']==c['battle_frames']==0 and before==sha(save)==sha(out/'patrol.sav');verdict['native_cold_exact']=True
  assert sha(seed)==SEED and sha(engine/'pokeemerald.gba')==ROM
 except Exception as e:
  verdict['validation_failure']=str(e);summary.append(verdict);summaryfile.write_text(json.dumps(summary,indent=2)+'\n');(out/'STOP.json').write_text(json.dumps(verdict,indent=2)+'\n');raise SystemExit('STOP: first failure preserved; no further emulator execution')
 summary.append(verdict);summaryfile.write_text(json.dumps(summary,indent=2)+'\n');print('PASS',a.stage,verdict['assertions'],'assertions',c['absolute_frames'],'exact frames; Save',sha(save))
if __name__=='__main__':main()
