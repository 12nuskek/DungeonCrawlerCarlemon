"""Strict shared classifier, actual source glyphs, numbered AND named pixels."""
from pathlib import Path
import hashlib,importlib.util,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
gate=module('pixelCompleteGate',ROOT/'scripts/floor1/c01a-complete-artifacts.py')
def verify():
    assert not (OUT/'STOP.json').exists()
    certificate=json.loads((OUT/'retained-baseline-acceptance.json').read_text());freeze=json.loads((OUT/'freeze.json').read_text())
    assert certificate['PASS'] and gate.sha(OUT/'retained-baseline-acceptance.json')==freeze['retained_baseline_certificate_SHA256']
    assert json.loads((OUT/'candidate/runtime-result.json').read_text())['PASS'] and json.loads((OUT/'candidate/complete-artifact-verification.json').read_text())['PASS']
    baseline=Path(certificate['retained_root'])/'baseline';candidate=OUT/'candidate';m=module('sourceCorrectedNativeGlyphs',ROOT/'scripts/floor1/c01a-ui-native-pixels-r2.py')
    pa=gate.classifier.classify(baseline,7051,certificate['baseline_declared_derivatives']);pb=gate.classifier.classify(candidate,7051)
    # Named-start is independently compared as a full original native frame.
    assert Image.open(baseline/'battle-start.ppm').convert('RGB').tobytes()==Image.open(candidate/'battle-start.ppm').convert('RGB').tobytes()
    shots={'carl-strike':'ONE FOE','carl-brace':'SELF DEF+','carl-return':'ONE FOE','donut-spark':'BOTH FOES','donut-weaken':'ALL FOES ATK-','donut-return':'BOTH FOES','spark-one':'BOTH FOES','spark-empty':'BOTH FOES','spark-empty-return':'BOTH FOES','weaken-after-empty':'ALL FOES ATK-'}
    glyphs={}
    for n,hint in shots.items():
        glyphs[n]=dict(label=m.check_glyph(candidate/(n+'.ppm'),'USES',(168,120,32,16)),hint=m.check_glyph(candidate/(n+'.ppm'),hint,(168,136,64,16)),baseline_label=m.check_glyph(baseline/(n+'.ppm'),'PP',(168,120,32,16)))
        a=Image.open(baseline/(n+'.ppm')).convert('RGB');b=Image.open(candidate/(n+'.ppm')).convert('RGB');assert a.crop((200,120,232,136)).tobytes()==b.crop((200,120,232,136)).tobytes()
    differs=matched=0;allhash=hashlib.sha256();named={}
    for a,b in list(zip(pa,pb))+[(baseline/n,candidate/n) for n in gate.classifier.NAMED]:
        assert a.name==b.name;aa=Image.open(a).convert('RGB').tobytes();bb=Image.open(b).convert('RGB').tobytes();assert len(aa)==len(bb)==240*160*3
        if aa!=bb:differs+=1
        for y in range(160):
            ranges=[(0,168),(200,240)] if 120<=y<136 else ([(0,168),(232,240)] if 136<=y<152 else [(0,240)])
            for lo,hi in ranges:
                sa=aa[3*(y*240+lo):3*(y*240+hi)];sb=bb[3*(y*240+lo):3*(y*240+hi)];assert sa==sb,(a.name,y,lo,hi,'Unexpected pixels outside authorized panes');matched+=hi-lo;allhash.update(sa)
        if a.name in gate.classifier.NAMED:named[a.name]=dict(outside_authorized_panes_equal=True,baseline_RGB_SHA256=hashlib.sha256(aa).hexdigest(),candidate_RGB_SHA256=hashlib.sha256(bb).hexdigest(),all_pixels_equal=aa==bb)
    return dict(PASS=True,scope='Actual source-bound glyphs/current-max digits/every numbered and named capture outside original two panes; technical frame review, no human pacing/legacy/full-floor claim',numbered_frames=7051,named_captures=len(named),shared_strict_classifier=True,named_start_full_RGB_equal=True,frames_and_named_with_pane_difference=differs,unchanged_pixels_compared=matched,unchanged_RGB_SHA256=allhash.hexdigest(),actual_glyph_cases=glyphs,named_capture_comparisons=named,current_max_digits_identical=True,retained_baseline_certificate_SHA256=gate.sha(OUT/'retained-baseline-acceptance.json'))
if __name__=='__main__':
    try:r=verify();(OUT/'actual-candidate-pixel-proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['actual_glyph_cases','named_capture_comparisons']},indent=2))
    except Exception as e:
        (OUT/'STOP.json').write_text(json.dumps(dict(phase='Candidate pixel review',failure=repr(e),no_retry=True),indent=2)+'\n');raise
