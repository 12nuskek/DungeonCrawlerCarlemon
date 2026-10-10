"""Freeze reviewed menu-input correction; reuse r2 observer/builds/normal Save."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-action-hints-r3-20261010')
OLD=Path('/workspace/scratch/c01a-action-hints-r2-20261010')
FIRST=Path('/workspace/scratch/c01a-action-hints-20261010')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(1048576):h.update(b)
    return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prepare():
    assert not git('status','--porcelain'),'Commit offline-tested helpers before freezing'
    assert not (OUT/'freeze.json').exists() and not (OUT/'STOP.json').exists()
    old=json.loads((OLD/'freeze.json').read_text());seed=Path(old['Save_path'])
    assert sha(seed)==old['Save_SHA256']=='53f62dc2e283d89236d5572f47c3e7449c0bc1c06de738b1427fc9664ae67eb6'
    preserved={}
    for root,exitcode in [(FIRST,121),(OLD,122)]:
        assert json.loads((root/'STOP.json').read_text())['exit']==exitcode
        manifest=json.loads((root/'private-retention-manifest.json').read_text())
        for n,r in manifest.items():assert sha(root/n)==r['SHA256'] and (root/n).stat().st_size==r['size'],(root,n)
        preserved[str(exitcode)]=dict(files=len(manifest),manifest_SHA256=sha(root/'private-retention-manifest.json'),archive_SHA256=sha(root/'private-evidence.tar.gz'),STOP_SHA256=sha(root/'STOP.json'),freeze_SHA256=sha(root/'freeze.json'))
    assert preserved['121']['archive_SHA256']=='3fc4ed0f7381e9c7e4a4a72c948dfa81df03f53508e2fe3e4668d33f59754861'
    assert preserved['122']['archive_SHA256']=='ba172a84626a0676e662198a8a63be6c54abc2c59e6df16348a1f2f88cbb47c5'
    for n,h in old['tool_files'].items():assert sha(n)==h,n
    route=ROOT/'scripts/contracts/f1-c01a-ui-r3.route'
    proof=json.loads((OUT/'offline-route-proof.json').read_text())
    assert proof['PASS'] and proof['commands']==156 and proof['original_mistakes_rejected']==20 and proof['corrected_route_SHA256']==sha(route)
    code=module('c01r3host',ROOT/'scripts/floor1/c01a-ui-host.py').generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()==sha(OLD/'observer.c')=='9cbe47619817803bb075f8b59470b24b45deccb172e87e7a0859fa2c71d76c18'
    assert sha(OLD/'observer')=='8589d38042ea026d8a7a8b936ae98dad79b90dfc806e9f3a997b2f97c185964c'
    for n in ['observer','observer.c']:shutil.copyfile(OLD/n,OUT/n);assert sha(OUT/n)==sha(OLD/n)
    os.chmod(OUT/'observer',0o700)
    cases={}
    for case in ['baseline','candidate']:
        previous=json.loads((OLD/case/'identity.json').read_text());assert sha(OLD/case/'identity.json')==old['cases'][case]
        engine=Path(previous['ROM']).parent
        assert sha(engine/'pokeemerald.gba')==previous['ROM_SHA256'] and sha(engine/'pokeemerald.elf')==previous['ELF_SHA256']
        assert git('rev-parse',previous['source']+':engine')==previous['engine_tree']
        # Native offline proof executes the real build-source handlers. Compare
        # those source bytes to their recorded build commit, allowing only the
        # repository's historical CRLF checkout representation.
        for n,h in proof['cases'][case]['source_SHA256'].items():
            assert sha(engine/n)==h
            blob=subprocess.check_output(['git','show',previous['source']+':engine/'+n],cwd=ROOT)
            assert (engine/n).read_bytes().replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),n
        out=OUT/case;out.mkdir();files={}
        for n,h in previous['files_SHA256'].items():
            assert sha(OLD/case/n)==h,n
            shutil.copyfile(route if n=='input.route' else OLD/case/n,out/n);files[n]=sha(out/n)
            assert files[n]==(sha(route) if n=='input.route' else h)
        assert sha(out/'game.sav')==sha(seed)
        ident=dict(previous,files_SHA256=files,revision='C01a r3 reviewed ten menu input corrections; r2 observer unchanged',overall_process=3 if case=='baseline' else 4,overall_baseline_attempt=3,overall_candidate_attempt=0 if case=='baseline' else 1)
        write(out/'identity.json',ident);cases[case]=sha(out/'identity.json')
    storage=dict(old['storage']);st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=storage['pair_total_reserved_bytes']
    dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    freeze=dict(source_checkpoint=git('rev-parse','HEAD'),helper_commit=git('rev-parse','HEAD'),base=old['base'],tested=old['tested'],cases=cases,route_SHA256=sha(route),Save_path=str(seed),Save_SHA256=sha(seed),storage=storage,dependencies=dependencies,tool_files=old['tool_files'],scope='Reviewed ten command/input corrections only; reuse unchanged16-slot observer, game builds and ordinary Save; no rebuild/reconstruction/V01 replay',prior_STOPs_preserved=preserved,offline_route_proof_SHA256=sha(OUT/'offline-route-proof.json'),overall_counts_before=dict(processes=2,baseline_attempts=2,candidates=0),overall_case_counts=dict(baseline=[3,3,0],candidate=[4,3,1]),first_failure_stop=True,candidate_requires_complete_baseline_PASS=True)
    write(OUT/'freeze.json',freeze)
    public={k:v for k,v in freeze.items() if k not in ['dependencies','tool_files','Save_path']}
    public['freeze_SHA256']=sha(OUT/'freeze.json');public['observer_source_SHA256']=sha(OUT/'observer.c');public['observer_binary_SHA256']=sha(OUT/'observer')
    public['builds']={case:{k:v for k,v in json.loads((OUT/case/'identity.json').read_text()).items() if k in ['source','engine_tree','ROM_SHA256','ELF_SHA256','Save_SHA256','overall_process','overall_baseline_attempt','overall_candidate_attempt']} for case in cases}
    write(OUT/'freeze-summary.json',public)
    print('C01a r3 freeze PASS; reused observer, verified builds/Save/tools/native sources; prior57+3472 entries exact; no emulator/compile')
if __name__=='__main__':prepare()
