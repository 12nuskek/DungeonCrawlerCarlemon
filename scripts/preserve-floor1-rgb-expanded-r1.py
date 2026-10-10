#!/usr/bin/env python3
"""One local preservation operation; no retries, game calls or uploads."""
from pathlib import Path
import argparse,importlib.util,json,os,shutil,subprocess,sys,time
p=Path(__file__).resolve().parent/'floor1/rgb-preservation-expanded.py'
s=importlib.util.spec_from_file_location('expanded_preservation',p);a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.m
def freeze():
    m.require(not a.OUT.exists(),'separately named exclusive output required')
    m.require(not a.git('status','--porcelain'),'commit admitted preservation source')
    prior=a.prior_admission();free=shutil.disk_usage(a.SCRATCH).free
    m.require(free>=m.CAP,'fresh full temporary/replacement capacity unavailable')
    admission=json.loads(Path('/workspace/scratch/floor1-rgb-expanded-offline-admission-r1-20261010.json').read_text())
    m.require(admission['PASS'] and admission['source_commit']==a.git('rev-parse','HEAD'),'new scope adapter admission')
    a.OUT.mkdir(mode=0o700);budget=m.Budget(a.OUT);rows=[];recordings=[]
    definitions=a.definitions()
    for plan in a.PLANS:
        label,base,stage,count,n,manifest=plan;directory=a.SCRATCH/base/stage
        wants=[r for r in definitions if r['recording']==label]
        m.require(sorted(str(p) for p in directory.glob('motion*.rgb'))==sorted(r['raw_path'] for r in wants),'actual original raw inventory differs')
        (a.OUT/label).mkdir(mode=0o700);whole=m.hashlib.sha256()
        for want in wants:
            raw=Path(want['raw_path']);ident=m.identity(raw);m.require(raw.stat().st_nlink==1,'target must have one link')
            m.require(ident['bytes']==want['frames']*m.FRAME,'original complete frame byte count')
            h=m.hashlib.sha256();ledger=bytearray()
            with raw.open('rb') as f:
                for _ in range(want['frames']):
                    frame=m.read_exact(f,m.FRAME);m.require(len(frame)==m.FRAME,'truncated original frame')
                    h.update(frame);whole.update(frame);ledger.extend(m.hashlib.sha256(frame).digest())
                m.require(not f.read(1),'original exact EOF')
            m.require(h.hexdigest()==a.expected_hash(plan,raw) and m.identity(raw)==ident,'original retained chunk hash/identity mismatch')
            budget.write(a.OUT/want['frame_hashes_relative_path'],ledger)
            rows.append(dict(want,raw_identity=ident,raw_SHA256=h.hexdigest(),frame_hashes_SHA256=m.hashlib.sha256(ledger).hexdigest()))
            print(f'INVENTORY {label} chunk={want["chunk"]} frames={want["frames"]} original={h.hexdigest()}',flush=True)
        index=directory/'frame-index.bin' if not base.startswith('ordinary-') else None
        if index:m.index_check(index,count)
        source=a.SCRATCH/base/manifest
        recordings.append(dict(recording=label,frames=count,chunks=n,original_stream_SHA256=whole.hexdigest(),index_path=str(index) if index else None,index_SHA256=m.digest(index) if index else None,historical_manifest_path=str(source),historical_manifest_SHA256=m.digest(source),
            timing=dict(native_frame_numerator=16777216,native_frame_denominator=280896,sample_interval_native_frames=4 if base.startswith('ordinary-') else 1,storage_frame_numbers='one-based sample ordinal; original indices/implicit order unchanged')))
        if label=='opening4-STOP101':
            original=a.SCRATCH/base/'opening-native-frame-sha256.bin'
            m.require(original.read_bytes()==b''.join((a.OUT/r['frame_hashes_relative_path']).read_bytes() for r in rows if r['recording']==label),'retained opening4 per-frame hash ledger')
    a.validate_layout(rows);protected={}
    for file in a.protected_paths([r['raw_path'] for r in rows]):protected[str(file)]=dict(identity=m.identity(file),SHA256=m.digest(file))
    # No unexplained gameplay RGB remains: all other *.rgb paths are explicitly
    # protected offline fixtures or the original decoded review derivative.
    exclusions=[p for p in protected if p.endswith('.rgb')]
    for p in exclusions:
        m.require('offline' in p or 'source-admission' in p or 'medicine-sampling' in p or 'medicine-transaction' in p or 'howler-continuation' in p or 'rgb-preservation-r1' in p or p.endswith('/review-export/decoded-roundtrip.rgb'),'unclassified remaining raw recording')
    budget.write(a.OUT/'heads-before.tsv',subprocess.check_output(['git','ls-remote','--heads','origin'],cwd=a.ROOT))
    old=json.loads((a.PRIOR/'preservation-contract.json').read_text())
    zlib_extension=Path(m.zlib.__file__).resolve()
    linked=subprocess.check_output(['ldd',str(zlib_extension),str(m.GZIP),str(Path(sys.executable).resolve())],text=True)
    dependencies={zlib_extension,Path(sys.executable).resolve(),m.GZIP.resolve()}
    for line in linked.splitlines():
        for word in line.split():
            if word.startswith('/') and Path(word).is_file():dependencies.add(Path(word).resolve())
    c=dict(name='Floor1 expanded local RGB preservation r1',source_commit=a.git('rev-parse','HEAD'),main_base='65bc4073d140b9d58bf1b83bd33235e28c972b23',output_root=str(a.OUT),authorization_UTC='2026-10-10T21:42:24Z',authorization='Kurt authenticated Yes to remaining/future local gameplay recordings after TWO complete byte verification passes; local only.',prior_admission=prior,
        width=240,height=160,pixel_format='RGB24',bytes_per_frame=m.FRAME,frames=a.FRAMES,original_bytes=a.BYTES,chunk_count=a.CHUNKS,chunks=rows,recordings=recordings,protected_entries=protected,excluded_raw_paths=exclusions,
        format=old['format'],compress_command=old['compress_command'],decoder_pass1=old['decoder_pass1'],decoder_pass2=old['decoder_pass2'],gzip_version=old['gzip_version'],gzip_executable_SHA256=old['gzip_executable_SHA256'],python_version=sys.version,python_executable_SHA256=old['python_executable_SHA256'],zlib_version=old['zlib_version'],
        source_files_SHA256={p:m.digest(a.ROOT/p) for p in (*a.OLD_FILES,*a.NEW_FILES)},scope_adapter_admission_SHA256=m.digest(Path('/workspace/scratch/floor1-rgb-expanded-offline-admission-r1-20261010.json')),
        tool_dependencies_SHA256={str(p):m.digest(p) for p in sorted(dependencies)},
        all_inclusive_cap_bytes=m.CAP,external_code_docs_Git_audit_reserve_bytes=m.EXTERNAL_RESERVE,initial_available_bytes=free,fresh_available_bytes_after_inventory=shutil.disk_usage(a.OUT).free,minimum_net_savings_bytes=max(0,m.RESERVATION-free),future_runtime_reservation_bytes=m.RESERVATION,
        protected_scope='Every non-target regular file in the six recording parent roots and previous preservation root; every other existing scratch RGB file.',first_failure_terminal=True,no_alternative_settings_or_retry=True,all_originals_retained_until_both_complete_passes=True,preservation_only=True,runtime_freeze=False,gameplay_processes=0,runtime_claims=0,opening_claims_processes=[5,5],cold_claims_processes=[2,2],Howler_processes=0,independent_backup_verified=False)
    m.require(sum(r['raw_identity']['bytes'] for r in rows)==a.BYTES,'exact original byte total')
    m.require(shutil.disk_usage(a.OUT).free>=m.CAP,'fresh full cap after inventory')
    budget.json(a.OUT/'preservation-contract.json',c);print('FROZEN preservation-only contract '+m.digest(a.OUT/'preservation-contract.json'),flush=True)
