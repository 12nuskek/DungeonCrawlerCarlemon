#!/usr/bin/env python3
"""Fresh committed five-map diagnostics; no production adoption or save migration."""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json,os,re,shlex,shutil,struct,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=root,text=True).strip()
def module(name,path):
    l=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(l);l.loader.exec_module(m);return m
assert not git('status','--porcelain'),'Commit before testing'
head=git('rev-parse','HEAD')
retained=Path(os.environ['DCC_G01D_CLOSED_RUN']).resolve() if os.environ.get('DCC_G01D_CLOSED_RUN') else None
if retained:
    compiled_source=(retained/'tested-commit.txt').read_text().strip()
    subprocess.run(['git','diff','--quiet',compiled_source,head,'--','engine','scripts/playtest.c','scripts/contracts/f1-g01d-relocation.json','scripts/floor1/relocation-graybox.py','scripts/floor1/coordinated-graybox.py','scripts/floor1/walking-harness.py'],cwd=root,check=True)
    assert hashlib.sha256((retained/'closed/diagnostic.gba').read_bytes()).hexdigest()==(retained/'closed/rom.sha256').read_text().split()[0]
subprocess.run(['git','diff','--quiet','0cb6674',head,'--','engine','scripts/playtest.c','scripts/floor1/coordinated-graybox.py','scripts/contracts/f1-g01b-coordinated.json','scripts/floor1/travel-measurements.py'],cwd=root,check=True)
out=Path(tempfile.mkdtemp(prefix='complete-',dir=root/'artifacts/floor1/g01d'));print('Evidence:',out,flush=True)
(out/'tested-commit.txt').write_text(head+'\n')
snap=module('snapshot',root/'scripts/floor1/committed-snapshot.py');source=out/'source'
snap.snapshot(root,head,source,os.environ.get('DCC_G01_CACHE'),['scripts/contracts/f1-g01b-coordinated.json','scripts/contracts/f1-g01b-recovery.json','scripts/contracts/f1-g01d-relocation.json','scripts/floor1/coordinated-graybox.py','scripts/floor1/relocation-graybox.py','scripts/floor1/walking-harness.py','scripts/floor1/travel-measurements.py'])
with (out/'setup.log').open('w') as log:subprocess.run(['bash',str(source/'scripts/setup-foundation.sh')],stdout=log,stderr=subprocess.STDOUT,check=True)
g=module('geometry',source/'scripts/floor1/relocation-graybox.py');walking=module('walking',source/'scripts/floor1/walking-harness.py');gate=module('travel_gate',source/'scripts/floor1/travel-measurements.py')
spec=json.loads((source/'scripts/contracts/f1-g01d-relocation.json').read_text());ceiling=json.loads((source/'scripts/contracts/f1-g01b-recovery.json').read_text())
def source_audit(d):
    rows=[line.split(None,3) for line in git('ls-tree','-r',head,'engine').splitlines()]
    expected={path:blob for mode,kind,blob,path in rows if kind=='blob'}
    allowed={'engine/src/new_game.c','engine/data/maps/map_groups.json','engine/data/layouts/layouts.json','engine/data/event_scripts.s'}
    # git hash-object applies committed .gitattributes (including CRLF text
    # normalization); these are canonical Git inputs, not raw-byte claims.
    hashes=subprocess.check_output(['git','hash-object','--stdin-paths'],cwd=source,
        input=''.join(str(source/p)+'\n' for p in expected),text=True).splitlines()
    mismatches={p:{'original_git_blob':expected[p],'diagnostic_git_blob':h} for p,h in zip(expected,hashes) if expected[p]!=h}
    assert len(hashes)==len(expected) and set(mismatches)==allowed,mismatches
    expected_c={p for p in expected if p.endswith('.c')}
    actual_c={str(p.relative_to(source)) for p in (source/'engine').rglob('*.c')}
    assert actual_c==expected_c,('Unexpected C source',actual_c-expected_c,expected_c-actual_c)
    (d/'source-review.json').write_text(json.dumps({'committed_source':head,'tracked_inputs':len(expected),'C_inputs':len(expected_c),'game_C_inputs':sum(p.startswith('engine/src/') for p in expected_c),
        'unexpected_C':[],'approved_fixture_modifications':mismatches,'other_tracked_git_blob_identities_match':True,
        'method':'Fresh committed archive; only separately pinned toolchain/three verified multiboot inputs hydrated. All other tracked Git-canonical blob hashes match; no engine cache.'},indent=2)+'\n')
