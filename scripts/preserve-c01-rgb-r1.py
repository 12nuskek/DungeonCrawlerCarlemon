#!/usr/bin/env python3
"""One frozen local preservation operation; first failure stops, no alternative."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,shutil,subprocess,sys,time
P=Path(__file__).resolve().parent/'floor1/rgb-preservation.py'
s=importlib.util.spec_from_file_location('rgb_preservation',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
SOURCES=('scripts/floor1/rgb-preservation.py','scripts/preserve-c01-rgb-r1.py','scripts/verify-c01-rgb-r1.py','scripts/test-rgb-preservation-offline.py','docs/floor1/c01-rgb-preservation-r1-contract.md')
def git(*args):return subprocess.check_output(['git',*args],cwd=m.ROOT,text=True).strip()
def freeze():
    m.require(not (m.OUT/'preservation-STOP.json').exists(),'prior preservation failure is terminal')
    m.require(not git('status','--porcelain'),'commit tested preservation source before freezing')
    m.require(not (m.OUT/'preservation-contract.json').exists() and not (m.OUT/'operation-start.json').exists(),'no repeat freeze/operation')
    tests=json.loads((m.OUT/'offline-tests.json').read_text());m.require(tests['PASS'],'offline verifier admission')
    budget=m.Budget(m.OUT);budget.check();free=shutil.disk_usage(m.OUT).free
    m.require(free>=m.CAP,'complete replacement/audit cap unavailable')
    rows=[];recordings=[];protected={}
    for label,base,count,chunks,manifest_name in m.RECORDINGS:
        directory=base/'opening';actual=sorted(directory.glob('motion-*.rgb'))
        m.require([p.name for p in actual]==[f'motion-{i:03}.rgb' for i in range(chunks)],'original raw chunk inventory mismatch')
        old_manifest=base/manifest_name;old=json.loads(old_manifest.read_text())['entries']
        index=directory/'frame-index.bin';m.index_check(index,count)
        m.require(str(index) in old and m.digest(index)==old[str(index)]['SHA256'],'retained frame index identity')
        target=m.OUT/label;target.mkdir(mode=0o700)
        first=1
        for i,raw in enumerate(actual):
            ident=m.identity(raw);frames=min(2000,count-first+1)
            m.require(str(raw) in old and ident['bytes']==frames*m.FRAME==old[str(raw)]['bytes'],'original chunk sizes/dimensions')
            h=hashlib.sha256();ledger=bytearray()
            with raw.open('rb') as f:
                for _ in range(frames):
                    frame=m.read_exact(f,m.FRAME);m.require(len(frame)==m.FRAME,'truncated original frame');h.update(frame);ledger.extend(hashlib.sha256(frame).digest())
                m.require(not f.read(1),'original extra bytes/EOF')
            m.require(h.hexdigest()==old[str(raw)]['SHA256'] and m.identity(raw)==ident,'original hash/identity differs from historical retention')
            hashes=f'{label}/motion-{i:03}.frame-sha256.bin';budget.write(m.OUT/hashes,ledger)
            rows.append(dict(recording=label,chunk=i,first_frame=first,last_frame=first+frames-1,frames=frames,raw_path=str(raw),raw_identity=ident,raw_SHA256=h.hexdigest(),
                             compressed_relative_path=f'{label}/motion-{i:03}.rgb.gz',frame_hashes_relative_path=hashes,frame_hashes_SHA256=hashlib.sha256(ledger).hexdigest()))
            first+=frames;print(f'RECONCILED {label} chunk={i} frames={frames} raw_SHA256={h.hexdigest()}',flush=True)
        recordings.append(dict(recording=label,frames=count,chunks=chunks,index_path=str(index),index_SHA256=m.digest(index),historical_manifest_path=str(old_manifest),historical_manifest_SHA256=m.digest(old_manifest)))
        raw_names={str(p) for p in actual}
        for p in sorted(base.rglob('*')):
            if p.is_file() and str(p) not in raw_names:
                protected[str(p)]={'identity':m.identity(p),'SHA256':m.digest(p)}
    m.validate_layout(rows)
    m.require(sum(r['raw_identity']['bytes'] for r in rows)==6907968000,'expected 6,907,968,000 original bytes')
    heads=subprocess.check_output(['git','ls-remote','--heads','origin'],cwd=m.ROOT);budget.write(m.OUT/'heads-before.tsv',heads)
    contract=dict(name='C01 RGB local lossless preservation r1',source_commit=git('rev-parse','HEAD'),audit_start_commit='704e5950760551f53be5453515b39914187def42',main_base=git('rev-parse','origin/main'),
        output_root=str(m.OUT),authorization_UTC='2026-10-10 13:28:29',authorization_scope='Only STOP90 opening2 and STOP104 opening3 raw RGB files, after both complete verification passes.',
        width=240,height=160,pixel_format='RGB24',bytes_per_frame=m.FRAME,timing={'numerator':16777216,'denominator':280896,'index_format':'little-endian four u32: absolute frame, kind, battle flag, attempts; no rewrite'},
        original_chunk_frames=2000,frames=59965,original_bytes=6907968000,chunks=rows,recordings=recordings,protected_entries=protected,
        format='single-member RFC1952 gzip containing exact original RGB bytes',compress_command=['/usr/bin/gzip','-6','-n','-c','--','ORIGINAL'],decoder_pass1='Python zlib.decompressobj(31), bounded 65536-byte output blocks',decoder_pass2='separate Python process with GNU gzip -dc, bounded 65536-byte reads',
        gzip_version=subprocess.check_output([str(m.GZIP),'--version'],text=True).splitlines()[0],gzip_executable_SHA256=m.digest(m.GZIP),python_version=sys.version,python_executable_SHA256=m.digest(Path(sys.executable)),zlib_version=m.zlib.ZLIB_RUNTIME_VERSION,
        source_files_SHA256={p:m.digest(m.ROOT/p) for p in SOURCES},offline_tests_SHA256=m.digest(m.OUT/'offline-tests.json'),all_inclusive_cap_bytes=m.CAP,external_code_docs_Git_audit_reserve_bytes=m.EXTERNAL_RESERVE,
        initial_available_bytes=free,minimum_net_savings_bytes=max(0,m.RESERVATION-free),future_runtime_reservation_bytes=m.RESERVATION,first_failure_terminal=True,no_alternative_settings_or_retry=True,
        runtime_freeze=False,gameplay_processes=0,runtime_claims=0,opening_claims_processes=[3,3],cold_claims_processes=[0,0],medicine_preparation_gate='closed',independent_backup_verified=False)
    budget.json(m.OUT/'preservation-contract.json',contract);print('FROZEN preservation-only contract SHA256='+m.digest(m.OUT/'preservation-contract.json'),flush=True)
def execute():
    m.require(not (m.OUT/'preservation-STOP.json').exists(),'prior preservation failure is terminal')
    budget=m.Budget(m.OUT);contract=json.loads((m.OUT/'preservation-contract.json').read_text());m.code_check(contract);m.validate_layout(contract['chunks']);m.protected_check(contract)
    m.require(git('rev-parse','HEAD')==contract['source_commit'] and not git('status','--porcelain'),'frozen committed source only')
    m.require(shutil.disk_usage(m.OUT).free>=m.CAP,'complete replacement/audit capacity recheck')
    budget.json(m.OUT/'operation-start.json',dict(contract_SHA256=m.digest(m.OUT/'preservation-contract.json'),pid=os.getpid(),UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),preservation_only=True,gameplay_processes=0,runtime_claims=0))
    mapping={'contract_SHA256':m.digest(m.OUT/'preservation-contract.json'),'chunks':[],'timing':contract['timing'],'local_only':True,'independent_backup_verified':False}
    for original in contract['chunks']:
        row=dict(original);m.check_identity(row);dest=m.OUT/row['compressed_relative_path']
        m.compress_once(Path(row['raw_path']),dest,budget);m.check_identity(row)
        row['compressed_identity']=m.identity(dest);row['compressed_SHA256']=m.digest(dest);mapping['chunks'].append(row)
        print(f'COMPRESSED {row["recording"]} chunk={row["chunk"]} bytes={dest.stat().st_size} SHA256={row["compressed_SHA256"]}',flush=True)
    budget.json(m.OUT/'representation-mapping-private.json',mapping)
    one=m.verify_all(contract,mapping,m.zlib_blocks,'pass1-zlib');budget.json(m.OUT/'verification-pass1-private.json',one)
    log=m.OUT/'independent-verification.log';budget.check(65536)
    with log.open('xb') as f:subprocess.run([sys.executable,str(m.ROOT/'scripts/verify-c01-rgb-r1.py')],cwd=m.ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    m.require(log.stat().st_size<=65536,'independent verification log bound');budget.check()
    two=json.loads((m.OUT/'verification-pass2-private.json').read_text());accounting=m.removal_barrier(contract,mapping,one,two)
    budget.json(m.OUT/'removal-admission-private.json',dict(PASS=True,**accounting,contract_SHA256=m.digest(m.OUT/'preservation-contract.json'),mapping_SHA256=m.digest(m.OUT/'representation-mapping-private.json'),pass1_SHA256=m.digest(m.OUT/'verification-pass1-private.json'),pass2_SHA256=m.digest(m.OUT/'verification-pass2-private.json'),all_31_originals_still_retained=True))
    # This is the only deletion in the operation: exact frozen, twice-decoded raw paths.
    removed=[]
    for row in mapping['chunks']:
        m.check_identity(row);Path(row['raw_path']).unlink();removed.append(row['raw_path'])
    m.protected_check(contract)
    for row in mapping['chunks']:m.require(m.digest(m.OUT/row['compressed_relative_path'])==row['compressed_SHA256'],'replacement readback after removal')
    budget.json(m.OUT/'preservation-result-private.json',dict(PASS=True,replaced_file_count=len(removed),replaced_paths=removed,frames=59965,original_bytes=6907968000,compressed_bytes=sum(r['compressed_identity']['bytes'] for r in mapping['chunks']),
        accounting=accounting,available_bytes_after_replacement=shutil.disk_usage(m.OUT).free,runtime_reservation_bytes=m.RESERVATION,full_runtime_storage_capacity_available=shutil.disk_usage(m.OUT).free>=m.RESERVATION,
        runtime_sampling_admitted=False,medicine_preparation_gate='closed',gameplay_processes=0,runtime_claims=0,opening_claims_processes=[3,3],cold_claims_processes=[0,0],independent_backup_verified=False,all_protected_evidence_unchanged=True))
    budget.check();print('PASS local preservation: 31 exact raw files replaced after both full verification passes; no runtime',flush=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('freeze','execute'));args=parser.parse_args()
    try:freeze() if args.action=='freeze' else execute()
    except Exception as error:
        stop={'PASS':False,'action':args.action,'error':type(error).__name__+': '+str(error),'first_failure_terminal':True,'retry_permitted':False,'partial_outputs_retained':True}
        p=m.OUT/'preservation-STOP.json'
        if m.OUT.exists() and not p.exists():
            # A 4096-byte emergency receipt is inside the reserved audit budget.
            payload=(json.dumps(stop,indent=2)+'\n').encode();m.require(len(payload)<4096,'STOP receipt bound');p.write_bytes(payload)
        print(json.dumps(stop),flush=True);raise
if __name__=='__main__':main()
