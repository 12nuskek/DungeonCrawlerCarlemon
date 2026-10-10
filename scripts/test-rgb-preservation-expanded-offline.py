#!/usr/bin/env python3
"""New scope/layout/receipt tests; never repeat the completed codec admission."""
from pathlib import Path
import copy,importlib.util,json
p=Path(__file__).resolve().parent/'floor1/rgb-preservation-expanded.py'
s=importlib.util.spec_from_file_location('expanded_scope_test',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.m
def main():
    m.require(not a.git('status','--porcelain'),'clean committed scope source')
    out=Path('/workspace/scratch/floor1-rgb-expanded-offline-admission-r1-20261010.json')
    m.require(not out.exists(),'exclusive new scope admission')
    prior=a.prior_admission();cases=[]
    rows=[dict(r,raw_identity=dict(bytes=r['frames']*m.FRAME),raw_SHA256='raw-'+str(i),compressed_SHA256='gzip-'+str(i)) for i,r in enumerate(a.definitions())]
    a.validate_layout(rows);cases.append('complete43-file82482-frame-layout')
    bads=[rows[:-1],list(reversed(rows)),[rows[1],rows[0],*rows[2:]]]
    for key,value in (('raw_path','/tmp/unapproved.rgb'),('compressed_relative_path','../outside.gz'),('first_frame',0),('last_frame',0),('frames',0),('recording','unapproved')):
        bad=copy.deepcopy(rows);bad[0][key]=value;bads.append(bad)
    bad=copy.deepcopy(rows);bad[0]['raw_identity']['bytes']-=1;bads.append(bad)
    for i,bad in enumerate(bads):
        try:a.validate_layout(bad)
        except RuntimeError:cases.append('scope-negative-'+str(i))
        else:raise AssertionError('scope expansion accepted')
    chunks=[dict(r,exact_frame_bytes=True,exact_EOF=True) for r in rows]
    good=dict(PASS=True,verification='pass1-zlib',chunk_count=a.CHUNKS,frames=a.FRAMES,decoded_bytes=a.BYTES,originals_retained=True,contract_SHA256='contract',mapping_SHA256='mapping',chunks=chunks)
    a.receipt_check(good,'pass1-zlib','contract','mapping',rows);cases.append('complete-new-scope-removal-receipt')
    bads=[dict(good,**{k:v}) for k,v in (('PASS',False),('verification','pass2-independent-gzip'),('chunk_count',42),('frames',82481),('decoded_bytes',a.BYTES-1),('originals_retained',False),('contract_SHA256','other'),('mapping_SHA256','other'))]
    for key,value in (('exact_frame_bytes',False),('exact_EOF',False),('raw_SHA256','other'),('compressed_SHA256','other'),('frames',0)):
        bad=copy.deepcopy(good);bad['chunks'][0][key]=value;bads.append(bad)
    bads.extend((dict(good,chunks=chunks[:-1]),dict(good,chunks=list(reversed(chunks)))))
    for i,bad in enumerate(bads):
        try:a.receipt_check(bad,'pass1-zlib','contract','mapping',rows)
        except RuntimeError:cases.append('receipt-negative-'+str(i))
        else:raise AssertionError('incomplete receipt accepted')
    pins={rel:m.digest(a.ROOT/rel) for rel in (*a.OLD_FILES,*a.NEW_FILES)}
    m.require(m.CAP==3758096384 and m.EXTERNAL_RESERVE==134217728 and m.RESERVATION==10000408128,'unchanged all-inclusive capacity definitions')
    m.require(a.BYTES-m.CAP>m.RESERVATION-m.shutil.disk_usage(a.SCRATCH).free,'whole cap and original retention fit worst-case future capacity')
    m.require(not a.git('status','--porcelain'),'source unchanged during adapter checks')
    out.write_text(json.dumps(dict(PASS=True,source_commit=a.git('rev-parse','HEAD'),prior_admission=prior,cases=cases,case_count=len(cases),source_files_SHA256=pins,codec_tests_repeated=False,recordings_compressed=0,gameplay_processes=0,runtime_claims=0),indent=2)+'\n')
    print('PASS expanded scope '+str(len(cases))+' cases; prior36 codec/EOF/cap tests and STOP90/104 preservation reused unchanged')
if __name__=='__main__':main()
