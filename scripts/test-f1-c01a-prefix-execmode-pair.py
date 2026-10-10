"""One baseline prefix, then one conditional candidate; never a full PASS."""
from pathlib import Path
import argparse,json,subprocess,hashlib,os,resource,time,struct,importlib.util
ROOT=Path(__file__).resolve().parents[1];OUT=Path('/workspace/scratch/c01a-diagnostic-prefix-execmode-r2-20261010');OLD=Path('/workspace/scratch/c01a-action-hints-r4-20261010');CERTROOT=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010')
FAILED=Path('/workspace/scratch/c01a-diagnostic-prefix-pair-20261010')
spec=importlib.util.spec_from_file_location('execfile',ROOT/'scripts/floor1/c01a-prefix-execfile.py');execfile=importlib.util.module_from_spec(spec);spec.loader.exec_module(execfile)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def eligible(r):return r.get('diagnostic_prefix_only') is True and r.get('prefix_matches_original_reference') is True and r.get('diagnostic_terminal_complete') is True and r.get('exit')==0 and r.get('full_acceptance') is False and r.get('Save_unchanged') is True
def limits():resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024**3,2*1024**3))
def run(case):
    assert case in ['baseline','candidate'] and not (OUT/'STOP.json').exists()
    f=json.loads((OUT/'freeze.json').read_text());out=OUT/case;i=json.loads((out/'identity.json').read_text());assert sha(out/'identity.json')==f['cases'][case]
    assert f['diagnostic_claim_only'] and f['prefix_commands']==27 and f['counts_before']=={'baselines':4,'candidates':1,'processes':5}
    for p,h in f['dependencies'].items():assert sha(ROOT/p)==h,p
    for p,h in f['tool_files'].items():assert sha(p)==h,p
    for p,h in f['preserved_inputs'].items():assert sha(p)==h,p
    for n,h in i['files_SHA256'].items():assert sha(out/n)==h,n
    assert sha(i['ROM'])==i['ROM_SHA256'] and sha(Path(i['ROM']).with_suffix('.elf'))==i['ELF_SHA256']
    assert sha(OUT/'observer')==i['observer_binary_SHA256'] and sha(OUT/'observer.c')==i['observer_source_SHA256']
    assert sha(out/'game.sav')==sha(f['Save_path'])==f['Save_SHA256']
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();subprocess.run(['git','merge-base','--is-ancestor',f['helper_commit'],head],cwd=ROOT,check=True)
    if case=='candidate':
        r=json.loads((OUT/'baseline/runtime-result.json').read_text());assert eligible(r) and r['overall_process']==7
        assert sha(OUT/'baseline/controller-dma-diagnostic-private.bin')==r['diagnostic_SHA256']
    used=sum(p.stat().st_size for root in [OLD,CERTROOT,FAILED,OUT] for p in root.rglob('*') if p.is_file());st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=max(0,f['storage']['pair_total_reserved_bytes']-used)
    assert f['claimed_counts_before']=={'baseline':5,'candidate':1,'total':6} and f['actual_counts_before']=={'baseline':4,'candidate':1,'total':5}
    assert i['overall_process']==(7 if case=='baseline' else 8) and i['actual_emulator_process_if_launched']==(6 if case=='baseline' else 7)
    claim={'case':case,'claim_number':i['overall_process'],'overall_process':i['overall_process'],'baseline_attempt':6,'candidate_attempt':i['candidate_attempt'],'execution_commit':head,'freeze_SHA256':sha(OUT/'freeze.json'),'limit':1,'diagnostic_prefix_only':True,'first_failure_stop':True,'no_retry':True,'start_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
    # Read-only executable admission immediately before create-only claim.
    executable_check=execfile.verify_executable(OUT/'observer',f['observer_executable']);claim['observer_executable_check']=executable_check
    with (out/'exclusive-claim.json').open('x') as fp:json.dump(claim,fp,indent=2);fp.write('\n')
    env=dict(os.environ,LD_LIBRARY_PATH='/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root/usr/lib/x86_64-linux-gnu')
    try:
        with (out/'input.route').open('rb') as route,(out/'runtime.log').open('xb') as log:
            p=subprocess.Popen([str(OUT/'observer'),i['ROM'],str(out/'game.sav'),str(out/'game.sym')],cwd=out,env=env,stdin=route,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=limits)
            write(out/'started-process.json',{'pid':p.pid,'overall_process':i['overall_process'],'actual_emulator_process':i['actual_emulator_process_if_launched'],'actual_baseline_run':5,'execution_commit':head})
            size=0
            while b:=p.stdout.read(65536):
                size+=len(b)
                if size>f['storage']['logs_max_per_case']:p.kill();p.wait();raise RuntimeError('Frozen log cap exceeded')
                log.write(b)
            exitcode=p.wait()
        text=(out/'runtime.log').read_text();data=(out/'controller-dma-diagnostic-private.bin').read_bytes();assert data[:8]==b'C01DIAG1' and len(data)<=f['storage']['diagnostic_per_case'] and (len(data)-16)%256==0
        rows=[struct.unpack_from('<64I',data,x) for x in range(16,len(data),256)];terminal=bool(rows and rows[-1][0]==11 and rows[-1][1]==exitcode)
        unchanged=sha(out/'game.sav')==sha(f['Save_path'])==f['Save_SHA256'];assert unchanged
        for n,h in f['reference_stream_SHA256'].items():assert sha(out/('expected-'+n))==h
        close=[l for l in text.splitlines() if l.startswith('DIAGNOSTIC_CLOSE ')];assert len(close)==1
        closefields=dict(x.split('=',1) for x in close[0].split()[1:]);retained=closefields['retention']=='0' and closefields['terminal']=='1' and terminal
        endpoint='DIAGNOSTIC_PREFIX_END command=27 ' in text
        r=dict(case=case,claim_number=i['overall_process'],actual_emulator_process=i['actual_emulator_process_if_launched'],actual_baseline_run=5,overall_process=i['overall_process'],baseline_attempt=6,candidate_attempt=i['candidate_attempt'],execution_commit=head,exit=exitcode,diagnostic_prefix_only=True,
          prefix_matches_original_reference=exitcode==0 and endpoint,diagnostic_terminal_complete=retained,diagnostic_rows=len(rows),diagnostic_SHA256=sha(out/'controller-dma-diagnostic-private.bin'),
          Save_unchanged=unchanged,full_acceptance=False,PASS=False,no_retry=True,log_SHA256=sha(out/'runtime.log'),close=closefields,
          captures=len(list(out.glob('battle-[0-9][0-9][0-9][0-9][0-9].ppm'))),native_reference_full_EOF_not_run=True,supplemental_full_EOF_not_run=True,
          outcome='matched partial baseline diagnostic prefix' if case=='baseline' and exitcode==0 else 'candidate did not reproduce within approved prefix' if exitcode==0 else 'first strict mismatch or other failure; no later instructions')
        write(out/'runtime-result.json',r)
        if exitcode or not retained or not endpoint:write(OUT/'STOP.json',r)
        print(json.dumps(r,indent=2))
        if case=='baseline' and not eligible(r):raise RuntimeError('Baseline diagnostic prefix gate failed; candidate forbidden')
    except Exception as e:
        if not (OUT/'STOP.json').exists():write(OUT/'STOP.json',{'case':case,'failure':repr(e),'no_retry':True,'full_acceptance':False,'overall_process':i['overall_process']})
        raise
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('case',choices=['baseline','candidate']);run(a.parse_args().case)
