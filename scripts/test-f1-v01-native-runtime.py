"""Compile concrete host and run installed synthetic instruction fixtures only.

Never invokes gameplay host, loads a ROM/Save, or prepares a gameplay trial.
Run inside the pinned dcc-party-resource environment.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    library=Path('/usr/lib/x86_64-linux-gnu/libmgba.so.0.10');assert sha(library)=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
    symbols=module('runtime_boundary_symbols',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
    builds={}
    for case,path in [('before','artifacts/floor1/v01-overworld/build-registered/source/engine'),('after','artifacts/floor1/v01-battle/build-headers/source/engine')]:
        builds[case]=symbols.write(ROOT/path/'pokeemerald.elf',out/(case+'-boundary.json'))
    compiler=['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'scripts/floor1')]
    host,_=module('concrete_runtime_host',ROOT/'scripts/floor1/v01-battle-host.py').generate(git)
    assert 'core->runFrame(core);' not in host and host.count('bv_native_frame(&native,')==1
    assert host.count('core->setKeys(core,')==13 and 'busWrite' not in host
    (out/'observer.c').write_text(host)
    with (out/'host-build.log').open('w') as log:
        subprocess.run(compiler+[str(out/'observer.c'),'-lmgba','-o',str(out/'host-compile-only')],stdout=log,stderr=subprocess.STDOUT,check=True)
    with (out/'interpreter.log').open('w') as log:
        subprocess.run(compiler+[str(ROOT/'scripts/floor1/v01-native-boundary-interpreter-fixture.c'),'-lmgba','-o',str(out/'interpreter')],stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'interpreter')],cwd=out,stdout=log,stderr=subprocess.STDOUT,check=True)
    with (out/'complete-reader.log').open('w') as log:
        subprocess.run(compiler+['-DBV_COMPLETE_SNAPSHOT_FIXTURE','-I'+str(out),str(ROOT/'scripts/floor1/v01-native-boundary-interpreter-fixture.c'),'-lmgba','-o',str(out/'complete-reader')],stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'complete-reader')],cwd=out,stdout=log,stderr=subprocess.STDOUT,check=True)
    result={'result':'PASS actual installed interpreter synthetic fixtures and full host compile only',
        'installed_library_SHA256':sha(library),'host_SHA256':sha(out/'observer.c'),'host_binary_SHA256':sha(out/'host-compile-only'),
        'interpreter_fixture_binary_SHA256':sha(out/'interpreter'),'complete_reader_fixture_binary_SHA256':sha(out/'complete-reader'),'gameplay_host_invocations':0,'ROMs_loaded':0,'Saves_loaded':0,'new_execution_claims':0,
        'actual_instruction_fixtures':'Installed ARMRunLoop baseline versus guarded ARMRun binding, actual GBA processEvents/mTiming APIs and hardware breakpoint snapshots; synthetic memory/instructions/events only',
        'game_equivalence':'UNVERIFIED; parent review before any fresh game execution',
        'builds':{case:{k:r[k] for k in ['ELF_SHA256','entry','caller_BL','caller_LR','entry_opcode']} for case,r in builds.items()},
        'source_SHA256':{str(f.relative_to(ROOT)):sha(f) for f in [ROOT/'scripts'/n for n in ['floor1/v01-native-boundary-runtime.h','floor1/v01-native-boundary-interpreter-fixture.c','floor1/v01-battle-host.py','floor1/v01-battle-observer.h','test-f1-v01-native-runtime.py','test-f1-v01-battle.py','test-f1-v01-battle-observer.py']]}}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_SHA256'}))
if __name__=='__main__':main()
