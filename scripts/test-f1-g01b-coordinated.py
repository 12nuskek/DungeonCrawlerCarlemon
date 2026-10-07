#!/usr/bin/env python3
"""Fresh committed third-layout diagnostics, ordinary inputs and walking gates."""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json,os,re,shlex,shutil,struct,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=root,text=True).strip()
def module(name,path):
    l=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(l);l.loader.exec_module(m);return m
assert not git('status','--porcelain'),'Commit before testing'
head=git('rev-parse','HEAD');base=Path(os.environ['DCC_A01_BASE_RUN']).resolve()
retained=Path(os.environ['DCC_G01B_CLOSED_RUN']).resolve() if os.environ.get('DCC_G01B_CLOSED_RUN') else None
if retained:
    retained_source=(retained/'tested-commit.txt').read_text().strip()
    subprocess.run(['git','diff','--quiet',retained_source,head,'--','engine','scripts/playtest.c','scripts/contracts/f1-g01b-coordinated.json','scripts/floor1/coordinated-graybox.py','scripts/floor1/walking-harness.py'],cwd=root,check=True)
    assert hashlib.sha256((retained/'closed/diagnostic.gba').read_bytes()).hexdigest()==(retained/'closed/rom.sha256').read_text().split()[0]
subprocess.run(['git','diff','--quiet','ed592e7',head,'--','engine','scripts/playtest.c'],cwd=root,check=True)
assert hashlib.sha256((base/'production.gba').read_bytes()).hexdigest()=='5c4f865a95c0b9e4c65f13d86c8ba44c9082599432b387f6fc350c0bd99b7230'
out=Path(tempfile.mkdtemp(prefix='third-',dir=root/'artifacts/floor1/g01b'));print('Evidence:',out,flush=True);(out/'tested-commit.txt').write_text(head+'\n')
snap=module('snapshot',root/'scripts/floor1/committed-snapshot.py');source=out/'source'
snap.snapshot(root,head,source,os.environ.get('DCC_G01_CACHE'),['scripts/contracts/f1-g01b-coordinated.json','scripts/contracts/f1-g01b-recovery.json','scripts/floor1/coordinated-graybox.py','scripts/floor1/walking-harness.py'])
with (out/'setup.log').open('w') as log:subprocess.run(['bash',str(source/'scripts/setup-foundation.sh')],stdout=log,stderr=subprocess.STDOUT,check=True)
g=module('geometry',source/'scripts/floor1/coordinated-graybox.py');walking=module('walking',source/'scripts/floor1/walking-harness.py')
spec=json.loads((source/'scripts/contracts/f1-g01b-coordinated.json').read_text());ceiling=json.loads((source/'scripts/contracts/f1-g01b-recovery.json').read_text())
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
flags=list(range(32,49))+list(range(2135,2140));summary=[]
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
    def exit(self):assert self.key!='field';self.anchor('arrival');assert self.key=='field'
    def unchanged(self):self.lines+=['duo healthy','uses 8 40 2 40']+[f'flag {v} 0' for v in flags]
    def save(self):
        self.step(1,8);self.step(120,0);self.step(1,128);self.step(20,0);self.step(1,128);self.step(20,0);self.step(1,1);self.step(160,0);self.step(1,1);self.step(600,0,'saved.ppm');self.expect()
