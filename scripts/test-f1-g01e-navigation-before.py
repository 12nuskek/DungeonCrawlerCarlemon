#!/usr/bin/env python3
"""Actual pre-change native windows, replaying the same bounded ordinary routes."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json,re,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--candidate-run',type=Path,required=True);p.add_argument('--originals',type=Path,required=True);p.add_argument('--rom',type=Path,required=True);p.add_argument('--symbols',type=Path,required=True);a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rom=a.rom.resolve();assert sha(rom)=='baf67ceb9b39e151673af2fed480651d1d2ce799a050e2a8df5ee2f06c276b82'
candidate=a.candidate_run.resolve();out=Path(tempfile.mkdtemp(prefix='before-',dir=ROOT/'artifacts/floor1/navigation'));print('Evidence:',out,flush=True);summary=[]
for name,original in [('guide-repeat-posttrial','guide-after-trial'),('ordinary-optional-quest','both-pending'),('ordinary-completed-context','continuous')]:
    d=out/name;d.mkdir();source=a.originals/(original+'.sav');old=sha(source);save=out/(name+'.sav');shutil.copyfile(source,save)
    text=(candidate/name/'input.route').read_text().replace('DCC_Live_','DCC_');assert 'snapshot' not in text
    (d/'input.route').write_text(text)
    with (d/'input.route').open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
        subprocess.run([str(candidate/'playtest'),str(rom),str(save),str(a.symbols.resolve())],cwd=d,stdin=inp,stdout=log,stderr=err,check=True)
    text=(d/'replay.log').read_text();assert sha(source)==old and not (d/'errors.log').stat().st_size
    checks=int(re.search(r'result=0 assertions=(\d+)\n$',text)[1]);summary.append(dict(route=name,assertions=checks,emulator_errors=0,original_unchanged=True))
    for image in d.glob('*.ppm'):
        frame=Image.open(image);assert frame.size==(240,160);frame.save(image.with_suffix('.png'))
    print('PASS',name,checks,flush=True)
(out/'summary.json').write_text(json.dumps(dict(engine_source='a52de748f89e82c39f97361b2295d72c88b69856',rom_sha256=sha(rom),observer_from_candidate_run=str(candidate),sessions=summary,method='Actual unchanged pre-navigation ROM, same ordinary controller routes, legacy compiled text labels. Scoped comparison, not whole-floor acceptance.'),indent=2)+'\n')
print('PASS',len(summary),'before sessions',sum(x['assertions'] for x in summary),'assertions')