code=walking.instrument(git('show',head+':scripts/playtest.c')+'\n')
code=code.replace('!number(values[0],15,&tx)','!number(values[0],255,&tx)').replace('!number(values[1],11,&ty)','!number(values[1],255,&ty)')
code=code.replace('strncmp(line,"tile ",5) &&','strncmp(line,"extent ",7) && strncmp(line,"tile ",5) &&')
code=code.replace('        if (!strncmp(line,"tile ",5)) {','''        if (!strncmp(line,"extent ",7)) {
            unsigned w,h;char trailing;
            if (!maplayout || sscanf(line,"extent %u %u %c",&w,&h,&trailing)!=2 || core->busRead32(core,maplayout)!=w || core->busRead32(core,maplayout+4)!=h) {result=25;break;}
            checks++;printf("PASS %s",line);continue;
        }
        if (!strncmp(line,"tile ",5)) {''')
assert 'busWrite' not in code
(out/'walking.c').write_text(code)
subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',*shlex.split(os.environ.get('DCC_TEST_CFLAGS','')),str(out/'walking.c'),*shlex.split(os.environ.get('DCC_TEST_LDFLAGS','')),'-lmgba','-o',str(out/'playtest')],check=True)
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 arrival.ppm']
flags=list(range(32,50))+list(range(2135,2140));summary=[]
class Route:
    def __init__(self,opened,clip=False):self.opened=opened;self.key='field';self.pos=tuple(spec['maps']['field']['anchors']['arrival']);self.face=0;self.lines=list(boot);self.clip=clip;self.frames=0;self.steps=0;self.expect()
    @property
    def m(self):return spec['maps'][self.key]
    def expect(self):self.lines.append(f'expect 35 {self.m["map_num"]} {self.pos[0]} {self.pos[1]} 0')
    def step(self,n,key,label='-'):
        label=label.replace('_','-')
        if key in [16,32,64,128]:self.face=key
        if self.clip:
            for _ in range(n):self.lines.append(f'step 1 {key} frame-{self.frames:05d}.ppm');self.frames+=1
        else:self.lines.append(f'step {n} {key} {label}')
    def capture(self,label):self.step(40,0,label+'.ppm')
    def follow(self,end,label=None):
        # Standing on an arrival warp does not trigger it a second time. Leave
        # and re-enter with ordinary walking before claiming another transition.
        if tuple(end)==self.pos and any(tuple(w['at'])==self.pos for w in self.m['warps']):
            legal=g.cells(self.m,self.opened)-{tuple(w['at']) for w in self.m['warps']}
            x,y=self.pos
            neighbor=next((n for n in [(x,y+1),(x+1,y),(x,y-1),(x-1,y)] if n in legal),None)
            assert neighbor is not None
            self.follow(neighbor)
        route=g.path(self.m,self.opened,self.pos,end);self.steps+=len(route)-1
        keys=[{(0,-1):64,(1,0):16,(0,1):128,(-1,0):32}[(b[0]-a[0],b[1]-a[1])] for a,b in zip(route,route[1:])];i=0
        while i<len(keys):
            j=i+1
            while j<len(keys) and keys[j]==keys[i]:j+=1
            self.step(16*(j-i)+(4 if keys[i]!=self.face else 0),keys[i]);self.face=keys[i];self.pos=route[j];self.step(40,0);i=j
            if i<len(keys):self.expect()
        warp=next((w for w in self.m['warps'] if tuple(w['at'])==tuple(end)),None)
        if warp:
            self.step(300,0);self.key=next(k for k,v in spec['maps'].items() if v['map_num']==warp['dest']);self.pos=tuple(self.m['warps'][warp['dest_warp']]['at'])
        self.expect()
        if label:self.capture(label)
    def anchor(self,name,label=None):self.follow(self.m['anchors'][name],label)
    def measure(self,name):self.lines.append('measure start '+name)
    def stop(self):self.lines.append('measure stop')
    def guide(self):
        assert self.key=='field';self.anchor('quiet_door','quiet-arrival');assert self.key=='quiet';self.anchor('guide','guide-approach')
    def heal(self):
        assert self.key=='quiet' and self.pos==tuple(self.m['anchors']['guide']);self.step(1,128);self.step(40,0);self.step(1,1);self.step(400,0,'guide-rest.ppm');self.lines+=['duo healthy','uses 8 40 2 40'];self.step(1,1);self.step(400,0);self.step(1,2);self.step(40,0);self.expect()
    def exit(self):
        assert self.key!='field';self.anchor('arrival')
        while self.key!='field':self.anchor('arrival')
    def stairs(self):
        assert self.key=='boss';self.anchor('stairs','stairs-approach');self.step(1,128);self.step(40,0);self.step(1,1);self.step(400,0,'checkpoint-arrival.ppm');self.key='checkpoint';self.pos=(4,3);self.face=128;self.expect()
    def talk(self,button,label):
        self.step(1,button);self.step(40,0);self.step(1,1);self.step(400,0,label+'.ppm');self.step(1,1);self.step(400,0);self.step(1,2);self.step(40,0);self.expect()
    def unchanged(self):self.lines+=['duo healthy','uses 8 40 2 40']+[f'flag {v} 0' for v in flags]
    def save(self):
        self.step(1,8);self.step(120,0);self.step(1,128);self.step(20,0);self.step(1,128);self.step(20,0);self.step(1,1);self.step(160,0);self.step(1,1);self.step(600,0,'saved.ppm');self.expect()
