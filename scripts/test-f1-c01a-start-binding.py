"""Post-STOP source-only cardinality diagnosis and unapplied correction guards."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[1]
def validate(header,host,available):
    count=int(re.search(r'unsigned a\[(\d+)\]',header)[1]);mandatory=int(re.search(r'for\(unsigned z=0;z<(\d+);z\+\+\)if\(!ui.a\[z\]\)',host)[1])
    fields=re.search(r"fields=\[(.*?)\]",host,re.S)[1];names=re.findall(r"'([^']+)'",fields)
    assert count==mandatory==len(names)==16
    assert all(available.get(n,0) for n in names)
def run():
    header=(ROOT/'scripts/floor1/c01a-ui-observer.h').read_text();host=(ROOT/'scripts/floor1/c01a-ui-host.py').read_text();names=re.findall(r"'([^']+)'",re.search(r"fields=\[(.*?)\]",host,re.S)[1]);available={n:i+1 for i,n in enumerate(names)}
    try:validate(header,host,available)
    except AssertionError:pass
    else:raise AssertionError('Frozen 17/16 startup defect not detected')
    proposed_header=header.replace('unsigned a[17]','unsigned a[16]');proposed_host=host.replace('for(unsigned z=0;z<17;z++)if(!ui.a[z])','for(unsigned z=0;z<16;z++)if(!ui.a[z])')
    validate(proposed_header,proposed_host,available)
    for invalid in [{n:v for n,v in available.items() if n!='uiSummary'},dict(available,uiSummary=0)]:
        try:validate(proposed_header,proposed_host,invalid)
        except AssertionError:pass
        else:raise AssertionError('Missing/zero actual receiving callback accepted')
    return dict(PASS=True,scope='Offline source-only proposal guards; frozen failed adapter remains unapplied and no emulator invoked',cases=4,frozen_defect_detected=True,proposal_cardinality=16,missing_and_zero_required_callbacks_rejected=True)
if __name__=='__main__':print(json.dumps(run(),indent=2))
