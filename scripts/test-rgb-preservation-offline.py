#!/usr/bin/env python3
"""Synthetic byte/EOF/order/cap negatives; no original recording writes."""
from pathlib import Path
import copy,gzip,hashlib,importlib.util,json,shutil
P=Path(__file__).resolve().parent/'floor1/rgb-preservation.py'
s=importlib.util.spec_from_file_location('rgb_preservation_test',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def main():
    m.OUT.mkdir(mode=0o700,exist_ok=True)
    m.require(not (m.OUT/'preservation-contract.json').exists() and not (m.OUT/'offline-tests.json').exists(),'fresh offline admission only')
    d=m.OUT/'offline-fixtures-r2';d.mkdir();budget=m.Budget(m.OUT);cases=[]
    frames=[bytes([i])*m.FRAME for i in (13,28)];raw=d/'original.rgb';budget.write(raw,b''.join(frames))
    ledger=d/'frames.bin';budget.write(ledger,b''.join(hashlib.sha256(f).digest() for f in frames))
    compressed=d/'good.gz';m.compress_once(raw,compressed,budget)
    row=dict(recording='synthetic',chunk=0,raw_path=str(raw),raw_identity=m.identity(raw),raw_SHA256=m.digest(raw),frames=2,
             compressed_relative_path='good.gz',compressed_SHA256=m.digest(compressed),frame_hashes_relative_path='frames.bin',frame_hashes_SHA256=m.digest(ledger))
    original_hash=m.digest(raw)
    for decoder in (m.zlib_blocks,m.gzip_blocks):
        m.verify_chunk(row,d,decoder);cases.append('positive-'+decoder.__name__)
        good=compressed.read_bytes();corrupt=bytearray(good);corrupt[-8]^=128 # CRC32 trailer, guaranteed integrity failure.
        variants={'corrupt':bytes(corrupt),'truncated':good[:-5],'trailing':good+b'bad-tail','reordered':gzip.compress(frames[1]+frames[0],compresslevel=6,mtime=0),
                  'missing-frame':gzip.compress(frames[0],compresslevel=6,mtime=0),'extra-frame':gzip.compress(b''.join(frames)+frames[0],compresslevel=6,mtime=0)}
        for name,data in variants.items():
            p=d/(decoder.__name__+'-'+name+'.gz');budget.write(p,data);bad=dict(row,compressed_relative_path=p.name,compressed_SHA256=m.digest(p))
            try:m.verify_chunk(bad,d,decoder)
            except (RuntimeError,m.zlib.error):cases.append(decoder.__name__+'-'+name)
            else:raise AssertionError('corrupt stream accepted: '+name)
        try:m.verify_chunk(dict(row,compressed_relative_path='missing.gz'),d,decoder)
        except FileNotFoundError:cases.append(decoder.__name__+'-missing-file')
        else:raise AssertionError('missing chunk accepted')
    partial=d/'cap-partial.gz'
    try:m.compress_once(raw,partial,m.Budget(d,cap=m.usage(d)['allocated_bytes']+4096,reserve=0))
    except RuntimeError as e:m.require('cap exceeded' in str(e),'cap failure reason');cases.append('compression-cap-first-failure')
    else:raise AssertionError('cap overflow accepted')
    index=d/'index.bin';budget.write(index,m.struct.pack('<4I',1,0,0,0)+m.struct.pack('<4I',1,0,0,0))
    try:m.index_check(index,2)
    except RuntimeError:cases.append('reordered-native-index')
    else:raise AssertionError('bad frame order accepted')
    rows=[]
    for label,base,count,chunks,_ in m.RECORDINGS:
        for i in range(chunks):
            start=2000*i+1;nf=min(2000,count-start+1);rows.append(dict(recording=label,chunk=i,first_frame=start,frames=nf,raw_path=str(base/'opening'/f'motion-{i:03}.rgb'),raw_identity={'bytes':nf*m.FRAME},compressed_relative_path=f'{label}/motion-{i:03}.rgb.gz'))
    m.validate_layout(rows);cases.append('31-chunk-layout-positive')
    for name,bad in (('missing-chunk',rows[:-1]),('reordered-chunks',[rows[1],rows[0],*rows[2:]]),('incorrect-dimensions',[dict(rows[0],raw_identity={'bytes':rows[0]['raw_identity']['bytes']-1}),*rows[1:]])):
        try:m.validate_layout(bad)
        except RuntimeError:cases.append(name)
        else:raise AssertionError('bad layout accepted')
    ledger_rows=[dict(r,raw_SHA256='raw-'+str(i),compressed_SHA256='compressed-'+str(i),exact_frame_bytes=True,exact_EOF=True) for i,r in enumerate(rows)]
    good=dict(PASS=True,verification='pass1-zlib',chunk_count=31,frames=59965,decoded_bytes=6907968000,contract_SHA256='contract',mapping_SHA256='mapping',chunks=ledger_rows)
    m.receipt_check(good,'pass1-zlib','contract','mapping',ledger_rows);cases.append('complete-removal-receipt-positive')
    bads=[dict(good,PASS=False),dict(good,frames=59964),dict(good,chunk_count=30),dict(good,decoded_bytes=6907967999),dict(good,contract_SHA256='other'),dict(good,mapping_SHA256='other'),dict(good,verification='pass2-independent-gzip')]
    for field in ('exact_frame_bytes','exact_EOF','frames','raw_SHA256','compressed_SHA256'):
        bad=copy.deepcopy(good);bad['chunks'][0][field]=False if field.startswith('exact') else 'invalid';bads.append(bad)
    bads.append(dict(good,chunks=list(reversed(ledger_rows))))
    for i,bad in enumerate(bads):
        try:m.receipt_check(bad,'pass1-zlib','contract','mapping',ledger_rows)
        except RuntimeError:cases.append('removal-gate-negative-'+str(i))
        else:raise AssertionError('incomplete removal receipt accepted')
    m.require(m.digest(raw)==original_hash,'synthetic original changed');budget.check()
    budget.json(m.OUT/'offline-tests.json',dict(PASS=True,cases=cases,case_count=len(cases),synthetic_original_retained=True,standard_codec='GNU gzip fixed -6 -n',gameplay_processes=0,runtime_claims=0))
    print('PASS offline preservation verifier: '+str(len(cases))+' positive/negative cases; originals untouched')
if __name__=='__main__':main()