def result(d,name,lines):
    session=d/name
    checks=sum(v.startswith(('expect ','duo ','uses ','flag ','tile ','extent ')) for v in lines);log=(session/'replay.log').read_text();assert log.endswith(f'result=0 assertions={checks}\n') and not (session/'errors.log').stat().st_size
    for p in session.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
    metrics=[{'name':a,'frames':int(b),'walking_frames':int(c),'steps':int(e),'warps':int(f)} for a,b,c,e,f in re.findall(r'MEASURE name=(\S+) frames=(\d+) walking=(\d+) tiles=(\d+) warps=(\d+)',log)]
    if name in {'workshop-route','checkpoint-route','workshop-route-cold-buffer','checkpoint-route-cold-buffer'}:assert not metrics
    else:gate.validate(name,metrics,spec,ceiling)
    summary.append({'route':f'{d.name}/{name}','assertions':checks,'diagnostic':True,'measurements':metrics});print(d.name,name,'PASS',checks,metrics,flush=True);return session
def run(d,name,rom,sym,save,lines):
    session=d/name;session.mkdir();(session/'input.route').write_text('\n'.join(lines+['quit'])+'\n')
    with (session/'input.route').open() as inputs,(session/'replay.log').open('w') as log,(session/'errors.log').open('w') as errors:subprocess.run([str(out/'playtest'),str(rom),str(save),str(sym)],cwd=session,stdin=inputs,stdout=log,stderr=errors,check=True)
    return result(d,name,lines)