def run(d,name,rom,sym,save,lines):
    session=d/name;session.mkdir();(session/'input.route').write_text('\n'.join(lines+['quit'])+'\n')
    with (session/'input.route').open() as inputs,(session/'replay.log').open('w') as log,(session/'errors.log').open('w') as errors:subprocess.run([str(out/'playtest'),str(rom),str(save),str(sym)],cwd=session,stdin=inputs,stdout=log,stderr=errors,check=True)
    checks=sum(v.startswith(('expect ','duo ','uses ','flag ','tile ','extent ')) for v in lines);log=(session/'replay.log').read_text();assert log.endswith(f'result=0 assertions={checks}\n') and not (session/'errors.log').stat().st_size
    for p in session.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
    metrics=[{'name':a,'frames':int(b),'walking_frames':int(c),'steps':int(e),'warps':int(f)} for a,b,c,e,f in re.findall(r'MEASURE name=(\S+) frames=(\d+) walking=(\d+) tiles=(\d+) warps=(\d+)',log)]
    for who in ['guard','howler']:
        pair=[v for v in metrics if v['name'] in [who+'-out',who+'-back']]
        if pair:
            assert len(pair)==2 and all(v['steps']==spec['expected_steps'][who+'_each_leg'] for v in pair)
            assert sum(v['steps'] for v in pair)<=ceiling['roundtrips'][who]['steps_total'] and sum(v['walking_frames'] for v in pair)<=ceiling['roundtrips'][who]['walking_frames_total']
    pair=[v for v in metrics if v['name'] in ['preboss-out','preboss-back']]
    if pair:assert len(pair)==2 and sum(v['steps'] for v in pair)==spec['expected_steps']['preboss_total'] and sum(v['walking_frames'] for v in pair)<=ceiling['preboss']['walking_frames_total']
    summary.append({'route':f'{d.name}/{name}','assertions':checks,'diagnostic':True,'measurements':metrics});print(d.name,name,'PASS',checks,metrics,flush=True);return session
for opened in [False,True]:
    mode='open' if opened else 'closed';d=out/mode;d.mkdir()
    if opened:
        for p in ['src/new_game.c','data/maps/map_groups.json','data/layouts/layouts.json','data/event_scripts.s']:(source/'engine'/p).write_bytes(subprocess.check_output(['git','show',head+':engine/'+p],cwd=root))
        for m in spec['maps'].values():
            for area in ['maps','layouts']:shutil.rmtree(source/'engine/data'/area/m['name'])
    subprocess.run(['python3','-B',str(source/'scripts/floor1/coordinated-graybox.py'),'--engine',str(source/'engine'),'--out',str(d)]+(['--opened'] if opened else []),stdout=(d/'export.log').open('w'),check=True)
    rom=d/'diagnostic.gba'
    sym=d/'game.sym'
    if retained and not opened:
        assert json.loads((d/'map-identities.json').read_text())==json.loads((retained/'closed/map-identities.json').read_text())
        shutil.copyfile(retained/'closed/diagnostic.gba',rom);shutil.copyfile(retained/'closed/game.sym',sym)
        (d/'build-reuse.json').write_text(json.dumps({'compiled_source':retained_source,'original_build':str(retained/'closed/build.log'),'sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'method':'Replay original clean committed diagnostic ROM; engine/shared harness/contract/exporter/walking source diff verified empty. No engine/cache inputs copied. Open variant builds in this new fresh snapshot.'},indent=2)+'\n')
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
            for name in ['workshop_door','trap','tag','secret','far_junction','junction']:r.anchor(name,name)
            r.anchor('loop_home');r.step(148 if not opened else 36,16);r.step(40,0,'loop-wall.ppm' if not opened else 'loop-pass.ppm');r.pos=(36,16) if opened else (34,16);r.expect()
            for key in ['field','quiet','boss']:
                if r.key!='field':r.exit()
                if key!='field':r.anchor('quiet_door' if key=='quiet' else 'warden_door')
                for name,v in r.m['widths'].items():r.follow(v[:2]);r.follow(v[2:4],key+'-'+name);r.follow(v[:2])
                # Main actors and pillar remain blocking under ordinary held input.
                target,button=({'field':((29,27),16),'quiet':((10,7),128),'boss':((8,7),128)})[key];r.follow(target);r.step(148,button);r.step(40,0,key+'-collision.ppm');r.expect()
            r.exit()
            if final=='quiet':r.guide()
            else:r.anchor('junction')
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
