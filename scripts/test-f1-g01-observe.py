#!/usr/bin/env python3
"""Read-only runtime buffer/scene measurements and a continuous actual-frame clip."""
from pathlib import Path
from PIL import Image
import hashlib,json,os,shlex,struct,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
assert not git('status','--porcelain'),'Commit first'
revision=git('rev-parse','HEAD');base=Path(os.environ['DCC_G01_BASE_RUN']).resolve();tested=(base/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',tested,revision,'--','engine','scripts/playtest.c','scripts/floor1/opening-graybox.py','scripts/contracts/f1-g01-opening.json'],cwd=root,check=True)
summary=json.loads((base/'validation-summary.json').read_text());assert (len(summary),sum(s['assertions'] for s in summary))==(9,708)
assert all(not (base/s['route']/'errors.log').stat().st_size for s in summary)
out=Path(tempfile.mkdtemp(prefix='observe-',dir=root/'artifacts/floor1/g01'));print('Evidence:',out,flush=True)
code=git('show',tested+':scripts/playtest.c')+'\n'
# No game/RAM writes; only the shared harness's coordinate limit and observability change.
code=code.replace('maplayout=0, addr;','maplayout=0, sprites=0, peakObjects=0, peakSprites=0, samples=0, addr;')
code=code.replace('if (!strcmp(symbol,"gBackupMapLayout"))', 'if (!strcmp(symbol,"gSprites")) sprites=addr;\n        if (!strcmp(symbol,"gBackupMapLayout"))')
code=code.replace('for (unsigned i=0;i<frames;i++) core->runFrame(core);','''for (unsigned i=0;i<frames;i++) {
                core->runFrame(core);
                if (maplayout && core->busRead32(core,maplayout)==79 && core->busRead32(core,maplayout+4)==62) {
                    unsigned active=0, used=0;
                    for (unsigned j=0;j<16;j++) active+=core->busRead8(core,objects+j*0x24)&1;
                    if (sprites) for (unsigned j=0;j<64;j++) used+=core->busRead8(core,sprites+j*0x44+0x3e)&1;
                    if (active>peakObjects) peakObjects=active;
                    if (used>peakSprites) peakSprites=used;
                    samples++;
                }
            }''')
code=code.replace('strncmp(line,"tile ",5) &&','strncmp(line,"extent ",7) && strncmp(line,"tile ",5) &&')
point='        if (!strncmp(line,"tile ",5)) {'
assert code.count(point)==1
code=code.replace(point,'''        if (!strncmp(line,"extent ",7)) {
            unsigned w,h; char trailing;
            if (!maplayout || sscanf(line,"extent %u %u %c",&w,&h,&trailing)!=2
                || core->busRead32(core,maplayout)!=w || core->busRead32(core,maplayout+4)!=h) {result=25;break;}
            checks++;printf("PASS %s",line);continue;
        }
'''+point)
code=code.replace('!number(values[0],15,&tx)','!number(values[0],255,&tx)').replace('!number(values[1],11,&ty)','!number(values[1],255,&ty)')
point='    printf("result=%d assertions=%u\\n",result,checks);';assert code.count(point)==1
code=code.replace(point,'    printf("observed map-frame samples=%u peak-active-objects=%u peak-used-sprites=%u\\n",samples,peakObjects,peakSprites);\n'+point)
assert 'busWrite' not in code
(out/'playtest-observe.c').write_text(code)
subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',*shlex.split(os.environ.get('DCC_TEST_CFLAGS','')),str(out/'playtest-observe.c'),*shlex.split(os.environ.get('DCC_TEST_LDFLAGS','')),'-lmgba','-o',str(out/'playtest')],check=True)
results=[]
def run(name,rom,sym,save,lines,expected):
    d=out/name;d.mkdir();(d/'input.route').write_text('\n'.join(lines)+'\n')
    with (d/'input.route').open() as inputs,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as errors:
        subprocess.run([str(out/'playtest'),str(rom),str(save),str(sym)],cwd=d,stdin=inputs,stdout=log,stderr=errors,check=True)
    assert (d/'replay.log').read_text().endswith(f'result=0 assertions={expected}\n') and not (d/'errors.log').stat().st_size
    for p in d.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
    results.append({'route':name,'assertions':expected,'diagnostic':True});print(name,'PASS',expected,flush=True);return d
for mode in ['closed','open']:
    d=base/mode;rom=d/'diagnostic.gba'
    assert hashlib.sha256(rom.read_bytes()).hexdigest()==(d/'rom.sha256').read_text().split()[0]
    route=(d/'guard-first-cold/input.route').read_text().splitlines();assert route[-1]=='quit'
    words=struct.unpack('<3072H',(base/'source/engine/data/layouts/DCC_OpeningPreview/map.bin').read_bytes())
    # Source cache ends open; reconstruct closed source words from the saved exporter map identity.
    if mode=='closed':
        for x,y in [(35,y) for y in range(13,20)]:
            # Both lateral neighbors are floors: exact exported left-wall metatile.
            words=list(words);words[y*64+x]=0x3c00|583
    digest=hashlib.sha256(struct.pack('<3072H',*words)).hexdigest()
    assert digest==json.loads((d/'map-identity.json').read_text())['blockdata_sha256']
    lines=route[:-1]+['extent 79 62']+[f'tile {i%64} {i//64} {v}' for i,v in enumerate(words)]+['quit']
    save=out/(mode+'-copy.sav');shutil.copyfile(d/'guard-first.sav',save)
    run(mode+'-buffer-cold',rom,d/'game.sym',save,lines,25+1+3072)
# Replay every ordinary motion/menu idle frame as a capture: no dropped waits or interpolation.
d=base/'open';source=(d/'motion/input.route').read_text().splitlines();lines=[];active=False;frame=0
for line in source:
    if line.startswith('step ') and 'motion-' in line:active=True
    if active and line.startswith('step '):
        _,n,key,_=line.split()
        for i in range(int(n)):lines.append(f'step 1 {key} frame-{frame:05d}.ppm');frame+=1
    else:lines.append(line)
session=run('continuous-motion',d/'diagnostic.gba',d/'game.sym',out/'motion.sav',lines,7)
with (session/'encode.log').open('w') as log:
    subprocess.run(['ffmpeg','-y','-framerate','59.7275005696','-i',str(session/'frame-%05d.png'),'-c:v','libvpx-vp9','-pix_fmt','yuv420p','-crf','30','-b:v','0',str(session/'walking.webm')],stdout=log,stderr=subprocess.STDOUT,check=True)
(out/'identity.json').write_text(json.dumps({'observer_source':revision,'diagnostic_game_source':tested,'base':str(base),'main_sessions':9,'main_assertions':708,'observer_sessions':len(results),'observer_assertions':sum(r['assertions'] for r in results),'motion_frames':frame,'motion_hz':59.7275005696,'motion_seconds':frame/59.7275005696,'method':'Two cold ordinary saves: all3072 field cells compared against exact diagnostic map source; extent79x62. Sampled engine arrays via read-only mGBA bus reads. Continuous actual-frame silent motion, includes all stationary segment waits; no interpolation or skipped frames. No hardware performance/human pacing claim.'},indent=2)+'\n')
(out/'validation-summary.json').write_text(json.dumps(results,indent=2)+'\n')
assert git('rev-parse','HEAD')==revision and not git('status','--porcelain')
print('PASS',len(results),'observer sessions /',sum(r['assertions'] for r in results),'assertions; continuous actual frames',frame,flush=True)
