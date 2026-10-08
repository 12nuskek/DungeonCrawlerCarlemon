#!/usr/bin/env python3
"""Ordinary-controller optional loop/trap/craft/cache checks; no battle replay."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,importlib.util,json,os,re,shlex,shutil,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--originals',type=Path,required=True);p.add_argument('--case',choices=['loop','trap','craft']);args=p.parse_args()
assert not git('status','--porcelain'), 'Commit runner first'
head=git('rev-parse','HEAD');build=args.build.resolve();compiled=(build/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',compiled,head,'--','engine'],cwd=ROOT,check=True)
rom=build/'source/engine/pokeemerald.gba';assert sha(rom)=='b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a'
parent=ROOT/'artifacts/floor1/optional';parent.mkdir(parents=True,exist_ok=True);out=Path(tempfile.mkdtemp(prefix='runtime-',dir=parent));print('Evidence:',out,flush=True)
sym=out/'game.sym'
with sym.open('w') as f:subprocess.run(['arm-none-eabi-nm','--defined-only',str(build/'source/engine/pokeemerald.elf')],stdout=f,check=True)
with sym.open('a') as f:subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(build/'source/engine')],stdout=f,check=True)
observer=module('observer',ROOT/'scripts/floor1/live-save-observer.py');native=module('native',ROOT/'scripts/floor1/native-text-observer.py');walking=module('walking',ROOT/'scripts/floor1/walking-harness.py')
code=native.instrument(observer.instrument(walking.instrument(git('show',head+':scripts/playtest.c')+'\n')))
code=code.replace('!number(values[0],15,&tx)','!number(values[0],255,&tx)').replace('!number(values[1],11,&ty)','!number(values[1],255,&ty)')
assert 'busWrite' not in code
(out/'observer.c').write_text(code)
with (out/'host-build.log').open('w') as f:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',*shlex.split(os.environ.get('DCC_TEST_CFLAGS','')),str(out/'observer.c'),*shlex.split(os.environ.get('DCC_TEST_LDFLAGS','')),'-lmgba','-o',str(out/'playtest')],stdout=f,stderr=subprocess.STDOUT,check=True)
spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text());g=module('geometry',ROOT/'scripts/floor1/relocation-graybox.py');routes=module('routes',ROOT/'scripts/floor1/live-route.py');summary=[];originals={}
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 cold.ppm','ready']
def R(key,pos,opened=False,facing=1):
    r=routes.Route(spec,g,key,pos,facing,7,opened=opened);r.cursor=0;return r

def copy(name,original='both-pending'):
    f=args.originals.resolve()/(original+'.sav');originals[f]=sha(f);dest=out/(name+'.sav');shutil.copyfile(f,dest);return dest

def cold(name,save):
    dest=out/(name+'.sav');shutil.copyfile(save,dest);return dest,sha(dest)

def run(name,save,r):
    assert not any(line.startswith(('pilot ','engage ','snapshot','policy ')) for line in r.lines)
    d=out/name;d.mkdir();(d/'input.route').write_text('\n'.join(boot+r.lines+['quit'])+'\n')
    with (d/'input.route').open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:result=subprocess.run([str(out/'playtest'),str(rom),str(save),str(sym)],cwd=d,stdin=inp,stdout=log,stderr=err)
    for image in d.glob('*.ppm'):
        frame=Image.open(image);assert frame.size==(240,160);frame.save(image.with_suffix('.png'))
    assert result.returncode==0,(name,'retained failed route',d,result.returncode)
    log=(d/'replay.log').read_text();assert not (d/'errors.log').stat().st_size
    checks=int(re.search(r'result=0 assertions=(\d+)\n$',log)[1]);summary.append(dict(route=name,assertions=checks,emulator_errors=0,native_messages=sum(map(int,re.findall(r'native-pages messages=(\d+)',log))),native_pages=sum(map(int,re.findall(r'native-pages messages=\d+ pages=(\d+)',log))),method='Preserved ordinary save or controller-created manual Save; ordinary buttons, RAM reads only')))
    print('PASS',name,checks,flush=True)

def page(r,prefix,*labels):r.lines.append('pages '+prefix+' '+','.join(labels))
def close(r):r.lines+=['dialog 3600','ready'];r.step(40);r.expect()
def face(r,button):
    # Avoid stepping onto a walkable BG target when already facing it.
    if r.face!=button:r.step(1,button);r.face=button;r.step(40)
def talk(r,button,prefix,*labels,finish=True):
    face(r,button);r.step(1,1);r.step(400);page(r,prefix,*labels)
    if finish:close(r)
def choice(r,prefix,label,no=False):
    # Native MSGBOX_YESNO opens automatically after its last printed page.
    r.step(40,0,prefix+'-choice.ppm')
    if no:r.step(1,128);r.step(20)
    r.step(1,1);r.step(400);page(r,prefix,label);close(r)
def save(r):r.save();r.lines=[line for line in r.lines if line!='snapshot'];r.cursor=2

def unchanged_progress(r):
    r.lines+=['flag 2135 1','flag 2136 0','flag 2137 0','flag 47 0','flag 48 0','flag 43 0']
def field_words(r,loop=False,trap=False):
    assert r.key=='field'
    raw=(build/'source/engine/data/layouts/DCC_F1D1Field/map.bin').read_bytes();words=list(struct.unpack('<'+'H'*(len(raw)//2),raw));w=64
    # Apply the existing persistent presentation table to the immutable source.
    flags={'FLAG_DCC_D1_LOOP_OPEN':loop,'FLAG_DCC_TRAP_SPENT':trap,'FLAG_DCC_SECRET_TAKEN':False}
    text=(build/'source/engine/src/data/dcc_opening.h').read_text()
    for x,y,flag,off,on in re.findall(r'MAP_DCC_F1D1FIELD, (\d+), (\d+), (FLAG_DCC_\w+), 0x([0-9A-F]+), 0x([0-9A-F]+)',text):words[int(y)*w+int(x)]=int(on if flags[flag] else off,16)
    r.lines += [f'tile {i%w} {i//w} {value}' for i,value in enumerate(words)]

def gate_words(r,opened):r.lines += [f'tile 35 {y} {0x323B if opened else 0x3E47}' for y in range(13,22)]
def blocked(r,key):r.step(20,key);r.step(40);r.expect()

def gate_capture(r,name):r.follow((32,16));face(r,16);r.step(40,0,name+'.ppm')

if not args.case or args.case=='loop':
    s=copy('loop');r=R('field',(37,31));unchanged_progress(r);r.lines+=['flag 49 0','flag 40 0','flag 45 0','item 378 2','item 380 0','item 22 0'];field_words(r)
    gate_capture(r,'closed');r.anchor('loop_home');talk(r,16,'wrong-side','DCC_F1D1Field_LoopLockedText');r.lines+=['flag 49 0'];gate_words(r,False);blocked(r,16)
    r.anchor('loop_far');talk(r,32,'opening','DCC_F1D1Field_LoopOpenText');r.lines+=['flag 49 1'];r.opened=True;gate_words(r,True);r.anchor('loop_home');r.anchor('loop_far');talk(r,32,'repeat','DCC_F1D1Field_LoopOpenText');unchanged_progress(r)
    gate_capture(r,'opened');r.anchor('quiet_door');r.anchor('donut_staging');r.anchor('arrival');gate_capture(r,'reentered');field_words(r,loop=True);r.lines+=['flag 49 1','item 378 2','item 380 0','item 22 0'];unchanged_progress(r)
    r.anchor('loop_far');save(r);saved_facing={128:1,64:2,32:3,16:4}[r.face];run('ordinary-loop-opening-reentry-save',s,r)
    c,identity=cold('loop-cold',s);r=R('field',(36,16),True,saved_facing);r.lines+=['flag 49 1'];gate_words(r,True);r.anchor('loop_home');r.anchor('loop_far');talk(r,32,'cold-repeat','DCC_F1D1Field_LoopOpenText');gate_capture(r,'cold-opened');field_words(r,loop=True);unchanged_progress(r);r.lines+=['item 378 2','item 380 0','item 22 0'];run('ordinary-loop-cold-two-way',c,r);assert sha(c)==identity

if not args.case or args.case=='trap':
    s=copy('trap');r=R('field',(37,31));r.lines+=['flag 40 0','roster 33 28 8 2 0 0','tile 46 42 12943'];r.anchor('wire');talk(r,64,'warning','DCC_Service_Text_Warning')
    r.follow((45,42));r.follow((46,42));r.step(400);page(r,'shock','DCC_Service_Text_Trap');close(r);r.lines+=['flag 40 1','tile 46 42 12956','roster 29 28 8 2 64 0']
    r.follow((47,42));r.follow((46,42));r.lines+=['ready','roster 29 28 8 2 64 0'];r.anchor('wire');talk(r,64,'spent','DCC_Service_Text_WarningSpent');unchanged_progress(r);r.follow((47,42));save(r);saved_facing={128:1,64:2,32:3,16:4}[r.face];run('ordinary-trap-first-repeat-save',s,r)
    c,identity=cold('trap-cold',s);r=R('field',(47,42),False,saved_facing);r.lines+=['flag 40 1','tile 46 42 12956','roster 29 28 8 2 64 0'];field_words(r,trap=True);r.follow((46,42));r.lines+=['ready','roster 29 28 8 2 64 0'];r.anchor('wire');talk(r,64,'cold-spent','DCC_Service_Text_WarningSpent');run('ordinary-trap-cold-no-retrigger',c,r);assert sha(c)==identity
    c,unused=cold('trap-recovery',s);r=R('field',(47,42),False,saved_facing);r.anchor('quiet_door');r.anchor('guide');talk(r,128,'recovery','DCC_Live_Vestibule_Text_RepeatService');r.lines+=['duo healthy','uses 8 40 2 40','roster 33 28 8 2 0 0'];r.anchor('donut_staging');r.anchor('arrival');r.anchor('wire');talk(r,64,'reentered-spent','DCC_Service_Text_WarningSpent');r.follow((45,42));r.follow((46,42));r.follow((47,42));r.lines+=['flag 40 1','ready','roster 33 28 8 2 0 0'];field_words(r,trap=True);save(r);run('ordinary-trap-guide-recovery-reentry',c,r)
    d,identity=cold('recovered-cold',c);r=R('field',(47,42),False,{128:1,64:2,32:3,16:4}[r.face]);r.lines+=['flag 40 1','duo healthy','uses 8 40 2 40','roster 33 28 8 2 0 0'];r.follow((46,42));r.lines+=['ready','roster 33 28 8 2 0 0'];run('ordinary-trap-recovered-cold',d,r);assert sha(d)==identity

if not args.case or args.case=='craft':
    s=copy('craft');r=R('field',(37,31));r.lines+=['item 378 2','item 380 0','item 22 0','flag 46 0'];r.anchor('workshop_door');r.anchor('cache');talk(r,128,'no-charge','DCC_Service_Text_NeedsCharge');r.lines+=['item 378 2','item 380 0','item 22 0','flag 46 0']
    r.anchor('workbench');talk(r,128,'recipe-cancel','DCC_Service_Text_Recipe',finish=False);choice(r,'cancel','DCC_Service_Text_Cancel',True);r.lines+=['item 378 2','item 380 0']
    talk(r,128,'recipe-success','DCC_Service_Text_Recipe',finish=False);choice(r,'crafted','DCC_Service_Text_Crafted');r.lines+=['item 378 0','item 380 1'];talk(r,128,'recipe-missing','DCC_Service_Text_Recipe',finish=False);choice(r,'missing','DCC_Service_Text_Missing');r.lines+=['item 378 0','item 380 1']
    r.anchor('cache');talk(r,128,'blast-cancel','DCC_Service_Text_BlastOffer',finish=False);choice(r,'cache-cancel','DCC_Service_Text_CacheCancel',True);r.lines+=['flag 46 0','item 380 1','item 22 0'];talk(r,128,'blast-use','DCC_Service_Text_BlastOffer',finish=False);choice(r,'blasted','DCC_Service_Text_Blasted');r.lines+=['flag 46 1','item 380 0','item 22 1'];talk(r,128,'cache-repeat','DCC_Service_Text_CacheOpened');r.lines+=['item 378 0','item 380 0','item 22 1'];unchanged_progress(r)
    r.anchor('arrival');r.anchor('workshop_door');r.anchor('cache');talk(r,128,'cache-reentered','DCC_Service_Text_CacheOpened');r.lines+=['flag 46 1','item 378 0','item 380 0','item 22 1'];save(r);run('ordinary-recipe-cache-reentry-save',s,r)
    c,identity=cold('craft-cold',s);r=R('workshop',(12,9));r.lines+=['flag 46 1','item 378 0','item 380 0','item 22 1'];talk(r,128,'cold-cache','DCC_Service_Text_CacheOpened');r.lines+=['item 22 1','item 380 0'];r.anchor('workbench');talk(r,128,'cold-recipe','DCC_Service_Text_Recipe',finish=False);choice(r,'cold-missing','DCC_Service_Text_Missing');r.lines+=['item 378 0','item 380 0','item 22 1'];unchanged_progress(r);run('ordinary-recipe-cache-cold',c,r);assert sha(c)==identity

assert all(sha(f)==identity for f,identity in originals.items())
(out/'summary.json').write_text(json.dumps(dict(compiled_source=compiled,runner_source=head,rom_sha256=sha(rom),sessions=summary,originals_unchanged=True,read_only_cold_inputs_unchanged=True,method='Actual production ROM/normal controllers, original ordinary saves and controller-authored copies only. No synthetic save input, RAM/ROM write, policy, snapshot dump or battle. Raw routes/logs/saves remain local.'),indent=2)+'\n')
assert not git('status','--porcelain') and git('rev-parse','HEAD')==head
print('PASS',len(summary),'ordinary sessions',sum(x['assertions'] for x in summary),'assertions',flush=True)
