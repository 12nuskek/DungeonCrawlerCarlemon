#!/usr/bin/env python3
"""Ordinary copied saves/controller migration, second cold loads, read-only state."""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json,os,re,shlex,shutil,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def module(name,path):
    l=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(l);l.loader.exec_module(m);return m
assert not git('status','--porcelain'),'Commit before runtime checks'
head=git('rev-parse','HEAD');build=Path(os.environ['DCC_G01E_BUILD']).resolve();compiled=(build/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',compiled,head,'--','engine'],cwd=ROOT,check=True)
assert (build/'source/engine/pokeemerald.gba').is_file(),'Fresh committed production build required'
out=Path(tempfile.mkdtemp(prefix='ordinary-',dir=ROOT/'artifacts/floor1/g01e'));print('Evidence:',out,flush=True)
(out/'tested-commit.txt').write_text(head+'\n');(out/'compiled-source.txt').write_text(compiled+'\n')
rom=build/'source/engine/pokeemerald.gba';sym=out/'game.sym'
with sym.open('w') as log:subprocess.run(['arm-none-eabi-nm','--defined-only',str(build/'source/engine/pokeemerald.elf')],stdout=log,check=True)
subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(build/'source/engine')],stdout=sym.open('a'),check=True)
obs=module('observer',ROOT/'scripts/floor1/live-save-observer.py');walk=module('walking',ROOT/'scripts/floor1/walking-harness.py');g=module('geometry',ROOT/'scripts/floor1/relocation-graybox.py');save_input=module('save_input',ROOT/'scripts/floor1/save-boundary-input.py')
code=obs.instrument(walk.instrument(git('show',head+':scripts/playtest.c')+'\n'))
code=code.replace('!number(values[0],15,&tx)','!number(values[0],255,&tx)').replace('!number(values[1],11,&ty)','!number(values[1],255,&ty)')
(out/'observer.c').write_text(code)
with (out/'host-build.log').open('w') as log:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',*shlex.split(os.environ.get('DCC_TEST_CFLAGS','')),str(out/'observer.c'),*shlex.split(os.environ.get('DCC_TEST_LDFLAGS','')),'-lmgba','-o',str(out/'playtest')],stdout=log,stderr=subprocess.STDOUT,check=True)
spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text());ids=spec['production_identity_proposal']['maps'];maps=spec['maps'];boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 cold.ppm']
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
summary=[]
def run(name,save,lines):
    d=out/name;d.mkdir();(d/'input.route').write_text('\n'.join(lines+['quit'])+'\n')
    with (d/'input.route').open() as inputs,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:subprocess.run([str(out/'playtest'),str(rom),str(save),str(sym)],cwd=d,stdin=inputs,stdout=log,stderr=err,check=True)
    log=(d/'replay.log').read_text();checks=int(re.search(r'result=0 assertions=(\d+)\n$',log)[1]);assert not (d/'errors.log').stat().st_size
    states=[json.loads(v) for v in re.findall(r'^STATE (.+)$',log,re.M)]
    (d/'states.json').write_text(json.dumps(states,indent=2)+'\n')
    for p in d.glob('*.ppm'):Image.open(p).save(p.with_suffix('.png'))
    summary.append(dict(route=name,assertions=checks,states=len(states),errors=0));print(name,'PASS',checks,flush=True);return states
