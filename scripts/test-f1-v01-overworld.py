"""One exclusive ordinary character-stage route per committed before/after build."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,importlib.util,json,re,shutil,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='c2f0d74759bb35b2f25e99f104e48f88635f049f'
SEED='030b12fd3516351b0935b9298f24d0a2078fb33afecbccb6ba3a9b4c2db6b73c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def packed(atlas,width,height):
    im=Image.open(atlas);out=bytearray()
    for f in range(im.width//width):
        for y in range(0,height,8):
            for x in range(0,width,8):
                pixels=im.crop((f*width+x,y,f*width+x+8,y+8)).tobytes();out.extend(pixels[i]|pixels[i+1]<<4 for i in range(0,64,2))
    return bytes(out)
def fixtures(source,seed,out,candidate):
    module('character_fixtures',ROOT/'scripts/test-f1-v01-environment.py').fixtures(source,seed,out)
    engine=source/'engine';(out/'character-mode.bin').write_bytes(bytes([candidate]))
    (out/'character-carl.bin').write_bytes(packed(engine/'graphics/object_events/pics/people/carl/walking.png',16,32))
    (out/'character-donut.bin').write_bytes(packed(engine/'graphics/dcc/donut/overworld.png',16,16))
    values=[]
    for name in ['carl','donut']:
        for line in (engine/'graphics/object_events/palettes'/f'{name}.pal').read_text().splitlines()[3:]:
            r,g,b=map(int,line.split());values.append((r>>3)|((g>>3)<<5)|((b>>3)<<10))
    (out/'character-palettes.bin').write_bytes(struct.pack('<32H',*values))
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['before','after'],required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=Path,required=True);p.add_argument('--prepare',action='store_true');a=p.parse_args()
    assert not git('status','--porcelain'),'Commit source, host and route before preparation/execution'
    head=git('rev-parse','HEAD');build=a.build.resolve();out=a.output.resolve()/a.case;seed=a.seed.resolve();source=build/'source';engine=source/'engine';rom=engine/'pokeemerald.gba';game=(build/'tested-commit.txt').read_text().strip();route=ROOT/'scripts/contracts/f1-v01-overworld.route'
    assert sha(seed)==SEED and git('rev-parse',game+':engine')==git('rev-parse',(BASE if a.case=='before' else head)+':engine')
    if a.case=='before':assert sha(rom)=='76dd6ae4606ad52167e7cdad5966ae02c695b968407b6e7c3b9bc5c66d0cc4e5'
    if a.prepare:
        out.mkdir(parents=True,exist_ok=False);code,_=module('character_host',ROOT/'scripts/floor1/v01-overworld-host.py').generate(git);(out/'observer.c').write_text(code)
        with (out/'host-build.log').open('w') as f:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],stdout=f,stderr=subprocess.STDOUT,check=True)
        with (out/'game.sym').open('w') as f:subprocess.run(['arm-none-eabi-nm','--defined-only',str(engine/'pokeemerald.elf')],stdout=f,check=True)
        with (out/'game.sym').open('a') as f:subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)],stdout=f,check=True)
        fixtures(source,seed,out,a.case=='after');shutil.copyfile(route,out/'input.route')
        ident={'source':head,'base':BASE,'game_build':game,'engine_tree':git('rev-parse',game+':engine'),'ROM_SHA256':sha(rom),'ELF_SHA256':sha(engine/'pokeemerald.elf'),'host_SHA256':sha(out/'observer.c'),'binary_SHA256':sha(out/'playtest'),'route_SHA256':sha(route),'input_Save_SHA256':SEED,'fixture_SHA256':{f.name:sha(f) for f in sorted(out.glob('*.bin'))},'frame_bound':24000,'battle_bound':0,'execution_limit':1,'case':a.case}
        (out/'identity.json').write_text(json.dumps(ident,indent=2)+'\n');print('PASS prepared',a.case,'no emulator');return
    ident=json.loads((out/'identity.json').read_text());assert ident['source']==head and ident['host_SHA256']==sha(out/'observer.c') and ident['binary_SHA256']==sha(out/'playtest') and ident['ROM_SHA256']==sha(rom) and ident['route_SHA256']==sha(route)==sha(out/'input.route')
    for name,digest in ident['fixture_SHA256'].items():assert sha(out/name)==digest
    assert not (a.output.resolve()/'STOP.json').exists(),'First STOP blocks dependent execution'
    if a.case=='after':
        before=json.loads((a.output.resolve()/'before/summary.json').read_text());assert before['native_exit']==0 and before['errors_bytes']==0
    save=out/'ordinary.sav';assert not save.exists();shutil.copyfile(seed,save)
    with (out/'execution-claim.json').open('x') as f:json.dump(ident,f,indent=2)
    with (out/'input.route').open() as inp,(out/'replay.log').open('w') as log,(out/'errors.log').open('w') as err:result=subprocess.run([str(out/'playtest'),str(rom),str(save),str(out/'game.sym')],cwd=out,stdin=inp,stdout=log,stderr=err)
    log=(out/'replay.log').read_text();footer=re.search(r'result=(\d+) assertions=(\d+)\n$',log)
    summary={'case':a.case,'execution_source':head,'native_exit':result.returncode,'errors_bytes':(out/'errors.log').stat().st_size,'assertions':int(footer[2]) if footer else None,'input_Save_SHA256':SEED,'output_Save_SHA256':sha(save),'replay_log_SHA256':sha(out/'replay.log'),'clock':re.findall(r'COLD_CLOCK .*',log),'battles':re.findall(r'WARDEN .*',log),'characters':re.findall(r'CHAR_FINISH .*',log),'talks':re.findall(r'CHAR_TALK .*',log),'clips':re.findall(r'CLIP .*',log),'scene_peaks':re.findall(r'SCENE_PEAK .*',log),'views':re.findall(r'SCENE_VIEW .*',log)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    try:
        assert result.returncode==0 and summary['errors_bytes']==0 and footer and int(footer[1])==0
        assert summary['output_Save_SHA256']==SEED and sha(seed)==SEED and sha(rom)==ident['ROM_SHA256']
        assert len(summary['talks'])==4 and len(summary['characters'])==1 and len(summary['clips'])==5 and len(summary['views'])==5
        assert 'WARDEN battle_frames=0 attempts=0' in log
    except Exception as e:
        (a.output.resolve()/'STOP.json').write_text(json.dumps({'case':a.case,'validation_failure':str(e),'summary':summary},indent=2)+'\n');raise SystemExit('STOP first failure; preserve claim/log/input; no dependent execution')
    for f in out.glob('*.ppm'):
        im=Image.open(f);assert im.size==(240,160);im.save(f.with_suffix('.png'))
    # Media encoding consumes existing frames offline on the host. No additional
    # emulator execution occurs here; missing container ffmpeg cannot trigger replay.
    print('PASS',a.case,summary['assertions'],'native assertions; media ready for offline encoding')
if __name__=='__main__':main()
