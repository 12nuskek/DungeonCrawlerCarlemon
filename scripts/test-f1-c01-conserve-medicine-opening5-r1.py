#!/usr/bin/env python3
"""One named, hash-bound opening5 after explicit review; conditional cold only."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,shutil,stat,subprocess,traceback
if not __debug__:
    raise RuntimeError('opening5 requires enabled checks; no preparation or process')
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01-conserve-medicine-opening5-r1-20261010')
CONTRACT=ROOT/'docs/floor1/c01-conserve-medicine-opening5-r1-contract.md'
AGGREGATE=Path('/workspace/scratch/c01-conserve-medicine-offline-r1-20261010/aggregate')
PROOF=Path('/workspace/scratch/c01-medicine-transaction-offline-r3-20261010/reviewed-offsets-proof')
WIRING=Path('/workspace/scratch/c01-opening5-conserve-wiring-offline-r1-20261010/receipt.json')
REGISTRY=ROOT/'docs/evidence/floor1/c01/conserve-medicine-opening5-r1-20261010/reviewed-artifacts.json'
registry=json.loads(REGISTRY.read_text())
REVIEWED_SOURCE=registry['aggregate_tested_source_commit']
REVIEWED_PUBLICATION='037bc3cbcfaed70fb0979a88dae47c9383c7cf0c'
PINS=registry['identities']
PRIOR={
 'c01-uninterrupted-unprepared-r1-20261010':'e5724e30f31b18673feb2a0f9d772bc8752873924fbd1cc0eeac598a8c47f17b',
 'c01-uninterrupted-unprepared-r2-20261010':'9416c3308d59ced178cb48f0b3c41c4fe75bfe99b2bfccfa8d9e3bc2e69aa23c',
 'c01-guard-choice-r1-20261010':'8cbb8b5dc447bb65ac99eb8c50c323e0ce25755c4a4f1b1794fb04f739fa42fe',
 'c01-guard-choice-opening4-r3-20261010':'0f49162fc55f438cb18cf4974ee529009397413d6f70ac83fa457b82841e02e6'}
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
runner=module('opening5_inherited',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
gate=module('opening5_reviewed_closed',ROOT/'scripts/test-f1-c01-guard-choice-r3.py')
sha=runner.sha;write=runner.write;git=runner.git
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def require(value,reason):
    if not value:raise AssertionError(reason)
def capacity(available,reservation):require(available>=reservation,'full unchanged storage reservation/headroom unavailable')
def verify_wiring():
    v=json.loads(WIRING.read_text());required={str(p.relative_to(ROOT)) for p in (Path(__file__),ROOT/'scripts/test-conserve-medicine-opening5-wiring-offline.py',CONTRACT)}
    require(v['PASS'] and v['named_scope_NEGATIVES']==len(PINS)+60 and v['new_output_freeze_claim_or_emulator']==0,'final scoped wiring checks missing')
    require(v['reviewed_identities']==PINS and v['generated_C_unchanged'] and v['compiled_observer_reused_exact'],'wiring tested a different observer')
    require(set(v['source_files'])==required,'wiring test source identity removed or added')
    for rel,h in v['source_files'].items():
        require(sha(ROOT/rel)==h,'tested wiring source changed: '+rel)
        require(hashlib.sha256(subprocess.check_output(['git','show',v['tested_wiring_source_commit']+':'+rel],cwd=ROOT)).hexdigest()==h,'wiring receipt commit/source mismatch')
    return v
def verify_files(f,a):
    copied=('observer.c','observer','game.sym','actual-ELF-bindings-private.json','native-ABI.s','native-ABI.o')
    names=set(copied)|{'opening.route','cold.route','transaction-proof-private.json','transaction-bindings.h','execution-contract.md','source-checkpoint.tar','reviewed-execution-binding.json','opening5-wiring-offline-receipt.json'}
    require(set(f['files'])=={str(OUT/name) for name in names},'frozen file identity removed or added')
    for name in copied:require(f['files'][str(OUT/name)]==a['artifacts'][name],'reviewed copied artifact identity waived')
    for mode,h in scope()['route_SHA256'].items():require(f['files'][str(OUT/(mode+'.route'))]==h,'reviewed route identity waived')
    for name,h in [('transaction-proof-private.json',PINS['compiled_context_proof']),('transaction-bindings.h',PINS['compiled_bindings']),('execution-contract.md',sha(CONTRACT)),('opening5-wiring-offline-receipt.json',sha(WIRING))]:
        require(f['files'][str(OUT/name)]==h,'reviewed proof/contract identity waived')
def scope():
    return {'schema':'c01-guard-choice-opening5/reviewed-hashes/v1',
      'reviewed_source_commit':REVIEWED_SOURCE,'reviewed_publication_commit':REVIEWED_PUBLICATION,
      'identities':PINS,'output_directory':str(OUT),'opening_ordinal':5,
      'opening_claims_allowed':1,'conditional_cold_claims_allowed':1,'prior_opening_claims':PRIOR,
      'opening_frame_limit':72000,'cold_frame_limit':6000,'encounter_frame_limit':36000,
      'contract_SHA256':sha(CONTRACT),
      'route_SHA256':{m:sha(ROOT/f'scripts/contracts/f1-c01-guard-choice-{m}.route') for m in ('opening','cold')}}
def verify_scope(record):
    require(canonical(record)==canonical(scope()),'named reviewed execution binding mismatch; no boolean or identity waiver')
def dependencies():
    d=runner.dependencies()
    for p in (CONTRACT,REGISTRY):d[str(p.relative_to(ROOT))]=sha(p)
    return d
def reviewed():
    history=module('opening5_immutable_history',ROOT/'scripts/test-f1-c01-guard-choice-opening4-r3.py')
    history.reviewed()
    a=json.loads((AGGREGATE/'admission-receipt.json').read_text())
    require(a['PASS'] and a['full_aggregate'] and a['gameplay_processes']==0,'fresh full aggregate absent')
    require(a['tested_source_commit']==REVIEWED_SOURCE and a['source_status_at_receipt']=='','fresh aggregate did not test exact clean source')
    require(sha(AGGREGATE/'admission-receipt.json')==PINS['aggregate_receipt'],'fresh aggregate receipt changed')
    for rel,h in a['dependencies'].items():
        require(sha(ROOT/rel)==h,'aggregate source dependency changed: '+rel)
        require(hashlib.sha256(subprocess.check_output(['git','show',REVIEWED_SOURCE+':'+rel],cwd=ROOT)).hexdigest()==h,'aggregate tested commit mismatch: '+rel)
    for rel,h in a['artifacts'].items():require(sha(AGGREGATE/rel)==h,'aggregate artifact changed: '+rel)
    host=module('opening5_fresh_host',ROOT/'scripts/floor1/conserve-medicine-host.py');code,_=host.generate(git)
    require(hashlib.sha256(code.encode()).hexdigest()==PINS['generated_observer']==sha(AGGREGATE/'observer.c'),'new generated observer changed')
    require(sha(AGGREGATE/'observer')==PINS['compiled_observer'],'new compiled observer changed')
    for key,path in [('validator',ROOT/'scripts/floor1/medicine-transaction.h'),('generator',ROOT/'scripts/floor1/conserve-medicine-host.py'),('policy',ROOT/'scripts/floor1/conserve-medicine-policy.h'),('model',ROOT/'scripts/floor1/conserve-medicine-model.py'),('integration',ROOT/'scripts/floor1/conserve-medicine-integration.h'),('inert_adapter',ROOT/'scripts/floor1/conserve-medicine-inert.py'),('proof_script',ROOT/'scripts/floor1/medicine-transaction-proof.py'),('compiled_context_proof',PROOF/'transaction-proof-private.json'),('compiled_bindings',PROOF/'transaction-bindings.h')]:
        require(sha(path)==PINS[key],'reviewed artifact identity changed: '+key)
    require(PINS['ELF']==runner.ELF_SHA and PINS['library']==sha(runner.TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5'),'native ELF/library changed')
    for name,h in PRIOR.items():
        d=OUT.parent/name;require(sha(d/'opening-exclusive-claim.json')==h,'prior claim changed')
        start=json.loads((d/'opening/process-started.json').read_text());stop=json.loads((d/'STOP.json').read_text())
        require(start['exclusive_claim_SHA256']==h and stop['actual_processes_started']==1 and stop['terminal_no_retry'],'prior claim/process/STOP changed')
        require(not(d/'cold-exclusive-claim.json').exists(),'unexpected old cold claim')
    require(not(OUT.parent/'c01-guard-choice-r2-20261010').exists(),'unused r2 slot consumed')
    return a
def prepare():
    require(not OUT.exists(),'one separately named preparation; existing output is terminal')
    require(not git('status','--porcelain'),'publish clean wiring before preparation')
    a=reviewed();wiring=verify_wiring();capacity(shutil.disk_usage(OUT.parent).free,runner.reservation());game=runner.verify_game()
    tools=dict(json.loads(Path('/workspace/scratch/c01a-journal-admission-r3-20261010/freeze.json').read_text())['tool_files'])
    for name in ('ffmpeg','ffprobe','python3'):tools[str(Path(shutil.which(name)).resolve())]=sha(shutil.which(name))
    for p,h in tools.items():require(sha(p)==h,'retained tool changed: '+p)
    OUT.mkdir()
    binding=scope();verify_scope(binding);write(OUT/'reviewed-execution-binding.json',binding)
    for name in ('observer.c','observer','game.sym','actual-ELF-bindings-private.json','native-ABI.s','native-ABI.o'):
        shutil.copyfile(AGGREGATE/name,OUT/name);require(sha(OUT/name)==a['artifacts'][name],'reviewed artifact copy differs: '+name)
    os.chmod(OUT/'observer',0o700);s=(OUT/'observer').lstat()
    executable={'SHA256':PINS['compiled_observer'],'owner_uid':s.st_uid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino}
    exec_check=module('opening5_execfile',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(OUT/'observer',executable)
    plans=module('opening5_routes',ROOT/'scripts/floor1/guard-choice-route.py').routes()
    for mode,text in plans.items():
        require(text==(ROOT/f'scripts/contracts/f1-c01-guard-choice-{mode}.route').read_text(),'reviewed route changed')
        (OUT/(mode+'.route')).write_text(text)
    for name in ('transaction-proof-private.json','transaction-bindings.h'):shutil.copyfile(PROOF/name,OUT/name)
    shutil.copyfile(CONTRACT,OUT/'execution-contract.md')
    shutil.copyfile(WIRING,OUT/'opening5-wiring-offline-receipt.json')
    with (OUT/'source-checkpoint.tar').open('wb') as f:subprocess.run(['git','archive','HEAD','scripts','AGENTS.md',str(CONTRACT.relative_to(ROOT)),str(REGISTRY.relative_to(ROOT))],cwd=ROOT,stdout=f,check=True)
    require((OUT/'source-checkpoint.tar').stat().st_size<32*runner.MiB,'source checkpoint exceeds budget')
    capacity(shutil.disk_usage(OUT).free,runner.reservation())
    frozen_dependencies=dependencies()
    f={'helper_commit':git('rev-parse','HEAD'),'base':runner.BASE,'compiled_game':runner.GAME,'engine_tree':runner.TREE,
      'ROM_SHA256':runner.ROM_SHA,'ELF_SHA256':runner.ELF_SHA,'output_directory':str(OUT),'reviewed_scope':binding,
      'reviewed_identities':PINS,'wiring_tested_source':wiring['tested_wiring_source_commit'],'wiring_receipt_SHA256':sha(WIRING),'source_verification':game,'native_ABI':a['native_ABI'],'binding_count':a['binding_count'],
      'files':{str(p):sha(p) for p in OUT.iterdir() if p.is_file()},'dependencies':frozen_dependencies,'tool_files':tools,
      'executable':executable,'executable_admission':exec_check,'storage':runner.storage(),'reservation_bytes':runner.reservation(),
      'available_bytes_at_freeze':shutil.disk_usage(OUT).free,'opening_ordinal':5,'opening_claims_allowed':1,'conditional_cold_claims_allowed':1,
      'first_failure_stop':True,'all_frames_captured':True,'chunk_frames':2000,'native_fps':'16777216/280896',
      'opening_frame_limit':72000,'cold_frame_limit':6000,'earlier_whole_battle_limits':36000,'wall_limit_seconds':600,
      'no_retry':True,'reviewed_production_observer_reused_without_rebuild':True,'independent_backup_verified':False}
    write(OUT/'freeze.json',f);print('PASS opening5 frozen exact reviewed executable/source/proof/routes/tools/full reservation; no claim or emulator')
def admission(out,mode):
    require(out.resolve()==OUT and mode in ('opening','cold'),'one named output and scoped mode only')
    require(not(OUT/'STOP.json').exists() and not(OUT/'PREPARATION-STOP.json').exists(),'terminal STOP; no retry')
    require(not(OUT/(mode+'-exclusive-claim.json')).exists() and not(OUT/mode).exists(),'claim or process directory already consumed')
    f=json.loads((OUT/'freeze.json').read_text());verify_scope(f['reviewed_scope'])
    require(f['output_directory']==str(OUT) and f['helper_commit']==git('rev-parse','HEAD') and not git('status','--porcelain'),'frozen published helper changed')
    require(f['reviewed_identities']==PINS and f['storage']==runner.storage() and f['reservation_bytes']==runner.reservation(),'frozen identities/bounds changed')
    verify_scope(json.loads((OUT/'reviewed-execution-binding.json').read_text()));a=reviewed();verify_wiring();runner.verify_game();verify_files(f,a)
    require(f['wiring_receipt_SHA256']==sha(WIRING),'frozen scoped wiring receipt changed')
    current=dependencies()
    require(f['dependencies']==current,'frozen source dependency identity removed or changed')
    for rel,h in f['dependencies'].items():require(sha(ROOT/rel)==h,'frozen source dependency changed: '+rel)
    for path,h in f['files'].items():require(sha(path)==h,'frozen file changed: '+path)
    for path,h in f['tool_files'].items():require(sha(path)==h,'frozen tool changed: '+path)
    module('opening5_admit_exec',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(OUT/'observer',f['executable'])
    if mode=='opening':require(not(OUT/'cold').exists() and not(OUT/'cold-exclusive-claim.json').exists(),'cold precedes opening')
    else:
        opening=OUT/'opening';v=json.loads((OUT/'opening-verdict-private.json').read_text());log=(opening/'runtime.log').read_text()
        require(v['PASS'] and v['helper']==f['helper_commit'] and v['mode']=='opening' and v['battle_attempts']==2,'actual opening verdict required')
        require(sha(opening/'game.sav')==v['actual_Save_SHA256'] and sha(opening/'runtime.log')==v['runtime_log_SHA256'],'successful actual Save/log changed')
        require('PASS CONTINUOUS phase=save' in log and not(opening/'errors.log').stat().st_size,'manual Save/native success missing')
        require((OUT/'opening-exclusive-claim.json').is_file() and (opening/'process-started.json').is_file(),'actual opening claim/process missing')
        claim=json.loads((OUT/'opening-exclusive-claim.json').read_text());start=json.loads((opening/'process-started.json').read_text())
        require(claim['freeze_SHA256']==sha(OUT/'freeze.json') and start['exclusive_claim_SHA256']==sha(OUT/'opening-exclusive-claim.json'),'actual opening freeze/claim binding changed')
        model=module('opening5_cold_admit_model',ROOT/'scripts/floor1/guard-choice-r2-state.py')
        model.disk_equivalence(opening/'game.sav',model.snapshot(opening/'phase-09-state.bin'))
    reserve=runner.reservation() if mode=='opening' else runner.storage()['cold']['limit_bytes']+256*runner.MiB
    capacity(shutil.disk_usage(OUT).free,reserve);return f
def execute(mode):
    runner.DEFAULT=OUT;runner.admission=admission;runner.execute(OUT,mode)
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','opening','cold'],required=True);args=p.parse_args()
    try:
        if args.stage=='prepare':prepare()
        else:execute(args.stage)
    except BaseException as error:
        if OUT.exists() and not(OUT/'STOP.json').exists() and not(OUT/'PREPARATION-STOP.json').exists():
            name='PREPARATION-STOP.json' if args.stage=='prepare' else 'STOP.json'
            write(OUT/name,{'mode':args.stage,'error':type(error).__name__,'reason':str(error),'terminal_no_retry':True,'claims_added_by_this_error_handler':0})
            (OUT/'wiring-errors.log').write_text(traceback.format_exc())
        raise
if __name__=='__main__':main()
