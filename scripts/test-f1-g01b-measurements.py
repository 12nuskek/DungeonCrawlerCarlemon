#!/usr/bin/env python3
"""Audit real accepted logs; demonstrate missing pairs and duplicates are rejected."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,re,subprocess
root=Path(__file__).resolve().parents[1]
def git(*a):return subprocess.check_output(['git',*a],cwd=root,text=True).strip()
assert not git('status','--porcelain'),'Commit first'
head=git('rev-parse','HEAD');run=Path(os.environ['DCC_G01B_ACCEPTED_RUN']).resolve();tested=(run/'tested-commit.txt').read_text().strip()
subprocess.run(['git','diff','--quiet',tested,head,'--','engine','scripts/playtest.c','scripts/floor1/coordinated-graybox.py','scripts/contracts/f1-g01b-coordinated.json','scripts/floor1/walking-harness.py'],cwd=root,check=True)
l=importlib.util.spec_from_file_location('gate',root/'scripts/floor1/travel-measurements.py');gate=importlib.util.module_from_spec(l);l.loader.exec_module(gate)
spec=json.loads((root/'scripts/contracts/f1-g01b-coordinated.json').read_text());ceiling=json.loads((root/'scripts/contracts/f1-g01b-recovery.json').read_text());summary=json.loads((run/'validation-summary.json').read_text());assert len(summary)==13
tests=[]
def rejection(route,rows,reason):
    try:gate.validate(route,rows,spec,ceiling)
    except AssertionError as error:tests.append({'route':route,'case':reason,'result':'rejected','message':str(error)})
    else:raise AssertionError(('Invalid evidence accepted',route,reason))
for row in summary:
    route=row['route'].split('/')[1];path=run/row['route'];log=(path/'replay.log').read_text()
    assert log.endswith(f'result=0 assertions={row["assertions"]}\n') and not (path/'errors.log').stat().st_size
    metrics=[{'name':a,'frames':int(b),'walking_frames':int(c),'steps':int(e),'warps':int(f)} for a,b,c,e,f in re.findall(r'MEASURE name=(\S+) frames=(\d+) walking=(\d+) tiles=(\d+) warps=(\d+)',log)]
    assert metrics==row['measurements'];gate.validate(route,metrics,spec,ceiling);tests.append({'route':row['route'],'case':'actual accepted runtime measurements','result':'passed','log_sha256':hashlib.sha256(log.encode()).hexdigest()})
    if route in gate.TRAVEL_NAMES:
        # Regression for the review finding: remove BOTH entries, not just one.
        prefixes=['guard','howler'] if route!='preboss' else ['preboss']
        for prefix in prefixes:rejection(route,[v for v in metrics if not v['name'].startswith(prefix+'-')],'both '+prefix+' measurements missing')
        rejection(route,[], 'all measurements missing')
        rejection(route,metrics+[copy.deepcopy(metrics[0])],'duplicate expected measurement')
        bad=copy.deepcopy(metrics);bad[0]['name']='unexpected';rejection(route,bad,'unexpected name replacing required one')
        bad=copy.deepcopy(metrics);bad[0]['walking_frames']=10000;bad[0]['frames']=20000;rejection(route,bad,'active walking ceiling exceeded')
    else:
        rejection(route,[{'name':'unexpected','frames':20,'walking_frames':16,'steps':1,'warps':0}],'unexpected measurement on nontravel route')
result={'validator_source':head,'runtime_runner_source':tested,'runtime_sessions':len(summary),'runtime_assertions':sum(v['assertions'] for v in summary),'positive_cases':sum(v['result']=='passed' for v in tests),'negative_cases':sum(v['result']=='rejected' for v in tests),'tests':tests,'scope':'Revalidates exact real emulator logs; no gameplay, compile or emulator rerun claimed.'}
(run/'measurement-gate.json').write_text(json.dumps(result,indent=2)+'\n')
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
print('PASS',result['positive_cases'],'real log cases;',result['negative_cases'],'negative cases; source',head)
