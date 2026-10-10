"""Freeze reviewed readiness/diagnostics; reuse exact games, route and Save."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-action-hints-r4-20261010')
OLD=Path('/workspace/scratch/c01a-action-hints-r3-20261010')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(1048576):h.update(b)
    return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prepare():
    assert not git('status','--porcelain')
    assert not (OUT/'freeze.json').exists() and not (OUT/'STOP.json').exists()
    old=json.loads((OLD/'freeze.json').read_text());seed=Path(old['Save_path']);assert sha(seed)==old['Save_SHA256']
    preserved={}
    for revision,exitcode,archive in [('c01a-action-hints-20261010',121,'3fc4ed0f7381e9c7e4a4a72c948dfa81df03f53508e2fe3e4668d33f59754861'),('c01a-action-hints-r2-20261010',122,'ba172a84626a0676e662198a8a63be6c54abc2c59e6df16348a1f2f88cbb47c5'),('c01a-action-hints-r3-20261010',122,'d2061de7c4816de637eb490111191da30cb4adcb933cb739ae5b8469059de551')]:
        root=OUT.parent/revision;assert json.loads((root/'STOP.json').read_text())['exit']==exitcode
        assert sha(root/'private-evidence.tar.gz')==archive
        manifest=json.loads((root/'private-retention-manifest.json').read_text())
        seen=set()
        with tarfile.open(root/'private-evidence.tar.gz','r|gz') as tar:
            for member in tar:
                # Verify the completed archive independently, including frozen
                # source entries whose live paths need not still exist.
                n=member.name
                if n not in manifest:continue
                assert n not in seen and member.isfile();seen.add(n);r=manifest[n]
                data=tar.extractfile(member).read();assert len(data)==r['size'] and hashlib.sha256(data).hexdigest()==r['SHA256'],n
                if (root/n).is_file():assert sha(root/n)==r['SHA256'] and (root/n).stat().st_size==r['size'],n
        assert seen==set(manifest)
        preserved[revision]=dict(exit=exitcode,files=len(manifest),archive_SHA256=archive,manifest_SHA256=sha(root/'private-retention-manifest.json'),STOP_SHA256=sha(root/'STOP.json'),freeze_SHA256=sha(root/'freeze.json'))
    for n,h in old['tool_files'].items():assert sha(n)==h,n
    proofs=['readiness-proof.json','native-edge-layout-proof.json','passivity-compile-proof.json','baseline-bindings-proof.json','candidate-bindings-proof.json']
    for n in proofs:assert json.loads((OUT/n).read_text())['PASS'],n
    code=module('hostr4',ROOT/'scripts/floor1/c01a-ui-host-r4.py').generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()==sha(OUT/'observer.c')
    p=json.loads((OUT/'passivity-compile-proof.json').read_text());assert p['observer_binary_SHA256']==sha(OUT/'observer')
    route=ROOT/'scripts/contracts/f1-c01a-ui-r3.route';assert sha(route)==old['route_SHA256']
    cases={}
    for case in ['baseline','candidate']:
        previous=json.loads((OLD/case/'identity.json').read_text());assert sha(OLD/case/'identity.json')==old['cases'][case]
        engine=Path(previous['ROM']).parent
        assert sha(engine/'pokeemerald.gba')==previous['ROM_SHA256'] and sha(engine/'pokeemerald.elf')==previous['ELF_SHA256']
        assert git('rev-parse',previous['source']+':engine')==previous['engine_tree']
        binding=json.loads((OUT/(case+'-bindings-proof.json')).read_text());assert binding['ELF_SHA256']==previous['ELF_SHA256'] and len(binding['points'])==12
        out=OUT/case;out.mkdir();files={}
        for n,h in previous['files_SHA256'].items():
            assert sha(OLD/case/n)==h,n
            shutil.copyfile(OUT/(case+'-game.sym') if n=='game.sym' else OLD/case/n,out/n);files[n]=sha(out/n)
            if n!='game.sym':assert files[n]==h
        shutil.copyfile(OUT/(case+'-bindings-proof.json'),out/'edge-profile.json');files['edge-profile.json']=sha(out/'edge-profile.json')
        assert sha(out/'game.sav')==sha(seed)
        ident=dict(previous,files_SHA256=files,observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'),revision='r4 exact scoped all-menu readiness plus bounded passive native edge evidence; unchanged r3 route/builds/Save',overall_process=4 if case=='baseline' else 5,overall_baseline_attempt=4,overall_candidate_attempt=0 if case=='baseline' else 1)
        write(out/'identity.json',ident);cases[case]=sha(out/'identity.json')
    storage=dict(old['storage'],edge_record_words=40,edge_records_max_per_case=18000*64+156*3+1,edge_bytes_max_per_case=16+(18000*64+156*3+1)*160,edge_frame_buffer_rows=64)
    assert os.statvfs(OUT).f_bavail*os.statvfs(OUT).f_frsize>=storage['pair_total_reserved_bytes']
    dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    freeze=dict(source_checkpoint=git('rev-parse','HEAD'),helper_commit=git('rev-parse','HEAD'),base=old['base'],tested=old['tested'],cases=cases,route_SHA256=sha(route),Save_path=str(seed),Save_SHA256=sha(seed),storage=storage,dependencies=dependencies,tool_files=old['tool_files'],scope='All-menu actual running scoped CB2/exact active task/fade-clear guard; bounded passive native-edge evidence; no game build/reconstruction/V01 replay',prior_STOPs_preserved=preserved,offline_proofs_SHA256={n:sha(OUT/n) for n in proofs},dedup_receipt_SHA256=sha(OUT/'immutable-capture-dedup-receipt-private.json'),overall_counts_before=dict(processes=3,baseline_attempts=3,candidates=0),overall_case_counts=dict(baseline=[4,4,0],candidate=[5,4,1]),first_failure_stop=True,candidate_requires_complete_baseline_PASS=True)
    write(OUT/'freeze.json',freeze)
    public={k:v for k,v in freeze.items() if k not in ['dependencies','tool_files','Save_path']};public.update(freeze_SHA256=sha(OUT/'freeze.json'),observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'))
    public['builds']={case:{k:v for k,v in json.loads((OUT/case/'identity.json').read_text()).items() if k in ['source','engine_tree','ROM_SHA256','ELF_SHA256','Save_SHA256','overall_process','overall_baseline_attempt','overall_candidate_attempt']} for case in cases}
    write(OUT/'freeze-summary.json',public);print('r4 freeze PASS: all three archives/manifests exact; both actual builds/bindings, Save, tools, observer and unchanged route verified; no emulator')
if __name__=='__main__':prepare()
