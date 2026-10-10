"""One r4 baseline; candidate only after complete strict baseline PASS."""
from pathlib import Path
import argparse,importlib.util,json,os,struct,hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-action-hints-r4-20261010')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def validate_edges(case,require_complete):
    out=OUT/case;p=out/'native-input-edge-private.bin';data=p.read_bytes()
    assert data[:8]==b'C01EDGE4' and struct.unpack_from('<II',data,8)==(40,18000*64+156*3+1)
    assert (len(data)-16)%160==0
    rows=[struct.unpack_from('<40I',data,i) for i in range(16,len(data),160)]
    assert rows and len(rows)<=18000*64+156*3+1
    profile=json.loads((out/'edge-profile.json').read_text());points=profile['points']
    counts={};frameends=0;consumed=[]
    for w in rows:
        tag=w[0];counts[str(tag)]=counts.get(str(tag),0)+1
        assert tag in [1,2,3,4,5,6,7,8,9,11] and w[1]<=156 and w[4]<=1023 and w[5]<=1023
        if w[39]<12:
            assert w[35]==points[w[39]]['address'] and w[36]
        if tag==8:frameends+=1
        if tag==4:assert w[30] in (0,1) and w[23] and w[24]==w[30] and w[25]==w[2]
        if w[31]:assert tag==6 and w[30]==0xfffffffe and w[9]&2;consumed.append(dict(command=w[1],visual=w[3],epoch=w[2]))
    assert rows[-1][0]==11
    if require_complete:
        result=json.loads((out/'runtime-result.json').read_text());assert result['PASS'] and rows[-1][30]==0 and rows[-1][1]==156 and frameends==result['visual_frames']
    receipt=dict(PASS=True,complete=require_complete,rows=len(rows),bytes=len(data),SHA256=hashlib.sha256(data).hexdigest(),tags=counts,frame_end_rows=frameends,ListMenu_native_B_consumed_events=consumed,scope='Passive native instruction/command/input/frame records; raw hardware and actual gMain fields, scoped callbacks/tasks, fade, source queue operands and actual native link/ListMenu returns')
    (out/'native-edge-validation.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=['baseline','candidate']);case=p.parse_args().case
    freeze=json.loads((OUT/'freeze.json').read_text());assert freeze['first_failure_stop']
    allocated=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=freeze['storage']['pair_total_reserved_bytes']-allocated
    if case=='candidate':validate_edges('baseline',True)
    m=module('c01r4prior',ROOT/'scripts/test-f1-c01a-ui.py');m.OUT=OUT
    try:m.run(case)
    except Exception:
        if (OUT/case/'native-input-edge-private.bin').exists():validate_edges(case,False)
        raise
    try:print(json.dumps(validate_edges(case,True),indent=2))
    except Exception as e:
        stop=dict(case=case,reason='Native edge evidence validation failed',failure=repr(e),no_retry=True)
        (OUT/'STOP.json').write_text(json.dumps(stop,indent=2)+'\n');raise
