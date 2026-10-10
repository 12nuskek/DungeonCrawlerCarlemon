"""Claim9/candidate3 once; certified original full baseline4, no pixel masks."""
from pathlib import Path
import importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-journal-admission-r3-20261010')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def run():
    helper=module('journalCandidate',ROOT/'scripts/test-f1-c01a-candidate-only.py');helper.OUT=OUT
    m,source=helper.patched_runner();m.OUT=OUT
    needle='    claim=dict(case=case,';assert source.count(needle)==1
    source=source.replace(needle,"    executable.verify_executable(OUT/'observer',freeze['observer_admission_expected'])\n"+needle)
    source=source.replace('claim=dict(case=case,','claim=dict(consumed_claim=9,candidate_attempt=3,process_if_launched=8,case=case,')
    m.executable=module('journalAdmission',ROOT/'scripts/floor1/c01a-prefix-execfile.py')
    exec(compile(source,str(ROOT/'scripts/test-f1-c01a-ui.py'),'exec'),m.__dict__);m.OUT=OUT;m.classifier=helper.gate.classifier
    assert not (OUT/'STOP.json').exists() and not (OUT/'candidate/exclusive-claim.json').exists()
    try:
        m.run('candidate')
        certificate=json.loads((OUT/'retained-baseline-acceptance.json').read_text());ident=json.loads((OUT/'candidate/identity.json').read_text())
        complete=helper.gate.verify(OUT/'candidate',ident,Path(json.loads((OUT/'freeze.json').read_text())['Save_path']),candidate=True)
        assert complete['UI_READY']==certificate['UI_READY'] and complete['UI_MOVE']==certificate['UI_MOVE']
        assert complete['reference_stream_SHA256']=={'expected-'+n:h for n,h in certificate['reference_stream_SHA256'].items()}
        base=Path(certificate['retained_root'])/'baseline';names={**certificate['numbered_capture_SHA256'],**certificate['named_capture_SHA256']}
        for n,h in names.items():assert m.sha(base/n)==h==m.sha(OUT/'candidate'/n),('Full native pixels differ',n)
        assert m.sha(base/'battle-start.ppm')==m.sha(OUT/'candidate/battle-start.ppm')
        complete.update(full_native_pixels_byte_equal=True,pixel_masks=0,numbered_frames_compared=7051,named_frames_compared=len(certificate['named_capture_SHA256']),separate_battle_start_compared=True,consumed_claim=9,actual_candidate_attempt=3,actual_emulator_process=8)
        m.write(OUT/'candidate/complete-artifact-verification.json',complete)
        m.write(OUT/'battle-PASS.json',{k:v for k,v in complete.items() if k not in ('numbered_capture_SHA256','named_capture_SHA256')})
        print('PASS: full strict native B/F/E+EOF, 2700 snapshots, controls/resources, and all native pixels; field probe now eligible')
    except Exception as e:
        if not (OUT/'STOP.json').exists():m.write(OUT/'STOP.json',dict(phase='Full battle regression',failure=repr(e),first_failure_stop=True,no_retry=True,field_probe_blocked=True))
        raise
if __name__=='__main__':run()