def flag(data,n):return (data[n//8]>>(n%8))&1
def expected(old,sb):
    if old==0:return 'field',(8,38)
    if old==1:return 'quiet',(4,5)
    if old==2:return 'workshop',(4,4)
    if old==3:
        x,y=struct.unpack_from('<hh',sb);return 'field',((51,27) if 8<=x<16 and 0<=y<12 else (37,31))
    if old==4:return 'boss',(8,7)
    if old==5:return 'checkpoint',(4,4)
    raise ValueError(old)
def check_initial(state,sb,sb2,key,pos):
    assert (state['group'],state['map'],state['layout'],state['version'],state['loop'],tuple(state['pos']))==(35,ids[key]['map_num'],ids[key]['layout_id'],1,0,pos)
    regions=state['regions'];assert bytes.fromhex(regions['live_duo'])==sb[0x238:0x300], 'Migration changed live party'
    inv=bytes.fromhex(regions['inventory_money']);key_new=int.from_bytes(bytes.fromhex(regions['encryption_key']),'little');key_old=struct.unpack_from('<I',sb2,0xAC)[0]
    assert save_input.inventory(inv,key_new)==save_input.inventory(sb[0x490:0xA30],key_old),'Logical inventory/money changed'
    flags=bytes.fromhex(regions['flags']);assert all(flag(flags,n)==flag(sb[0x1270:0x139c],n) for n in list(range(32,49))+list(range(2135,2140)))
    vars_new=bytes.fromhex(regions['vars']);assert vars_new[32:156]==sb[0x139c+32:0x139c+156] and vars_new[158:]==sb[0x139c+158:0x159c],'Unowned persistent vars changed'
    players=[o for o in state['objects'] if o['player']];assert len(players)==1
    player=players[0];assert player['slot']==state['avatar'] and tuple(player['pos'])==pos and player['group']==35 and player['map']==ids[key]['map_num'] and 1<=player['facing']<=4
    for obj in state['objects']:
        assert obj['group']==35 and obj['map']==ids[key]['map_num'] and obj['pos']==obj['initial']==obj['previous']
        if not obj['player']:
            m=json.loads((build/'source/engine/data/maps'/ids[key]['name']/'map.json').read_text());source=m['object_events'][obj['local_id']-1];assert obj['pos']==[source['x'],source['y']]
    assert set(bytes.fromhex(regions['map_view']))=={0},'Stale cache survived'
    for i,w in enumerate(state['warps'][1:],1):
        original=struct.unpack_from('<bbbBhh',sb,4+8*i)
        if original[0]!=34:assert w==[original[0],original[1],original[2],original[4],original[5]],'Stock/dummy warp changed'
route_module=module('route',ROOT/'scripts/floor1/live-route.py')
Route=lambda key,pos,facing,flags:route_module.Route(spec,g,key,pos,facing,flags)
fixtures=json.loads((ROOT/'artifacts/floor1/g01c/state-v866mr6r/summary.json').read_text())
for fixture in fixtures:
    name=fixture['route'];original=ROOT/fixture['source_save'];sha=digest(original);sb,sb2=save_input.blocks(original.read_bytes());old=sb[5];key,pos=expected(old,sb);ef=sb[0x1274]&7
    save=out/(name+'.sav');shutil.copyfile(original,save)
    states=run(name+'-first',save,boot+[f'expect 35 {ids[key]["map_num"]} {pos[0]} {pos[1]} {ef}','ready','snapshot'])
    check_initial(states[0],sb,sb2,key,pos);assert digest(save)==sha and digest(original)==sha
    r=Route(key,pos,next(o['facing'] for o in states[0]['objects'] if o['player']),ef)
    if key=='quiet':r.anchor('donut_staging');r.talk(128,'donut');r.anchor('arrival')
    elif key=='workshop':r.anchor('lev');r.talk(128,'lev');r.anchor('arrival')
    elif key=='checkpoint':r.anchor('review');r.talk(128,'review');r.anchor('arrival')
    elif key=='boss':
        r.anchor('stairs');r.talk(128,'stairs')
        if flag(sb[0x1270:0x139c],47):
            r.key='checkpoint';r.pos=(4,4);r.expect();r.anchor('arrival')
        else:r.anchor('arrival')
    else:
        r.anchor('quiet_door');r.anchor('donut_staging');r.talk(128,'donut');r.anchor('arrival')
    while r.key!='field':r.anchor('arrival')
    # Return through a different meaningful interior, then manual Save. No heal,
    # battle/reward/craft is used to obscure preserved migration resources.
    r.anchor('workshop_door');r.anchor('lev');r.talk(128,'lev-after-transition');r.save()
    after=run(name+'-controller-save',save,boot+r.lines)[-1];assert digest(original)==sha and digest(save)!=sha
    copy=out/(name+'-second.sav');shutil.copyfile(save,copy);second_sha=digest(copy)
    after2=run(name+'-second-cold',copy,boot+[f'expect 35 2 {r.pos[0]} {r.pos[1]} {ef}','ready','snapshot'])[-1]
    for field in ['version','loop','layout','pos','warps']:assert after[field]==after2[field],('Second load changed',name,field)
    for field in ['live_duo','flags','vars']:assert after['regions'][field]==after2['regions'][field],('Second load changed',name,field)
    a,b=after['regions'],after2['regions'];ka=int.from_bytes(bytes.fromhex(a['encryption_key']),'little');kb=int.from_bytes(bytes.fromhex(b['encryption_key']),'little')
    assert save_input.inventory(bytes.fromhex(a['inventory_money']),ka)==save_input.inventory(bytes.fromhex(b['inventory_money']),kb),'Second cold changed logical inventory/money'
    assert bytes.fromhex(a['inventory_money'])[0x848-0x490:]==bytes.fromhex(b['inventory_money'])[0x848-0x490:],'Second cold changed unencrypted inventory tail'
    assert digest(copy)==second_sha and digest(original)==sha
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'identity.json').write_text(json.dumps(dict(compiled_source=compiled,runner_source=head,rom_sha256=digest(rom),build=str(build),method='Copied ordinary originals; actual controller interactions/transitions/manual Save/second cold; read-only observer. No ROM fixtures, RAM writes or save patch in ordinary matrix.'),indent=2)+'\n')
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
print('PASS',len(summary),'ordinary production sessions',sum(r['assertions'] for r in summary),'assertions',flush=True)
