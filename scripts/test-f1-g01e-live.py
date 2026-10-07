#!/usr/bin/env python3
"""Live opening controller travel, battles/recovery, loop persistence and map words."""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json,os,re,shutil,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    l=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(l);l.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
assert not git('status','--porcelain'),'Commit first'
head=git('rev-parse','HEAD');ordinary=Path(os.environ['DCC_G01E_ORDINARY_RUN']).resolve();identity=json.loads((ordinary/'identity.json').read_text())
subprocess.run(['git','diff','--quiet',identity['runner_source'],head,'--','engine','scripts/playtest.c','scripts/floor1/live-save-observer.py','scripts/floor1/walking-harness.py'],cwd=ROOT,check=True)
build=Path(identity['build']);rom=build/'source/engine/pokeemerald.gba';digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert digest(rom)==identity['rom_sha256']
out=Path(tempfile.mkdtemp(prefix='gameplay-',dir=ROOT/'artifacts/floor1/g01e'));print('Evidence:',out,flush=True)
spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text());maps=spec['maps'];ids=spec['production_identity_proposal']['maps'];g=module('geometry',ROOT/'scripts/floor1/relocation-graybox.py');route=module('route',ROOT/'scripts/floor1/live-route.py');gate=module('gate',ROOT/'scripts/floor1/travel-measurements.py');ceiling=json.loads((ROOT/'scripts/contracts/f1-g01b-recovery.json').read_text())
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 cold.ppm'];summary=[]
def R(key,pos=(4,5),flags=7):return route.Route(spec,g,key,pos,1,flags)
def run(name,save,lines,travel=None):
    d=out/name;d.mkdir();(d/'input.route').write_text('\n'.join(lines+['quit'])+'\n')
    with (d/'input.route').open() as inputs,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:subprocess.run([str(ordinary/'playtest'),str(rom),str(save),str(ordinary/'game.sym')],cwd=d,stdin=inputs,stdout=log,stderr=err,check=True)
    log=(d/'replay.log').read_text();checks=int(re.search(r'result=0 assertions=(\d+)\n$',log)[1]);assert not (d/'errors.log').stat().st_size
    states=[json.loads(v) for v in re.findall(r'^STATE (.+)$',log,re.M)]
    if states:(d/'states.json').write_text(json.dumps(states,indent=2)+'\n')
    metrics=[dict(name=a,frames=int(b),walking_frames=int(c),steps=int(e),warps=int(f)) for a,b,c,e,f in re.findall(r'MEASURE name=(\S+) frames=(\d+) walking=(\d+) tiles=(\d+) warps=(\d+)',log)]
    if travel:gate.validate(travel,metrics,spec,ceiling)
    else:assert not metrics
    for p in d.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
    summary.append(dict(route=name,assertions=checks,measurements=metrics,states=len(states),production=True));print(name,'PASS',checks,metrics,flush=True);return states
def copied(name,original):
    original=Path(original);p=out/(name+'.sav');shutil.copyfile(original,p);return p,digest(original)
def fight(r,policy,flag_id,win=True,incap=None):
    r.step(1,128);r.face=128;r.step(40);r.lines+=['engage 3600'];r.step(1200,0,'battle-start.ppm');r.lines+=['pilot '+policy+' 36000'];r.step(600,0,'battle-result.ppm');r.lines+=['dialog 6000','ready'];r.expect()
    if incap is not None:r.lines.append('incap '+str(incap))
    r.lines.append(f'flag {flag_id} {int(win)}')
    if not win:r.lines+=['duo healthy','uses 8 40 2 40']
def heal(r):r.talk(128,'guide-rest');r.lines+=['duo healthy','uses 8 40 2 40']
def to_field(r):
    while r.key!='field':r.anchor('arrival')
