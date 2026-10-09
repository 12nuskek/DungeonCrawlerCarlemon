"""Run synthetic installed-core neutrality; never invoke the gameplay host."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,stat,struct,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    private=out/'private-fixture-output';private.mkdir(mode=0o700)
    with (out/'fixture.log').open('w') as log:
        subprocess.run(['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(ROOT/'scripts/floor1'),
            str(ROOT/'scripts/floor1/v01-native-timeline-fixture.c'),'-lmgba','-o',str(out/'fixture')],stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run([str(out/'fixture')],cwd=private,stdout=log,stderr=subprocess.STDOUT,check=True)
    assert 'total38 synthetic timeline cases' in (out/'fixture.log').read_text()
    data=[]
    for f in sorted(private.glob('*.bin')):
        assert stat.S_IMODE(f.stat().st_mode)==0o600
        b=f.read_bytes();assert b[:8]==b'BVTIME01' and struct.unpack_from('<II',b,8)==(46,1000000)
        assert (len(b)-16)%184==0
        rows=[struct.unpack_from('<46I',b,i) for i in range(16,len(b),184)]
        data.append({'file':f.name,'records':len(rows),'synthetic':True,'SHA256':sha(f)})
    spec=importlib.util.spec_from_file_location('timeline_symbols',ROOT/'scripts/floor1/v01-native-timeline-symbols.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    pins={}
    for case,path in [('before','artifacts/floor1/v01-overworld/build-registered/source/engine'),('original_candidate','artifacts/floor1/v01-battle/build-headers/source/engine')]:
        pins[case]=m.resolve(ROOT/path/'pokeemerald.elf');(out/(case+'-points.json')).write_text(json.dumps(pins[case],indent=2)+'\n')
    result={'result':'PASS installed synthetic timeline parity/neutrality/strict stream/fail-closed cases','cases':38,
        'gameplay_host_invocations':0,'ROMs_loaded':0,'Saves_loaded':0,'new_execution_claims':0,
        'installed_library_SHA256':sha('/usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5'),'fixture_binary_SHA256':sha(out/'fixture'),
        'source_SHA256':{str(f.relative_to(ROOT)):sha(f) for f in [ROOT/'scripts/floor1'/n for n in ['v01-native-timeline.h','v01-native-timeline-fixture.c','v01-native-timeline-symbols.py','v01-native-boundary-runtime.h','v01-native-boundary-adapter.h']]},
        'synthetic_binary_inventory':data,'ELF_pins':{k:v['ELF_SHA256'] for k,v in pins.items()},
        'limits':{'per_batch_records':4096,'total_records':1000000,'event_queue_nodes':64,'copy_requests':64},
        'scope':'Synthetic mechanism/control neutrality only. No actual timing ground truth or gameplay-equivalence claim.'}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['source_SHA256','synthetic_binary_inventory']}))
if __name__=='__main__':main()
