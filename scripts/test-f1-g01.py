#!/usr/bin/env python3
"""Committed-source, ordinary-input D1 geometry previews; never a production gate."""
import importlib.util,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
assert not git('status','--porcelain'),'Commit changes first'
revision=git('rev-parse','HEAD');base=Path(os.environ['DCC_A01_BASE_RUN']).resolve()
# The live engine must remain exactly the accepted production source.
subprocess.run(['git','diff','--quiet','cee81f8f5dd5cce93990007f06491c8d607a7161',revision,'--','engine','scripts/playtest.c'],cwd=root,check=True)
assert hashlib.sha256((base/'production.gba').read_bytes()).hexdigest()=='5c4f865a95c0b9e4c65f13d86c8ba44c9082599432b387f6fc350c0bd99b7230'
out=Path(tempfile.mkdtemp(prefix='preview-',dir=root/'artifacts/floor1/g01'));print('Evidence:',out,flush=True)
(out/'tested-commit.txt').write_text(revision+'\n')
loader=importlib.util.spec_from_file_location('committed_snapshot',root/'scripts/floor1/committed-snapshot.py');snap=importlib.util.module_from_spec(loader);loader.loader.exec_module(snap)
source=out/'source';snap.snapshot(root,revision,source,os.environ.get('DCC_G01_CACHE'))
# Build compiler and hydrate only hash-checked upstream inputs through the pinned setup.
# No cached engine source, generated dependency, object, linker input or asset is copied.
with (out/'setup-toolchain.log').open('w') as log:
    subprocess.run(['bash',str(source/'scripts/setup-foundation.sh')],stdout=log,stderr=subprocess.STDOUT,check=True)
