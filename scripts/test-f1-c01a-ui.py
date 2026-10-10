"""One separately frozen menu baseline and conditional candidate; first STOP only."""
from pathlib import Path
import argparse,json,hashlib,subprocess,shutil,os,resource,importlib.util,selectors,time
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-action-hints-20261010')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(1048576):h.update(b)
    return h.hexdigest()
def write(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def limits():resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024**3,2*1024**3))
def run(case):
    assert case in ('baseline','candidate') and not (OUT/'STOP.json').exists()
    freeze=json.loads((OUT/'freeze.json').read_text());ident=json.loads((OUT/case/'identity.json').read_text());out=OUT/case
    assert sha(out/'identity.json')==freeze['cases'][case]
    for name,h in freeze['dependencies'].items():assert sha(ROOT/name)==h,name
    for name,h in freeze['tool_files'].items():assert sha(name)==h,name
    for name,h in ident['files_SHA256'].items():assert sha(out/name)==h,name
    assert sha(ident['ROM'])==ident['ROM_SHA256'] and sha(Path(ident['ROM']).with_suffix('.elf'))==ident['ELF_SHA256']
    seed=Path(freeze['Save_path']);assert sha(seed)==freeze['Save_SHA256']==sha(out/'game.sav')
    assert sha(OUT/'observer')==ident['observer_binary_SHA256'] and sha(OUT/'observer.c')==ident['observer_source_SHA256']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip(),'Commit before execution'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert freeze['helper_commit']==head or subprocess.check_output(['git','merge-base','--is-ancestor',freeze['helper_commit'],head],cwd=ROOT)==b''
    if case=='candidate':
        base=OUT/'baseline';receipt=json.loads((base/'runtime-result.json').read_text());assert receipt['PASS'] and receipt['exit']==0
        for name,target in [('native-boundary-trace.bin','expected-native-boundary-trace.bin'),('ui-frame-trace.bin','expected-ui-frame-trace.bin')]:
            assert sha(base/name)==receipt['output_SHA256'][name];shutil.copyfile(base/name,out/target);assert sha(out/target)==sha(base/name)
    claim=dict(case=case,execution_commit=head,freeze_SHA256=sha(OUT/'freeze.json'),identity_SHA256=sha(out/'identity.json'),pid=os.getpid(),start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),limit=1,no_retry=True)
    with (out/'exclusive-claim.json').open('x') as f:json.dump(claim,f,indent=2);f.write('\n')
    env=dict(os.environ);env['LD_LIBRARY_PATH']=str(TOOL/'usr/lib/x86_64-linux-gnu')
    command=[str(OUT/'observer'),ident['ROM'],str(out/'game.sav'),str(out/'game.sym')]
    with (out/'input.route').open('rb') as route,(out/'runtime.log').open('xb') as log:
        p=subprocess.Popen(command,cwd=out,env=env,stdin=route,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=limits)
        size=0
        while chunk:=p.stdout.read(65536):
            size+=len(chunk)
            if size>freeze['storage']['logs_max_per_case']:
                p.kill();p.wait();write(OUT/'STOP.json',dict(case=case,reason='Frozen log cap exceeded',no_retry=True));raise RuntimeError('STOP: log capacity')
            log.write(chunk)
        exitcode=p.wait()
    unchanged=sha(seed)==freeze['Save_SHA256']==sha(out/'game.sav')
    summary=dict(exit=exitcode,case=case,execution_commit=head,Save_unchanged=unchanged,log_SHA256=sha(out/'runtime.log'))
    try:
        assert exitcode==0 and unchanged
        lines=(out/'runtime.log').read_text().splitlines();finish=[l for l in lines if l.startswith('UI_FINISH frames=')];assert len(finish)==1
        frames=int(finish[0].split('frames=')[1].split()[0]);assert 0<frames<=18000
        path=out/('expected-native-boundary-trace.bin' if case=='candidate' else 'native-boundary-trace.bin')
        reference=module('c01ref',ROOT/'scripts/floor1/v01-new-input-reference.py').scan(path)
        assert path.stat().st_size<=freeze['storage']['native_reference_max_per_case']
        extra=out/('expected-ui-frame-trace.bin' if case=='candidate' else 'ui-frame-trace.bin');assert extra.stat().st_size==frames*2700
        captures=list(out.glob('battle-*.ppm'));assert len(captures)==frames
        shots=['carl-strike','carl-brace','strike-target','bag','party','summary','carl-return','donut-spark','donut-weaken','donut-return','spark-one','spark-empty','spark-rejected','spark-empty-return','weaken-after-empty']
        assert all((out/(s+'.ppm')).is_file() for s in shots)
        assert any(l.startswith('UI_MOVE actor=2 cursor=0 pp=0 ') for l in lines)
        assert lines[-1].startswith('result=0 assertions=')
        summary.update(PASS=True,visual_frames=frames,native_reference=reference,assertions=int(lines[-1].split('assertions=')[1]),ui_move_assertions=sum(l.startswith('UI_MOVE ') for l in lines),ui_callback_readiness_assertions=sum(l.startswith('UI_READY ') for l in lines),output_SHA256={path.name:sha(path),extra.name:sha(extra)},capture_count=len(captures),ui_state_full_frame_bytes=2700,no_Save=True,scope='Focused UI route only; native full B/F/E/EOF and supplemental EOF, no whole-battle/legacy/pacing acceptance')
    except Exception as error:
        summary.update(PASS=False,failure=repr(error),no_retry=True);write(out/'runtime-result.json',summary);write(OUT/'STOP.json',summary);print(json.dumps(summary,indent=2));raise
    write(out/'runtime-result.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=['baseline','candidate']);run(p.parse_args().case)
