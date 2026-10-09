"""Offline retained-reference/storage contract. Never prepare or execute a game."""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, os, shutil, struct, subprocess, tempfile

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def rejected(operation):
    try:operation()
    except (AssertionError,ValueError,FileNotFoundError):return
    raise AssertionError('Invalid binding/format/storage must fail closed')
def main():
    parser=argparse.ArgumentParser()
    for name in ['output','reference','seed','trace','partial','fixture','stress-log']:parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(mode=0o700,parents=True,exist_ok=False)
    binding=module('storage_binding',ROOT/'scripts/floor1/v01-retained-reference.py')
    fmt=module('storage_format',ROOT/'scripts/floor1/v01-timeline-storage-format.py')
    report=binding.verify(args.reference,args.seed)
    assert binding.sha(args.trace)=='aac0963fde9fbd6237f44dd8082ddca59f6b40627a8b6857a017c82673b8669a'
    code,_=module('storage_host',ROOT/'scripts/floor1/v01-battle-host.py').generate(git);binding.legacy_host(code,git)
    # Match the production runner's translation-unit basename: ELF FILE symbols
    # include it even without debug information, so host.c is a different binary.
    (out/'observer.c').write_text(code)
    with (out/'compile.log').open('w') as log:
        subprocess.run(['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'host')],stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run(['cc','-DUSE_DEBUGGERS','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-I'+str(ROOT/'scripts/floor1'),str(ROOT/'scripts/floor1/v01-timeline-storage-fixture.c'),'-lmgba','-o',str(out/'fixture')],stdout=log,stderr=subprocess.STDOUT,check=True)
    assert binding.sha(out/'fixture')==binding.sha(args.fixture), 'Reuse only an identical tested fixture binary'
    stress=json.loads(args.stress_log.read_text().splitlines()[-1]);assert stress['cases']==2968 and stress['CPU_instructions']==0
    private=out/'private-replay';private.mkdir(mode=0o700)
    replay=subprocess.run([str(out/'fixture'),'--replay',str(args.trace.resolve()),str(args.partial.resolve())],cwd=private,capture_output=True,text=True,check=True)
    replay_report=json.loads(replay.stdout);assert replay_report['observations']==999932 and replay_report['accepted_boundaries']==13721
    summaries=private/'summary-0.bin';detail=private/'detail-0.bin'
    assert summaries.stat().st_mode&0o777==detail.stat().st_mode&0o777==0o600
    observations=frames=0;last_anchor=None;counts={}
    with args.partial.open('rb') as partial:
        while h:=partial.read(29):
            if h[0]==ord('B'):
                epoch=struct.unpack_from('<I',h,13)[0];counts[epoch]=counts.get(epoch,0)+1
                assert len(partial.read(2560))==2560
            else:assert h[0]==ord('F')
    with args.trace.open('rb') as original,summaries.open('rb') as packed:
        assert original.read(8)==b'BVTIME01';original.read(8);decoded=fmt.summaries(packed)
        digest=hashlib.sha256();chunk=0
        while raw:=original.read(184):
            assert len(raw)==184;words=struct.unpack('<46I',raw);digest.update(raw);chunk+=1;observations+=1
            if words[0]==1 and words[41]&(1<<7) and words[4]==0x080004bf and words[3]==0x080008ae and words[6]==1 and words[7]==0x1f and words[39]>2044:
                assert counts[words[39]];counts[words[39]]-=1;last_anchor=original.tell()-184
            if words[0]==6:
                info,data=next(decoded);assert info[5]==chunk and data[120:152]==digest.digest()
                digest=hashlib.sha256();chunk=0;frames+=1
        info,data=next(decoded);assert info[3]==119 and info[4]&2 and info[5]==chunk==2
        assert data[120:152]==digest.digest() and next(decoded,None) is None
    assert observations==999932 and frames==16000 and last_anchor is not None and not any(counts.values())
    with args.trace.open('rb') as original,detail.open('rb') as retained:
        original.seek(last_anchor);decoded=fmt.detail(retained);retained_count=0
        for words,raw in decoded:assert raw==original.read(184);retained_count+=1
        assert not original.read(1) and retained_count==18
    # Format corruption and truncation; no bytes after a first stop accepted.
    cases=0;summary_bytes=summaries.read_bytes();first=summary_bytes[:32+184]
    for size in range(32):rejected(lambda:list(fmt.summaries(io.BytesIO(first[:size]))));cases+=1
    for size in range(1,184):rejected(lambda:list(fmt.summaries(io.BytesIO(first[:32]+first[32:32+size]))));cases+=1
    for offset in [0,8,12,16,20,32,36,52,64,112,120,152,180]:
        wrong=bytearray(first);wrong[offset]^=1;rejected(lambda:list(fmt.summaries(io.BytesIO(wrong))));cases+=1
    rejected(lambda:list(fmt.summaries(io.BytesIO(summary_bytes+summary_bytes[-184:]))));cases+=1
    detailed=detail.read_bytes()
    for size in range(1,184):rejected(lambda:list(fmt.detail(io.BytesIO(detailed[:32]+detailed[32:32+size]))));cases+=1
    # Verify every provenance gate before any output/Save/claim is created.
    for name in ['identity.json','execution-claim.json','summary.json','input.route','ordinary.sav','native-boundary-trace.bin']:
        with tempfile.TemporaryDirectory(dir=out) as directory:
            directory=Path(directory)
            for old in args.reference.iterdir():
                if old.is_file() and not old.name.endswith(('.ppm','.png')):(directory/old.name).symlink_to(old.resolve())
            path=directory/name;path.unlink();path.write_bytes(b'invalid original provenance\n')
            rejected(lambda:binding.verify(directory,args.seed));cases+=1
    with tempfile.TemporaryDirectory(dir=out) as directory:
        rejected(lambda:binding.verify(directory,args.seed));cases+=1
    rejected(lambda:binding.verify(args.partial.parent,args.seed));cases+=1
    working=binding.working_bound(code,(out/'host').stat().st_size,args.reference)
    budget=binding.storage_bound(code,working['upper_bytes']);required=budget['required_available_bytes']
    assert binding.preflight(budget,out,available=required)['passed'];cases+=1
    rejected(lambda:binding.preflight(budget,out,available=required-1));cases+=1
    assert binding.preflight(budget,out,available=required-4096,credited=4096)['passed'];cases+=1
    rejected(lambda:binding.preflight(budget,out,available=required,credited=required));cases+=1
    # Candidate-only CLI rejects a baseline restart before even creating output.
    runner=module('storage_runner',ROOT/'scripts/test-f1-v01-battle.py');old_argv=__import__('sys').argv
    runner.git=lambda *a:'' if a==('status','--porcelain') else ('268fa9a8e0673824ff47e191e7be5777e8b6489e' if a==('rev-parse','HEAD') else '76001ee128785714b7c15aef6d9c95630587d0a9')
    target=out/'forbidden-baseline'
    __import__('sys').argv=['runner','--case','before','--prepare','--build',str(ROOT/'artifacts/floor1/v01-overworld/build-registered'),'--output',str(target),'--seed',str(args.seed),'--retained-reference',str(args.reference)]
    try:rejected(runner.main)
    finally:__import__('sys').argv=old_argv
    assert not target.exists();cases+=1
    storage_check=binding.preflight(budget,out)
    pins=json.loads((ROOT/'docs/evidence/floor1/v01/battle/storage-binding/build-identity.json').read_text())
    assert binding.sha(out/'observer.c')==pins['host_source_SHA256'] and binding.sha(out/'host')==pins['host_binary_SHA256']
    assert working['upper_bytes']==pins['working_files_upper_bytes']
    result=dict(result='PASS offline bounded-detail/full-run-summary/original-reference/storage-preflight contract',
                writer_cases=2968,format_binding_preflight_cases=cases,replayed_observations=observations,
                summaries=16001,all_frame_payload_SHA256_matches=True,summary_chain_continuity=True,
                retained_detail_records=retained_count,retained_payload_bytes_equal_original=True,
                retained_start_is_last_accepted_boundary=True,original_trace_SHA256=binding.sha(args.trace),
                summary_SHA256=binding.sha(summaries),detail_SHA256=binding.sha(detail),
                host_source_SHA256=binding.sha(out/'observer.c'),host_binary_SHA256=binding.sha(out/'host'),
                fixture_binary_SHA256=binding.sha(out/'fixture'),original_reference=report,
                working_bound=working,storage_bound=budget,storage_preflight=storage_check,
                production_buffer_bytes=753664,production_storage_context_bytes=88,
                CPU_instructions=0,gameplay_host_invocations=0,candidate_preparations=0,ROMs_loaded=0,Saves_loaded=0,
                execution_counts={'baselines':6,'candidates':3},Library_transfer_attempts=0,
                no_lossless_full_history_claim=True,
                development_note='Synthetic metadata-failure fixture initially omitted required timing.relativeCycles pointer; diagnosed and fixed its zeroed board before rerun. Final identity test also diagnosed ELF FILE-symbol basename mismatch: offline compilation now uses production observer.c. No production/gameplay failure or source waiver.')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['original_reference','working_bound']}))
if __name__=='__main__':main()