for opened in [False,True]:
    mode='open' if opened else 'closed';d=out/mode
    d.mkdir()
    if opened:
        for p in ['src/new_game.c','data/maps/map_groups.json','data/layouts/layouts.json','data/event_scripts.s']:(source/'engine'/p).write_bytes(subprocess.check_output(['git','show',head+':engine/'+p],cwd=root))
        for m in spec['maps'].values():
            for area in ['maps','layouts']:shutil.rmtree(source/'engine/data'/area/m['name'])
    subprocess.run(['python3','-B',str(source/'scripts/floor1/relocation-graybox.py'),'--engine',str(source/'engine'),'--out',str(d)]+(['--opened'] if opened else []),stdout=(d/'export.log').open('w'),check=True)
    source_audit(d)
    rom=d/'diagnostic.gba';sym=d/'game.sym'
    if retained and not opened:
        assert json.loads((d/'map-identities.json').read_text())==json.loads((retained/'closed/map-identities.json').read_text())
        shutil.copyfile(retained/'closed/diagnostic.gba',rom);shutil.copyfile(retained/'closed/game.sym',sym)
        (d/'build-reuse.json').write_text(json.dumps({'compiled_source':compiled_source,'original_build':str(retained/'closed/build.log'),'method':'Exact original clean diagnostic ROM; fresh archive/export identities match; no engine/cache inputs copied. Only host doorway re-entry controls changed.'},indent=2)+'\n')
    else:
        with (d/'build.log').open('w') as log:subprocess.run(['make','-C',str(source/'engine'),'-j2'],stdout=log,stderr=subprocess.STDOUT,check=True)
        shutil.copyfile(source/'engine/pokeemerald.gba',rom)
        with sym.open('w') as log:subprocess.run(['arm-none-eabi-nm','-g','--defined-only',str(source/'engine/pokeemerald.elf')],stdout=log,check=True)
    (d/'rom.sha256').write_text(hashlib.sha256(rom.read_bytes()).hexdigest()+'  diagnostic.gba\n')
    for label,order,final in [('guard-first',['guard','howler'],'field'),('howler-first',['howler','guard'],'quiet'),('preboss',['howler'],'boss')]:
        r=Route(opened);r.unchanged();r.anchor('junction','junction')
        if label=='preboss':
            r.anchor('howler','howler');r.measure('preboss-out');r.guide();r.stop();r.heal();r.measure('preboss-back');r.exit();r.anchor('warden_door','warden-arrival');r.anchor('warden','warden-approach');r.stop()
        else:
            for who in order:
                r.anchor(who,who);r.measure(who+'-out');r.guide();r.stop();r.heal();r.measure(who+'-back');r.exit();r.anchor(who,who+'-returned');r.stop();r.unchanged()
            for name in ['trap','tag','secret','far_junction','junction']:r.anchor(name,name)
            r.anchor('loop_home');r.step(148 if not opened else 32+(4 if r.face!=16 else 0),16);r.step(40,0,'loop-wall.ppm' if not opened else 'loop-pass.ppm');r.pos=(36,16) if opened else (34,16);r.expect()
            for key in ['field','quiet','workshop','boss','checkpoint']:
                if r.key!='field':r.exit()
                if key!='field':r.anchor({'quiet':'quiet_door','workshop':'workshop_door','boss':'warden_door','checkpoint':'warden_door'}[key])
                if key=='checkpoint':r.stairs()
                for name,v in r.m['widths'].items():r.follow(v[:2]);r.follow(v[2:4],key+'-'+name);r.follow(v[:2])
                # Main actors and pillar remain blocking under ordinary held input.
                target,button=({'field':((29,27),16),'quiet':((10,7),128),'boss':((8,7),128),'workshop':((4,5),128),'checkpoint':((8,6),128)})[key];r.follow(target);r.step(148,button);r.step(40,0,key+'-collision.ppm');r.expect()
            r.exit()
            if final=='quiet':r.guide()
            else:r.anchor('junction')
        r.unchanged();r.save();save=d/(label+'.sav');run(d,label,rom,sym,save,r.lines)
        m=r.m;data=(source/'engine/data/layouts'/m['name']/'map.bin').read_bytes();words=struct.unpack('<'+str(len(data)//2)+'H',data)
        cold=boot[:-1]+['step 600 0 cold.ppm',f'expect 35 {m["map_num"]} {r.pos[0]} {r.pos[1]} 0','duo healthy','uses 8 40 2 40']+[f'flag {v} 0' for v in flags]+[f'extent {m["width"]+15} {m["height"]+14}']+[f'tile {i%m["width"]} {i//m["width"]} {v}' for i,v in enumerate(words)]
        copied=d/(label+'-cold-copy.sav');digest=hashlib.sha256(save.read_bytes()).hexdigest();shutil.copyfile(save,copied);run(d,label+'-cold-buffer',rom,sym,copied,cold);assert hashlib.sha256(save.read_bytes()).hexdigest()==digest
    for room in ['workshop','checkpoint']:
        label=room+'-route';r=Route(opened);r.unchanged()
        if room=='workshop':r.anchor('workshop_door','workshop-arrival')
        else:r.anchor('warden_door');r.stairs()
        targets={'workshop':['mara','lev','workbench','cache'],'checkpoint':['review','donut_staging']}[room]
        for who in targets:r.anchor(who,who+'-approach');r.talk(128,who+'-interaction')
        r.unchanged();r.save();save=d/(label+'.sav');run(d,label,rom,sym,save,r.lines)
        m=r.m;data=(source/'engine/data/layouts'/m['name']/'map.bin').read_bytes();words=struct.unpack('<'+str(len(data)//2)+'H',data)
        cold=boot[:-1]+['step 600 0 cold.ppm',f'expect 35 {m["map_num"]} {r.pos[0]} {r.pos[1]} 0','duo healthy','uses 8 40 2 40']+[f'flag {v} 0' for v in flags]+[f'extent {m["width"]+15} {m["height"]+14}']+[f'tile {i%m["width"]} {i//m["width"]} {v}' for i,v in enumerate(words)]
        copied=d/(label+'-cold-copy.sav');digest=hashlib.sha256(save.read_bytes()).hexdigest();shutil.copyfile(save,copied);run(d,label+'-cold-buffer',rom,sym,copied,cold);assert hashlib.sha256(save.read_bytes()).hexdigest()==digest
    if opened:
        r=Route(True);r.clip=True;r.anchor('junction');r.unchanged();session=run(d,'continuous-motion',rom,sym,d/'motion.sav',r.lines)
        with (session/'encode.log').open('w') as log:subprocess.run(['ffmpeg','-y','-framerate','59.7275005696','-i',str(session/'frame-%05d.png'),'-c:v','libvpx-vp9','-pix_fmt','yuv420p','-crf','30','-b:v','0',str(session/'walking.webm')],stdout=log,stderr=subprocess.STDOUT,check=True)
        (session/'identity.json').write_text(json.dumps({'actual_continuous_frames':r.frames,'hz':59.7275005696,'includes_idle':True,'no_interpolation':True,'human_pacing_claim':False},indent=2)+'\n')
    if not retained or opened:
        for ext in ['map','elf']:shutil.copyfile(source/'engine'/('pokeemerald.'+ext),d/('diagnostic.'+ext))
(out/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
print('PASS',len(summary),'sessions',sum(v['assertions'] for v in summary),'assertions; production unchanged, live adoption pending.',flush=True)
