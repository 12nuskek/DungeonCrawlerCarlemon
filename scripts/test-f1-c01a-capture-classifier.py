"""Reviewed eight capture negatives plus malformed extra/namespace rejections."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010')
BASE=Path('/workspace/scratch/c01a-action-hints-r4-20261010/baseline')
def run():
    s=importlib.util.spec_from_file_location('classifier',ROOT/'scripts/floor1/c01a-capture-classifier.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    names={p.name for p in BASE.iterdir()};derivatives={'battle-start.png'};assert len(m.classify_names(names,7051,derivatives))==7051
    cases=[('missing-first',names-{'battle-00000.ppm'},7051),('missing-middle',names-{'battle-03000.ppm'},7051),('missing-last',names-{'battle-07050.ppm'},7051),('extra-numbered',names|{'battle-07051.ppm'},7051),('declared-count-low',names,7050),('declared-count-high',names,7052),('missing-required-named-start',names-{'battle-start.ppm'},7051),('malformed-numbered-replacement',(names-{'battle-03000.ppm'})|{'battle-03000x.ppm'},7051),('malformed-extra',names|{'battle-03000x.ppm'},7051),('out-of-range-extra',names|{'battle-99999.ppm'},7051),('unexpected-battle-name',names|{'battle-surprise.ppm'},7051),('unexpected-battle-extension',names|{'battle-03000.ppm.tmp'},7051),('missing-other-named',names-{'summary.ppm'},7051)]
    rejected=[]
    for label,n,f in cases:
        try:m.classify_names(n,f,derivatives)
        except AssertionError:rejected.append(label)
        else:raise AssertionError(label)
    record=dict(PASS=True,actual_numbered_count=7051,original_eight_negative_cases_preserved=True,negative_cases_rejected=rejected,named_captures_required=m.NAMED,retained_named_PNG_derivative_separate_from_native_capture_inventory=True,scope='Offline filename classification only; no emulator/baseline receipt rewrite')
    (OUT/'capture-classifier-proof.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if __name__=='__main__':run()
