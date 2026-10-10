"""Separately named corrected observer preparation; reuse verified game builds/Save."""
from pathlib import Path
import json,hashlib,subprocess,shutil,os,importlib.util
ROOT=Path(__file__).resolve().parents[2]
OLD=Path('/workspace/scratch/c01a-action-hints-20261010')
OUT=Path('/workspace/scratch/c01a-action-hints-r2-20261010')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def prepare():
    assert not (OUT/'freeze.json').exists() and not (OUT/'STOP.json').exists()
    assert (OLD/'STOP.json').is_file() and json.loads((OLD/'STOP.json').read_text())['exit']==121
    # Verify every byte retained by the old archive manifest, including failed
    # observer/claim/contract/input/runtime evidence. Never edit those files.
    oldmanifest=json.loads((OLD/'private-retention-manifest.json').read_text())
    for n,r in oldmanifest.items():assert sha(OLD/n)==r['SHA256'] and (OLD/n).stat().st_size==r['size'],n
    oldfreeze=json.loads((OLD/'freeze.json').read_text());seed=Path(oldfreeze['Save_path']);assert sha(seed)==oldfreeze['Save_SHA256']
    for n,h in oldfreeze['tool_files'].items():assert sha(n)==h,n
    proof=json.loads((OUT/'start-binding-proof.json').read_text());assert proof['PASS'] and proof['declared']==proof['checked']==16 and proof['missing_zero_and_extra_rejected']==66
    code=module('r2host',ROOT/'scripts/floor1/c01a-ui-host.py').generate(git)
    oldcode=(OLD/'observer.c').read_text();assert code==oldcode.replace('unsigned a[17]','unsigned a[16]').replace('for(unsigned z=0;z<17;z++)if(!ui.a[z])','for(unsigned z=0;z<16;z++)if(!ui.a[z])')
    (OUT/'observer.c').write_text(code)
    env=dict(os.environ);env['PATH']=str(TOOL/'usr/bin')+':'+env['PATH']
    command=['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(TOOL/'usr/include'),str(OUT/'observer.c'),'-L'+str(TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(OUT/'observer')]
    proc=subprocess.run(command,env=env,capture_output=True);(OUT/'observer-compile.log').write_bytes(proc.stdout+proc.stderr);assert proc.returncode==0
    cases={}
    for case in ['baseline','candidate']:
        previous=json.loads((OLD/case/'identity.json').read_text());assert sha(OLD/case/'identity.json')==oldfreeze['cases'][case]
        engine=Path(previous['ROM']).parent
        assert sha(engine/'pokeemerald.gba')==previous['ROM_SHA256'] and sha(engine/'pokeemerald.elf')==previous['ELF_SHA256']
        assert git('rev-parse',previous['source']+':engine')==previous['engine_tree']
        out=OUT/case;out.mkdir()
        for n,h in previous['files_SHA256'].items():
            assert sha(OLD/case/n)==h,n
            shutil.copyfile(OLD/case/n,out/n);assert sha(out/n)==h
        assert sha(out/'game.sav')==sha(seed)
        assert sha(out/'input.route')==oldfreeze['route_SHA256']
        identity=dict(previous,observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'),revision='C01a r2 reviewed slot count only',overall_process=2 if case=='baseline' else 3,overall_baseline_attempt=2 if case=='baseline' else None,overall_candidate_attempt=1 if case=='candidate' else None)
        write(out/'identity.json',identity);cases[case]=sha(out/'identity.json')
    storage=dict(oldfreeze['storage']);storage['pair_total_reserved_bytes']=20*1024**3
    st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=storage['pair_total_reserved_bytes']
    dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    write(OUT/'freeze.json',dict(source_checkpoint=git('rev-parse','HEAD'),helper_commit=git('rev-parse','HEAD'),base=oldfreeze['base'],tested=oldfreeze['tested'],cases=cases,route_SHA256=oldfreeze['route_SHA256'],Save_path=str(seed),Save_SHA256=sha(seed),storage=storage,dependencies=dependencies,tool_files=oldfreeze['tool_files'],scope='Reviewed two-line corrected C01a observer only; same ordinary menu route; no game rebuild/reconstruction/V01 replay',prior_STOP121_preserved=dict(manifest_SHA256=sha(OLD/'private-retention-manifest.json'),files=len(oldmanifest),freeze_SHA256=sha(OLD/'freeze.json'),observer_SHA256=sha(OLD/'observer.c')),overall_counts_before=dict(processes=1,baseline_attempts=1,candidates=0),overall_case_counts=dict(baseline=[2,2,0],candidate=[3,2,1]),first_failure_stop=True,candidate_requires_complete_baseline_PASS=True))
    print('Corrected C01a r2 preparation PASS; old57 retained entries/builds/Save verified; one host compile; no emulator')
if __name__=='__main__':prepare()
