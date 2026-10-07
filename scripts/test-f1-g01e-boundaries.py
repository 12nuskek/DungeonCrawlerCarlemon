#!/usr/bin/env python3
"""Labeled checksum-valid copied input boundaries, actual production cold Continue.

These are synthetic save inputs, not ordinary playthroughs. No RAM writes or ROM
fixture behavior. Ordinary controller acceptance is a separate required matrix.
"""
from pathlib import Path
from PIL import Image
import hashlib,importlib.util,json,os,re,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    l=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(l);l.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
assert not git('status','--porcelain'),'Commit first'
head=git('rev-parse','HEAD');ordinary=Path(os.environ['DCC_G01E_ORDINARY_RUN']).resolve();identity=json.loads((ordinary/'identity.json').read_text());compiled=identity['compiled_source']
subprocess.run(['git','diff','--quiet',identity['runner_source'],head,'--','engine','scripts/playtest.c','scripts/floor1/live-save-observer.py','scripts/floor1/walking-harness.py'],cwd=ROOT,check=True)
rom=Path(identity['build'])/'source/engine/pokeemerald.gba';digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert digest(rom)==identity['rom_sha256']
out=Path(tempfile.mkdtemp(prefix='boundaries-',dir=ROOT/'artifacts/floor1/g01e'));print('Evidence:',out,flush=True)
si=module('input',ROOT/'scripts/floor1/save-boundary-input.py');seed=ROOT/'artifacts/floor1/a01/run-I7PJq0/guide-before-trial.sav';original_hash=digest(seed)
boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 boundary.ppm']
cases=[]
def case(name,changes,expected=None,sb2=(),base=seed):cases.append(dict(name=name,changes=changes,expected=expected,sb2=sb2,base=base))
u16=lambda value:struct.pack('<H',value)
pos=lambda x,y:struct.pack('<hh',x,y)
for value in [2,65535]:case('future-legacy-'+str(value),[(0x1438,u16(value))])
for value in [0,2]:case('unsupported-live-'+str(value),[(4,si.warp(35,1,-1,4,5)),(0x1438,u16(value))])
for group,num in [(36,0),(34,6),(-1,0),(35,5)]:case('unknown-'+str(group).replace('-','negative')+'-'+str(num),[(4,si.warp(group,num,-1,4,5))])
for layout in [0,65535]:case('stale-layout-'+str(layout),[(0x32,u16(layout))],(35,1,4,5,449))
case('all-owned-return-warps',[(12,si.warp(34,2,1,-1,-1)),(20,si.warp(34,3,1,-1,-1)),(28,si.warp(34,4,0,-1,-1)),(36,si.warp(34,5,-1,13,9))],(35,1,4,5,449))
case('dummy-and-stock-returns',[(12,si.warp(-1,-1,-1,-1,-1)),(20,si.warp(0,0,0,0,0)),(28,si.warp(1,0,-1,5,5)),(36,si.warp(-1,-1,-1,-1,-1))],(35,1,4,5,449))
case('continue-owned-howler',[(12,si.warp(34,3,1,-1,-1))],(35,0,51,27,448),[(9,b'\x01')])
case('continue-owned-warden',[(12,si.warp(34,4,-1,8,5))],(35,3,8,7,451),[(9,b'\x01')])
case('continue-invalid',[(12,si.warp(127,0,-1,4,5))],None,[(9,b'\x01')])
corridor=ROOT/'artifacts/floor1/a01/run-I7PJq0/howler-pending.sav'
for label,x,y,dx,dy in [('wall',14,0,37,31),('actor',10,6,37,31),('legal-howler',10,5,51,27),('negative',-1,-1,37,31),('oversized',32767,32767,37,31)]:
    case('corridor-'+label,[(0,pos(x,y))],(35,0,dx,dy,448),base=corridor)
live=ordinary/'i01-motion-second.sav'
case('live-stale-layout',[(0x32,u16(65535))],(35,2,10,5,450),base=live)
summary=[]
for c in cases:
    d=out/c['name'];d.mkdir();base=c['base'];before=digest(base);save=d/'controlled-copy.sav';save.write_bytes(si.patch(base.read_bytes(),c['changes'],c['sb2']));input_hash=digest(save)
    expected=c['expected'];lines=list(boot)
    if expected:
        sb,sb2=si.blocks(save.read_bytes());ef=sb[0x1274]&7;group,num,x,y,layout=expected
        lines += [f'expect {group} {num} {x} {y} {ef}','ready','snapshot']
    else:lines+=['menu','snapshot']
    lines+=['quit'];(d/'input.route').write_text('\n'.join(lines)+'\n')
    with (d/'input.route').open() as inputs,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:subprocess.run([str(ordinary/'playtest'),str(rom),str(save),str(ordinary/'game.sym')],cwd=d,stdin=inputs,stdout=log,stderr=err,check=True)
    log=(d/'replay.log').read_text();checks=int(re.search(r'result=0 assertions=(\d+)\n$',log)[1]);state=json.loads(re.findall(r'^STATE (.+)$',log,re.M)[0]);assert not (d/'errors.log').stat().st_size
    assert digest(base)==before and digest(save)==input_hash,'Cold boundary wrote save/original'
    if expected:
        assert state['version']==1 and state['layout']==layout
        assert len([o for o in state['objects'] if o['player']])==1
        if c['name']=='all-owned-return-warps':assert state['warps'][1:]==[[35,2,-1,4,4],[35,0,-1,51,27],[35,3,-1,8,7],[35,4,-1,4,4]]
        if c['name']=='dummy-and-stock-returns':assert state['warps'][1:]==[[-1,-1,-1,-1,-1],[0,0,0,0,0],[1,0,-1,5,5],[-1,-1,-1,-1,-1]]
    else:
        sb,sb2=si.blocks(save.read_bytes());assert state['version']==struct.unpack_from('<H',sb,0x1438)[0]
        assert (state['group'],state['map'])==(sb[4],sb[5]),'Rejected current identity changed'
    Image.open(d/'boundary.ppm').save(d/'boundary.png');(d/'state.json').write_text(json.dumps(state,indent=2)+'\n')
    summary.append(dict(route=c['name'],assertions=checks,synthetic_input=True,source=str(base.relative_to(ROOT)),source_hash=before,input_hash=input_hash,expected=expected,original_and_copy_unchanged=True));print(c['name'],'PASS',checks,flush=True)
assert digest(seed)==original_hash
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'identity.json').write_text(json.dumps(dict(runner=head,compiled_source=compiled,rom_sha256=digest(rom),ordinary_runtime=str(ordinary),method='Controlled copied checksum-valid save inputs; actual production cold Continue and read-only observer. No ROM fixture/RAM writes; not ordinary playthrough evidence.'),indent=2)+'\n')
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
print('PASS',len(summary),'controlled sessions',sum(v['assertions'] for v in summary),'assertions')
