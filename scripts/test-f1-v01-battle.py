"""One frozen ordinary visual battle per build; exclusive claims and first STOP."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,importlib.util,json,re,shutil,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='c6d647a815ffce44a2419a2cf83b6c2c094359f0'
SEED='030b12fd3516351b0935b9298f24d0a2078fb33afecbccb6ba3a9b4c2db6b73c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def packed(p):
    im=Image.open(p);assert im.size==(64,64) and im.mode=='P';out=bytearray()
    for y in range(0,64,8):
        for x in range(0,64,8):
            b=im.crop((x,y,x+8,y+8)).tobytes();out.extend(b[i]|b[i+1]<<4 for i in range(0,64,2))
    return bytes(out)
def fixtures(out,seed,candidate):
    state=module('visual_seed_state',ROOT/'scripts/floor1/guard-first-state.py');decoded=state.seed_snapshot(seed,out/'expected')
    (out/'expected-counter.bin').write_bytes(struct.pack('<H',decoded['friendship_counter']))
    rows=json.loads((ROOT/'scripts/contracts/f1-v01-battle-assets.json').read_text())
    data=b''.join(packed(ROOT/r['source']) for r in rows)+packed(ROOT/'engine/graphics/dcc/warden/front.png')
    assert len(data)==18*2048;(out/'visual-poses.bin').write_bytes(data);(out/'visual-mode.bin').write_bytes(bytes([candidate]))
    palette=[]
    for ch in ['carl','donut','warden']:
        for line in (ROOT/'engine/graphics/dcc'/ch/'normal.pal').read_text().splitlines()[3:]:
            r,g,b=map(int,line.split());palette.append((r>>3)|((g>>3)<<5)|((b>>3)<<10))
    assert len(palette)==48;(out/'visual-palettes.bin').write_bytes(struct.pack('<48H',*palette))
def main():
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['before','after'],required=True);p.add_argument('--build',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=Path,required=True);p.add_argument('--prepare',action='store_true');a=p.parse_args()
    library=Path('/usr/lib/x86_64-linux-gnu/libmgba.so.0.10')
    assert sha(library)=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
    assert not git('status','--porcelain'),'Commit source/host/route before preparation or execution'
    head=git('rev-parse','HEAD');build=a.build.resolve();out=a.output.resolve()/a.case;seed=a.seed.resolve();engine=build/'source/engine';rom=engine/'pokeemerald.gba';game=(build/'tested-commit.txt').read_text().strip();route=ROOT/'scripts/contracts/f1-v01-battle.route'
    assert sha(seed)==SEED and git('rev-parse',game+':engine')==git('rev-parse',(BASE if a.case=='before' else head)+':engine')
    if a.case=='before':assert sha(rom)=='ae1e9d36a94ed2eaa9d8fc79d790a2dc47173b932551891d889c657e12ca8461'
    assert not (a.output.resolve()/'STOP.json').exists(),'Retain first STOP; no dependent execution'
    if a.prepare:
        out.mkdir(parents=True,exist_ok=False);code,_=module('visual_host',ROOT/'scripts/floor1/v01-battle-host.py').generate(git);(out/'observer.c').write_text(code)
        with (out/'host-build.log').open('w') as f:subprocess.run(['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],stdout=f,stderr=subprocess.STDOUT,check=True)
        with (out/'game.sym').open('w') as f:subprocess.run(['arm-none-eabi-nm','--defined-only',str(engine/'pokeemerald.elf')],stdout=f,check=True)
        with (out/'game.sym').open('a') as f:subprocess.run(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)],stdout=f,check=True)
        with (out/'game.sym').open('a') as f:f.write(module('verified_battle_functions',ROOT/'scripts/floor1/v01-battle-symbols.py').export(engine/'pokeemerald.elf',out/'verified-functions.json'))
        boundary=module('native_boundary_symbols',ROOT/'scripts/floor1/v01-native-boundary-symbols.py').write(engine/'pokeemerald.elf',out/'native-boundary.json')
        with (out/'game.sym').open('a') as f:
            for name,key in [('Entry','entry'),('Caller','caller_LR'),('Opcode','entry_opcode')]:f.write(f"{boundary[key]:08x} A bv_native{name}\n")
            f.write(module('native_timeline_symbols',ROOT/'scripts/floor1/v01-native-timeline-symbols.py').export(engine/'pokeemerald.elf',out/'native-timeline-points.json'))
        fixtures(out,seed,a.case=='after');shutil.copyfile(route,out/'input.route')
        identity={'source':head,'base':BASE,'game_build':game,'engine_tree':git('rev-parse',game+':engine'),'ROM_SHA256':sha(rom),'ELF_SHA256':sha(engine/'pokeemerald.elf'),'installed_library_SHA256':sha(library),'host_SHA256':sha(out/'observer.c'),'binary_SHA256':sha(out/'playtest'),'route_SHA256':sha(route),'input_Save_SHA256':SEED,'fixture_SHA256':{f.name:sha(f) for f in sorted(out.glob('*.bin'))},'symbols_SHA256':sha(out/'game.sym'),'verified_functions_SHA256':sha(out/'verified-functions.json'),'native_boundary_SHA256':sha(out/'native-boundary.json'),'battle_bound':30000,'visual_bound':36000,'execution_limit':1,'case':a.case}
        (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');print('PASS prepared',a.case,'without emulator');return
    identity=json.loads((out/'identity.json').read_text());assert identity['source']==head and identity['host_SHA256']==sha(out/'observer.c') and identity['binary_SHA256']==sha(out/'playtest') and identity['ROM_SHA256']==sha(rom) and identity['route_SHA256']==sha(route)==sha(out/'input.route')
    assert identity['installed_library_SHA256']==sha(library)
    for name,digest in identity['fixture_SHA256'].items():assert sha(out/name)==digest
    assert identity['native_boundary_SHA256']==sha(out/'native-boundary.json')
    assert identity['symbols_SHA256']==sha(out/'game.sym') and identity['verified_functions_SHA256']==sha(out/'verified-functions.json')
    if a.case=='after':
        before=a.output.resolve()/'before';summary=json.loads((before/'summary.json').read_text());assert summary['native_exit']==0 and summary['errors_bytes']==0
        shutil.copyfile(before/'native-boundary-trace.bin',out/'expected-native-boundary-trace.bin')
    save=out/'ordinary.sav';assert not save.exists();shutil.copyfile(seed,save)
    with (out/'execution-claim.json').open('x') as f:json.dump(identity,f,indent=2)
    with (out/'input.route').open() as inp,(out/'replay.log').open('w') as log,(out/'errors.log').open('w') as err:run=subprocess.run([str(out/'playtest'),str(rom),str(save),str(out/'game.sym')],cwd=out,stdin=inp,stdout=log,stderr=err)
    log=(out/'replay.log').read_text();footer=re.search(r'result=(\d+) assertions=(\d+)\n$',log)
    if (out/'visual-stop.json').exists():
        diagnostic=json.loads((out/'visual-stop.json').read_text());functions=json.loads((out/'verified-functions.json').read_text());lookup={r['address']:r['aliases'] for r in functions}
        diagnostic['native_phase_functions']=lookup.get(diagnostic['native_phase_address']&~1,[])
        diagnostic['CB2_functions']=lookup.get(diagnostic['CB2']&~1,[])
        diagnostic['unresolved_callback_functions']=lookup.get(diagnostic['unresolved_callback_address']&~1,[])
        diagnostic['private_VRAM_SHA256']={f.name:sha(f) for f in out.glob('visual-stop-actor*-vram.bin')}
        (out/'visual-stop.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    summary={'case':a.case,'execution_source':head,'native_exit':run.returncode,'errors_bytes':(out/'errors.log').stat().st_size,'assertions':int(footer[2]) if footer else None,'input_Save_SHA256':SEED,'output_Save_SHA256':sha(save),'replay_log_SHA256':sha(out/'replay.log'),'visual':re.findall(r'BV_FINISH .*',log),'peaks':re.findall(r'BV_PEAK .*',log),'warning':re.findall(r'BV_WARNING .*',log),'battles':re.findall(r'WARDEN .*',log),'vitals':re.findall(r'VITALS .*',log),'pilot':re.findall(r'pilot completed .*',log),'ordinary_controls_SHA256':hashlib.sha256('\n'.join(re.findall(r'pilot frame=.*',log)).encode()).hexdigest(),'pose_events':len(re.findall(r'BV_POSE .*',log))}
    summary['native_readiness']=re.findall(r'BV_READY .*',log);summary['native_phase_events']=len(re.findall(r'BV_PHASE .*',log));(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    try:
        assert run.returncode==0 and summary['errors_bytes']==0 and footer and int(footer[1])==0 and len(summary['visual'])==1 and len(summary['peaks'])==1
        assert summary['output_Save_SHA256']==SEED and sha(seed)==SEED
        if a.case=='after':
            before=json.loads((a.output.resolve()/'before/summary.json').read_text())
            for field in ['peaks','battles','vitals','pilot','ordinary_controls_SHA256']:assert summary[field]==before[field],field
        assert sha(rom)==identity['ROM_SHA256']
    except Exception as e:
        (a.output.resolve()/'STOP.json').write_text(json.dumps({'case':a.case,'validation_failure':str(e),'summary':summary},indent=2)+'\n');print((out/'errors.log').read_text());raise SystemExit('STOP first failure; no further emulator execution')
    for f in out.glob('*.ppm'):
        if re.fullmatch(r'battle-\d{5}\.ppm',f.name):continue
        im=Image.open(f);assert im.size==(240,160);im.save(f.with_suffix('.png'))
    print('PASS',a.case,summary['assertions'],'native assertions; actual raw clip ready for offline encoding')
if __name__=='__main__':main()
