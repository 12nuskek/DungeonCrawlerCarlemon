#!/usr/bin/env python3
"""One named, hash-bound opening4 after explicit review; conditional cold only."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,shutil,stat,subprocess,traceback
if not __debug__:
    raise RuntimeError('opening4 requires enabled checks; no preparation or process')
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01-guard-choice-opening4-r3-20261010')
CONTRACT=ROOT/'docs/floor1/c01-guard-choice-opening4-r3-contract.md'
AGGREGATE=Path('/workspace/scratch/c01-medicine-transaction-offline-r3-20261010/aggregate-reviewed-offsets')
PROOF=AGGREGATE.parent/'reviewed-offsets-proof'
WIRING=Path('/workspace/scratch/c01-opening4-wiring-offline-r3-final-20261010/receipt.json')
REVIEWED_SOURCE='32a25769c5427656a010287bed6cf03c5f62b45c'
REVIEWED_PUBLICATION='fd73289ae75dcbb61b3fb2fbb576cdc605e53361'
PINS={
 'validator':'89501c5e2090a44d59ab880e5b1e36be5b47264cbdf3ce6389faee53a2790a78',
 'generator':'bcfc14f9879693db0183c005e35891beb4cf4ece2f69dd05fb0059d885268bbb',
 'proof_script':'0021349e5e5f8ed1bf76709799eb28d49d612c3f165307a3261d7eecc6ada436',
 'generated_observer':'a5d0fd49bb8a3cdff3653b7505d0e8d303716d4a1a4e7064dca8377ea68d2938',
 'compiled_observer':'8a7c91422d418d6b5e5b54938c0a4e0a4daa24f0110c55643ffa8b83832449ea',
 'ELF':'7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d',
 'library':'a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63',
 'compiled_context_proof':'7cbaee646dfc10b741a0b262b190f120d0284a2980c1ef872fa7784452aeb4f1',
 'compiled_bindings':'623e3b3c6a1f478151e995a093dd3048a7b326d6e6d86be377e8ac927b7a0fa4',
 'aggregate_receipt':'494cffaacee62baad875bf3956d66cf73bdfc7d9c7b0d816cdbf4ee3cdc218ee'}
PRIOR={
 'c01-uninterrupted-unprepared-r1-20261010':'e5724e30f31b18673feb2a0f9d772bc8752873924fbd1cc0eeac598a8c47f17b',
 'c01-uninterrupted-unprepared-r2-20261010':'9416c3308d59ced178cb48f0b3c41c4fe75bfe99b2bfccfa8d9e3bc2e69aa23c',
 'c01-guard-choice-r1-20261010':'8cbb8b5dc447bb65ac99eb8c50c323e0ce25755c4a4f1b1794fb04f739fa42fe'}
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
runner=module('opening4_inherited',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
gate=module('opening4_reviewed_closed',ROOT/'scripts/test-f1-c01-guard-choice-r3.py')
sha=runner.sha;write=runner.write;git=runner.git
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def require(value,reason):
    if not value:raise AssertionError(reason)
def capacity(available,reservation):require(available>=reservation,'full unchanged storage reservation/headroom unavailable')
def verify_wiring():
    v=json.loads(WIRING.read_text());required={str(p.relative_to(ROOT)) for p in (Path(__file__),ROOT/'scripts/test-guard-choice-opening4-wiring-offline.py',CONTRACT)}
    require(v['PASS'] and v['named_scope_NEGATIVES']==70 and v['new_output_freeze_claim_or_emulator']==0,'final scoped wiring checks missing')
    require(v['reviewed_identities']==PINS and v['generated_C_unchanged'] and v['compiled_observer_reused_exact'],'wiring tested a different observer')
    require(set(v['source_files'])==required,'wiring test source identity removed or added')
    for rel,h in v['source_files'].items():
        require(sha(ROOT/rel)==h,'tested wiring source changed: '+rel)
        require(hashlib.sha256(subprocess.check_output(['git','show',v['tested_wiring_source_commit']+':'+rel],cwd=ROOT)).hexdigest()==h,'wiring receipt commit/source mismatch')
    return v
def verify_files(f,a):
    copied=('observer.c','observer','game.sym','actual-ELF-bindings-private.json','native-ABI.s','native-ABI.o')
    names=set(copied)|{'opening.route','cold.route','transaction-proof-private.json','transaction-bindings.h','execution-contract.md','source-checkpoint.tar','reviewed-execution-binding.json','opening4-wiring-offline-receipt.json'}
    require(set(f['files'])=={str(OUT/name) for name in names},'frozen file identity removed or added')
    for name in copied:require(f['files'][str(OUT/name)]==a['artifacts'][name],'reviewed copied artifact identity waived')
    for mode,h in scope()['route_SHA256'].items():require(f['files'][str(OUT/(mode+'.route'))]==h,'reviewed route identity waived')
    for name,h in [('transaction-proof-private.json',PINS['compiled_context_proof']),('transaction-bindings.h',PINS['compiled_bindings']),('execution-contract.md',sha(CONTRACT)),('opening4-wiring-offline-receipt.json',sha(WIRING))]:
        require(f['files'][str(OUT/name)]==h,'reviewed proof/contract identity waived')
def scope():
    return {'schema':'c01-guard-choice-opening4/reviewed-hashes/v1',
      'reviewed_source_commit':REVIEWED_SOURCE,'reviewed_publication_commit':REVIEWED_PUBLICATION,
      'identities':PINS,'output_directory':str(OUT),'opening_ordinal':4,
      'opening_claims_allowed':1,'conditional_cold_claims_allowed':1,'prior_opening_claims':PRIOR,
      'opening_frame_limit':72000,'cold_frame_limit':6000,'encounter_frame_limit':36000,
      'contract_SHA256':sha(CONTRACT),
      'route_SHA256':{m:sha(ROOT/f'scripts/contracts/f1-c01-guard-choice-{m}.route') for m in ('opening','cold')}}
def verify_scope(record):
    require(canonical(record)==canonical(scope()),'named reviewed execution binding mismatch; no boolean or identity waiver')
def reviewed():
    require(gate.identities()==PINS,'reviewed source/build/proof identities changed')
    a=json.loads((AGGREGATE/'admission-receipt.json').read_text())
    require(a['tested_source_commit']==REVIEWED_SOURCE and a['source_status_at_receipt']=='','reviewed aggregate source was not exact/clean')
    closed=json.loads((PROOF/'transaction-admission-private.json').read_text());gate.verify_closed(closed,PINS)
    g=AGGREGATE.parent/'closed-gate-final/receipt.json'
    require(sha(g)=='c8b5ce612707d8b4321ce690a37eca4dca81c71811222d0a8ad984c4ccd5de53','reviewed closed-gate evidence changed')
    require(json.loads(g.read_text())['PASS'],'closed-gate negatives missing')
    for name,h in PRIOR.items():
        d=OUT.parent/name;require(sha(d/'opening-exclusive-claim.json')==h,'prior opening claim changed')
        start=json.loads((d/'opening/process-started.json').read_text());stop=json.loads((d/'STOP.json').read_text())
        require(start['exclusive_claim_SHA256']==h and stop['actual_processes_started']==1 and stop['terminal_no_retry'],'prior claim/process/terminal STOP mismatch')
        require(not(d/'cold-exclusive-claim.json').exists(),'unexpected historical cold claim')
    require(not(OUT.parent/'c01-guard-choice-r2-20261010').exists(),'unused r2 execution slot was consumed')
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
    exec_check=module('opening4_execfile',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(OUT/'observer',executable)
    plans=module('opening4_routes',ROOT/'scripts/floor1/guard-choice-route.py').routes()
    for mode,text in plans.items():
        require(text==(ROOT/f'scripts/contracts/f1-c01-guard-choice-{mode}.route').read_text(),'reviewed route changed')
        (OUT/(mode+'.route')).write_text(text)
    for name in ('transaction-proof-private.json','transaction-bindings.h'):shutil.copyfile(PROOF/name,OUT/name)
    shutil.copyfile(CONTRACT,OUT/'execution-contract.md')
    shutil.copyfile(WIRING,OUT/'opening4-wiring-offline-receipt.json')
    with (OUT/'source-checkpoint.tar').open('wb') as f:subprocess.run(['git','archive','HEAD','scripts','AGENTS.md',str(CONTRACT.relative_to(ROOT))],cwd=ROOT,stdout=f,check=True)
    require((OUT/'source-checkpoint.tar').stat().st_size<32*runner.MiB,'source checkpoint exceeds budget')
    capacity(shutil.disk_usage(OUT).free,runner.reservation())
    dependencies=runner.dependencies();dependencies[str(CONTRACT.relative_to(ROOT))]=sha(CONTRACT)
    f={'helper_commit':git('rev-parse','HEAD'),'base':runner.BASE,'compiled_game':runner.GAME,'engine_tree':runner.TREE,
      'ROM_SHA256':runner.ROM_SHA,'ELF_SHA256':runner.ELF_SHA,'output_directory':str(OUT),'reviewed_scope':binding,
      'reviewed_identities':PINS,'wiring_tested_source':wiring['tested_wiring_source_commit'],'wiring_receipt_SHA256':sha(WIRING),'source_verification':game,'native_ABI':a['native_ABI'],'binding_count':a['binding_count'],
      'files':{str(p):sha(p) for p in OUT.iterdir() if p.is_file()},'dependencies':dependencies,'tool_files':tools,
      'executable':executable,'executable_admission':exec_check,'storage':runner.storage(),'reservation_bytes':runner.reservation(),
      'available_bytes_at_freeze':shutil.disk_usage(OUT).free,'opening_ordinal':4,'opening_claims_allowed':1,'conditional_cold_claims_allowed':1,
      'first_failure_stop':True,'all_frames_captured':True,'chunk_frames':2000,'native_fps':'16777216/280896',
      'opening_frame_limit':72000,'cold_frame_limit':6000,'earlier_whole_battle_limits':36000,'wall_limit_seconds':600,
      'no_retry':True,'reviewed_production_observer_reused_without_rebuild':True,'independent_backup_verified':False}
    write(OUT/'freeze.json',f);print('PASS opening4 frozen exact reviewed executable/source/proof/routes/tools/full reservation; no claim or emulator')
def admission(out,mode):
    require(out.resolve()==OUT and mode in ('opening','cold'),'one named output and scoped mode only')
    require(not(OUT/'STOP.json').exists() and not(OUT/'PREPARATION-STOP.json').exists(),'terminal STOP; no retry')
    require(not(OUT/(mode+'-exclusive-claim.json')).exists() and not(OUT/mode).exists(),'claim or process directory already consumed')
    f=json.loads((OUT/'freeze.json').read_text());verify_scope(f['reviewed_scope'])
    require(f['output_directory']==str(OUT) and f['helper_commit']==git('rev-parse','HEAD') and not git('status','--porcelain'),'frozen published helper changed')
    require(f['reviewed_identities']==PINS and f['storage']==runner.storage() and f['reservation_bytes']==runner.reservation(),'frozen identities/bounds changed')
    verify_scope(json.loads((OUT/'reviewed-execution-binding.json').read_text()));a=reviewed();verify_wiring();runner.verify_game();verify_files(f,a)
    require(f['wiring_receipt_SHA256']==sha(WIRING),'frozen scoped wiring receipt changed')
    current=runner.dependencies();current[str(CONTRACT.relative_to(ROOT))]=sha(CONTRACT)
    require(f['dependencies']==current,'frozen source dependency identity removed or changed')
    for rel,h in f['dependencies'].items():require(sha(ROOT/rel)==h,'frozen source dependency changed: '+rel)
    for path,h in f['files'].items():require(sha(path)==h,'frozen file changed: '+path)
    for path,h in f['tool_files'].items():require(sha(path)==h,'frozen tool changed: '+path)
    module('opening4_admit_exec',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(OUT/'observer',f['executable'])
    if mode=='opening':require(not(OUT/'cold').exists() and not(OUT/'cold-exclusive-claim.json').exists(),'cold precedes opening')
    else:
        opening=OUT/'opening';v=json.loads((OUT/'opening-verdict-private.json').read_text());log=(opening/'runtime.log').read_text()
        require(v['PASS'] and v['helper']==f['helper_commit'] and v['mode']=='opening' and v['battle_attempts']==2,'actual opening verdict required')
        require(sha(opening/'game.sav')==v['actual_Save_SHA256'] and sha(opening/'runtime.log')==v['runtime_log_SHA256'],'successful actual Save/log changed')
        require('PASS CONTINUOUS phase=save' in log and not(opening/'errors.log').stat().st_size,'manual Save/native success missing')
        require((OUT/'opening-exclusive-claim.json').is_file() and (opening/'process-started.json').is_file(),'actual opening claim/process missing')
        claim=json.loads((OUT/'opening-exclusive-claim.json').read_text());start=json.loads((opening/'process-started.json').read_text())
        require(claim['freeze_SHA256']==sha(OUT/'freeze.json') and start['exclusive_claim_SHA256']==sha(OUT/'opening-exclusive-claim.json'),'actual opening freeze/claim binding changed')
        model=module('opening4_cold_admit_model',ROOT/'scripts/floor1/guard-choice-r2-state.py')
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
