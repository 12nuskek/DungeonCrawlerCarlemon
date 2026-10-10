"""One reviewed r3 route; unchanged observer/native runner and first STOP."""
from pathlib import Path
import argparse,importlib.util,json,os
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-action-hints-r3-20261010')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=['baseline','candidate']);case=p.parse_args().case
    freeze=json.loads((OUT/'freeze.json').read_text());assert freeze['first_failure_stop']
    allocated=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=freeze['storage']['pair_total_reserved_bytes']-allocated,'Frozen remaining pair storage unavailable; no claim'
    m=module('c01r3prior',ROOT/'scripts/test-f1-c01a-ui.py');m.OUT=OUT;m.run(case)
