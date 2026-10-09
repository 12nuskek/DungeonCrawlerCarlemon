#!/usr/bin/env python3
"""One pinned unprepared Warden battle, first stairs NO/YES, ordinary Save/cold."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,importlib.util,json,re,shutil,subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='1263d8b915f37d70bdcb04167c9088cd107666bc'
GAME='c643f01c11ec68119b0347b107ee20115131debc'
ROM='b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a'
SEED='026c16feccd0a1741ff0c3ec077e7272fc6ee43bf0e4fa12ab8953c50523220a'

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

parser=argparse.ArgumentParser()
parser.add_argument('--build',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--seed',type=Path,required=True)
parser.add_argument('--stage',choices=['prepare','first-clear','cold'],required=True)
args=parser.parse_args()
assert not git('status','--porcelain'),'Commit separate contract/source before execution'
head=git('rev-parse','HEAD');build=args.build.resolve();out=args.output.resolve();seed=args.seed.resolve()
assert sha(seed)==SEED
assert (build/'tested-commit.txt').read_text().strip()==GAME
subprocess.run(['git','diff','--quiet',GAME,head,'--','engine'],cwd=ROOT,check=True)
subprocess.run(['git','diff','--quiet',BASE,head,'--','docs/floor1/accepted-plan.md',
    'docs/floor1/g01e-recovery-contract.md','docs/floor1/g01e-new-save-recovery-contract.md',
    'scripts/test-f1-g01e-recovery.py','scripts/test-f1-g01e-current-patrol.py',
    'scripts/test-f1-g01e-new-save-recovery.py','scripts/floor1/new-save-recovery-host.py',
    'docs/evidence/floor1/g01e/recovery','docs/evidence/floor1/g01e/new-save-recovery',
    'docs/evidence/floor1/g01e/attempts'],cwd=ROOT,check=True)
engine=build/'source/engine';rom=engine/'pokeemerald.gba';assert sha(rom)==ROM
out.mkdir(parents=True,exist_ok=True)
spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
geometry=module('warden_geometry',ROOT/'scripts/floor1/relocation-graybox.py')
routes=module('warden_routes',ROOT/'scripts/floor1/live-route.py')
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -',
    'step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 cold.ppm','ready']
patrol=['flag 2135 1','flag 2136 1','flag 2137 1','flag 46 0','flag 49 0',
    'item 13 0','item 378 2','item 22 0','item 379 0','item 380 0']
initial=['expect 35 0 37 31 7','levels 11 10','growth 11 748 0 10 1058 0','duo healthy',
    'vitals 38 30 0 0 8 40 2 40','uses 8 40 2 40']+patrol+['flag 47 0','flag 48 0','flag 2138 0','flag 2139 0']
def won(checkpoint):
    return ['levels 12 10','growth 12 974 0 10 1284 0']+patrol+[
        'flag 47 1',f'flag 48 {int(checkpoint)}','flag 2138 1','flag 2139 0']
def R(key,pos,facing=1):return routes.Route(spec,geometry,key,pos,facing,7)
def talk(r,button,prefix,label,finish=True):
    if r.face!=button:r.step(1,button);r.face=button;r.step(40)
    r.step(1,1);r.step(400);r.lines.append('pages '+prefix+' '+label)
    if finish:r.lines+=['dialog 3600','ready'];r.step(40);r.expect()
def repeat(r,prefix,checkpoint):
    r.anchor('warden');talk(r,128,prefix,'DCC_Live_Boss_Text_Won')
    r.lines+=won(checkpoint)+['xp same','money same','preserve check']
def stairs(r,prefix,no,checkpoint):
    r.anchor('stairs');talk(r,128,prefix,'DCC_F1D1Warden_StairsText',False)
    r.lines.append('choice-ready');r.step(40,0,prefix+'-choice.ppm')
    if no:r.step(1,128);r.step(20)
    r.step(1,1);r.step(400)
    if no:
        r.lines.append('pages '+prefix+'-cancelled DCC_Boss_Text_StairsCancel')
        r.lines+=['dialog 3600','ready'];r.step(40);r.expect();r.lines.append('choice-result 0')
        r.lines+=won(checkpoint)+['tile 12 11 13866']
    else:
        r.lines+=['ready','choice-result 1'];r.key='checkpoint';r.pos=(4,4);r.face=128;r.expect()
        r.step(40,0,prefix+'-arrived.ppm');r.lines+=won(True)
    r.lines+=['xp same','money same','preserve check']
def route(stage,vitals=None):
    if stage=='first-clear':
        r=R('field',(37,31));r.lines+=initial+['money remember','inventory start','no-battle start']
        r.anchor('warden_door');r.anchor('warden')
        r.lines+=['duo healthy','vitals 38 30 0 0 8 40 2 40']+patrol+['flag 47 0','flag 48 0','flag 2138 0','flag 2139 0','no-battle end']
        r.step(1,128);r.face=128;r.step(40);r.lines.append('engage 3600')
        r.step(1200,0,'warden-start.ppm')
        r.lines+=['foes 42 30','battle 1 4 0 8 2 1 0','pilot fortify 30000']
        r.step(600,0,'warden-result.ppm');r.lines+=['dialog 6000','ready'];r.expect()
        r.lines+=won(False)+['money gain 360','inventory check','xp remember','money remember',
            'vitals record','preserve start','no-battle start','tile 12 11 13866']
        repeat(r,'warden-resolved',False)
        stairs(r,'stairs-no',True,False);stairs(r,'stairs-yes',False,False)
        r.anchor('review');talk(r,128,'opening-checkpoint','DCC_F1D1Checkpoint_ReviewText')
        r.lines+=won(True)+['xp same','money same','preserve check']
        r.save();r.lines=[x for x in r.lines if x!='snapshot']
        r.lines+=won(True)+['xp same','money same','preserve check','vitals record','no-battle end']
    else:
        assert vitals is not None and len(vitals)==8
        v='vitals '+' '.join(map(str,vitals))
        r=R('checkpoint',(8,6));r.expect();r.lines+=won(True)+[v,'xp remember','money remember','preserve start','no-battle start']
        talk(r,128,'cold-opening-checkpoint','DCC_F1D1Checkpoint_ReviewText')
        r.anchor('arrival');repeat(r,'cold-warden-resolved',True)
        stairs(r,'cold-stairs-no',True,True);stairs(r,'cold-stairs-yes',False,True)
        r.anchor('review');r.lines+=won(True)+[v,'xp same','money same','preserve check','no-battle end']
        r.step(40,0,'cold-returned.ppm')
    return boot+r.lines+['quit']

if args.stage=='prepare':
    assert not (out/'identity.json').exists(),'Preserve prepared host and all executions'
    code,base=module('warden_host',ROOT/'scripts/floor1/warden-first-clear-host.py').generate(git)
    (out/'observer.c').write_text(code)
    with (out/'host-build.log').open('w') as log:
        subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],stdout=log,stderr=subprocess.STDOUT,check=True)
    with (out/'game.sym').open('w') as symbols:
        subprocess.run(['arm-none-eabi-nm','--defined-only',str(engine/'pokeemerald.elf')],stdout=symbols,check=True)
    with (out/'game.sym').open('a') as symbols:
        subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)],stdout=symbols,check=True)
    plan='\n'.join(route('first-clear'))+'\n';(out/'planned-first-clear.route').write_text(plan)
    identity=dict(runner=head,base=BASE,game=GAME,rom=ROM,seed_sha256=SEED,host_sha256=sha(out/'observer.c'),
        first_route_sha256=sha(out/'planned-first-clear.route'),reconstructed_base_observer=base,
        method='Single unprepared Warden first-clear from reviewed new ordinary save; actual normal controls, read-only observer, whole-battle30000 bound')
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    print('PASS prepared/compiled/frozen route; no emulator');raise SystemExit(0)

identity=json.loads((out/'identity.json').read_text());assert identity['host_sha256']==sha(out/'observer.c')
subprocess.run(['git','diff','--quiet',identity['runner'],head,'--','engine',
    'scripts/test-f1-g01e-warden-first-clear.py','scripts/floor1/warden-first-clear-host.py',
    'scripts/floor1/warden-attempt-bound.h','scripts/floor1/native-text-observer.py',
    'scripts/floor1/live-route.py','scripts/contracts/f1-g01d-relocation.json'],cwd=ROOT,check=True)
assert not (out/'STOP.json').exists(),'Stop on failure; parent direction required'
summary_path=out/'summary.json';summary=json.loads(summary_path.read_text()) if summary_path.exists() else []
assert [x['stage'] for x in summary]==([] if args.stage=='first-clear' else ['first-clear'])
d=out/args.stage;d.mkdir();save=out/(args.stage+'.sav')
if args.stage=='first-clear':
    assert identity['first_route_sha256']==sha(out/'planned-first-clear.route')
    lines=(out/'planned-first-clear.route').read_text();shutil.copyfile(seed,save)
else:
    prior=(out/'first-clear/replay.log').read_text()
    records=re.findall(r'^VITALS (.+)$',prior,re.M);assert len(records)==2 and records[0]==records[1]
    vitals=list(map(int,records[0].split()));lines='\n'.join(route('cold',vitals))+'\n'
    shutil.copyfile(out/'first-clear.sav',save)
path=d/'input.route';path.write_text(lines);before=sha(save)
with (d/'execution-claim.json').open('x') as claim:
    json.dump(dict(runner=head,stage=args.stage,route_sha256=sha(path),input_save_sha256=before,attempt_limit=1,battle_frame_limit=30000),claim,indent=2)
with path.open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
    result=subprocess.run([str(out/'playtest'),str(rom),str(save),str(out/'game.sym')],cwd=d,stdin=inp,stdout=log,stderr=err)
for frame in d.glob('*.ppm'):
    im=Image.open(frame);assert im.size==(240,160);im.save(frame.with_suffix('.png'))
log=(d/'replay.log').read_text();footer=re.search(r'assertions=(\d+)\n$',log)
counter=re.search(r'WARDEN battle_frames=(\d+) attempts=(\d+)\n',log)
verdict=dict(stage=args.stage,runner=head,host_runner=identity['runner'],exit=result.returncode,
    errors_bytes=(d/'errors.log').stat().st_size,assertions=int(footer[1]) if footer else None,
    battle_frames=int(counter[1]) if counter else None,attempts=int(counter[2]) if counter else None,
    input_save_sha256=before,output_save_sha256=sha(save),route_sha256=sha(path),reconstructed_input=True)
summary.append(verdict);summary_path.write_text(json.dumps(summary,indent=2)+'\n')
if result.returncode or verdict['errors_bytes'] or footer is None or counter is None:
    (out/'STOP.json').write_text(json.dumps(verdict,indent=2)+'\n');raise SystemExit('STOP: preserve failure; no further execution')
assert sha(rom)==ROM and sha(seed)==SEED
if args.stage=='first-clear':assert verdict['attempts']==1 and 0<verdict['battle_frames']<=30000
else:assert verdict['attempts']==verdict['battle_frames']==0 and before==sha(save)==sha(out/'first-clear.sav')
print('PASS',args.stage,verdict['assertions'],'assertions;',verdict['battle_frames'],'battle frames; save',sha(save),flush=True)