def execute():
    c=json.loads((a.OUT/'preservation-contract.json').read_text());a.ensure_source(c);a.validate_layout(c['chunks']);a.protected_check(c)
    budget=m.Budget(a.OUT);m.require(shutil.disk_usage(a.OUT).free>=m.CAP,'fresh full cap before operation')
    budget.json(a.OUT/'operation-start.json',dict(contract_SHA256=m.digest(a.OUT/'preservation-contract.json'),pid=os.getpid(),UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),preservation_only=True,gameplay_processes=0,runtime_claims=0))
    mapping=dict(contract_SHA256=m.digest(a.OUT/'preservation-contract.json'),chunks=[],recordings=c['recordings'],local_only=True,independent_backup_verified=False)
    for original in c['chunks']:
        row=dict(original);a.check_identity(row);dest=a.OUT/row['compressed_relative_path'];m.compress_once(Path(row['raw_path']),dest,budget);a.check_identity(row)
        row.update(compressed_identity=m.identity(dest),compressed_SHA256=m.digest(dest));mapping['chunks'].append(row)
        print(f'COMPRESSED {row["recording"]} chunk={row["chunk"]} bytes={dest.stat().st_size}',flush=True)
    budget.json(a.OUT/'representation-mapping-private.json',mapping)
    one=a.verify(c,mapping,m.zlib_blocks,'pass1-zlib');budget.json(a.OUT/'verification-pass1-private.json',one)
    log=a.OUT/'independent-verification.log';budget.check(65536)
    with log.open('xb') as f:subprocess.run([sys.executable,str(Path(__file__).resolve()),'verify'],cwd=a.ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
    m.require(log.stat().st_size<=65536,'independent log bound');budget.check()
    two=json.loads((a.OUT/'verification-pass2-private.json').read_text());m.require(one['pid']!=two['pid'],'independent verifier process required')
    accounting=m.removal_barrier(c,mapping,one,two,base=a.OUT)
    budget.json(a.OUT/'replacement-admission-private.json',dict(PASS=True,**accounting,contract_SHA256=m.digest(a.OUT/'preservation-contract.json'),mapping_SHA256=m.digest(a.OUT/'representation-mapping-private.json'),pass1_SHA256=m.digest(a.OUT/'verification-pass1-private.json'),pass2_SHA256=m.digest(a.OUT/'verification-pass2-private.json'),all43_originals_still_retained=True))
    removed=[]
    for row in mapping['chunks']:
        a.check_identity(row);Path(row['raw_path']).unlink();removed.append(row['raw_path'])
    a.protected_check(c)
    for row in mapping['chunks']:m.require(m.identity(a.OUT/row['compressed_relative_path'])==row['compressed_identity'] and m.digest(a.OUT/row['compressed_relative_path'])==row['compressed_SHA256'],'replacement final readback')
    budget.json(a.OUT/'preservation-result-private.json',dict(PASS=True,replaced_file_count=len(removed),replaced_paths=removed,frames=a.FRAMES,original_bytes=a.BYTES,compressed_bytes=sum(r['compressed_identity']['bytes'] for r in mapping['chunks']),accounting=accounting,available_bytes_after_replacement=shutil.disk_usage(a.OUT).free,runtime_reservation_bytes=m.RESERVATION,full_runtime_storage_capacity_available=shutil.disk_usage(a.OUT).free>=m.RESERVATION,protected_entries_unchanged=len(c['protected_entries']),opening_claims_processes=[5,5],cold_claims_processes=[2,2],Howler_processes=0,gameplay_processes=0,runtime_claims=0,runtime='CLOSED',independent_backup_verified=False))
    budget.check();print('PASS43 originals replaced after TWO independent complete decoded byte/frame/chunk/EOF passes; runtime CLOSED',flush=True)
def verify():
    m.require((a.OUT/'operation-start.json').exists() and (a.OUT/'verification-pass1-private.json').exists(),'independent verifier requires first complete pass')
    m.require(not (a.OUT/'verification-pass2-private.json').exists(),'no verifier repetition')
    c=json.loads((a.OUT/'preservation-contract.json').read_text());mapping=json.loads((a.OUT/'representation-mapping-private.json').read_text())
    result=a.verify(c,mapping,m.gzip_blocks,'pass2-independent-gzip');m.Budget(a.OUT).json(a.OUT/'verification-pass2-private.json',result)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('freeze','execute','verify'));args=parser.parse_args()
    try:
        m.require(not (a.OUT/'preservation-STOP.json').exists(),'first preservation failure remains terminal')
        {'freeze':freeze,'execute':execute,'verify':verify}[args.action]()
    except Exception as error:
        stop=dict(PASS=False,action=args.action,error=type(error).__name__+': '+str(error),first_failure_terminal=True,retry_permitted=False,partial_outputs_retained=True)
        p=a.OUT/'preservation-STOP.json'
        if a.OUT.exists() and not p.exists():p.write_text(json.dumps(stop,indent=2)+'\n')
        print(json.dumps(stop),flush=True);raise
if __name__=='__main__':main()
