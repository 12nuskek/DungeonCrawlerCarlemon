#!/usr/bin/env python3
"""Read-only scene peaks on identical accepted diagnostic binaries; no new game build."""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json,os,re,shlex,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=root,text=True).strip()
assert not git('status','--porcelain'),'Commit first'
head=git('rev-parse','HEAD');base=Path(os.environ['DCC_G01B_ACCEPTED_RUN']).resolve();tested=(base/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',tested,head,'--','engine','scripts/playtest.c','scripts/floor1/walking-harness.py','scripts/floor1/coordinated-graybox.py','scripts/contracts/f1-g01b-coordinated.json'],cwd=root,check=True)
accepted=json.loads((base/'validation-summary.json').read_text());assert len(accepted)==13 and sum(v['assertions'] for v in accepted)==8397
l=importlib.util.spec_from_file_location('gate',root/'scripts/floor1/travel-measurements.py');gate=importlib.util.module_from_spec(l);l.loader.exec_module(gate)
spec=json.loads((root/'scripts/contracts/f1-g01b-coordinated.json').read_text());ceiling=json.loads((root/'scripts/contracts/f1-g01b-recovery.json').read_text())
out=Path(tempfile.mkdtemp(prefix='scene-',dir=root/'artifacts/floor1/g01b'));print('Evidence:',out,flush=True)
code=(base/'walking.c').read_text();code=code.replace('maplayout=0, overworld=0, fade=0, addr;','maplayout=0, overworld=0, fade=0, sceneSprites=0, addr;')
code=code.replace('unsigned measuring=0,','unsigned sceneFrames[3]={0}, peakObjects[3]={0}, peakSprites[3]={0};\n    unsigned measuring=0,')
code=code.replace('if (!strcmp(symbol,"gBackupMapLayout"))','if (!strcmp(symbol,"gSprites")) sceneSprites=addr;\n        if (!strcmp(symbol,"gBackupMapLayout"))')
point='for (unsigned i=0;i<frames;i++) {\n                core->runFrame(core);';assert code.count(point)==1
code=code.replace(point,point+'''
                unsigned sceneSb=core->busRead32(core,saveptr), sceneMap=core->busRead8(core,sceneSb+5);
                if (sceneSprites && core->busRead8(core,sceneSb+4)==35 && sceneMap<3
                    && (core->busRead32(core,mainstate+4)&~1u)==(overworld&~1u) && !(core->busRead8(core,fade+7)&128)) {
                    unsigned active=0,used=0;
                    for (unsigned j=0;j<16;j++) active+=core->busRead8(core,objects+j*0x24)&1;
                    for (unsigned j=0;j<64;j++) used+=core->busRead8(core,sceneSprites+j*0x44+0x3e)&1;
                    if (active>peakObjects[sceneMap]) peakObjects[sceneMap]=active;
                    if (used>peakSprites[sceneMap]) peakSprites[sceneMap]=used;
                    sceneFrames[sceneMap]++;
                }''')
point='    printf("result=%d assertions=%u\\n",result,checks);';assert code.count(point)==1
code=code.replace(point,'    for(unsigned j=0;j<3;j++) printf("SCENE map=%u samples=%u peak_objects=%u peak_sprites=%u\\n",j,sceneFrames[j],peakObjects[j],peakSprites[j]);\n'+point)
assert 'busWrite' not in code
(out/'scene.c').write_text(code)
subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',*shlex.split(os.environ.get('DCC_TEST_CFLAGS','')),str(out/'scene.c'),*shlex.split(os.environ.get('DCC_TEST_LDFLAGS','')),'-lmgba','-o',str(out/'playtest')],check=True)
results=[]
for mode in ['closed','open']:
    d=base/mode;rom=d/'diagnostic.gba';assert hashlib.sha256(rom.read_bytes()).hexdigest()==(d/'rom.sha256').read_text().split()[0]
    original=d/'guard-first';session=out/mode;session.mkdir();lines=(original/'input.route').read_text();(session/'input.route').write_text(lines)
    with (session/'input.route').open() as inputs,(session/'replay.log').open('w') as log,(session/'errors.log').open('w') as errors:subprocess.run([str(out/'playtest'),str(rom),str(out/(mode+'.sav')),str(d/'game.sym')],cwd=session,stdin=inputs,stdout=log,stderr=errors,check=True)
    log=(session/'replay.log').read_text();checks=next(v['assertions'] for v in accepted if v['route']==mode+'/guard-first');assert log.endswith(f'result=0 assertions={checks}\n') and not (session/'errors.log').stat().st_size
    metrics=[{'name':a,'frames':int(b),'walking_frames':int(c),'steps':int(e),'warps':int(f)} for a,b,c,e,f in re.findall(r'MEASURE name=(\S+) frames=(\d+) walking=(\d+) tiles=(\d+) warps=(\d+)',log)];gate.validate('guard-first',metrics,spec,ceiling)
    peaks=[{'map':int(a),'samples':int(b),'peak_objects':int(c),'peak_sprites':int(d)} for a,b,c,d in re.findall(r'SCENE map=(\d+) samples=(\d+) peak_objects=(\d+) peak_sprites=(\d+)',log)];assert len(peaks)==3 and all(v['samples']>0 and 1<=v['peak_objects']<=16 and 1<=v['peak_sprites']<=64 for v in peaks)
    captures=0
    for p in session.glob('*.ppm'):
        actual=Image.open(p);reference=Image.open(original/(p.stem+'.png'));assert actual.size==(240,160) and actual.tobytes()==reference.tobytes();actual.save(p.with_suffix('.png'));captures+=1
    assert captures==len(list(original.glob('*.png')))
    results.append({'mode':mode,'assertions':checks,'peaks':peaks,'exact_capture_pixel_matches':captures,'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest()});print(mode,'PASS',checks,peaks,captures,'pixel matches',flush=True)
(out/'result.json').write_text(json.dumps({'observer_source':head,'diagnostic_runner_source':tested,'sessions':2,'assertions':sum(v['assertions'] for v in results),'results':results,'method':'Actual object/sprite in-use flags sampled each stable overworld frame on all three maps; all captures exactly match original. No game/RAM writes, build, hardware performance or human pacing claim.'},indent=2)+'\n')
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
