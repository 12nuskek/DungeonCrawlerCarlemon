"""Exactly process5/attempt1 using separately certified retained baseline4."""
from pathlib import Path
import importlib.util,json,os
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
gate=module('candidateCompleteGate',ROOT/'scripts/floor1/c01a-complete-artifacts.py')
def patched_runner():
    m=module('originalNativeMenuRunner',ROOT/'scripts/test-f1-c01a-ui.py');source=(ROOT/'scripts/test-f1-c01a-ui.py').read_text()
    def replace(a,b):
        nonlocal source
        assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
    replace("assert case in ('baseline','candidate') and not (OUT/'STOP.json').exists()","assert case=='candidate' and not (OUT/'STOP.json').exists()")
    begin=source.index("    if case=='candidate':\n");end=source.index('    claim=dict(',begin)
    original=source[begin:end];assert "receipt['PASS']" in original and 'shutil.copyfile' in original
    source=source[:begin]+'''    certificate=json.loads((OUT/'retained-baseline-acceptance.json').read_text())
    assert certificate['PASS'] and sha(OUT/'retained-baseline-acceptance.json')==freeze['retained_baseline_certificate_SHA256']
    base=Path(certificate['retained_root'])/'baseline'
    for name,target in [('native-boundary-trace.bin','expected-native-boundary-trace.bin'),('ui-frame-trace.bin','expected-ui-frame-trace.bin')]:
        assert sha(base/name)==certificate['reference_stream_SHA256'][name]==sha(out/target)
    for name,h in certificate['original_r4_artifacts_SHA256'].items():assert sha(Path(certificate['retained_root'])/name)==h
    for name,h in dict(certificate['named_capture_SHA256'],**certificate['numbered_capture_SHA256']).items():assert sha(base/name)==h
'''+source[end:]
    replace("        captures=list(out.glob('battle-*.ppm'));assert len(captures)==frames","        captures=classifier.classify(out,frames)")
    exec(compile(source,str(ROOT/'scripts/test-f1-c01a-ui.py'),'exec'),m.__dict__);m.OUT=OUT;m.classifier=gate.classifier
    return m,source
def run():
    assert not (OUT/'STOP.json').exists() and not (OUT/'candidate/exclusive-claim.json').exists()
    freeze=json.loads((OUT/'freeze.json').read_text());assert freeze['candidate_only'] and freeze['overall_counts_before']==dict(baseline_processes=4,candidate_processes=0)
    allocated=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())+sum(p.stat().st_size for p in Path(freeze['retained_pair_root']).rglob('*') if p.is_file())
    st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=freeze['storage']['pair_total_reserved_bytes']-allocated
    m,source=patched_runner();assert m.sha(OUT/'candidate-only-runner-generated.py')==__import__('hashlib').sha256(source.encode()).hexdigest()
    m.run('candidate')
    try:
        certificate=json.loads((OUT/'retained-baseline-acceptance.json').read_text());ident=json.loads((OUT/'candidate/identity.json').read_text())
        complete=gate.verify(OUT/'candidate',ident,Path(freeze['Save_path']),candidate=True)
        assert complete['UI_READY']==certificate['UI_READY'] and complete['UI_MOVE']==certificate['UI_MOVE']
        assert complete['reference_stream_SHA256']=={'expected-'+n:h for n,h in certificate['reference_stream_SHA256'].items()}
        (OUT/'candidate/complete-artifact-verification.json').write_text(json.dumps(complete,indent=2)+'\n')
        summary={k:v for k,v in complete.items() if k!='numbered_capture_SHA256'};summary['retained_baseline_certificate_SHA256']=m.sha(OUT/'retained-baseline-acceptance.json');summary['runtime_full_native_and_supplemental_comparison']=True
        (OUT/'candidate/complete-artifact-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        print('Candidate process5/attempt1 complete strict streams/captures/coverage/native-edge validation PASS; pixel review remains separate')
    except Exception as e:
        stop=dict(case='candidate',phase='Complete candidate post-processing',failure=repr(e),no_retry=True)
        (OUT/'STOP.json').write_text(json.dumps(stop,indent=2)+'\n');raise
if __name__=='__main__':run()
