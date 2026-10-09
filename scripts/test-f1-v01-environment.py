#!/usr/bin/env python3
"""Exclusive equivalent native scene routes; ordinary input, strict preservation."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,importlib.util,json,re,shutil,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='54526744eb7ed961007ffe6100f976a1e7448e8b'
SEED='030b12fd3516351b0935b9298f24d0a2078fb33afecbccb6ba3a9b4c2db6b73c'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fixtures(source,seed,out):
    state=module('v01_seed',ROOT/'scripts/floor1/guard-first-state.py')
    decoded=state.seed_snapshot(seed,out/'expected')
    (out/'expected-counter.bin').write_bytes(struct.pack('<H',decoded['friendship_counter']))
    flags=(out/'expected-flags.bin').read_bytes()
    names=['DCC_F1D1Field','DCC_F1D1Quiet','DCC_F1D1Workshop','DCC_F1D1Warden','DCC_F1D1Checkpoint']
    values={name:int(value,16) for name,value in re.findall(r'#define (FLAG_DCC_\w+)\s+(0x[0-9A-Fa-f]+)',(source/'engine/include/constants/flags.h').read_text())}
    patches=re.findall(r'\{ MAP_(\w+), (\d+), (\d+), (FLAG_\w+), (0x\w+), (0x\w+) \}',(source/'engine/src/data/dcc_opening.h').read_text())
    for i,name in enumerate(names):
        data=bytearray((source/'engine/data/layouts'/name/'map.bin').read_bytes());width=64 if i==0 else 16
        for mapname,x,y,flag,off,on in patches:
            if mapname==name.upper():
                value=values[flag];word=int(on if flags[value//8]&(1<<(value%8)) else off,16)
                struct.pack_into('<H',data,2*(int(y)*width+int(x)),word)
        (out/f'expected-map-{i}.bin').write_bytes(data)
    tiles=source/'engine/data/tilesets/secondary/dcc';im=Image.open(tiles/'tiles.png');data=bytearray()
    for y in range(0,im.height,8):
        for x in range(0,im.width,8):
            pixels=im.crop((x,y,x+8,y+8)).tobytes();data.extend(pixels[j]|pixels[j+1]<<4 for j in range(0,64,2))
    (out/'expected-atlas.bin').write_bytes(data)
    colors=[]
    for bank in (6,7,8):
        for line in (tiles/'palettes'/f'{bank:02}.pal').read_text().splitlines()[3:]:
            r,g,b=map(int,line.split());colors.append((r>>3)|((g>>3)<<5)|((b>>3)<<10))
    (out/'expected-palettes.bin').write_bytes(struct.pack('<48H',*colors))
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['before','after'],required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=Path,required=True);p.add_argument('--prepare',action='store_true');a=p.parse_args()
    assert not git('status','--porcelain'),'Commit all inputs before preparation/execution'
    head=git('rev-parse','HEAD');build=a.build.resolve();out=a.output.resolve()/a.case;seed=a.seed.resolve();source=build/'source';engine=source/'engine';rom=engine/'pokeemerald.gba'
    assert sha(seed)==SEED
    game=(build/'tested-commit.txt').read_text().strip();assert git('rev-parse',game+':engine')==git('rev-parse',(BASE if a.case=='before' else head)+':engine')
    if a.case=='before':assert sha(rom)=='23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167'
    route=ROOT/'scripts/contracts/f1-v01-environment.route'
    if a.prepare:
        out.mkdir(parents=True,exist_ok=False)
        code,base=module('v01_host',ROOT/'scripts/floor1/v01-environment-host.py').generate(git);(out/'observer.c').write_text(code)
        with (out/'host-build.log').open('w') as f:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],stdout=f,stderr=subprocess.STDOUT,check=True)
        with (out/'game.sym').open('w') as f:subprocess.run(['arm-none-eabi-nm','--defined-only',str(engine/'pokeemerald.elf')],stdout=f,check=True)
        with (out/'game.sym').open('a') as f:subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)],stdout=f,check=True)
        fixtures(source,seed,out);shutil.copyfile(route,out/'input.route')
        ident={'source':head,'base':BASE,'game_build':game,'engine_tree':git('rev-parse',game+':engine'),'ROM_SHA256':sha(rom),'host_SHA256':sha(out/'observer.c'),'binary_SHA256':sha(out/'playtest'),'route_SHA256':sha(route),'input_Save_SHA256':SEED,'native_fixture_SHA256':{f.name:sha(f) for f in sorted(out.glob('expected-*'))},'frame_bound':24000,'battle_bound':0,'execution_limit':1,'case':a.case}
        (out/'identity.json').write_text(json.dumps(ident,indent=2)+'\n');print('PASS prepared',a.case,'no emulator');return
    ident=json.loads((out/'identity.json').read_text());assert ident['source']==head and ident['host_SHA256']==sha(out/'observer.c') and ident['binary_SHA256']==sha(out/'playtest') and ident['ROM_SHA256']==sha(rom) and ident['route_SHA256']==sha(route)==sha(out/'input.route')
    for name,digest in ident['native_fixture_SHA256'].items():assert sha(out/name)==digest
    assert not (a.output.resolve()/'STOP.json').exists(),'Preserve first STOP; no dependent run'
    if a.case=='after':
        before=json.loads((a.output.resolve()/'before/summary.json').read_text());assert before['exit']==0 and before['errors_bytes']==0
    save=out/'ordinary.sav';assert not save.exists();shutil.copyfile(seed,save)
    with (out/'execution-claim.json').open('x') as f:json.dump(ident,f,indent=2)
    with (out/'input.route').open() as inp,(out/'replay.log').open('w') as log,(out/'errors.log').open('w') as err:result=subprocess.run([str(out/'playtest'),str(rom),str(save),str(out/'game.sym')],cwd=out,stdin=inp,stdout=log,stderr=err)
    log=(out/'replay.log').read_text();footer=re.search(r'result=(\d+) assertions=(\d+)\n$',log)
    summary={'case':a.case,'execution_source':head,'exit':result.returncode,'errors_bytes':(out/'errors.log').stat().st_size,'assertions':int(footer[2]) if footer else None,'input_Save_SHA256':SEED,'output_Save_SHA256':sha(save),'replay_log_SHA256':sha(out/'replay.log'),'scene_peaks':re.findall(r'SCENE_PEAK .*',log),'views':re.findall(r'SCENE_VIEW .*',log),'clock':re.findall(r'COLD_CLOCK .*',log),'battles':re.findall(r'WARDEN .*',log)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    try:
        assert result.returncode==0 and summary['errors_bytes']==0 and footer and int(footer[1])==0
        assert summary['output_Save_SHA256']==SEED and sha(seed)==SEED
        assert len(summary['views'])==14 and 'WARDEN battle_frames=0 attempts=0' in log
        assert 'CLIP native_frames=' in log and 'record' not in (out/'errors.log').read_text()
        assert sha(rom)==ident['ROM_SHA256']
    except Exception as e:
        (a.output.resolve()/'STOP.json').write_text(json.dumps({'case':a.case,'validation_failure':str(e),'summary':summary},indent=2)+'\n');raise SystemExit('STOP first failure; no further emulator execution')
    for f in out.glob('*.ppm'):
        im=Image.open(f);assert im.size==(240,160);im.save(f.with_suffix('.png'))
    subprocess.run(['ffmpeg','-v','error','-framerate','262144/4389','-i',str(out/'clip-%05d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','18',str(out/'ordinary-walking.mp4')],check=True)
    print('PASS',a.case,summary['assertions'],'assertions; zero battles; unchanged ordinary Save')
if __name__=='__main__':main()