def full_words(key,state):
    raw=(build/'source/engine/data/layouts'/ids[key]['name']/'map.bin').read_bytes();words=list(struct.unpack('<'+'H'*(len(raw)//2),raw));w=maps[key]['width'];flags=bytes.fromhex(state['regions']['flags']);flag=lambda n:(flags[n//8]>>(n%8))&1
    if key=='field':
        words[42*w+46]=0x329c if flag(40) else 0x328f
        text=(build/'source/engine/src/data/dcc_opening.h').read_text()
        for x,y,closed,opened in re.findall(r'MAP_DCC_F1D1FIELD, (\d+), (\d+), FLAG_DCC_D1_LOOP_OPEN, 0x([0-9A-F]+), 0x([0-9A-F]+)',text):words[int(y)*w+int(x)]=int(opened if flag(49) else closed,16)
    elif key=='boss':words[11*w+12]=0x362a if flag(47) else 0x3618
    return [f'tile {i%w} {i//w} {v}' for i,v in enumerate(words)]
# Fresh new game + once-only reader/supply grant; guide and trial remain actual
# original content at reviewed new anchors. No synthetic input for this route.
r=R('field',(8,38),1);fresh=out/'fresh.sav';lines=boot+['dialog 6000','ready','snapshot'];r.anchor('note');r.flags=3;r.talk(64,'note');r.lines+=['flag 33 1','flag 36 1'];r.anchor('supply');r.talk(64,'supply');r.lines+=['item 13 2','flag 38 1'];r.talk(64,'supply-repeat');r.lines+=['item 13 2'];r.anchor('quiet_door');r.anchor('guide');r.flags=7;heal(r);r.anchor('trial');fight(r,'offensive',2135);r.lines+=['flag 37 1'];r.save();states=run('fresh-trial',fresh,lines+r.lines);assert states[0]['version']==1 and states[0]['loop']==0
# Both actual patrol orders, each wounded encounter followed by measured normal
# guide recovery/re-entry. Battle wins and return travel share the same route.
original=ROOT/'artifacts/floor1/a01/run-I7PJq0/both-pending.sav'
for name,order in [('guard-first',['guard','howler']),('howler-first',['howler','guard'])]:
    save,sha=copied(name,original);r=R('field',(37,31));r.lines+=['flag 2136 0','flag 2137 0']
    for who in order:
        r.anchor(who);fight(r,'offensive',2136 if who=='guard' else 2137)
        r.lines.append('measure start '+who+'-out');r.anchor('quiet_door');r.anchor('guide');r.lines.append('measure stop');heal(r)
        r.lines.append('measure start '+who+'-back');to_field(r);r.anchor(who);r.lines.append('measure stop')
    r.lines+=['flag 2136 1','flag 2137 1','flag 49 0'];r.save();states=run(name,save,boot+r.lines,travel=name);assert digest(original)==sha
    cold,unused=copied(name+'-cold',save);state=states[-1];run(name+'-cold-full',cold,boot+['ready','snapshot',f'expect 35 0 {r.pos[0]} {r.pos[1]} 7','flag 49 0']+full_words('field',state))
# Pre-boss hub route uses its unchanged exact names/ceilings and real guide.
original=ROOT/'artifacts/floor1/a01/run-I7PJq0/boss-pending.sav';save,sha=copied('preboss',original);r=R('field',(51,27));r.lines.append('measure start preboss-out');r.anchor('quiet_door');r.anchor('guide');r.lines.append('measure stop');heal(r);r.lines.append('measure start preboss-back');to_field(r);r.anchor('warden_door');r.anchor('warden');r.lines.append('measure stop');r.save();states=run('preboss',save,boot+r.lines,travel='preboss');assert digest(original)==sha
# Normal wrong-side gate denial, far-side opening, two-way traversal, manual Save
# and cold persistence. Optional gate changes no old outcome or consumable.
original=ROOT/'artifacts/floor1/a01/run-I7PJq0/both-pending.sav';save,sha=copied('loop',original);r=R('field',(37,31));r.anchor('loop_home');r.talk(16,'loop-wrong-side');r.lines+=['flag 49 0'];r.anchor('loop_far');r.talk(32,'loop-open');r.lines+=['flag 49 1'];r.opened=True;r.anchor('loop_home');r.anchor('loop_far');r.save();states=run('loop',save,boot+r.lines);assert digest(original)==sha
state=states[-1];cold,unused=copied('loop-cold',save);r=R('field',(36,16));r.opened=True;r.anchor('loop_home');r.anchor('loop_far');r.lines+=['flag 49 1','flag 2136 0','flag 2137 0'];run('loop-cold-full',cold,boot+['ready','snapshot','expect 35 0 36 16 7','flag 49 1']+full_words('field',state)+r.lines)
# Ordinary migrated boss-pending file: defeat and immediate zero-walk local retry.
original=ROOT/'artifacts/floor1/a01/run-I7PJq0/boss-loss.sav';save,sha=copied('boss-recovery',original);r=R('boss',(8,7));fight(r,'loss',47,False,6);fight(r,'fortify',47,True);r.save();states=run('boss-recovery-and-win',save,boot+r.lines);assert digest(original)==sha
# Original resources provide2 scrap. Normal recipe/cache controls author a new
# prepared version1 seed, avoiding edited-in flags/resources. Repeated cache use
# and a cold reload cannot award/consume twice.
save,sha=copied('preparation',original);r=R('boss',(8,7));to_field(r);r.anchor('workshop_door');r.anchor('workbench');r.talk(128,'crafted');r.lines+=['item 378 0','item 380 1'];r.anchor('cache');r.talk(128,'blasted');r.lines+=['flag 46 1','item 380 0','item 22 1'];r.talk(128,'cache-repeat');r.lines+=['item 22 1','item 380 0'];r.save();run('ordinary-preparation',save,boot+r.lines);assert digest(original)==sha
prepared,unused=copied('prepared-recovery',save);r=R('workshop',(12,9));r.talk(128,'cache-cold-repeat');r.lines+=['item 22 1','item 380 0','flag 46 1'];to_field(r);r.anchor('warden_door');r.anchor('warden');fight(r,'loss',47,False,6);r.lines+=['flag 46 1'];fight(r,'offensive',47);r.lines+=['flag 2139 1','flag 2138 0'];r.anchor('stairs');r.step(1,128);r.face=128;r.step(40);r.step(1,1);r.step(400,0,'stairs-offer.ppm');r.lines+=['dialog 6000','ready'];r.key='checkpoint';r.pos=(4,4);r.expect();r.lines+=['flag 48 1'];r.anchor('review');r.talk(128,'opening-checkpoint');r.save();states=run('prepared-recovery-win-stairs',prepared,boot+r.lines)
state=states[-1];cold,unused=copied('prepared-ending-cold',prepared);run('prepared-ending-cold-full',cold,boot+['ready','snapshot','expect 35 4 8 6 7','flag 46 1','flag 47 1','flag 48 1','item 22 1','item 380 0']+full_words('checkpoint',state))
# All five full buffers after ordinary cold loads, including newly authored
# Quiet/Workshop and post-win arena presentation, use source words plus flags.
for name,key,save,pos in [('quiet','quiet',fresh,(10,7)),('workshop','workshop',out/'preparation.sav',(12,9)),('warden','boss',out/'boss-recovery.sav',(8,7))]:
    cold,unused=copied('full-'+name,save);states=run('full-'+name+'-state',cold,boot+['ready','snapshot']);run('full-'+name+'-words',cold,boot+[f'expect 35 {ids[key]["map_num"]} {pos[0]} {pos[1]} 7']+full_words(key,states[0]))
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'identity.json').write_text(json.dumps(dict(runner=head,compiled_source=identity['compiled_source'],rom_sha256=digest(rom),ordinary_runtime=str(ordinary),method='Actual live production controllers, ordinary copied inputs/fresh game, unmodified strict walking ceilings, recipe-created prepared file, manual Save/cold reload, read-only observer. No RAM/save input patches, engine balance or human pacing claim.'),indent=2)+'\n')
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
print('PASS',len(summary),'live sessions',sum(v['assertions'] for v in summary),'assertions')
