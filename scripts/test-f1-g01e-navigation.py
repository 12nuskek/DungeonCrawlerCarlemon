#!/usr/bin/env python3
"""Bounded live NPC/Journal native-window matrix; no battle strategy replay."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, importlib.util, json, os, re, shlex, shutil, struct, subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--originals',type=Path,required=True);p.add_argument('--case');args=p.parse_args()
assert not git('status','--porcelain'), 'Commit runner before runtime'
head=git('rev-parse','HEAD');build=args.build.resolve();compiled=(build/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',compiled,head,'--','engine'],cwd=ROOT,check=True)
source=build/'source';rom=source/'engine/pokeemerald.gba';originals=args.originals.resolve()
parent=ROOT/'artifacts/floor1/navigation';out=Path(tempfile.mkdtemp(prefix='runtime-',dir=parent));print('Evidence:',out,flush=True)
sym=out/'game.sym'
with sym.open('w') as f: subprocess.run(['arm-none-eabi-nm','--defined-only',str(source/'engine/pokeemerald.elf')],stdout=f,check=True)
with sym.open('a') as f: subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(source/'engine')],stdout=f,check=True)
obs=module('observer',ROOT/'scripts/floor1/live-save-observer.py');native=module('native',ROOT/'scripts/floor1/native-text-observer.py');walking=module('walking',ROOT/'scripts/floor1/walking-harness.py')
code=native.instrument(obs.instrument(walking.instrument(git('show',head+':scripts/playtest.c')+'\n')))
code=code.replace('!number(values[0],15,&tx)','!number(values[0],255,&tx)').replace('!number(values[1],11,&ty)','!number(values[1],255,&ty)')
# Snapshot dumps are unnecessary for this task and are never invoked.
assert 'busWrite' not in code
(out/'observer.c').write_text(code)
with (out/'host-build.log').open('w') as f: subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',*shlex.split(os.environ.get('DCC_TEST_CFLAGS','')),str(out/'observer.c'),*shlex.split(os.environ.get('DCC_TEST_LDFLAGS','')),'-lmgba','-o',str(out/'playtest')],stdout=f,stderr=subprocess.STDOUT,check=True)
g=module('geometry',ROOT/'scripts/floor1/relocation-graybox.py');routes=module('routes',ROOT/'scripts/floor1/live-route.py');saveinput=module('inputs',ROOT/'scripts/floor1/save-boundary-input.py')
spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text());summary=[];original_hashes={}
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 cold.ppm','ready']
def R(key,pos,flags=7):
    r=routes.Route(spec,g,key,pos,1,flags);r.cursor=0;return r
def copy(name,original):
    f=originals/(original+'.sav');original_hashes[f]=digest(f);dest=out/(name+'.sav');shutil.copyfile(f,dest);return dest

def run(name,save,r,kind='ordinary copied save and controller route'):
    if args.case and name!=args.case:return
    d=out/name;d.mkdir();(d/'input.route').write_text('\n'.join(boot+r.lines+['quit'])+'\n')
    with (d/'input.route').open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
        result=subprocess.run([str(out/'playtest'),str(rom),str(save),str(sym)],cwd=d,stdin=inp,stdout=log,stderr=err)
    for image in d.glob('*.ppm'):
        frame=Image.open(image);assert frame.size==(240,160);frame.save(image.with_suffix('.png'))
    assert result.returncode==0, (name,'retained failed route',d,result.returncode)
    log=(d/'replay.log').read_text();assert not (d/'errors.log').stat().st_size
    checks=int(re.search(r'result=0 assertions=(\d+)\n$',log)[1]);summary.append(dict(route=name,assertions=checks,method=kind,emulator_errors=0,native_messages=sum(map(int,re.findall(r'native-pages messages=(\d+)',log))),native_pages=sum(map(int,re.findall(r'native-pages messages=\d+ pages=(\d+)',log)))))
    print('PASS',name,checks,flush=True)

def pages(r,prefix,*labels):r.lines.append('pages '+prefix+' '+','.join('DCC_Live_'+label for label in labels))
def close(r):r.lines+=['dialog 3600','ready'];r.step(40);r.expect()
def talk(r,button,prefix,*labels,finish=True):
    r.step(1,button);r.face=button;r.step(40);r.step(1,1);r.step(400);pages(r,prefix,*labels)
    if finish:close(r)
def journal(r,prefix,objective,quest):
    r.step(1,8);r.step(120)
    for i in range((4-r.cursor)%6):r.step(1,128);r.step(20)
    r.cursor=4;r.step(1,1);r.step(400);pages(r,prefix,'Journal_Text_'+objective,'Journal_Text_Rules','Journal_Text_'+quest);close(r)
def save(r):
    if r.cursor:
        r.step(1,8);r.step(120)
        for i in range(r.cursor):r.step(1,64);r.step(20)
        r.step(1,2);r.step(120);r.cursor=0
    r.save();r.lines=[x for x in r.lines if x!='snapshot'];r.cursor=2

def choose_mara(r,no=False):
    # MSGBOX_YESNO opens automatically when the final page finishes.
    r.step(40,0,'mara-choice.ppm')
    if no:r.step(1,128);r.step(20)
    r.step(1,1);r.step(400);pages(r,'decline' if no else 'accept','Service_Text_Decline' if no else 'Service_Text_Accept');close(r)

# Ordinary first/repeat pretrial introduction and recovery, without new combat.
s=copy('guide-first','equipment');r=R('quiet',(4,5),3)
talk(r,128,'guide-first','Vestibule_Text_GuideIntro','Vestibule_Text_Rested','Vestibule_Text_TrialAdvice');r.flags=7
# First guide interaction sets the existing flag; adjust subsequent expectations.
r.lines=[x.replace('expect 35 1 4 5 3','expect 35 1 4 5 7') for x in r.lines]
r.lines+=['flag 34 1','duo healthy','uses 8 40 2 40'];talk(r,128,'guide-repeat','Vestibule_Text_RepeatTrial');journal(r,'pretrial','Trial','Optional');run('guide-first-pretrial',s,r)
s=copy('guide-post','guide-after-trial');r=R('quiet',(4,5));talk(r,128,'guide-post','Vestibule_Text_RepeatService');r.lines+=['duo healthy','uses 8 40 2 40'];r.anchor('trial');talk(r,128,'trial-repeat','Vestibule_Text_Won');journal(r,'posttrial','Patrols','Optional');run('guide-repeat-posttrial',s,r)

# Ordinary optional route: reserve, decline, accept, wait, take, hand in, repeat,
# all four quest Journal hints, and manual Save/cold-file persistence.
s=copy('quest','both-pending');r=R('field',(37,31));r.lines+=['item 378 2'];r.anchor('tag_interaction');talk(r,64,'reserved','Service_Text_TagReserved');r.anchor('workshop_door');r.anchor('lev');talk(r,128,'lev','Service_Text_Lev');r.anchor('mara');talk(r,128,'offer','Service_Text_Offer',finish=False);choose_mara(r,True);r.lines+=['flag 41 1','flag 42 0'];journal(r,'declined','Patrols','Optional')
talk(r,128,'reoffer','Service_Text_Offer',finish=False);choose_mara(r);r.lines+=['flag 41 0','flag 42 1'];talk(r,128,'waiting','Service_Text_Waiting');journal(r,'accepted','Patrols','QuestActive')
r.anchor('arrival');r.anchor('tag_interaction');talk(r,64,'pickup','Service_Text_Tag');r.lines+=['flag 44 1','item 379 1'];journal(r,'tag-return','Patrols','QuestReturn');talk(r,64,'tag-repeat','Service_Text_TagEmpty');r.anchor('workshop_door');r.anchor('mara');talk(r,128,'handin','Service_Text_Complete');r.lines+=['flag 43 1','item 379 0','item 378 4'];talk(r,128,'completed','Service_Text_Done');journal(r,'complete','Patrols','QuestDone');save(r);run('ordinary-optional-quest',s,r)
if not args.case or args.case=='ordinary-quest-cold':
    # A --case cold run depends on the saved file from the ordinary route.
    assert not args.case, 'Run the complete matrix to create the ordinary cold input'
    cold=out/'quest-cold.sav';shutil.copyfile(s,cold);sha=digest(cold);r=R('workshop',(4,5));r.lines+=['flag 43 1','flag 44 1','item 379 0','item 378 4'];talk(r,128,'cold-done','Service_Text_Done');journal(r,'cold-quest','Patrols','QuestDone');run('ordinary-quest-cold',cold,r);assert digest(cold)==sha

# Actual completed legacy save: checkpoint is an opening milestone, not Floor1.
s=copy('checkpoint','continuous');r=R('checkpoint',(4,4));journal(r,'checkpoint','Done','Optional');r.anchor('arrival');r.anchor('warden');talk(r,128,'warden-cleared','Boss_Text_Won');journal(r,'arena-done','Done','Optional');run('ordinary-completed-context',s,r)

# Explicit checksum-valid branch inputs; actual live ROM/menu/text remain intact.
def controlled(name,key,pos,flags=(),clear=(),full=False):
    s=copy(name,'both-pending');raw=s.read_bytes();sb1,sb2=saveinput.blocks(raw);bits=bytearray(sb1[0x1270:0x139c])
    for n in clear:bits[n//8]&=~(1<<(n%8))
    for n in flags:bits[n//8]|=1<<(n%8)
    num=spec['production_identity_proposal']['maps'][key]['map_num'];layout=spec['production_identity_proposal']['maps'][key]['layout_id']
    changes=[(0,struct.pack('<hh',*pos)),(4,saveinput.warp(35,num,-1,*pos)),(0x32,struct.pack('<H',layout)),(0x1438,struct.pack('<H',1)),(0x1270,bytes(bits)),(0x34,bytes(512)),(0xA30,bytes(0x240)),(0xC70,bytes(0x600))]
    if full:
        encryption=struct.unpack_from('<I',sb2,0xAC)[0]&0xffff
        items=b''.join(struct.pack('<HH',item,qty^encryption) for item,qty in [(378,98)]+[(item,99) for item in range(13,42)])
        changes.extend([(0x560,items),(0x5D8,struct.pack('<HH',379,1^encryption))])
    s.write_bytes(saveinput.patch(raw,changes));return s
kind='explicit controlled checksum-valid save input; ordinary controllers; unmodified ROM'
s=controlled('first-post','quiet',(4,5),clear=(34,));r=R('quiet',(4,5),3);talk(r,128,'first-post','Vestibule_Text_GuideIntro','Vestibule_Text_Rested','Vestibule_Text_ReturnAdvice');r.flags=7;r.lines=[x.replace('expect 35 1 4 5 3','expect 35 1 4 5 7') for x in r.lines];r.lines+=['duo healthy','uses 8 40 2 40'];run('controlled-first-posttrial',s,r,kind)
s=controlled('locked','boss',(8,7));r=R('boss',(8,7));talk(r,128,'locked','Boss_Text_Locked');journal(r,'locked-journal','Patrols','Optional');run('controlled-warden-locked',s,r,kind)
s=controlled('stairs','boss',(8,7),flags=(47,));r=R('boss',(8,7));talk(r,128,'cleared','Boss_Text_Won');journal(r,'stairs','Stairs','Optional');run('controlled-warden-stairs-hint',s,r,kind)
s=controlled('capacity','workshop',(4,5),flags=(42,44),clear=(43,),full=True);r=R('workshop',(4,5));r.lines+=['item 378 98','item 379 1'];talk(r,128,'full','Service_Text_Full');r.lines+=['item 378 98','item 379 1','flag 43 0'];journal(r,'capacity-return','Patrols','QuestReturn');save(r);run('controlled-capacity-no-consumption',s,r,kind)
if not args.case:
    cold=out/'capacity-cold.sav';shutil.copyfile(s,cold);sha=digest(cold);r=R('workshop',(4,5));r.lines+=['item 378 98','item 379 1','flag 43 0'];talk(r,128,'full-cold','Service_Text_Full');journal(r,'capacity-cold','Patrols','QuestReturn');run('controlled-capacity-cold',cold,r,kind);assert digest(cold)==sha
for name,objective,on,off in [('trial','Trial',(),(2135,2136,2137)),('both','Patrols',(2135,),(2136,2137)),('guard','Guard',(2135,2137),(2136,)),('howler','Howler',(2135,2136),(2137,)),('boss','Boss',(2135,2136,2137),()),('stairs','Stairs',(47,),()),('done','Done',(47,48),())]:
    s=controlled('journal-'+name,'field',(37,31),flags=on,clear=off+(47,48) if name not in ('stairs','done') else off);r=R('field',(37,31));journal(r,name,objective,'Optional');run('controlled-journal-'+name,s,r,kind)
assert all(digest(f)==sha for f,sha in original_hashes.items())
(out/'summary.json').write_text(json.dumps(dict(compiled_source=compiled,runner_source=head,rom_sha256=digest(rom),sessions=summary,originals_unchanged=True,method='Real native 240x160 pages and expanded-message byte equality against compiled labels. Controller-only routes; controlled save inputs explicitly distinguished. No new strategy, timing fishing, RAM writes or public raw dumps.'),indent=2)+'\n')
assert not git('status','--porcelain') and git('rev-parse','HEAD')==head
print('PASS',len(summary),'sessions',sum(s['assertions'] for s in summary),'assertions',flush=True)
