"""New corrected offline acceptance certificate; original r4 STOP stays failed."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010')
OLD=Path('/workspace/scratch/c01a-action-hints-r4-20261010')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
gate=module('completeGate',ROOT/'scripts/floor1/c01a-complete-artifacts.py');sha=gate.sha
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def certify():
    assert not (OUT/'retained-baseline-acceptance.json').exists()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()
    freeze=json.loads((OLD/'freeze.json').read_text());manifest=json.loads((OLD/'private-retention-manifest.json').read_text());archive=OLD/'private-evidence.tar.gz'
    assert sha(archive)=='ff751f540a7e38023c0afd39261e602bf3625ef0e6d08da090e4c44889676269'
    seen=set()
    with tarfile.open(archive,'r|gz') as tar:
        for member in tar:
            n=member.name
            if n not in manifest:continue
            assert n not in seen and member.isfile();seen.add(n);r=manifest[n]
            h=hashlib.sha256();f=tar.extractfile(member);size=0
            while b:=f.read(1048576):h.update(b);size+=len(b)
            assert size==r['size'] and h.hexdigest()==r['SHA256'],n
            p=ROOT/n.removeprefix('frozen-source/') if n.startswith('frozen-source/') else OLD/n
            assert p.stat().st_size==r['size'] and sha(p)==r['SHA256'],n
    assert seen==set(manifest)
    for n,h in freeze['dependencies'].items():assert sha(ROOT/n)==h,n
    for n,h in freeze['tool_files'].items():assert sha(n)==h,n
    originals={n:sha(OLD/n) for n in ['STOP.json','freeze.json','baseline/exclusive-claim.json','baseline/runtime-result.json','baseline/native-edge-validation.json']}
    assert originals['STOP.json']=='230b71676ee002fa5fe9ec68ae85d9ddc19fffe292ae60f9657ac8bab6288312'
    assert not json.loads((OLD/'baseline/runtime-result.json').read_text())['PASS'] and not json.loads((OLD/'baseline/native-edge-validation.json').read_text())['complete']
    assert not (OLD/'candidate/exclusive-claim.json').exists()
    bindings=module('r4ActualBindings',ROOT/'scripts/floor1/c01a-ui-bindings-r4.py');builds={}
    for case in ['baseline','candidate']:
        ident=json.loads((OLD/case/'identity.json').read_text());assert sha(OLD/case/'identity.json')==freeze['cases'][case]
        for n,h in ident['files_SHA256'].items():assert sha(OLD/case/n)==h,n
        assert sha(ident['ROM'])==ident['ROM_SHA256'] and sha(Path(ident['ROM']).with_suffix('.elf'))==ident['ELF_SHA256']
        text,proof=bindings.profile(case);assert text==(OLD/case/'game.sym').read_text() and proof==json.loads((OLD/(case+'-bindings-proof.json')).read_text())
        assert subprocess.check_output(['git','rev-parse',ident['source']+':engine'],cwd=ROOT,text=True).strip()==ident['engine_tree']
        builds[case]={k:ident[k] for k in ['source','engine_tree','ROM_SHA256','ELF_SHA256','observer_source_SHA256','observer_binary_SHA256','Save_SHA256']}
    assert sha(OLD/'observer.c')=='564c8b04c4ab6e8ef1efb9a5d846ff1934525f9b64e647b0c0db69b23ecf8732' and sha(OLD/'observer')=='39a6ad526bee8c3550ddfe2566bbdcc9c24b1307aedeeaa8c124593c07e79429'
    assert sha(ROOT/'scripts/contracts/f1-c01a-ui-r3.route')==freeze['route_SHA256']=='f03cae6c47e866b49209f1a78f6fd2ca34e1653084422b5bab7c3c1e7175b3fa'
    for save in [Path(freeze['Save_path']),OLD/'baseline/game.sav',OLD/'candidate/game.sav']:assert sha(save)==freeze['Save_SHA256']
    derivative={'battle-start.png':manifest['baseline/battle-start.png']['SHA256']}
    record=gate.verify(OLD/'baseline',json.loads((OLD/'baseline/identity.json').read_text()),Path(freeze['Save_path']),derivative)
    assert record['reference_stream_SHA256']=={'native-boundary-trace.bin':'aedeac12d3161cd94a137b9a1805bff903616dc055efb5924447e9c9a18f9df9','ui-frame-trace.bin':'b0c21ea31aa7960431be6157c6b4c38f7ef670f777be2aee54c2c8b73fc57a8b'}
    classifier=module('negativeClassifier',ROOT/'scripts/test-f1-c01a-capture-classifier.py');classifier.run()
    for n,h in originals.items():assert sha(OLD/n)==h,n
    record.update(certificate='Separately named corrected offline retained-baseline4 acceptance',verifier_commit=head,verifier_SHA256={n:sha(ROOT/n) for n in ['scripts/floor1/c01a-capture-classifier.py','scripts/floor1/c01a-complete-artifacts.py','scripts/floor1/c01a-retained-baseline-certify.py']},retained_root=str(OLD),original_r4_contract_PASS=False,original_r4_artifacts_SHA256=originals,original_archive_SHA256=sha(archive),original_archive_manifest_SHA256=sha(OLD/'private-retention-manifest.json'),original_manifest_entries_verified=len(manifest),original_source_build_tool_fixtures_all_verified=True,builds=builds,baseline_declared_derivatives=derivative,baseline_execution='b222d75708e3eb3e48bd42e2318befce82e762f0',counts_before=dict(baseline_processes=4,candidate_processes=0),no_emulator=True,no_baseline_replay=True,no_game_build=True,candidate_authority='Parent review of ccc196473be4615d52d455c7a48afe2f5a208bec permits process5/attempt1 after this corrected certificate and separate freeze')
    write(OUT/'retained-baseline-acceptance.json',record)
    public={k:v for k,v in record.items() if k not in ['numbered_capture_SHA256','retained_root']};public['numbered_capture_manifest_SHA256']=hashlib.sha256(json.dumps(record['numbered_capture_SHA256'],sort_keys=True).encode()).hexdigest();public['certificate_SHA256']=sha(OUT/'retained-baseline-acceptance.json')
    write(OUT/'retained-baseline-acceptance-summary.json',public)
    print('Corrected offline retained-baseline certificate PASS; original r4 STOP/PASS=false/complete=false unchanged; no emulator or baseline replay')
if __name__=='__main__':certify()
