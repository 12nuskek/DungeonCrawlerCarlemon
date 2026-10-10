"""Freeze one candidate-only claim, no observer/game build or baseline replay."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010')
OLD=Path('/workspace/scratch/c01a-action-hints-r4-20261010')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
gate=module('freezeCompleteGate',ROOT/'scripts/floor1/c01a-complete-artifacts.py');sha=gate.sha
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def prepare():
    assert not git('status','--porcelain') and not (OUT/'freeze.json').exists() and not (OUT/'STOP.json').exists()
    old=json.loads((OLD/'freeze.json').read_text());cert=json.loads((OUT/'retained-baseline-acceptance.json').read_text());assert cert['PASS'] and cert['verifier_commit']==git('rev-parse','HEAD')
    for n,h in cert['original_r4_artifacts_SHA256'].items():assert sha(OLD/n)==h,n
    for n,h in cert['verifier_SHA256'].items():assert sha(ROOT/n)==h,n
    for n,h in old['tool_files'].items():assert sha(n)==h,n
    for n in ['observer.c','observer']:shutil.copyfile(OLD/n,OUT/n);assert sha(OUT/n)==sha(OLD/n)
    os.chmod(OUT/'observer',0o700)
    previous=json.loads((OLD/'candidate/identity.json').read_text());out=OUT/'candidate';out.mkdir()
    for n,h in previous['files_SHA256'].items():assert sha(OLD/'candidate'/n)==h;shutil.copyfile(OLD/'candidate'/n,out/n)
    for n,h in cert['reference_stream_SHA256'].items():
        assert sha(OLD/'baseline'/n)==h;shutil.copyfile(OLD/'baseline'/n,out/('expected-'+n));assert sha(out/('expected-'+n))==h
    assert sha(out/'game.sav')==cert['Save_SHA256'] and sha(previous['ROM'])==previous['ROM_SHA256'] and sha(Path(previous['ROM']).with_suffix('.elf'))==previous['ELF_SHA256']
    assert previous['source']=='807eeea457c973b097be9eab9e1556e20d0204aa' and git('rev-parse',previous['source']+':engine')==previous['engine_tree']==git('rev-parse','HEAD:engine')
    ident=dict(previous,revision='Candidate-only process5/attempt1 after separately corrected retained baseline4 acceptance',overall_process=5,overall_baseline_attempt=4,overall_candidate_attempt=1,files_SHA256={p.name:sha(p) for p in out.iterdir() if p.is_file()},retained_baseline_certificate_SHA256=sha(OUT/'retained-baseline-acceptance.json'))
    write(out/'identity.json',ident)
    _,generated=module('candidateOnlyRunner',ROOT/'scripts/test-f1-c01a-candidate-only.py').patched_runner();(OUT/'candidate-only-runner-generated.py').write_text(generated)
    dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    storage=dict(old['storage']);allocated=sum(p.stat().st_size for p in OLD.rglob('*') if p.is_file())+sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file());st=os.statvfs(OUT)
    assert st.f_bavail*st.f_frsize>=storage['pair_total_reserved_bytes']-allocated
    freeze=dict(helper_commit=git('rev-parse','HEAD'),source_checkpoint=git('rev-parse','HEAD'),base=old['base'],tested=old['tested'],candidate_only=True,retained_pair_root=str(OLD),retained_baseline_certificate_SHA256=sha(OUT/'retained-baseline-acceptance.json'),retained_baseline_reference_stream_SHA256=cert['reference_stream_SHA256'],original_r4_artifacts_SHA256=cert['original_r4_artifacts_SHA256'],cases=dict(candidate=sha(out/'identity.json')),Save_path=old['Save_path'],Save_SHA256=old['Save_SHA256'],route_SHA256=old['route_SHA256'],dependencies=dependencies,tool_files=old['tool_files'],storage=storage,remaining_reservation_check=dict(original_pair_bytes=storage['pair_total_reserved_bytes'],retained_and_current_allocated_bytes=allocated,available_bytes=st.f_bavail*st.f_frsize,required_remaining_bytes=storage['pair_total_reserved_bytes']-allocated),overall_counts_before=dict(baseline_processes=4,candidate_processes=0),overall_case_counts=dict(candidate=[5,4,1]),first_failure_stop=True,scope='One candidate process5/attempt1 using corrected offline certified original baseline4; unchanged observer/builds/route/Save, no baseline replay/rebuild',observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'),candidate_only_generated_runner_SHA256=sha(OUT/'candidate-only-runner-generated.py'))
    write(OUT/'freeze.json',freeze);public={k:v for k,v in freeze.items() if k not in ['dependencies','tool_files','Save_path','retained_pair_root']};public.update(freeze_SHA256=sha(OUT/'freeze.json'),build={k:ident[k] for k in ['source','engine_tree','ROM_SHA256','ELF_SHA256','observer_source_SHA256','observer_binary_SHA256','Save_SHA256']});write(OUT/'freeze-summary.json',public)
    print('Candidate-only freeze PASS; exact certified references/build/observer/bindings/independent Save copied and hashed; no compile or emulator')
if __name__=='__main__':prepare()