loader=importlib.util.spec_from_file_location('graybox',source/'scripts/floor1/opening-graybox.py');gray=importlib.util.module_from_spec(loader);loader.loader.exec_module(gray)
spec=json.loads((source/'scripts/contracts/f1-g01-opening.json').read_text())
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 arrival.ppm']
summary=[]
for opened in [False,True]:
    mode='open' if opened else 'closed';d=out/mode;d.mkdir()
    # Reset diagnostic inputs before rebuilding a variant; no compounded modifications.
    if opened:
        for p in ['src/new_game.c','data/maps/map_groups.json','data/layouts/layouts.json','data/event_scripts.s']:
            (source/'engine'/p).write_bytes(subprocess.check_output(['git','show',revision+':engine/'+p],cwd=root))
        shutil.rmtree(source/'engine/data/maps/DCC_OpeningPreview');shutil.rmtree(source/'engine/data/layouts/DCC_OpeningPreview')
    subprocess.run(['python3',str(source/'scripts/floor1/opening-graybox.py'),'--engine',str(source/'engine'),'--out',str(d)]+(['--opened'] if opened else []),stdout=(d/'export.log').open('w'),check=True)
    with (d/'build.log').open('w') as log:subprocess.run(['make','-C',str(source/'engine'),'-j2'],stdout=log,stderr=subprocess.STDOUT,check=True)
    rom=d/'diagnostic.gba';shutil.copyfile(source/'engine/pokeemerald.gba',rom)
    (d/'rom.sha256').write_text(hashlib.sha256(rom.read_bytes()).hexdigest()+'  diagnostic.gba\n')
    with (d/'game.sym').open('w') as log:subprocess.run(['arm-none-eabi-nm','-g','--defined-only',str(source/'engine/pokeemerald.elf')],stdout=log,check=True)
    cells=gray.geometry(spec,opened)
    def create(order,clip=False):
        lines=list(boot);position=tuple(spec['anchors']['arrival']);captures=0;walk=0;facing=128
        def expect():lines.append(f'expect 35 0 {position[0]} {position[1]} 0')
        def move(keys,frames,label=None):
            nonlocal captures,facing
            if clip:
                while frames:
                    n=min(3,frames);frames-=n;lines.append(f'step {n} {keys} motion-{captures:05d}.ppm');captures+=1
            else:lines.append(f'step {frames} {keys} -')
            facing=keys
            lines.append('step 40 0 '+(label.replace('_','-')+'.ppm' if label else '-'))
        def follow(target,label=None):
            nonlocal position,walk
            route=gray.path(cells,position,target);walk+=len(route)-1
            directions=[]
            for a,b in zip(route,route[1:]):directions.append({(0,-1):64,(1,0):16,(0,1):128,(-1,0):32}[(b[0]-a[0],b[1]-a[1])])
            i=0
            while i<len(directions):
                j=i+1
                while j<len(directions) and directions[j]==directions[i]:j+=1
                move(directions[i],16*(j-i)+(4 if directions[i]!=facing else 0));position=route[j];expect();i=j
            if label:lines.append('step 40 0 '+label.replace('_','-')+'.ppm')
        expect();lines+=['duo healthy','uses 8 40 2 40']
        if clip:
            follow(spec['anchors']['junction'],'junction');lines+=['quit'];return lines,walk
        for name in order:follow(spec['anchors'][name],name)
        # Every sampled lane is traversed across its clear width in both directions.
        for name,(x0,y0,x1,y1,width) in spec['width_samples'].items():
            follow((x0,y0));follow((x1,y1),name);follow((x0,y0))
        # Physical bounds, pillar and preview-object occupancy, not just BFS metadata.
        for target,keys,label in [((6,38),32,'west-wall'),((23,23),16,'pillar-collision'),((38,27),64,'actor-collision'),((55,42),16,'secret-edge'),(tuple(spec['anchors']['warden_door']),64,'north-edge')]:
            follow(target);move(keys,148,label);expect()
            if label=='actor-collision':lines.extend(['step 1 1 -','step 400 0 actor-dialogue.ppm','step 1 1 -','step 400 0 actor-anchor.ppm','step 1 1 -','step 120 0 -']);expect()
        follow(spec['anchors']['loop_home']);move(16,32+(4 if facing!=16 else 0),'loop-pass' if opened else 'loop-wall')
        if opened:position=(36,16)
        expect()
        follow(spec['anchors']['quiet_door'],'final-location')
        for flag in list(range(32,49))+list(range(2135,2140)):lines.append(f'flag {flag} 0')
        lines+=['duo healthy','uses 8 40 2 40','step 1 8 -','step 120 0 menu.ppm','step 1 128 -','step 20 0 -','step 1 128 -','step 20 0 -','step 1 1 -','step 160 0 save-choice.ppm','step 1 1 -','step 600 0 saved.ppm']
        expect();lines+=['quit'];return lines,walk
    orders=[('guard-first',['junction','quiet_door','workshop_door','trap','tag','secret','guard','howler','far_junction','warden_door','far_junction','quiet_door']),('howler-first',['junction','howler','guard','far_junction','warden_door','quiet_door'])]
    if opened:orders.append(('motion',[]))
    for name,order in orders:
        session=d/name;session.mkdir();lines,walk=create(order,name=='motion');(session/'input.route').write_text('\n'.join(lines)+'\n')
        with (session/'input.route').open() as inputs,(session/'replay.log').open('w') as log,(session/'errors.log').open('w') as errors:
            subprocess.run([str(base/'playtest'),str(rom),str(d/(name+'.sav')),str(d/'game.sym')],cwd=session,stdin=inputs,stdout=log,stderr=errors,check=True)
        expected=sum(x.startswith(('expect ','duo ','uses ','flag ')) for x in lines)
        assert (session/'replay.log').read_text().endswith(f'result=0 assertions={expected}\n') and not (session/'errors.log').stat().st_size
        for image in session.glob('*.ppm'):Image.open(image).save(image.with_suffix('.png'))
        summary.append({'route':f'{mode}/{name}','assertions':expected,'diagnostic':True,'walking_steps':walk});print(f'{mode}/{name} PASS {expected}',flush=True)
        if name!='motion':
            cold=d/(name+'-cold');cold.mkdir();coldlines=boot[:-1]+['step 600 0 cold.ppm',f"expect 35 0 {spec['anchors']['quiet_door'][0]} {spec['anchors']['quiet_door'][1]} 0",'duo healthy','uses 8 40 2 40']+[f'flag {f} 0' for f in list(range(32,49))+list(range(2135,2140))]+['quit'];(cold/'input.route').write_text('\n'.join(coldlines)+'\n')
            with (cold/'input.route').open() as inputs,(cold/'replay.log').open('w') as log,(cold/'errors.log').open('w') as errors:
                subprocess.run([str(base/'playtest'),str(rom),str(d/(name+'.sav')),str(d/'game.sym')],cwd=cold,stdin=inputs,stdout=log,stderr=errors,check=True)
            assert (cold/'replay.log').read_text().endswith('result=0 assertions=25\n') and not (cold/'errors.log').stat().st_size
            Image.open(cold/'cold.ppm').save(cold/'cold.png');summary.append({'route':f'{mode}/{name}-cold','assertions':25,'diagnostic':True});print(f'{mode}/{name}-cold PASS25',flush=True)
    for ext in ['map','elf']:shutil.copyfile(source/'engine'/('pokeemerald.'+ext),d/('diagnostic.'+ext))
(out/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
assert git('rev-parse','HEAD')==revision and not git('status','--porcelain')
print('PASS',len(summary),'diagnostic sessions;',sum(x['assertions'] for x in summary),'assertions. Production unchanged; G01 live relocation is pending.',flush=True)
